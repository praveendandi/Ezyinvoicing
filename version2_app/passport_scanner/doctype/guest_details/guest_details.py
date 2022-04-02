# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import datetime
import json
import re
import sys
import traceback

import frappe
import requests
from frappe.model.document import Document

# from version2_app.passport_scanner.doctype.dropbox.dropbox import (
#     merge_guest_to_guest_details,
# )
from version2_app.passport_scanner.doctype.guest_details.cform import intiate
from version2_app.passport_scanner.doctype.guest_details.pathik import intiate_pathik

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
            ]
        }
        column_dict["age"] = 0
        column_dict["no_of_nights"] = 0
        column_dict["uploaded_to_frro"] = 0
        column_dict["frro_checkout"] = 0
        column_dict["no_of_adults"] = get_doc.no_of_adults
        column_dict["pending_pathik"] = get_doc.pending_pathik
        column_dict["no_of_children"] = get_doc.no_of_children
        column_dict["main_guest"] = get_doc.main_guest
        column_dict["confirmation_number"] = get_doc.confirmation_number
        column_dict["given_name"] = get_doc.given_name
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
        url = (
            "http://0.0.0.0:8000/api/method/version2_app.passport_scanner.doctype.reservations.reservations."
            + data["api"]
        )
        del data["api"]
        x = requests.post(url, data=data)
        print(x)
        return {"success": True, "data": x.json()}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Helper Utility",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
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
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
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
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
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
            if company.ome_scanner == 1:
                if not frappe.db.exists("Dropbox", {"merged_to": confirmation_number}):
                    return {"success": False, "message": "data not found in dropbox"}
            if not frappe.db.exists(
                "Guest Details", {"confirmation_number": confirmation_number}
            ):
                return {"success": False, "message": "data not found in guest details"}
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
                )
                get_booking_status = frappe.db.get_value("Arrival Information", confirmation_number, "booking_status")
                get_guest_details = [dict(item, booking_status=get_booking_status) for item in get_guest_details]
                return {"success": True, "data": get_guest_details}
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
            # return guest_details
            if type == "rotate":
                get_data = get_data_vision_api(image_1, image_2, name, guest_details["guest_id_type"])
                return get_data
                # if not get_data["success"]:
                #     return get_data
            if type == "upload":
                pass
            if type == "refetch":
                pass
    except Exception as e:
        print(e)

def get_aadhaar_data(image1=None, image2=None):
    try:
        if image1:
            print("////////,,,,,,")
            aadhar_front = helper_utility(
                        {
                            "api": "scan_aadhar",
                            "aadhar_image": image1,
                            "scanView": "front",
                        }
                    )
            if not aadhar_front["success"]:
                return aadhar_front
            return {"success": True, "data": aadhar_front}
        if image2:
            pass
    except Exception as e:
        pass

def get_data_vision_api(image1=None, image2=None, name=None, document_type=None):
    try:
        if document_type:
            if document_type == "aadhaar":
                get_aadhaar_data(image1, image2)
                return get_aadhaar_data
    except Exception as e:
        print(e)
    