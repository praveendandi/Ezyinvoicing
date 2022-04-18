# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import datetime
import json
# from pydoc import doc
# from pydoc import doc
import re
import sys
# import os
import traceback

import frappe
import requests
from frappe.model.document import Document

# from version2_app.passport_scanner.doctype.dropbox.dropbox import (
#     merge_guest_to_guest_details,
# )
from version2_app.passport_scanner.doctype.guest_details.cform import intiate
from version2_app.passport_scanner.doctype.guest_details.pathik import intiate_pathik
from version2_app.passport_scanner.doctype.ml_utilities.common_utility import (
    format_date,
    get_address_from_zipcode,
)
from version2_app.events import guest_update_attachment_logs
from version2_app.passport_scanner.doctype.dropbox.dropbox import extract_id_details

class GuestDetails(Document):
    pass


@frappe.whitelist(allow_guest=True)
def empty_guest_details(name):
    try:
        get_doc = frappe.get_doc("Guest Details", name)
        get_columns = frappe.db.sql("""desc `tabGuest Details`""", as_dict=0)
        columns = list(zip(*get_columns))[0]
        column_dict = {
            key: None
            for key in columns
            if key
            not in [
                "_user_tags",
                "_comments",
                "_assign",
                "_liked_by",
                "name",
                "idx",
                "creation",
                "modified",
                "modified_by",
                "owner",
                "docstatus",
                "parent",
                "parentfield",
                "parenttype",
                "age"
            ]
        }
        column_dict["uploaded_to_opera"] = False
        column_dict["guest_age"] = 0
        column_dict["no_of_nights"] = 0
        column_dict["uploaded_to_frro"] = 0
        column_dict["frro_checkout"] = 0
        column_dict["no_of_adults"] = get_doc.no_of_adults
        column_dict["pending_pathik"] = get_doc.pending_pathik
        column_dict["no_of_children"] = get_doc.no_of_children
        column_dict["main_guest"] = get_doc.main_guest
        column_dict["confirmation_number"] = get_doc.confirmation_number
        column_dict["guest_first_name"] = "Guest"
        frappe.db.set_value("Guest Details", get_doc.name, column_dict)
        frappe.db.commit()
        return {"success": True, "message": "guest details are empty"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Ezy-Empty guest details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def guest_details_opera(confirmation_number):
    try:
        type = ""
        company_doc = frappe.get_last_doc("company")
        if company_doc.opera_scan == 1:
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists(
                    {
                        "doctype": "Precheckins",
                        "confirmation_number": confirmation_number,
                    }
                ):
                    guest_details = frappe.db.get_list(
                        "Precheckins",
                        filters={
                            "confirmation_number": ["like", confirmation_number + "%"]
                        },
                        fields=[
                            "name",
                            "confirmation_number",
                            "guest_first_name",
                            "guest_last_name",
                            "opera_scanned_status",
                            "guest_id_type",
                        ],
                        order_by="creation",
                    )
                    type = "ezy-checkins"
                else:
                    return {
                        "success": False,
                        "message": "Confirmation Number not found",
                    }
                return {"success": True, "data": guest_details, "type": type}
            else:
                return {
                    "success": False,
                    "message": "You dont have rights for ezy-checkins",
                }
            # elif company_doc.scan_ezy_module == 1 and company_doc.ezy_checkins_module == 0:
            #     if frappe.db.exists("Arrival Information", confirmation_number):
            #         guest_details = frappe.db.get_list("Arrival Information",filters={'name': confirmation_number},fields=["*"])
            #         type = "scan-ezy"
            #     else:
            #         return {"success":False,"message":"Confirmation Number not found"}
            # else:
            #     return {"success":False,"message":"You dont have rights"}

        else:
            return {"success": False, "message": "You dont have rights"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def helper_utility(data):
    try:
        company = frappe.get_last_doc("company")
        site_domain = (company.site_domain).rstrip("/")
        url = (
            site_domain+"/api/method/version2_app.passport_scanner.doctype.reservations.reservations."
            + data["api"]
        )
        del data["api"]
        x = requests.post(url, data=data)
        if x.status_code == 200:
            data = x.json()
            if not data["message"]["success"]:
                return data["message"]
            return {"success": True, "data": data["message"]}
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Helper Utility",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}


def convert_image_to_base64(image):
    try:
        with open(image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        # print(encoded_str)
        return {"success": True, "data": encoded_str}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}


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
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_guest_details(name):
    try:
        company_doc = frappe.get_last_doc("company")
        if company_doc.scan_ezy_module == 1 or company_doc.vision_api == 1:
            pre_checkins = frappe.get_doc("Precheckins", name)
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = folder_path + "/sites/" + company_doc.site_name
            file_path1 = ""
            file_path2 = ""
            if pre_checkins.image_1:
                if "private" in pre_checkins.image_1:
                    file_path1 = (
                        folder_path
                        + "/sites/"
                        + company_doc.site_name
                        + pre_checkins.image_1
                    )
                else:
                    file_path1 = (
                        folder_path
                        + "/sites/"
                        + company_doc.site_name
                        + "/public"
                        + pre_checkins.image_1
                    )
                convert1 = convert_image_to_base64(file_path1)
                if convert1["success"] is False:
                    return convert1
            if pre_checkins.image_2:
                if "private" in pre_checkins.image_2:
                    file_path2 = (
                        folder_path
                        + "/sites/"
                        + company_doc.site_name
                        + pre_checkins.image_2
                    )
                else:
                    file_path2 = (
                        folder_path
                        + "/sites/"
                        + company_doc.site_name
                        + "/public"
                        + pre_checkins.image_2
                    )
                # file_path2 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_2
                convert2 = convert_image_to_base64(file_path2)
                if convert2["success"] is False:
                    return convert2
            if pre_checkins.guest_id_type == "aadhaar":
                aadhar_details = {}
                if company_doc.scan_ezy_module == 1:
                    aadhar_details["scan_ezy"] = True
                else:
                    aadhar_details["scan_ezy"] = False
                if file_path1:
                    aadhar_details["pre_city"] = pre_checkins.guest_city
                    aadhar_details["pre_country"] = pre_checkins.guest_country
                    aadhar_details["pre_state"] = pre_checkins.guest_state
                    aadhar_details["pre_Nationality"] = pre_checkins.guest_nationality
                    aadhar_front = helper_utility(
                        {
                            "api": "scan_aadhar",
                            "aadhar_image": convert1["data"],
                            "scanView": "front",
                        }
                    )
                    if "success" in aadhar_front["data"]["message"].keys():
                        if aadhar_front["data"]["message"]["success"] is False:
                            aadhar_details["image_1"] = pre_checkins.image_1
                            aadhar_details["image_2"] = pre_checkins.image_2
                            aadhar_details.update(aadhar_front["data"]["message"])
                            del aadhar_details["success"]
                            del aadhar_details["aadhar_details"]
                            aadhar_details["id_type"] = "aadhaar"
                            return {"success": True, "data": aadhar_details}
                        # return aadhar_front["data"]["message"]
                    if (
                        "face"
                        in aadhar_front["data"]["message"]["aadhar_details"].keys()
                    ):
                        if aadhar_front["data"]["message"]["aadhar_details"]["face"]:
                            base_image = convert_base64_to_image(
                                aadhar_front["data"]["message"]["aadhar_details"][
                                    "face"
                                ],
                                name,
                                site_folder_path,
                                company_doc,
                            )
                            if "file_url" in base_image["message"].keys():
                                aadhar_details["face_url"] = base_image["message"][
                                    "file_url"
                                ]
                                del aadhar_front["data"]["message"]["aadhar_details"][
                                    "face"
                                ]
                    # aadhar_front["data"]["message"]["aadhar_details"]["front_image"] = aadhar_front["data"]["message"]["aadhar_details"]["base64_string"]
                    del aadhar_front["data"]["message"]["aadhar_details"][
                        "base64_string"
                    ]
                    aadhar_front["data"]["message"]["aadhar_details"][
                        "image_1"
                    ] = pre_checkins.image_1
                    aadhar_details.update(
                        aadhar_front["data"]["message"]["aadhar_details"]
                    )
                if file_path2:
                    aadhar_back = helper_utility(
                        {
                            "api": "scan_aadhar",
                            "aadhar_image": convert2["data"],
                            "scanView": "back",
                        }
                    )
                    if "message" in aadhar_back["data"].keys():
                        if aadhar_back["data"]["message"]["success"] is False:
                            aadhar_details["image_2"] = pre_checkins.image_2
                            aadhar_details.update(aadhar_back["data"]["message"])
                            del aadhar_details["success"]
                            del aadhar_details["aadhar_details"]
                            aadhar_details["id_type"] = "aadhaar"
                            aadhar_details[
                                "message"
                            ] = "Unable to fetch complete details"
                            return {"success": True, "data": aadhar_details}
                    else:
                        aadhar_details["image_2"] = pre_checkins.image_2
                        aadhar_details["id_type"] = "aadhaar"
                        return {"success": True, "data": aadhar_details}
                    # aadhar_back["data"]["message"]["aadhar_details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    del aadhar_back["data"]["message"]["aadhar_details"][
                        "base64_string"
                    ]
                    aadhar_back["data"]["message"]["aadhar_details"][
                        "image_2"
                    ] = pre_checkins.image_2
                    aadhar_details.update(
                        aadhar_back["data"]["message"]["aadhar_details"]
                    )
                aadhar_details["id_type"] = "aadhaar"
                if company_doc.scan_ezy_module == 1:
                    aadhar_details["scan_ezy"] = True
                else:
                    aadhar_details["scan_ezy"] = False
                return {"success": True, "data": aadhar_details}
            if pre_checkins.guest_id_type == "driving":
                driving_license_details = {}
                if company_doc.scan_ezy_module == 1:
                    driving_license_details["scan_ezy"] = True
                else:
                    driving_license_details["scan_ezy"] = False
                if file_path1:
                    driving_license_details["pre_city"] = pre_checkins.guest_city
                    driving_license_details["pre_country"] = pre_checkins.guest_country
                    driving_license_details["pre_state"] = pre_checkins.guest_state
                    driving_license_details[
                        "pre_Nationality"
                    ] = pre_checkins.guest_nationality
                    driving_license = helper_utility(
                        {
                            "api": "scan_driving_license",
                            "driving_image": convert1["data"],
                        }
                    )
                    if driving_license["data"]["message"]["success"] is False:
                        driving_license_details["image_1"] = pre_checkins.image_1
                        driving_license_details["image_2"] = pre_checkins.image_2
                        driving_license_details.update(
                            driving_license["data"]["message"]
                        )
                        del driving_license_details["success"]
                        del driving_license_details["driving_details"]
                        driving_license_details["id_type"] = "driving"
                        return {"success": True, "data": driving_license_details}
                        # return driving_license["data"]["message"]
                    if "driving_details" in driving_license["data"]["message"].keys():
                        if (
                            "face"
                            in driving_license["data"]["message"][
                                "driving_details"
                            ].keys()
                        ):
                            if driving_license["data"]["message"]["driving_details"][
                                "face"
                            ]:
                                base_image = convert_base64_to_image(
                                    driving_license["data"]["message"][
                                        "driving_details"
                                    ]["face"],
                                    name,
                                    site_folder_path,
                                    company_doc,
                                )
                                if "file_url" in base_image["message"].keys():
                                    driving_license_details["face_url"] = base_image[
                                        "message"
                                    ]["file_url"]
                                    del driving_license["data"]["message"][
                                        "driving_details"
                                    ]["face"]
                            # aadhar_front["data"]["message"]["driving_details"]["front_image"] = aadhar_front["data"]["message"]["driving_details"]["base64_string"]
                            del driving_license["data"]["message"]["driving_details"][
                                "base64_string"
                            ]
                            driving_license["data"]["message"]["driving_details"][
                                "image_1"
                            ] = pre_checkins.image_1
                            driving_license_details.update(
                                driving_license["data"]["message"]["driving_details"]
                            )
                driving_license_details["id_type"] = "driving"
                driving_license_details["image_1"] = pre_checkins.image_1
                driving_license_details["image_2"] = pre_checkins.image_2
                return {"success": True, "data": driving_license_details}
            if (
                pre_checkins.guest_id_type == "voterId"
                or pre_checkins.guest_id_type == "voter_id"
            ):
                voter_details = {}
                if company_doc.scan_ezy_module == 1:
                    voter_details["scan_ezy"] = True
                else:
                    voter_details["scan_ezy"] = False
                if file_path1:
                    voter_details["pre_city"] = pre_checkins.guest_city
                    voter_details["pre_country"] = pre_checkins.guest_country
                    voter_details["pre_state"] = pre_checkins.guest_state
                    voter_details["pre_Nationality"] = pre_checkins.guest_nationality
                    voter_front = helper_utility(
                        {
                            "api": "scan_votercard",
                            "voter_image": convert1["data"],
                            "scanView": "front",
                        }
                    )
                    if "success" in voter_front["data"]["message"].keys():
                        if voter_front["data"]["message"]["success"] is False:
                            voter_details["image_1"] = pre_checkins.image_1
                            voter_details["image_2"] = pre_checkins.image_2
                            voter_details["error"] = voter_front["data"]["message"][
                                "message"
                            ]
                            voter_details["message"] = "Unable to scan voter card"
                            voter_details["id_type"] = "voterId"
                            return {"success": True, "data": voter_details}
                            # return voter_front["data"]["message"]["voter_details"]
                    if "face" in voter_front["data"]["message"]["voter_details"]:
                        base_image = convert_base64_to_image(
                            voter_front["data"]["message"]["voter_details"]["face"],
                            name,
                            site_folder_path,
                            company_doc,
                        )
                        if "file_url" in base_image["message"].keys():
                            voter_details["face_url"] = base_image["message"][
                                "file_url"
                            ]
                            del voter_front["data"]["message"]["voter_details"]["face"]
                    # aadhar_front["data"]["message"]["voter_details"]["front_image"] = aadhar_front["data"]["message"]["voter_details"]["base64_string"]
                    del voter_front["data"]["message"]["voter_details"]["base64_string"]
                    voter_details["image_1"] = pre_checkins.image_1
                    voter_details.update(
                        voter_front["data"]["message"]["voter_details"]["data"]
                    )
                if file_path2:
                    voter_back = helper_utility(
                        {
                            "api": "scan_votercard",
                            "voter_image": convert2["data"],
                            "scanView": "back",
                        }
                    )
                    if "voter_details" in voter_back["data"]["message"].keys():
                        if voter_back["data"]["message"]["success"] is False:
                            voter_details["image_2"] = pre_checkins.image_2
                            voter_details["error"] = voter_back["data"]["message"][
                                "message"
                            ]
                            voter_details["id_type"] = "voterId"
                            voter_details[
                                "message"
                            ] = "Unable to fetch complete details"
                            return {"success": True, "data": voter_details}
                            # return voter_back["data"]["message"]["voter_details"]
                    # aadhar_back["data"]["message"]["voter_details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    del voter_back["data"]["message"]["voter_details"]["base64_string"]
                    voter_details["image_2"] = pre_checkins.image_2
                    voter_details.update(
                        voter_back["data"]["message"]["voter_details"]["data"]
                    )
                voter_details["id_type"] = "voterId"
                return {"success": True, "data": voter_details}
            if (
                pre_checkins.guest_id_type == "indianPassport"
                or pre_checkins.guest_id_type == "passport"
            ):
                passport_details = {}
                if company_doc.scan_ezy_module == 1:
                    passport_details["scan_ezy"] = True
                else:
                    passport_details["scan_ezy"] = False
                if file_path1:
                    passport_details["pre_city"] = pre_checkins.guest_city
                    passport_details["pre_country"] = pre_checkins.guest_country
                    passport_details["pre_state"] = pre_checkins.guest_state
                    passport_details["pre_Nationality"] = pre_checkins.guest_nationality
                    passport = helper_utility(
                        {
                            "api": "passportvisadetails",
                            "Passport_Image": convert1["data"],
                            "scan_type": "web",
                        }
                    )
                    if passport["data"]["message"]["success"] is False:
                        if "expired" in passport["data"]["message"].keys():
                            passport_details["pass_expired"] = passport["data"][
                                "message"
                            ]["expired"]
                        else:
                            passport_details["visa_expired"] = False
                        passport_details["image_1"] = pre_checkins.image_1
                        passport_details["image_2"] = pre_checkins.image_2
                        passport_details["passport_message"] = passport["data"][
                            "message"
                        ]["message"]
                        passport_details["id_type"] = (
                            "Foreign"
                            if pre_checkins.guest_id_type == "passport"
                            else pre_checkins.guest_id_type
                        )
                        # return {"success": True,"data":passport_details}
                        # return passport["data"]["message"]
                    if passport["data"]["message"]["success"] is True:
                        passport_details["pass_expired"] = False
                        if "face" in passport["data"]["message"]["details"].keys():
                            base_image = convert_base64_to_image(
                                passport["data"]["message"]["details"]["face"],
                                name,
                                site_folder_path,
                                company_doc,
                            )
                            if "file_url" in base_image["message"].keys():
                                passport_details["face_url"] = base_image["message"][
                                    "file_url"
                                ]
                                del passport["data"]["message"]["details"]["face"]
                        passport_details["image_1"] = pre_checkins.image_1
                    if "details" in passport["data"]["message"].keys():
                        if "data" in passport["data"]["message"]["details"].keys():
                            if (
                                "Date_of_Birth"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Date_of_birth"] = passport[
                                    "data"
                                ]["message"]["details"]["data"]["Date_of_Birth"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Date_of_Birth"
                                ]
                            if (
                                "country_code"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_country_code"] = passport[
                                    "data"
                                ]["message"]["details"]["data"]["country_code"]
                                del passport["data"]["message"]["details"]["data"][
                                    "country_code"
                                ]
                            if (
                                "FamilyName"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_FamilyName"] = passport["data"][
                                    "message"
                                ]["details"]["data"]["FamilyName"]
                                del passport["data"]["message"]["details"]["data"][
                                    "FamilyName"
                                ]
                            if (
                                "Given_Name"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Given_Name"] = passport["data"][
                                    "message"
                                ]["details"]["data"]["Given_Name"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Given_Name"
                                ]
                            if (
                                "Date_of_Issue"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Date_of_Issue"] = passport[
                                    "data"
                                ]["message"]["details"]["data"]["Date_of_Issue"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Date_of_Issue"
                                ]
                            if (
                                "Nationality"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Nationality"] = passport["data"][
                                    "message"
                                ]["details"]["data"]["Nationality"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Nationality"
                                ]
                            if (
                                "Date_of_Birth"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Date_of_Birth"] = passport[
                                    "data"
                                ]["message"]["details"]["data"]["Date_of_Birth"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Date_of_Birth"
                                ]
                            if (
                                "Gender"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Gender"] = passport["data"][
                                    "message"
                                ]["details"]["data"]["Gender"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Gender"
                                ]
                            if (
                                "Date_of_Expiry"
                                in passport["data"]["message"]["details"]["data"].keys()
                            ):
                                passport_details["pass_Date_of_Expiry"] = passport[
                                    "data"
                                ]["message"]["details"]["data"]["Date_of_Expiry"]
                                del passport["data"]["message"]["details"]["data"][
                                    "Date_of_Expiry"
                                ]
                            # aadhar_front["data"]["message"]["details"]["front_image"] = aadhar_front["data"]["message"]["aadhar_details"]["base64_string"]
                            # del passport["data"]["message"]["details"]["base64_string"]
                            passport_details.update(
                                passport["data"]["message"]["details"]["data"]
                            )

                if file_path2:
                    if pre_checkins.guest_id_type == "passport":
                        visa_details = helper_utility(
                            {
                                "api": "passportvisadetails",
                                "Passport_Image": convert2["data"],
                                "scan_type": "web",
                            }
                        )
                        if visa_details["data"]["message"]["success"] is False:
                            if "expired" in visa_details["data"]["message"].keys():
                                passport_details["visa_expired"] = visa_details["data"][
                                    "message"
                                ]["expired"]
                            else:
                                passport_details["visa_expired"] = False
                            passport_details["image_2"] = pre_checkins.image_2
                            error_message = visa_details["data"]["message"]["message"]
                            del visa_details["data"]["message"]["message"]
                            if "details" in visa_details["data"]["message"].keys():
                                if (
                                    "data"
                                    in visa_details["data"]["message"]["details"].keys()
                                ):
                                    passport_details.update(
                                        visa_details["data"]["message"]["details"][
                                            "data"
                                        ]
                                    )
                            passport_details["visa_message"] = error_message
                            passport_details["id_type"] = "Foreign"
                            return {"success": True, "data": passport_details}

                        passport_details["visa_expired"] = False
                        passport_details.update(
                            visa_details["data"]["message"]["details"]["data"]
                        )
                    else:
                        visa_details = helper_utility(
                            {
                                "api": "passport_address",
                                "Passport_Image": convert2["data"],
                            }
                        )
                        if visa_details["data"]["message"]["success"] is False:
                            passport_details["image_2"] = pre_checkins.image_2
                            passport_details.update(visa_details["data"]["message"])
                            del passport_details["success"]
                            passport_details["id_type"] = pre_checkins.guest_id_type
                            return {"success": True, "data": passport_details}
                        passport_details.update(visa_details["data"]["message"]["data"])
                    # aadhar_back["data"]["message"]["details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    # del visa_details["data"]["message"]["details"]["data"]["base64_string"]
                    passport_details["image_2"] = pre_checkins.image_2
                passport_details["id_type"] = (
                    pre_checkins.guest_id_type
                    if pre_checkins.guest_id_type == "indianPassport"
                    else "Foreign"
                )
                return {"success": True, "data": passport_details}
            if pre_checkins.guest_id_type == "OCI":
                pass
            if (
                pre_checkins.guest_id_type == "other"
                or pre_checkins.guest_id_type == "others"
            ):
                other_details = {}
                if file_path1:
                    driving_license = helper_utility(
                        {"api": "other_images", "image": convert1["data"]}
                    )
                    if driving_license["data"]["message"]["success"] is False:
                        other_details["image_1"] = pre_checkins.image_1
                        other_details["image_2"] = pre_checkins.image_2
                        other_details.update(driving_license["data"]["message"])
                        del other_details["success"]
                        other_details["id_type"] = "other"
                        return {"success": True, "data": other_details}
                        # return driving_license["data"]["message"]
                    if driving_license["data"]["message"]["otherimage_details"][
                        "base64_string"
                    ]:
                        base_image = convert_base64_to_image(
                            driving_license["data"]["message"]["otherimage_details"][
                                "base64_string"
                            ],
                            name,
                            site_folder_path,
                            company_doc,
                        )
                        if "file_url" in base_image["message"].keys():
                            other_details["image_1"] = base_image["message"]["file_url"]
                            del driving_license["data"]["message"][
                                "otherimage_details"
                            ]["base64_string"]
                if file_path2:
                    back2 = helper_utility(
                        {"api": "other_images", "image": convert2["data"]}
                    )
                    if back2["data"]["message"]["success"] is False:
                        other_details["image_2"] = pre_checkins.image_2
                        other_details.update(driving_license["data"]["message"])
                        del other_details["success"]
                        other_details["id_type"] = "other"
                        return {"success": True, "data": other_details}
                    if back2["data"]["message"]["otherimage_details"]["base64_string"]:
                        base_image = convert_base64_to_image(
                            back2["data"]["message"]["otherimage_details"][
                                "base64_string"
                            ],
                            name,
                            site_folder_path,
                            company_doc,
                        )
                        if "file_url" in base_image["message"].keys():
                            other_details["image_2"] = base_image["message"]["file_url"]
                            del back2["data"]["message"]["otherimage_details"][
                                "base64_string"
                            ]
                other_details["id_type"] = "other"
                if company_doc.scan_ezy_module == 1:
                    other_details["scan_ezy"] = True
                else:
                    other_details["scan_ezy"] = False
                return {"success": True, "data": other_details}
        else:
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists({"doctype": "Precheckins", "name": name}):
                    guest_details = frappe.db.get_value(
                        "Precheckins",
                        name,
                        [
                            "guest_first_name",
                            "guest_last_name",
                            "guest_last_name",
                            "no_of_adults",
                            "no_of_children",
                            "confirmation_number",
                            "address1",
                            "address2",
                            "zip_code",
                            "guest_city",
                            "guest_state",
                            "guest_country",
                            "guest_dob",
                            "guest_age",
                            "guest_nationality",
                            "gender",
                            "arrival_date",
                            "coming_from",
                            "departure_date",
                            "company",
                            "guest_id_type",
                            "image_1",
                            "image_2",
                            "going_to",
                        ],
                        as_dict=1,
                    )
                    guest_details["id_type"] = (
                        guest_details.guest_id_type
                        if guest_details.guest_id_type != "passport"
                        else "Foreign"
                    )
                    guest_details["reference"] = "No-Vision"
                    return {"success": True, "data": guest_details}
                else:
                    return {
                        "success": False,
                        "message": "Confirmation Number not found",
                    }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def add_guest_details():
    try:
        data = json.loads(frappe.request.data)
        data = data["data"]
        pre_checkins_count = 0
        company_doc = frappe.get_last_doc("company")
        if company_doc.scan_ezy_module == 1:
            if frappe.db.exists(
                {
                    "doctype": "Arrival Information",
                    "name": data["confirmation_number"],
                    "status": "Scanned",
                    "booking_status": "CHECKED OUT",
                }
            ):
                return {
                    "success": False,
                    "message": "Guest already scanned on this confirmation number",
                }
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = folder_path + "/sites/" + company_doc.site_name
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists(
                    {
                        "doctype": "Precheckins",
                        "confirmation_number": data["confirmation_number"],
                    }
                ):
                    pre_checkins_count = frappe.db.get_value(
                        "Precheckins",
                        {"confirmation_number": data["confirmation_number"]},
                        "no_of_adults",
                    )
            # if company_doc.ezy_checkins_module == 0 and company_doc.scan_ezy_module == 1:
            #     pre_checkins_count = frappe.db.get_value('Arrival Information',{"confirmation_number":data["confirmation_number"]},"no_of_adults")
            if "-" in data["confirmation_number"]:
                data["confirmation_number"] = data["confirmation_number"].split("-")[0]
            scan_guest_details = frappe.db.count(
                "Guest Details", {"confirmation_number": data["confirmation_number"]}
            )
            name = data["given_name"] + data["confirmation_number"] + data["id_type"]
            if data["id_image1"]:
                if (
                    "private" not in data["id_image1"]
                    and "/files/" not in data["id_image1"]
                ):
                    image_1 = convert_base64_to_image(
                        data["id_image1"], name, site_folder_path, company_doc
                    )
                    if image_1["message"] is False:
                        return image_1
                    data["id_image1"] = image_1["message"]["file_url"]
            if data["id_image2"]:
                if (
                    "private" not in data["id_image2"]
                    and "/files/" not in data["id_image2"]
                ):
                    image_2 = convert_base64_to_image(
                        data["id_image2"], name, site_folder_path, company_doc
                    )
                    if image_2["message"] is False:
                        return image_2
                    data["id_image2"] = image_2["message"]["file_url"]
            if "face_image" in data.keys():
                if data["face_image"] != "":
                    if (
                        "private" not in data["face_image"]
                        and "/files/" not in data["face_image"]
                    ):
                        face = convert_base64_to_image(
                            data["face_image"], name, site_folder_path, company_doc
                        )
                        if face["message"] is False:
                            return face
                        data["face_image"] = face["message"]["file_url"]
            data["doctype"] = "Guest Details"
            data["id_type"] = (
                "Foreigner" if data["id_type"] == "Foreign" else data["id_type"]
            )
            if company_doc.ezy_checkins_module == 1:
                if (
                    frappe.db.exists(
                        {
                            "doctype": "Precheckins",
                            "confirmation_number": data["confirmation_number"],
                        }
                    )
                    and "guest_id" in data.keys()
                ):
                    pre_doc = frappe.get_doc("Precheckins", data["guest_id"])
                    pre_doc.opera_scanned_status = "Scanned"
                    # arrival_doc.booking_status = "CHECKED IN"
                    pre_doc.guest_first_name = data["given_name"]
                    if "sur_name" in data.keys():
                        pre_doc.guest_last_name = (
                            data["sur_name"] if data["sur_name"] else ""
                        )
                    else:
                        pre_doc.guest_last_name = (
                            data["surname"] if data["surname"] else ""
                        )
                    pre_doc.save(ignore_permissions=True, ignore_version=True)
                    del data["guest_id"]
            if "address1" in data.keys():
                data["address"] = data["address1"]
                del data["address1"]
            if "address2" in data.keys():
                if data["address2"] != "":
                    if re.search(r"\d{6}", data["address2"]):
                        postal_code = re.match(
                            r"^.*(?P<zipcode>\d{6}).*$", data["address2"]
                        ).groupdict()["zipcode"]
                        data["postal_code"] = (
                            postal_code if len(postal_code) == 6 else ""
                        )
            if frappe.db.exists("Arrival Information", data["confirmation_number"]):
                now = datetime.datetime.now()
                arrival_doc = frappe.get_doc(
                    "Arrival Information", data["confirmation_number"]
                )
                data["no_of_nights"] = arrival_doc.no_of_nights
                data["checkin_date"] = arrival_doc.arrival_date
                data["checkin_time"] = now.strftime("%H:%M:%S")
            if data["id_type"] == "Foreigner":
                if frappe.db.exists(
                    {
                        "doctype": "Precheckins",
                        "confirmation_number": data["confirmation_number"],
                    }
                ):
                    pre_checkins = frappe.db.get_value(
                        "Precheckins",
                        {"confirmation_number": data["confirmation_number"]},
                        ["address1", "guest_city", "guest_country"],
                        as_dict=1,
                    )
                    data["address"] = pre_checkins["address1"]
                    data["city"] = pre_checkins["guest_city"]
                    data["country"] = pre_checkins["guest_country"]
            if data["date_of_birth"] != "":
                today = datetime.datetime.today()
                birthDate = datetime.datetime.strptime(
                    data["date_of_birth"], "%Y-%m-%d"
                )
                data["age"] = (
                    today.year
                    - birthDate.year
                    - ((today.month, today.day) < (birthDate.month, birthDate.day))
                )
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True, ignore_links=True)
            if frappe.db.exists("Arrival Information", data["confirmation_number"]):
                arrival_doc = frappe.get_doc(
                    "Arrival Information", data["confirmation_number"]
                )
                if frappe.db.exists(
                    {
                        "doctype": "Precheckins",
                        "confirmation_number": data["confirmation_number"],
                    }
                ):
                    if (scan_guest_details + 1) == pre_checkins_count:
                        arrival_doc.status = "Scanned"
                        arrival_doc.booking_status = "CHECKED IN"
                    else:
                        if (scan_guest_details + 1) < pre_checkins_count:
                            arrival_doc.status = "Partial Scanned"
                            arrival_doc.booking_status = "CHECKED IN"
                else:
                    if arrival_doc.no_of_adults:
                        pre_checkins_count = arrival_doc.no_of_adults
                    if pre_checkins_count == 0:
                        arrival_doc.status = "Scanned"
                        arrival_doc.booking_status = "CHECKED IN"
                    else:
                        if (scan_guest_details + 1) == pre_checkins_count:
                            arrival_doc.status = "Scanned"
                        else:
                            if (scan_guest_details + 1) < pre_checkins_count:
                                arrival_doc.status = "Partial Scanned"
                                arrival_doc.booking_status = "CHECKED IN"
                arrival_doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
            else:
                arrival_date = datetime.datetime.now().date()
                arrival_info_doc = frappe.get_doc(
                    {
                        "doctype": "Arrival Information",
                        "confirmation_number": data["confirmation_number"],
                        "status": "Scanned",
                        "booking_status": "CHECKED IN",
                        "arrival_date": arrival_date,
                        "company": company_doc.name,
                        "virtual_checkin_status": "Yes",
                        "guest_first_name": data["given_name"],
                    }
                )
                arrival_info_doc.insert(ignore_permissions=True, ignore_links=True)
            return {"success": True, "message": "Guest added"}
        else:
            return {"success": False, "message": "Scan-Ezy module is not enabled"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Add Guest Details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def process_cform():
    try:
        # data=json.loads(frappe.request.data)
        # data = data["data"]
        # company = frappe.get_last_doc("company")
        # if company.cform_session == 1:
        #     return {"success":False,"message":"Already cform inpogress"}
        cform = intiate()
        return {"success": True, "message": cform}
        # company_doc.cform_session = 0
        # company_doc.save(ignore_permissions=True,ignore_version=True)
    except Exception as e:
        print(str(e), "====================")
        # company_doc = frappe.get_doc('company',company.name)
        # company_doc.cform_session = 0
        # company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Process Cform",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def process_pathik(guest_details):
    company = frappe.get_last_doc("company")
    try:
        guest_details = json.loads(guest_details)
        if len(guest_details) == 0:
            return {"success": False, "message": "Please select the guests"}
        if company.pathik == 0:
            return {"success": False, "message": "Pathik is in disable mode"}
        if not (company.pathik_username and company.pathik_password):
            return {"success": False, "message": "Username and password not found"}
        if company.pathik_session == 1:
            return {"success": False, "message": "Already Pathik inpogress"}
        company_status = update_company(company.name, {"pathik_session": 1})
        if company_status["success"] is False:
            return company_status
        obj = {"userId": company.pathik_username, "password": company.pathik_password}
        status = intiate_pathik(obj, guest_details)
        update_company(company.name, {"pathik_session": 0})
        if company_status["success"] is False:
            return company_status
        return status
    except Exception as e:
        update_company(company.name, {"pathik_session": 0})
        if company_status["success"] is False:
            return company_status
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Process Pathik",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def update_company(company_code, obj):
    try:
        frappe.db.set_value("company", company_code, obj)
        frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-update_company",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def guest_details_for_opera(confirmation_number: str = None):
    try:
        company = frappe.get_last_doc("company")
        if confirmation_number:
            if not frappe.db.exists("Arrival Information", confirmation_number):
                return {"success": False, "message": "reservation not found"}
            arrival_info = frappe.db.get_value('Arrival Information', confirmation_number, ["guest_first_name","guest_last_name","no_of_adults"], as_dict=True)
            # if company.ome_scanner == 1:
            #     if not frappe.db.exists("Dropbox", {"merged_to": confirmation_number}):
            #         return {"success": True, "arrival": arrival_info, "is_guest_details": False}
            if not frappe.db.exists(
                "Guest Details", {"confirmation_number": confirmation_number}
            ):
                return {"success": True, "arrival": arrival_info, "is_guest_details": False}
            else:
                get_guest_details = frappe.db.get_list(
                    "Guest Details",
                    filters={"confirmation_number": confirmation_number},
                    fields=[
                        "guest_full_name",
                        "confirmation_number",
                        "guest_first_name",
                        "name",
                        "guest_id_type",
                        "uploaded_to_opera"
                    ],
                    order_by='creation asc'
                )
                get_booking_status = frappe.db.get_value("Arrival Information", confirmation_number, "booking_status")
                get_guest_details = [dict(item, booking_status=get_booking_status) for item in get_guest_details]
                return {"success": True, "data": get_guest_details, "arrival": arrival_info, "is_guest_details": True, "type": "scan-ezy"}
        else:
            return {
                "success": False,
                "message": "please enter a valid confirmation number",
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-guest_details_for_opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def opera_scan_api(type=None, name=None, image_1=None, image_2=None, document_type=None):
    try:
        if frappe.db.exists("Guest Details", name):
            guest_details = frappe.db.get_value("Guest Details", name, ["id_image1","id_image2","confirmation_number","guest_id_type"], as_dict=1)
            if type == "rotate":
                get_data = get_data_vision_api(image_1, image_2, name, guest_details["guest_id_type"], type, False, guest_details["confirmation_number"])
                return get_data
            if type == "upload":
                if document_type:
                    guest_details["guest_id_type"] = document_type
                if image_1 or image_2:
                    get_data = get_data_vision_api(image_1, image_2, name, guest_details["guest_id_type"], type, False, guest_details["confirmation_number"])
                else:
                    get_data = get_data_vision_api(guest_details["id_image1"], guest_details["id_image2"], name, guest_details["guest_id_type"], type, True, guest_details["confirmation_number"])
                return get_data
            if type == "refetch":
                get_data = get_data_vision_api(guest_details["id_image1"], guest_details["id_image2"], name, guest_details["guest_id_type"], type, True, guest_details["confirmation_number"])
                return get_data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-opera_scan_api",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": "something went wrong"}

def get_aadhaar_data(image1=None, image2=None):
    try:
        details = {}
        if image1:
            aadhar_front = helper_utility(
                        {
                            "api": "scan_aadhar",
                            "aadhar_image": image1,
                            "scanView": "front",
                        }
                    )
            if not aadhar_front["success"]:
                return aadhar_front
            details.update(aadhar_front["data"])
        if image2:
            aadhar_back = helper_utility(
                        {
                            "api": "scan_aadhar",
                            "aadhar_image": image2,
                            "scanView": "back",
                        }
                    )
            if not aadhar_back["success"]:
                return aadhar_back
            details.update(aadhar_back["data"])
        if bool(details):
            aadhaar_details = localids_details_change(details)
            if not aadhaar_details["success"]:
                return aadhaar_details
            return {"success": True, "data": aadhaar_details["data"]}
        return {"success":False, "data": {}}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-get_aadhaar_data",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": "something went wrong"}

