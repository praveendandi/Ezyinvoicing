import datetime
import re
import sys
import traceback

import frappe
import pandas as pd
import requests

from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    convert_base64_to_image,
    format_date,
    get_address_from_zipcode,
)


# @frappe.whitelist(allow_guest=True)
def fetch_driving_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.3,
            "version": "v2",
            "filters": ["confidence", "detections", "predection", "file_name"],
        }
        image_response = requests.post(
            company.detection_api,
            json=post_data,
        )
        if image_response.status_code == 200:
            image_response = image_response.json()
            if "success" in image_response:
                return image_response
            # return image_response
            driving_details = driving_data_changes(image_response)
            if not driving_details["success"]:
                return driving_details
            return {"success": True, "data": driving_details["data"]}
        return image_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
            "fetch_driving_details"
        )
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
def driving_data_changes(message):
    try:
        data = message
        driving_details = {}
        if bool(data):
            company = frappe.get_last_doc("company")
            df = pd.json_normalize(data, sep="_")
            data = df.to_dict(orient="records")[0]
            dob_list = []
            if "driving_front_details_driving_front_details_DLNBR" in data:
                driving_details["local_id_number"] = data[
                    "driving_front_details_driving_front_details_DLNBR"
                ]
            if "driving_front_details_driving_front_details_NAME" in data:
                name = data["driving_front_details_driving_front_details_NAME"].strip()
                if "\n" in name:
                    name = name.split("\n")[0]
                driving_details["guest_first_name"] = name
            if "Driving_Front_Face_Image_base_64" in data:
                folder_path = frappe.utils.get_bench_path()
                site_folder_path = folder_path + "/sites/" + company.site_name
                face_image = convert_base64_to_image(
                    data["Driving_Front_Face_Image_base_64"],
                    "driving_image",
                    site_folder_path,
                    company,
                )
                if "success" not in face_image:
                    driving_details["face_image"] = face_image["message"]["file_url"]
            if "driving_front_details_driving_front_details_DOB" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB"].strip(),
                ):
                    try:
                        dob_list.append(
                            format_date(
                                data[
                                    "driving_front_details_driving_front_details_DOB"
                                ].strip(),
                                "yyyy-mm-dd",
                            )
                        )
                    except Exception as e:
                        print(str(e))
            if "driving_front_details_driving_front_details_DOB1" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB1"].strip(),
                ):
                    try:
                        dob_list.append(
                            format_date(
                                data[
                                    "driving_front_details_driving_front_details_DOB1"
                                ].strip(),
                                "yyyy-mm-dd",
                            )
                        )
                    except Exception as e:
                        print(str(e))
            if "driving_front_details_driving_front_details_DOB2" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB2"].strip(),
                ):
                    try:
                        dob_list.append(
                            format_date(
                                data[
                                    "driving_front_details_driving_front_details_DOB2"
                                ].strip(),
                                "yyyy-mm-dd",
                            )
                        )
                    except Exception as e:
                        print(str(e))
            if "driving_front_details_driving_front_details_DOB3" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB3"].strip(),
                ):
                    try:
                        dob_list.append(
                            format_date(
                                data[
                                    "driving_front_details_driving_front_details_DOB3"
                                ].strip(),
                                "yyyy-mm-dd",
                            )
                        )
                    except Exception as e:
                        print(str(e))
            if "driving_front_details_driving_front_details_DOB4" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB4"].strip(),
                ):
                    try:
                        dob_list.append(
                            format_date(
                                data[
                                    "driving_front_details_driving_front_details_DOB4"
                                ].strip(),
                                "yyyy-mm-dd",
                            )
                        )
                    except Exception as e:
                        print(str(e))
            if len(dob_list) > 0:
                dob_date = datetime.datetime.strptime(min(dob_list), "%Y-%m-%d").date()
                before_date = (
                    datetime.datetime.today() - datetime.timedelta(days=18 * 365)
                ).date()
                if dob_date < before_date:
                    driving_details["guest_dob"] = dob_date
            if "driving_address_details_driving_address_details_ADRESS" in data:
                address = data["driving_address_details_driving_address_details_ADRESS"]
                if address != "":
                    address = address.replace("Address:", "").strip()
                    address = address.replace("\n", " ")
                driving_details["address1"] = address
            if "driving_address_details_driving_address_details_PINCODE" in data:
                pincode = data[
                    "driving_address_details_driving_address_details_PINCODE"
                ]
                regex_complie = re.compile(r"^[1-9]{1}[0-9]{2}[0-9]{3}$")
                if re.match(regex_complie, pincode):
                    driving_details["zip_code"] = pincode
                    address_details = get_address_from_zipcode(pincode)
                    if address_details["success"]:
                        driving_details.update(address_details["data"])
        driving_details["guest_country"] = "IND"
        driving_details["guest_nationality"] = "IND"
        driving_details["status"] = "In House"
        driving_details["guest_id_type"] = "driving"
        return {"success": True, "data": driving_details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
            "driving_data_changes"
        )
        return {"success": False, "message": str(e)}
