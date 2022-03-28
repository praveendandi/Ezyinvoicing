import re

import frappe
# import pandas as pd
import requests

# from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
#     convert_base64_to_image,
#     get_address_from_zipcode,
# )


@frappe.whitelist(allow_guest=True)
def fetch_voter_details(image_1=None, image_2=None):
    try:
        company = frappe.get_last_doc("company")
        post_data = {
            "base": image_1 if image_1 is not None else image_2,
            "thresh": 0.5,
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
            return image_response
            # data_changes = aadhaar_data_changes(image_response)
            # if not data_changes["success"]:
            #     return data_changes
            # return {"success": True, "data": data_changes["data"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        frappe.log_error(str(e), "fetch_voter_details")
        return {"success": False, "message": str(e)}