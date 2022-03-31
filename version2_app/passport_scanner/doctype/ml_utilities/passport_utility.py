import os
import frappe
import pandas as pd
import requests

from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    convert_base64_to_image,
)


@frappe.whitelist(allow_guest=True) 
def fetch_passport_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.4,
            # "class": "indianpassport",
            "version": "v2",
            "filters": ["confidence", "detections", "predection", "file_name"],
            # "preprocess": True
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
            passport_details = passport_data_changes(image_response)
            if not passport_details["success"]:
                return passport_details
            return {"success": True, "data": passport_details["data"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        frappe.log_error(str(e), "fetch_aadhaar_details")
        return {"success": False, "message": str(e)}


# @frappe.whitelist(allow_guest=True)
def passport_data_changes(data):
    try:
        print(os.path.dirname(os.path.abspath(__file__)))
        # with open("visa-types.py", 'r') as data:
        #     print(data)
        passport_details = {}
        company = frappe.get_last_doc("company")
        if bool(data):
            df = pd.json_normalize(data, sep="_")
            data = df.to_dict(orient="records")[0]
            if "Passport_Face_Image_base_64" in data or "Visa_Image_base_64" in data:
                folder_path = frappe.utils.get_bench_path()
                site_folder_path = folder_path + "/sites/" + company.site_name
                face_image = convert_base64_to_image(
                    data["Passport_Face_Image_base_64"]
                    if "Passport_Face_Image_base_64" in data
                    else data["Visa_Image_base_64"],
                    "passport_image",
                    site_folder_path,
                    company,
                )
                if "success" not in face_image:
                    if "Visa_Image_base_64" in data:
                        passport_details["visa_face_image"] = face_image["message"][
                            "file_url"
                        ]
                    else:
                        passport_details["face_image"] = face_image["message"]["file_url"]
            if "passport_details_passport_details_surname" in data:
                passport_details["guest_last_name"] = data[
                    "passport_details_passport_details_surname"
                ]
            if "passport_details_passport_details_name" in data:
                passport_details["guest_first_name"] = data[
                    "passport_details_passport_details_name"
                ]
            if "passport_details_passport_details_birth_date" in data:
                passport_details["guest_dob"] = frappe.utils.formatdate(
                    data["passport_details_passport_details_birth_date"].strip(),
                    "yyyy-mm-dd",
                )
            if "passport_details_passport_details_expiry_date" in data:
                passport_details["passport_valid_till"] = frappe.utils.format_date(
                    data["passport_details_passport_details_expiry_date"].strip(),
                    "yyyy-mm-dd",
                )
            if "passport_details_passport_details_nationality" in data:
                passport_details["guest_nationality"] = data[
                    "passport_details_passport_details_nationality"
                ]
            if "passport_details_passport_details_country" in data:
                passport_details["guest_country"] = data[
                    "passport_details_passport_details_country"
                ]
                passport_details["passport_place_of_issued_country"] = data[
                    "passport_details_passport_details_country"
                ]
                if data["passport_details_passport_details_country"] == "IND":
                    passport_details["status"] = "In House"
                    passport_details["guest_id_type"] = "indianPassport"
                else:
                    passport_details["status"] = "Pending Review"
                    passport_details["guest_id_type"] = "Foreigner"
            if (
                "passport_details_passport_details_sex" in data
                or "visa_details_visa_details_sex" in data
            ):
                passport_details["gender"] = (
                    data["passport_details_passport_details_sex"]
                    if "passport_details_passport_details_sex" in data
                    else data["visa_details_visa_details_sex"]
                )
            if "passport_details_passport_details_document_number" in data:
                passport_details["passport_number"] = data[
                    "passport_details_passport_details_document_number"
                ]
            if "visa_details_visa_details_birth_date" in data:
                passport_details["visa_guest_dob"] = frappe.utils.formatdate(
                    data["visa_details_visa_details_birth_date"].strip(),
                    "yyyy-mm-dd",
                )
            if "visa_date_of_issue_visa_date_of_issue" in data:
                passport_details["visa_date_of_issue"] = frappe.utils.formatdate(
                    data["visa_date_of_issue_visa_date_of_issue"].strip(),
                    "yyyy-mm-dd",
                )
            if "visa_details_visa_details_expiry_date" in data:
                passport_details["visa_valid_till"] = frappe.utils.formatdate(
                    data["visa_details_visa_details_expiry_date"].strip(),
                    "yyyy-mm-dd",
                )
            if "visa_details_visa_details_document_number" in data:
                passport_details["visa_number"] = data[
                    "visa_details_visa_details_document_number"
                ]
            if "visa_type_visa_type" in data:
                passport_details["visa_type"] = data["visa_type_visa_type"]
        return {"success": True, "data": passport_details}
    except Exception as e:
        frappe.log_error(str(e), "fetch_aadhaar_details")
        return {"success": False, "message": str(e)}