def localids_details_change(data):
    try:
        details = {}
        if "Date_of_birth" in data:
            check_dob = check_date(data["Date_of_birth"])
            if check_dob:
                details["guest_dob"] = check_dob
        if "sex" in data:
            if data["sex"] in ["male", "Male", "MALE", "M", "m"]:
                details["gender"] = "MALE"
            if data["sex"] in ["Female", "FeMale", "FEMALE", "F", "f"]:
                details["gender"] = "FEMALE"
        if "uid" in data:
            details["local_id_number"] = data["uid"].replace(" ", "")
        if "name" in data:
            details["guest_first_name"] = data["name"]
        if "postal_code" in data:
            pincode = data["postal_code"]
            regex_complie = re.compile(r"^[1-9]{1}[0-9]{2}[0-9]{3}$")
            if re.match(regex_complie, pincode):
                details["zip_code"] = pincode
                address_details = get_address_from_zipcode(pincode)
                if address_details["success"]:
                    details.update(address_details["data"])
        if "person_address" in data:
            details["address1"] = data["person_address"]
        if bool(details):
            details["guest_nationality"] = "IND"
            details["guest_country"] = "IND"
            details["status"] = "In House"
            details["guest_id_type"] = "aadhaar"
        return {"success": True, "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-localids_details_change",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}
        
