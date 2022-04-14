# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import datetime
import json
import sys
import traceback

import frappe
import qrcode
import requests
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue


class Precheckins(Document):
    pass


def convert_base64_to_image(base, name, site_folder_path, company):
    try:
        file = site_folder_path + "/private/files/" + name + ".png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, "rb")}
        payload = {"is_private": 0, "folder": "Home"}
        site = company.host
        upload_qr_image = requests.post(
            site + "api/method/upload_file", files=files, data=payload
        )
        response = upload_qr_image.json()
        if "message" in response:
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def add_pre_checkins():
    try:
        data = json.loads(frappe.request.data)
        data = data["data"]
        if "etd" in data.keys():
            if "+" in data["etd"]:
                date_time = data["etd"].split("+")[0]
                data["etd"] = datetime.datetime.strptime(
                    date_time, "%Y-%m-%dT%H:%M:%S.%f"
                ).strftime("%H:%M")
        company = frappe.get_doc("company", data["company"])
        no_of_adults = 0
        if "no_of_adults" in data:
            no_of_adults = data["no_of_adults"]
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path + "/sites/" + company.site_name
        pre_checkins = {}
        images = data["ids"]
        if "signature" in data.keys():
            if data["signature"] != "":
                name = "signature" + data["confirmation_number"]
                signature = convert_base64_to_image(
                    data["signature"], name, site_folder_path, company
                )
                if "success" in signature:
                    if signature["success"] is False:
                        return signature
                pre_checkins["signature"] = signature["message"]["file_url"]
                del data["signature"]
        count = 1
        guest_images = []
        for each in images:
            if "id_type" in each:
                if each["id_type"] == "passport":
                    each["guest_id_type"] = "Foreigner"
                else:
                    each["guest_id_type"] = each["id_type"]
            if each["img_1"] != "":
                name = data["confirmation_number"] + each["id_type"] + "front"
                front = convert_base64_to_image(
                    each["img_1"], name, site_folder_path, company
                )
                if "success" in front:
                    if front["success"] is False:
                        return front
                pre_checkins["image_1"] = front["message"]["file_url"]
            if each["img_2"] != "":
                name = data["confirmation_number"] + each["id_type"] + "back"
                back = convert_base64_to_image(
                    each["img_2"], name, site_folder_path, company
                )
                if "success" in back:
                    if back["success"] is False:
                        return back
                pre_checkins["image_2"] = back["message"]["file_url"]
            else:
                pre_checkins["image_2"] = ""
            if "img_3" in each:
                if each["img_3"] != "":
                    name = data["confirmation_number"] + each["id_type"] + "oci"
                    back = convert_base64_to_image(
                        each["img_3"], name, site_folder_path, company
                    )
                    if "success" in back:
                        if back["success"] is False:
                            return back
                    pre_checkins["image_3"] = back["message"]["file_url"]
                else:
                    pre_checkins["image_3"] = ""
            # pre_checkins["guest_id_type"] = each["id_type"]
            pre_checkins.update(data)
            if "ids" in pre_checkins.keys():
                del pre_checkins["ids"]
            if count > 1:
                pre_checkins["guest_first_name"] = "Guest-" + str(count)
                pre_checkins["guest_last_name"] = ""
                pre_checkins["confirmation_number"] = (
                    data["confirmation_number"] + "-" + str(count - 1)
                )
            if "loyalty_membership" in pre_checkins:
                pre_checkins["loyalty_membership"] = (
                    "Yes" if pre_checkins["loyalty_membership"] is True else "No"
                )
            if data["resident_of_india"] == "Yes":
                pre_checkins["guest_country"] = "IND"
            pre_checkins["doctype"] = "Precheckins"
            if frappe.db.exists("Arrival Information", data["confirmation_number"]):
                arrival_doc = frappe.get_doc(
                    "Arrival Information", data["confirmation_number"]
                )
                pre_checkins["arrival_date"] = arrival_doc.arrival_date
            precheckins_doc = frappe.get_doc(pre_checkins)
            precheckins_doc.insert(ignore_permissions=True, ignore_links=True)
            guest_images.append(
                {"image1": pre_checkins["image_1"], "image2": pre_checkins["image_2"]}
            )
            count += 1
        user_name = frappe.session.user
        date_time = datetime.datetime.now()
        if frappe.db.exists("Arrival Information", {"name": data["confirmation_number"], "is_group_code":"Yes"}):
            # get_adults_count = frappe.db.get_value("Arrival Information", data["confirmation_number"], "no_of_adults")
            # get_percheckins_count = frappe.db.count('Precheckins', {'confirmation_number': ["like", data["confirmation_number"]+"%"]})
            # if get_percheckins_count == get_adults_count:
            #     frappe.db.set_value(
            #         "Arrival Information",
            #         data["confirmation_number"],
            #         "virtual_checkin_status",
            #         "Yes",
            #     )
            pass
        else:
            frappe.db.set_value(
                "Arrival Information",
                data["confirmation_number"],
                "virtual_checkin_status",
                "Yes",
            )
        activity_data = {
            "doctype": "Activity Logs",
            "datetime": date_time,
            "confirmation_number": data["confirmation_number"],
            "module": "Ezycheckins",
            "event": "PreArrivals",
            "user": user_name,
            "activity": "Precheckedin Successfully",
        }
        frappe.db.commit()
        event_doc = frappe.get_doc(activity_data)
        event_doc.insert(ignore_permissions=True, ignore_links=True)
        if company.ezy_checkins_module == 1 and company.scan_ezy_module == 0:
            guest_attachments = {
                "doctype": "Documents",
                "guest_details": guest_images,
                "confirmation_number": data["confirmation_number"],
                "module_name": "Ezycheckins",
                "user": user_name,
                "number_of_guests": no_of_adults,
            }
            guestatt_doc = frappe.get_doc(guest_attachments)
            guestatt_doc.insert(ignore_permissions=True, ignore_links=True)
        if company.thank_you_email == 1 and company.self_assisted == 0:
            enqueue(
                thankyouMail,
                queue="default",
                timeout=800000,
                event="data_import",
                now=False,
                data=data,
                is_async=True,
            )
        return {"success": True, "message": "Pre-checkin completed successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Precheckins-Add Pre Checkins",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def thankyouMail(data):
    try:
        company = frappe.get_doc("company", data["company"])
        if not company.site_domain:
            return {
                "success": False,
                "message": "Please add site domain in property setting",
            }
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company.site_name
        file_path = (
            folder_path
            + "/sites/"
            + site_folder_path
            + company.thank_you_email_mail_content
        )
        f = open(file_path, "r")
        mail_templet = f.read()
        mail_templet = (
            mail_templet.replace("{{name}}", data["guest_first_name"])
            if "guest_first_name" in data.keys()
            else ""
        )
        mail_templet = (
            mail_templet.replace("{{lastName}}", data["guest_last_name"])
            if "guest_last_name" in data.keys()
            else ""
        )
        mail_templet = mail_templet.replace("{{hotelName}}", company.company_name)
        mail_templet = mail_templet.replace("{{email}}", company.email)
        mail_templet = mail_templet.replace("{{phone}}", company.phone_number)
        company_logo = (company.site_domain).rstrip("/") + company.company_logo
        mail_templet = mail_templet.replace("logoImg", company_logo)
        bg_logo = (company.site_domain).rstrip("/") + company.email_banner
        mail_templet = mail_templet.replace("headerBG", bg_logo)
        frappe.sendmail(
            recipients=data["guest_email_address"],
            subject=company.thank_you_mail_subject,
            message=mail_templet,
            now=True,
        )
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Precheckins-Thankyou Mail",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_pre_checkins_qr(company_code):
    try:
        company = frappe.get_doc("company", company_code)
        if company.ezycheckins_socket_host:
            url = "{}?company={}".format(company.ezycheckins_socket_host, company.name)
            img = qrcode.make(url)
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = (
                "/sites/" + company.site_name + "/private/files/precheckinqr.png"
            )
            file_path = folder_path + site_folder_path
            img.save(file_path)
            files = {"file": open(file_path, "rb")}
            payload = {"is_private": 1, "folder": "Home"}
            site = company.host
            upload_qr_image = requests.post(
                site + "api/method/upload_file", files=files, data=payload
            )
            response = upload_qr_image.json()
            if "message" in response:
                return {"success": True, "url": response["message"]["file_url"]}
            else:
                return {"success": False, "message": "something went wrong"}
        else:
            return {
                "success": False,
                "message": "Please give the precheckins url in property settings",
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Precheckins-Get Pre Checkins QR",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}
