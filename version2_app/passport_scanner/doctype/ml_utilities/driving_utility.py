import datetime
import re

import frappe
import pandas as pd
import requests

from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    convert_base64_to_image,
    format_date
)


@frappe.whitelist(allow_guest=True)
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
        frappe.log_error(str(e), "fetch_driving_details")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def driving_data_changes(message):
    try:
        data=message
        driving_details = {}
        if bool(data):
            company = frappe.get_last_doc("company")
            df = pd.json_normalize(data, sep="_")
            data = df.to_dict(orient="records")[0]
            dob_list = []
            if "driving_front_details_driving_front_details_NAME" in data:
                driving_details["guest_first_name"] = data[
                    "driving_front_details_driving_front_details_NAME"
                ].strip()
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
                    dob_list.append(
                        format_date(
                            data["driving_front_details_driving_front_details_DOB"].strip(),
                            "yyyy-mm-dd",
                        )
                    )
            if "driving_front_details_driving_front_details_DOB1" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB1"].strip(),
                ):
                    dob_list.append(
                        format_date(
                            data[
                                "driving_front_details_driving_front_details_DOB1"
                            ].strip(),
                            "yyyy-mm-dd",
                        )
                    )
            if "driving_front_details_driving_front_details_DOB2" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB2"].strip(),
                ):
                    dob_list.append(
                        format_date(
                            data[
                                "driving_front_details_driving_front_details_DOB2"
                            ].strip(),
                            "yyyy-mm-dd",
                        )
                    )
            if "driving_front_details_driving_front_details_DOB3" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB3"].strip(),
                ):
                    dob_list.append(
                        format_date(
                            data[
                                "driving_front_details_driving_front_details_DOB3"
                            ].strip(),
                            "yyyy-mm-dd",
                        )
                    )
            if "driving_front_details_driving_front_details_DOB4" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["driving_front_details_driving_front_details_DOB4"].strip(),
                ):
                    dob_list.append(
                        format_date(
                            data[
                                "driving_front_details_driving_front_details_DOB4"
                            ].strip(),
                            "yyyy-mm-dd",
                        )
                    )
            if len(dob_list) > 0:
                dob_date = datetime.datetime.strptime(min(dob_list), "%Y-%m-%d").date()
                before_date = (
                    datetime.datetime.today() - datetime.timedelta(days=18 * 365)
                ).date()
                if dob_date < before_date:
                    driving_details["guest_dob"] = dob_date
        driving_details["guest_country"] = "IND"
        driving_details["guest_nationality"] = "IND"
        driving_details["status"] = "In House"
        driving_details["guest_id_type"] = "driving"
        return {"success": True, "data": driving_details}
    except Exception as e:
        frappe.log_error(str(e), "driving_data_changes")
        return {"success": False, "message": str(e)}