def get_passport_details(image1=None, image2=None, document_type=None):
    try:
        details = {}
        if document_type:
            if image1:
                passport_front = helper_utility(
                            {
                                "api": "passportvisadetails",
                                "Passport_Image": image1,
                                "scan_type": "web",
                            }
                        )
                if not passport_front["success"]:
                    return passport_front
                details.update(passport_front["data"])
            if image2:
                if document_type == "Foreigner":
                    passport_back = helper_utility(
                                {
                                    "api": "passportvisadetails",
                                    "Passport_Image": image2,
                                    "scan_type": "web",
                                }
                            )
                    if not passport_back["success"]:
                        return passport_back
                    passport_back_details = passport_back["data"]
                    if "Given_Name" in passport_back_details:
                        passport_back_details["Visa_Given_Name"] = passport_back_details["Given_Name"]
                        del passport_back_details["Given_Name"]
                    if "FamilyName" in passport_back_details:
                        passport_back_details["Visa_Family_Name"] = passport_back_details["FamilyName"]
                        del passport_back_details["FamilyName"]
                    if "Document_Type" in passport_back_details:
                        passport_back_details["Visa_Document_Type"] = passport_back_details["Document_Type"]
                        del passport_back_details["Document_Type"] 
                    if "Issued_country" in passport_back_details:
                        passport_back_details["Visa_Issued_country"] = passport_back_details["Issued_country"]
                        del passport_back_details["Issued_country"]
                    if "Nationality" in passport_back_details:
                        passport_back_details["Visa_Nationality"] = passport_back_details["Nationality"]
                        del passport_back_details["Nationality"]
                    if "Date_of_Birth" in passport_back_details:
                        passport_back_details["Visa_Date_of_Birth"] = passport_back_details["Date_of_Birth"]
                        del passport_back_details["Date_of_Birth"]
                    details.update(passport_back_details)
                else:
                    passport_back = helper_utility(
                        {
                            "api": "passport_address",
                            "Passport_Image": image2,
                        }
                    )
                    if not passport_back["success"]:
                        return passport_back
                    details.update(passport_back["data"])
            if bool(details):
                passport_data = change_passport_details(details)
                if not passport_data["success"]:
                    return passport_data
                return {"success": True, "data": passport_data["data"]}
            return {"success": False, "data": {}}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-get_passport_details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}

