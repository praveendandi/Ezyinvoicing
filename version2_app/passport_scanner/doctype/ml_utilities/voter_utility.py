import re

import frappe
import pandas as pd
import requests

from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    convert_base64_to_image,
    # get_address_from_zipcode,
)


@frappe.whitelist(allow_guest=True)
def fetch_voter_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.3,
            # "class": "aadhaar",
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
            data_changes = voter_data_changes(image_response)
            if not data_changes["success"]:
                return data_changes
            return {"success": True, "data": data_changes["data"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        frappe.log_error(str(e), "fetch_voter_details")
        return {"success": False, "message": str(e)}
    

def voter_data_changes(data):
    try:
        voter_details = {}
        if bool(data):
            df = pd.json_normalize(data, sep="_")
            data = df.to_dict(orient="records")[0]
            if "voter_address_details_voter_address_details_NAME" in data:
                voter_details["guest_first_name"] = data[
                    "voter_address_details_voter_address_details_NAME"
                ]
            if "voter_address_details_voter_address_details_DOB" in data:
                regex_complie = re.compile(
                    r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
                )
                if re.match(
                    regex_complie,
                    data["voter_address_details_voter_address_details_DOB"].strip(),
                ):
                    voter_details["guest_dob"] = frappe.utils.formatdate(
                        data["voter_address_details_voter_address_details_DOB"].strip(),
                        "yyyy-mm-dd",
                    )
        voter_details["guest_country"] = "IND"
        voter_details["guest_nationality"] = "IND"
        voter_details["status"] = "In House"
        voter_details["guest_id_type"] = "voterId"
        return {"success": True, "data": voter_details}
    except Exception as e:
        frappe.log_error(str(e), "voter_data_changes")
        return {"success": False, "message": str(e)}
