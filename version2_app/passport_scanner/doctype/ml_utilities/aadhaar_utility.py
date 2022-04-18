import re
import sys
import traceback

# import flatdict
import frappe
import pandas as pd
import requests

from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    convert_base64_to_image,
    format_date,
    get_address_from_zipcode,
)

# import datefinder


# @frappe.whitelist(allow_guest=True)
def fetch_aadhaar_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.4,
            "class": "aadhaar",
            "version": "v2",
            "filters": ["confidence", "detections", "predection", "file_name"],
        }
        image_response = requests.post(
            company.detection_api,
            json=post_data,
        )
        if image_response.status_code == 200:
            image_response = image_response.json()
            # return image_response
            if "success" in image_response:
                return image_response
            data_changes = aadhaar_data_changes(image_response)
            if not data_changes["success"]:
                return data_changes
            return {"success": True, "data": data_changes["data"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
            "fetch_aadhaar_details"
        )
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
def aadhaar_data_changes(data):
    try:
        company = frappe.get_last_doc("company")
        # data = flatdict.FlatDict(data, delimiter="_")
        aadhaar_details = {}
        # print(data,"******************88")
        if bool(data):
            # print(data,"this aadhar data")
            df = pd.json_normalize(data, sep="_")
            data = df.to_dict(orient="records")[0]
            if "Aadhar_Face_Image_base_64" in data:
                folder_path = frappe.utils.get_bench_path()
                site_folder_path = folder_path + "/sites/" + company.site_name
                face_image = convert_base64_to_image(
                    data["Aadhar_Face_Image_base_64"],
                    "aadhar_image",
                    site_folder_path,
                    company,
                )
                if "success" not in face_image:
                    aadhaar_details["face_image"] = face_image["message"]["file_url"]
            if "aadhar_front_details_aadhar_front_details_NAME" in data:
                aadhaar_details["guest_first_name"] = data[
                    "aadhar_front_details_aadhar_front_details_NAME"
                ]
            if "aadhar_front_details_aadhar_front_details_GENDER" in data:
                aadhaar_details["gender"] = data[
                    "aadhar_front_details_aadhar_front_details_GENDER"
                ]
            if "aadhar_no_details_aadhar_no" in data:
                aadhaar_details["local_id_number"] = "".join(
                    re.findall(r"\d+", data["aadhar_no_details_aadhar_no"])
                )
            if "aadhar_front_details_aadhar_front_details_DOB" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/|\s)([1-9]|0[1-9]|1[0-2])(\.|-|/|\s)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/|\s)([1-9]|0[1-9]|1[0-2])(\.|-|/|\s)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["aadhar_front_details_aadhar_front_details_DOB"].strip(),
                ):
                    try:
                        guest_dob = data[
                            "aadhar_front_details_aadhar_front_details_DOB"
                        ].strip()
                        guest_dob = guest_dob.replace(" ", "/")
                        aadhaar_details["guest_dob"] = format_date(
                            guest_dob,
                            "yyyy-mm-dd",
                        )
                    except Exception as e:
                        print(e)
            if "aadhar_back_details_aadhar_back_details_ADRESS" in data:
                address = data["aadhar_back_details_aadhar_back_details_ADRESS"]
                if address != "":
                    address = address.replace("Address:", "").strip()
                    address = address.replace("\n", " ")
                aadhaar_details["address1"] = address
            

            if "aadhar_back_details_aadhar_back_details_PINCODE" in data:
                pincode = ''.join([n for n in  data["aadhar_back_details_aadhar_back_details_PINCODE"] if n.isdigit()])
    
                regex_complie = re.compile(r"^[1-9]{1}[0-9]{2}[0-9]{3}$")
                if re.match(regex_complie, pincode):
                    aadhaar_details["zip_code"] = pincode
                    address_details = get_address_from_zipcode(pincode)
                    if address_details["success"]:
                        aadhaar_details.update(address_details["data"])
            if 'guest_state' not in aadhaar_details.keys() and "aadhar_back_details_aadhar_back_details_STATE" in data:
                aadhaar_details['guest_state'] = data[
                    "aadhar_back_details_aadhar_back_details_STATE"
                ]

            if "guest_city" not in aadhaar_details.keys() and "aadhar_back_details_aadhar_back_details_LOCATION" in data:
                aadhaar_details['guest_city'] = data[
                    "aadhar_back_details_aadhar_back_details_LOCATION"
                ]

        aadhaar_details["guest_country"] = "IND"
        aadhaar_details["guest_nationality"] = "IND"
        aadhaar_details["status"] = "In House"
        aadhaar_details["guest_id_type"] = "aadhaar"
        if "aadhar_back_no_details_aadhar_back_no" in data:
            if 'local_id_number' not in aadhaar_details.keys() and data["aadhar_back_no_details_aadhar_back_no"] != '':
                aadhaar_details["local_id_number"] = "".join(
                    re.findall(r"\d+", data["aadhar_back_no_details_aadhar_back_no"])
                )
            #     aadhaar_details["back_aadhaar_no"] = "".join(
            #         re.findall(r"\d+", data["aadhar_back_no_details_aadhar_back_no"])
            #     )
            # else:
            #     aadhaar_details["back_aadhaar_no"] = "".join(
            #         re.findall(r"\d+", data["aadhar_back_no_details_aadhar_back_no"])
            #     )
        # print(aadhaar_details,"heeelooo")
        return {"success": True, "data": aadhaar_details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
            "aadhaar_data_changes"
        )
        return {"success": False, "message": str(e)}