def check_date(date_time):
    try:
        regex_complie = re.compile(
                r"^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/|\s)([1-9]|0[1-9]|1[0-2])(\.|-|/|\s)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/|\s)([1-9]|0[1-9]|1[0-2])(\.|-|/|\s)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$|([\d]{1,2}(\.|-|/|\s)(January|February|March|April|May|June|July|August|September|October|November|December)(\.|-|/|\s)[\d]{4})"
            )
        if re.match(
            regex_complie,
            date_time.strip(),
        ):
            try:
                guest_date = date_time.strip()
                guest_date = guest_date.replace(" ", "/")
                guest_date = format_date(
                    guest_date,
                    "yyyy-mm-dd",
                )
                return guest_date
            except Exception as e:
                print(e)
                return None
        return None
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-check_date",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return None

def change_passport_details(data):
    try:
        details = {}
        if "country_code" in data:
            details["guest_country"] = data["country_code"]
        if "FamilyName" in data:
            details["guest_last_name"] = data["FamilyName"]
        if "Given_Name" in data:
            details["guest_first_name"] = data["Given_Name"]
        if "Passport_Document_No" in data:
            details["passport_number"]  = data["Passport_Document_No"]
        if "Gender" in data:
            if data["Gender"] in ["male", "Male", "MALE", "M", "m"]:
                details["gender"] = "MALE"
            if data["Gender"] in ["Female", "FeMale", "FEMALE", "F", "f"]:
                details["gender"] = "FEMALE"   
        if "Date_of_Issue" in data:
            check_doi = check_date(data["Date_of_Issue"])
            if check_doi:
                details["passport_date_of_issue"] = check_doi
        if "Date_of_Expiry" in data:
            check_doe = check_date(data["Date_of_Expiry"])
            if check_doe:
                details["passport_valid_till"] = check_doe
        if "Date_of_Birth" in data:
            check_dob = check_date(data["Date_of_Birth"])
            if check_dob:
                details["guest_dob"] = check_dob
        if "Nationality" in data:
            details["guest_nationality"] = data["Nationality"]
        if "Visa_Issue_Date" in data:
            check_vid = check_date(data["Visa_Issue_Date"])
            if check_vid:
                details["visa_date_of_issue"] = check_vid
        if "Visa_Number" in data:
            details["visa_number"] = data["Visa_Number"]
        if "Visa_Expiry_Date" in data:
            check_ved = check_date(data["Visa_Expiry_Date"])
            if check_ved:
                details["visa_valid_till"] = check_ved
        if "Visa_Issued_country" in data:
            details["visa_place_of_issued_country"] = data["Visa_Issued_country"]
        if "visa_Type" in data:
            file_path = frappe.utils.get_bench_path()
            with open(file_path + "/apps/version2_app/version2_app/passport_scanner/doctype/ml_utilities/visa-types.json", "r") as myfile:
                visa_types = json.loads(myfile.read())
            for each in visa_types:
                if data["visa_Type"] == each["altValue"]:
                    details["visa_type"] = each["value"]
                    break
                for visa_types in each["subTypes"]:
                    if len(visa_types) > 0:
                        get_visa_type = (
                            visa_types["viewValue"].split(" - ")[0].strip()
                        )
                        if data["visa_Type"] == get_visa_type:
                            details["visa_sub_type"] = visa_types["value"]
                            details["visa_type"] = each["value"]
                            break
        if "personaddress" in data:
            details["address1"] = data["personaddress"]
            reg = re.compile(r'(\d{6})')
            match = re.findall(reg, data["personaddress"])
            if len(match) > 0:
                pin_code = match[0]
                regex_complie = re.compile(r"^[1-9]{1}[0-9]{2}[0-9]{3}$")
                if re.match(regex_complie, pin_code):
                    details["zip_code"] = pin_code
                    address_details = get_address_from_zipcode(pin_code)
                    if address_details["success"]:
                        details.update(address_details["data"])
        if bool(details):
            if "guest_country" in details:
                if details["guest_country"] == "IND":
                    details["status"] = "In House"
                    details["guest_id_type"] = "indianPassport"
                else:
                    details["status"] = "Pending Review"
                    # details["guest_id_type"] = "Foreigner"
        return {"success": True, "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-change_passport_details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}

def get_driving_details(image1=None):
    try:
        if image1:
            driving_license = helper_utility(
                {
                    "api": "scan_driving_license",
                    "driving_image": image1,
                }
            )
            if not driving_license["success"]:
                return driving_license
            details = driving_license["data"]
            driving_details = localids_details_change(details)
            if not driving_details["success"]:
                return driving_details
            return {"success": True, "data": driving_details["data"]}
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-get_driving_details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}

