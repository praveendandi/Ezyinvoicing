# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
import base64, requests
import sys, traceback, datetime
from frappe.model.document import Document
from frappe.utils import logger

class Precheckins(Document):
    pass

def convert_base64_to_image(base,name,site_folder_path,company):
    try:
        file = site_folder_path+"/private/files/"+name+".png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, 'rb')}
        payload = {
            "is_private": 1,
            "folder": "Home"
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        if 'message' in response:
            return response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def add_pre_checkins():
    try:
        data=json.loads(frappe.request.data)
        data = data["data"]
        company = frappe.get_doc("company",data["company"])
        no_of_adults = data["no_of_adults"]
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path+'/sites/'+company.site_name
        pre_checkins = {}
        images = data["ids"]
        if "signature" in data.keys():
            if data["signature"] != "":
                name = "signature"+data["confirmation_number"]
                signature = convert_base64_to_image(data["signature"],name,site_folder_path,company)
                if "success" in  signature:
                    if signature["success"] == False:
                        return signature
                pre_checkins["signature"] = signature["message"]["file_url"]
                del data["signature"]
        count = 1
        for each in images:
            if each["img_1"] != "":
                name = data["confirmation_number"]+each["id_type"]+"front"
                front = convert_base64_to_image(each["img_1"],name,site_folder_path,company)
                if "success" in  front:
                    if front["success"] == False:
                        return front
                pre_checkins["image_1"] = front["message"]["file_url"]
            if each["img_2"] != "":
                name = data["confirmation_number"]+each["id_type"]+"back"
                back = convert_base64_to_image(each["img_2"],name,site_folder_path,company)
                if "success" in  back:
                    if back["success"] == False:
                        return back
                pre_checkins["image_2"] = back["message"]["file_url"]
            pre_checkins["guest_id_type"] = each["id_type"]
            pre_checkins.update(data)
            if "ids" in pre_checkins.keys():
                del pre_checkins["ids"]
            if count > 1:
                pre_checkins["guest_first_name"] = "Guest-"+str(count)
                pre_checkins["guest_last_name"] = ""
                pre_checkins["confirmation_number"] = data["confirmation_number"]+"-"+str(count-1)
            if "loyalty_membership" in pre_checkins:
                pre_checkins["loyalty_membership"] = "Yes" if pre_checkins["loyalty_membership"] == True else "No"
            if data["resident_of_india"] == "Yes":
                pre_checkins["guest_country"] = "IND"
            pre_checkins["doctype"] = "Precheckins"
            if frappe.db.exists('Arrival Information', data["confirmation_number"]):
                arrival_doc = frappe.get_doc('Arrival Information', data["confirmation_number"])
                pre_checkins["arrival_date"] = arrival_doc.arrival_date
            precheckins_doc = frappe.get_doc(pre_checkins)
            precheckins_doc.insert(ignore_permissions=True, ignore_links=True)
            count+=1
        user_name =  frappe.session.user
        date_time = datetime.datetime.now()
        frappe.db.set_value('Arrival Information',data["confirmation_number"],'virtual_checkin_status','Yes')
        activity_data = {"doctype":"Activity Logs","datetime":date_time,"confirmation_number":data["confirmation_number"],"module":"Ezycheckins","event":"PreArrivals","user":user_name,"activity":"Precheckedin Successfully"}
        frappe.db.commit()
        event_doc=frappe.get_doc(activity_data)
        event_doc.insert(ignore_permissions=True, ignore_links=True)
        if company.thank_you_email == "1":
            cancel_email_address = pre_checkins["guest_email_address"]
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = company.site_name
            file_path = folder_path+'/sites/'+site_folder_path+company.thank_you_email_mail_content
            arrival_doc = frappe.get_doc("Arrival Information",data["confirmation_number"])
            if arrival_doc.mail_sent=="No":
                f = open(file_path, "r")
                data=f.read()
                data = data.replace('{{name}}',data["guest_first_name"])
                # data = data.replace('{{lastName}}',arrival_doc.guest_last_name)
                data = data.replace('{{hotelName}}',company.company_name)
                data = data.replace('{{email}}',company.email)
                data = data.replace('{{phone}}',company.phone_number)
                mail_send = frappe.sendmail(recipients=cancel_email_address,
                        subject = company.cancellation_email_mail_content,
                        message= data,now = True)
                frappe.db.set_value('Arrival Information',data["confirmation_number"],'mail_sent','Yes')
                frappe.db.set_value('Arrival Information',data["confirmation_number"],'mail_via','Automatic')
                activity_data = {"doctype":"Activity Logs","datetime":date_time,"confirmation_number":data["confirmation_number"],"module":"Ezycheckins","event":"PreArrivals","user":user_name,"activity":"Thankyou Mail Sent-out"}
                event_doc=frappe.get_doc(activity_data)
                event_doc.insert()
                frappe.db.commit()
            else:
                return {"success":False, "message":"Invitation Sent"}
        return {"success":True, "message":"Pre-checkin completed successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Precheckins-Add Pre Checkins","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}