import base64
import sys
import traceback

import frappe
import pandas as pd
import pgeocode
import requests


def convert_base64_to_image(base, name, site_folder_path, company):
    try:
        file = site_folder_path + "/private/files/" + name + "face.png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, "rb")}
        payload = {"is_private": 1, "folder": "Home"}
        site = company.host
        upload_qr_image = requests.post(
            site + "api/method/upload_file", files=files, data=payload
        )
        response = upload_qr_image.json()
        if "message" in response:
            return response
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def get_address_from_zipcode(postal_code):
    try:
        data = {}
        geo_country = pgeocode.Nominatim("IN")
        location = geo_country.query_postal_code(postal_code)
        # if not pd.isna(location.community_name):
        #     data["location"] = location.community_name
        if not pd.isna(location.county_name):
            data["guest_city"] = location.county_name
        if not pd.isna(location.state_name):
            data["guest_state"] = location.state_name
        if not pd.isna(location.country_code):
            if location.country_code == "IN":
                data["guest_country"] = "IND"
                data["guest_nationality"] = "IND"
        return {"success": True, "data": data}
    except Exception as e:
        frappe.log_error(
            "Scan-update_company",
            traceback.format_exc(),
        )
        return {"success": False, "message": str(e)}