def get_voter_details(image1=None, image2=None):
    try:
        details={}
        if image1:
            voter_front = helper_utility(
                {
                    "api": "scan_votercard",
                    "voter_image": image1,
                    "scanView": "front",
                }
            )
            if not voter_front["success"]:
                return voter_front
            details.update(voter_front["data"])
        if image2:
            voter_back = helper_utility(
                {
                    "api": "scan_votercard",
                    "voter_image": image2,
                    "scanView": "back",
                }
            )
            if not voter_back["success"]:
                return voter_back
            details.update(voter_back["data"])
        if bool(details):
            voter_details = localids_details_change(details)
            if not voter_details["success"]:
                return voter_details
            return {"success": True, "data": voter_details["data"]}
        return {"success":False, "data": {}}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-get_voter_details",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}

def get_data_vision_api(image1=None, image2=None, name=None, document_type=None, type=None, image_to_base=False, confirmation_number=None):
    try:
        details = {}
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path + "/sites/" + company.site_name
        if document_type:
            details["guest_id_type"] = document_type
            if document_type in ["voterId", "driving", "indianPassport", "aadhaar"]:
                details["status"] = "In House"
            elif document_type in ["Foreigner"]:
                details["status"] = "Pending Review"
        if confirmation_number:
            details["confirmation_number"] = confirmation_number
        if type in ["rotate", "upload"] and not image_to_base:
            if image1:
                image_1 = convert_base64_to_image(image1, name, site_folder_path, company)
                if "success" in  image_1:
                    return image_1
                if "file_url" in image_1["message"].keys():
                    details["id_image1"] = image_1["message"]["file_url"]
            if image2:
                image_2 = convert_base64_to_image(image2, name, site_folder_path, company)
                if "success" in  image_2:
                    return image_2
                if "file_url" in image_2["message"].keys():
                    details["id_image2"] = image_2["message"]["file_url"]
        if image_to_base:
            if image1:
                details["id_image1"] = image1
                if "private" in image1:
                    file_path1 = (
                        site_folder_path
                        + image1
                    )
                else:
                    file_path1 = (
                        site_folder_path
                        + "/public"
                        + image1
                    )
                convert1 = convert_image_to_base64(file_path1)
                if convert1["success"] is False:
                    return convert1
                image1 = convert1["data"]
            if image2:
                details["id_image2"] = image2
                if "private" in image2:
                    file_path2 = (
                        site_folder_path
                        + image2
                    )
                else:
                    file_path2 = (
                        site_folder_path
                        + "/public"
                        + image2
                    )
                convert2 = convert_image_to_base64(file_path2)
                if convert2["success"] is False:
                    return convert2
                image2 = convert1["data"]
        if document_type:
            if document_type == "aadhaar":
                aadhaar_data = get_aadhaar_data(image1, image2)
                if not aadhaar_data["success"]:
                    return {"success": False, "data": details, "message": "something went wrong"}
                details.update(aadhaar_data["data"])
            if document_type in ["indianPassport", "Foreigner"]:
                indian_passport = get_passport_details(image1, image2, document_type)
                if not indian_passport["success"]:
                    return {"success": False, "data": details, "message": "something went wrong"}
                details.update(indian_passport["data"])
            if document_type == "driving":
                driving = get_driving_details(image1)
                if not driving["success"]:
                    return {"success": False, "data": details, "message": "something went wrong"}
                details.update(driving["data"])
            if document_type == "voterId":
                voter = get_voter_details(image1, image2)
                if not voter["success"]:
                    return {"success": False, "data": details, "message": "something went wrong"}
                details.update(voter["data"])
        else:
            return {"success": False, "message": "something went wrong"}
        if bool(details):
            if document_type:
                details["guest_id_type"] = document_type
            return {"success": True, "data": details}
            # if document_type:
            #     details["guest_id_type"] = document_type
            # if confirmation_number:
            #     details["confirmation_number"] = confirmation_number
            # update_details = guest_details_update(details, name)
            # return update_details
        return {"success": False, "message": "something went wrong", "data": details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-get_data_vision_api",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def guest_details_update(data={},name=None):
    try:
        if name and bool(data):
            # empty_details = empty_guest_details(name)
            # if not empty_details["success"]:
            #     return empty_details
            if "guest_dob" in data:
                if data["guest_dob"] == "" or data["guest_dob"] is None:
                    del data["guest_dob"]
            frappe.db.set_value('Guest Details', name, data)
            frappe.db.commit()
            arrival_doc = frappe.get_doc("Guest Details", name)
            guest_update_attachment_logs(arrival_doc)
            return {"success": True, "message": "data updated"}
        return {"success": False, "message": "data should not be empty"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-guest_details_update",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}
    
@frappe.whitelist(allow_guest=True)
def extract_data_getting_from_opera(document_type=None, image_1=None, image_2=None, guest_details=False, confirmation_number=None):
    try:
        details = {}
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path + "/sites/" + company.site_name
        if document_type and confirmation_number:
            if image_1:
                image1 = convert_base64_to_image(image_1, "image1"+document_type, site_folder_path, company)
                if "success" in  image1:
                    return image1
                if "file_url" in image1["message"].keys():
                    details["id_image1"] = image1["message"]["file_url"]
            if image_2:
                image2 = convert_base64_to_image(image_2, "image2"+document_type, site_folder_path, company)
                if "success" in  image2:
                    return image2
                if "file_url" in image2["message"].keys():
                    details["id_image2"] = image2["message"]["file_url"]
            extract_detils = extract_id_details({
                    "image_1": image_1,
                    "image_2": image_2,
                    "id_type": document_type,
                    "reservation_number": confirmation_number,
                    "guest_details": guest_details
                })
            if not extract_detils["success"]:
                return extract_detils
            details.update(extract_detils["data"])
            if image_1:
                if "guest_first_name" not in details:
                    details["guest_first_name"] = "Guest"
            return {"success": True, "data": details}
        else:
            return {"success": False, "message": "confirmation number or document type should be mandatory"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-extract_data_getting_from_opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}


def rotate_image(base:str,name:str):
    '''
    rotate image based on base64
    '''
    try:
        pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "rotate image",
            "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)),
        )
        return {"success": False, "message": str(e)}
