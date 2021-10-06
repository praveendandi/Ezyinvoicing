# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import sys,traceback
import base64
from frappe.model.document import Document
from version2_app.passport_scanner.doctype.reservations.reservations import *

class GuestDetails(Document):
    pass



@frappe.whitelist(allow_guest=True)
def empty_guest_details(name):
    try:
        get_doc = frappe.get_doc("Guest Details",name)
        get_columns = frappe.db.sql("""desc `tabGuest Details`""", as_dict=0)
        columns = list(zip(*get_columns))[0]
        column_dict = {key: None for key in columns if key not in ['_user_tags', '_comments', '_assign', '_liked_by','name', 'idx', 'creation', 'modified', 'modified_by', 'owner', 'docstatus','parent', 'parentfield', 'parenttype']}
        column_dict["age"] = 0
        column_dict["no_of_nights"] = 0
        column_dict["uploaded_to_frro"] = 0
        column_dict["frro_checkout"] = 0
        column_dict["confirmation_number"] = get_doc.confirmation_number
        column_dict["given_name"] = get_doc.given_name
        frappe.db.set_value('Guest Details',get_doc.name, column_dict)
        frappe.db.commit()
        return {"success":True,"message":"guest details are empty"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-Empty guest details","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def guest_details_opera(confirmation_number):
    try:
        type = ""
        company_doc = frappe.get_last_doc("company")
        if company_doc.opera_scan == 1:
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists({"doctype":"Precheckins",'confirmation_number': confirmation_number}):
                    guest_details = frappe.db.get_list("Precheckins",filters={'confirmation_number': confirmation_number},fields=["*"])
                    type = "ezy-checkins"
                else:
                    return {"success":False,"message":"Confirmation Number not found"}
            elif company_doc.scan_ezy_module == 1 and company_doc.ezy_checkins_module == 0:
                if frappe.db.exists("Arrival Information", confirmation_number):
                    guest_details = frappe.db.get_list("Arrival Information",filters={'name': confirmation_number},fields=["*"])
                    type = "scan-ezy"
                else:
                    return {"success":False,"message":"Confirmation Number not found"}
            else:
                return {"success":False,"message":"You dont have rights"}
            return {"success":True,"data":guest_details,"type":type}
        else:
            return {"success":False,"message":"You dont have rights"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def helper_utility(data):
    try:
        url = "http://localhost:8000/api/method/version2_app.passport_scanner.doctype.reservations.reservations."+data["api"]
        del data["api"]
        x = requests.post(url, data = data)
        return {"success": True,"data":x.json()}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Helper Utility","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def convert_image_to_base64(image):
    try:
        with open(image, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        # print(encoded_str)
        return {"success":True, "data":encoded_str}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def convert_base64_to_image(base,name,site_folder_path,company):
    try:
        file = site_folder_path+"/private/files/"+name+"face.png"
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
def update_guest_details(name):
    try:
        company_doc = frappe.get_last_doc("company")
        if company_doc.scan_ezy_module == 1:
            pre_checkins = frappe.get_doc("Precheckins",name)
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = folder_path+'/sites/'+company_doc.site_name
            file_path1 = ""
            file_path2 = ""
            if company_doc.site_name:
                file_path1 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_1
                convert1= convert_image_to_base64(file_path1)
                if convert1["success"] == False:
                    return convert1
            if company_doc.site_name:
                file_path2 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_2
                convert2= convert_image_to_base64(file_path2)
                if convert2["success"] == False:
                    return convert2
            if pre_checkins.guest_id_type == "aadhaar":
                aadhar_details = {}
                if file_path1:
                    aadhar_front = helper_utility({"api":"scan_aadhar", "aadhar_image":convert1["data"], "scanView":"front"})
                    if aadhar_front["success"] == False:
                        return aadhar_front
                    if aadhar_front["data"]["message"]["aadhar_details"]["face"]:
                        base_image = convert_base64_to_image(aadhar_front["data"]["message"]["aadhar_details"]["face"],name,site_folder_path,company_doc)
                        if "file_url" in  base_image["message"].keys():
                            aadhar_details["face_url"] = base_image["message"]["file_url"]
                            del aadhar_front["data"]["message"]["aadhar_details"]["face"]
                    # aadhar_front["data"]["message"]["aadhar_details"]["front_image"] = aadhar_front["data"]["message"]["aadhar_details"]["base64_string"]
                    del aadhar_front["data"]["message"]["aadhar_details"]["base64_string"]
                    aadhar_front["data"]["message"]["aadhar_details"]["image_1"] = pre_checkins.image_1
                    aadhar_details.update(aadhar_front["data"]["message"]["aadhar_details"])
                if file_path2:
                    aadhar_back = helper_utility({"api":"scan_aadhar", "aadhar_image":convert2["data"], "scanView":"back"})
                    if aadhar_back["success"] == False:
                        return aadhar_back
                    # aadhar_back["data"]["message"]["aadhar_details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    del aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    aadhar_back["data"]["message"]["aadhar_details"]["image_2"] = pre_checkins.image_2
                    aadhar_details.update(aadhar_back["data"]["message"]["aadhar_details"])
                aadhar_details["id_type"] = "aadhaar"    
                return {"success": True,"data":aadhar_details}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
