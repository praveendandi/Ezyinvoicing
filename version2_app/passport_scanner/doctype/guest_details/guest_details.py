# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import datetime
import re
import frappe
import sys,traceback
import base64
from frappe.model.document import Document
from version2_app.passport_scanner.doctype.reservations.reservations import *
from version2_app.passport_scanner.doctype.guest_details.cform import *

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
                    guest_details = frappe.db.get_list("Precheckins",filters={'confirmation_number': ["like", confirmation_number+"%"]},fields=["name","confirmation_number","guest_first_name","guest_last_name","opera_scanned_status"],order_by="creation")
                    type = "ezy-checkins"
                else:
                    return {"success":False,"message":"Confirmation Number not found"}
                return {"success":True,"data":guest_details,"type":type}
            else:
                return {"success":False,"message":"You dont have rights for ezy-checkins"}
            # elif company_doc.scan_ezy_module == 1 and company_doc.ezy_checkins_module == 0:
            #     if frappe.db.exists("Arrival Information", confirmation_number):
            #         guest_details = frappe.db.get_list("Arrival Information",filters={'name': confirmation_number},fields=["*"])
            #         type = "scan-ezy"
            #     else:
            #         return {"success":False,"message":"Confirmation Number not found"}
            # else:
            #     return {"success":False,"message":"You dont have rights"}

            
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
        if company_doc.scan_ezy_module == 1 or company_doc.vision_api == 1:
            pre_checkins = frappe.get_doc("Precheckins",name)
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = folder_path+'/sites/'+company_doc.site_name
            file_path1 = ""
            file_path2 = ""
            if pre_checkins.image_1:
                if "private" in pre_checkins.image_1:
                    file_path1 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_1
                else:
                    file_path1 = folder_path+'/sites/'+company_doc.site_name+"/public"+pre_checkins.image_1
                convert1= convert_image_to_base64(file_path1)
                if convert1["success"] == False:
                    return convert1
            if pre_checkins.image_2:
                if "private" in pre_checkins.image_2:
                    file_path2 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_2
                else:
                    file_path2 = folder_path+'/sites/'+company_doc.site_name+"/public"+pre_checkins.image_2
                # file_path2 = folder_path+'/sites/'+company_doc.site_name+pre_checkins.image_2
                convert2= convert_image_to_base64(file_path2)
                if convert2["success"] == False:
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
                    aadhar_front = helper_utility({"api":"scan_aadhar", "aadhar_image":convert1["data"], "scanView":"front"})
                    if "success" in aadhar_front["data"]["message"].keys():
                        if aadhar_front["data"]["message"]["success"] == False:
                            aadhar_details["image_1"] = pre_checkins.image_1
                            aadhar_details["image_2"] = pre_checkins.image_2
                            aadhar_details.update(aadhar_front["data"]["message"])
                            del aadhar_details["success"]
                            del aadhar_details["aadhar_details"]
                            aadhar_details["id_type"] = "aadhaar"
                            return {"success": False,"data":aadhar_details}
                        # return aadhar_front["data"]["message"]
                    if "face" in aadhar_front["data"]["message"]["aadhar_details"].keys():
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
                    if "message" in aadhar_back["data"].keys():
                        if aadhar_back["data"]["message"]["success"] == False:
                            aadhar_details["image_2"] = pre_checkins.image_2
                            aadhar_details.update(aadhar_back["data"]["message"])
                            del aadhar_details["success"]
                            del aadhar_details["aadhar_details"]
                            aadhar_details["id_type"] = "aadhaar"
                            return {"success": False,"data":aadhar_details}
                    else:
                        aadhar_details["image_2"] = pre_checkins.image_2
                        aadhar_details["id_type"] = "aadhaar"
                        return {"success": True, "data":aadhar_details}
                    # aadhar_back["data"]["message"]["aadhar_details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    del aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    aadhar_back["data"]["message"]["aadhar_details"]["image_2"] = pre_checkins.image_2
                    aadhar_details.update(aadhar_back["data"]["message"]["aadhar_details"])
                aadhar_details["id_type"] = "aadhaar"    
                if company_doc.scan_ezy_module == 1:
                    aadhar_details["scan_ezy"] = True
                else:
                    aadhar_details["scan_ezy"] = False
                return {"success": True,"data":aadhar_details}
            if pre_checkins.guest_id_type == "driving":
                driving_license_details= {}
                if company_doc.scan_ezy_module == 1:
                    driving_license_details["scan_ezy"] = True
                else:
                    driving_license_details["scan_ezy"] = False
                if file_path1:
                    driving_license_details["pre_city"] = pre_checkins.guest_city
                    driving_license_details["pre_country"] = pre_checkins.guest_country
                    driving_license_details["pre_state"] = pre_checkins.guest_state
                    driving_license_details["pre_Nationality"] = pre_checkins.guest_nationality
                    driving_license = helper_utility({"api":"scan_driving_license", "driving_image":convert1["data"]})
                    if driving_license["data"]["message"]["success"] == False:
                        driving_license_details["image_1"] = pre_checkins.image_1
                        driving_license_details["image_2"] = pre_checkins.image_2
                        driving_license_details.update(driving_license["data"]["message"])
                        del driving_license_details["success"]
                        del driving_license_details["driving_details"]
                        driving_license_details["id_type"] = "driving"
                        return {"success": False,"data":driving_license_details}
                        # return driving_license["data"]["message"]
                    if "driving_details" in driving_license["data"]["message"].keys():
                        if "face" in driving_license["data"]["message"]["driving_details"].keys():
                            if driving_license["data"]["message"]["driving_details"]["face"]:
                                base_image = convert_base64_to_image(driving_license["data"]["message"]["driving_details"]["face"],name,site_folder_path,company_doc)
                                if "file_url" in  base_image["message"].keys():
                                    driving_license_details["face_url"] = base_image["message"]["file_url"]
                                    del driving_license["data"]["message"]["driving_details"]["face"]
                            # aadhar_front["data"]["message"]["driving_details"]["front_image"] = aadhar_front["data"]["message"]["driving_details"]["base64_string"]
                            del driving_license["data"]["message"]["driving_details"]["base64_string"]
                            driving_license["data"]["message"]["driving_details"]["image_1"] = pre_checkins.image_1
                            driving_license_details.update(driving_license["data"]["message"]["driving_details"])
                driving_license_details["id_type"] = "driving"
                driving_license_details["image_1"] = pre_checkins.image_1
                driving_license_details["image_2"] = pre_checkins.image_2
                if company_doc.scan_ezy_module == 1:
                    driving_license_details["scan_ezy"] = True
                else:
                    driving_license_details["scan_ezy"] = False
                return {"success":True, "data":driving_license_details}
            if pre_checkins.guest_id_type == "voterId":
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
                    voter_front = helper_utility({"api":"scan_votercard", "voter_image":convert1["data"], "scanView":"front"})
                    if "success" in voter_front["data"]["message"].keys():
                        if voter_front["data"]["message"]["success"] == False:
                            voter_details["image_1"] = pre_checkins.image_1
                            voter_details["image_2"] = pre_checkins.image_2
                            voter_details.update(voter_front["data"]["message"])
                            del voter_details["success"]
                            del voter_details["voter_details"]
                            voter_details["id_type"] = "voterId"
                            return {"success": False,"data":voter_details}
                            # return voter_front["data"]["message"]["voter_details"]
                    if "face" in voter_front["data"]["message"]["voter_details"]:
                        base_image = convert_base64_to_image(voter_front["data"]["message"]["voter_details"]["face"],name,site_folder_path,company_doc)
                        if "file_url" in  base_image["message"].keys():
                            voter_details["face_url"] = base_image["message"]["file_url"]
                            del voter_front["data"]["message"]["voter_details"]["face"]
                    # aadhar_front["data"]["message"]["voter_details"]["front_image"] = aadhar_front["data"]["message"]["voter_details"]["base64_string"]
                    del voter_front["data"]["message"]["voter_details"]["base64_string"]
                    voter_details["image_1"] = pre_checkins.image_1
                    voter_details.update(voter_front["data"]["message"]["voter_details"]["data"])
                if file_path2:
                    voter_back = helper_utility({"api":"scan_votercard", "voter_image":convert2["data"], "scanView":"back"})
                    if "success" in voter_back["data"]["message"].keys():
                        if voter_back["data"]["message"]["success"] == False:
                            voter_details["image_2"] = pre_checkins.image_2
                            voter_details.update(voter_back["data"]["message"])
                            del voter_details["success"]
                            del voter_details["voter_details"]
                            voter_details["id_type"] = "voterId"
                            return {"success": False,"data":voter_details}
                            # return voter_back["data"]["message"]["voter_details"]
                    # aadhar_back["data"]["message"]["voter_details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    del voter_back["data"]["message"]["voter_details"]["base64_string"]
                    voter_details["image_2"] = pre_checkins.image_2
                    voter_details.update(voter_back["data"]["message"]["voter_details"]["data"])
                voter_details["id_type"] = "voterId"
                return {"success": True,"data":voter_details}
            if pre_checkins.guest_id_type == "indianPassport" or pre_checkins.guest_id_type == "passport":
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
                    passport = helper_utility({"api":"passportvisadetails", "Passport_Image":convert1["data"], "scan_type":"web"})
                    if passport["data"]["message"]["success"] == False:
                        passport_details["image_1"] = pre_checkins.image_1
                        passport_details["image_2"] = pre_checkins.image_2
                        passport_details.update(passport["data"]["message"])
                        del passport_details["success"]
                        passport_details["id_type"] = "Foreign" if pre_checkins.guest_id_type == "passport" else pre_checkins.guest_id_type
                        # return {"success": True,"data":passport_details}
                        # return passport["data"]["message"]
                    if passport["data"]["message"]["success"] == True:
                        if "face" in passport["data"]["message"]["details"].keys():
                            base_image = convert_base64_to_image(passport["data"]["message"]["details"]["face"],name,site_folder_path,company_doc)
                            if "file_url" in  base_image["message"].keys():
                                passport_details["face_url"] = base_image["message"]["file_url"]
                                del passport["data"]["message"]["details"]["face"]
                        if "data" in passport["data"]["message"]["details"].keys():
                            if "Date_of_Birth" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Date_of_birth"] = passport["data"]["message"]["details"]["data"]["Date_of_Birth"]
                                del passport["data"]["message"]["details"]["data"]["Date_of_Birth"]
                            if "country_code" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_country_code"] = passport["data"]["message"]["details"]["data"]["country_code"]
                                del passport["data"]["message"]["details"]["data"]["country_code"]
                            if "FamilyName" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_FamilyName"] = passport["data"]["message"]["details"]["data"]["FamilyName"]
                                del passport["data"]["message"]["details"]["data"]["FamilyName"]
                            if "Given_Name" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Given_Name"] = passport["data"]["message"]["details"]["data"]["Given_Name"]
                                del passport["data"]["message"]["details"]["data"]["Given_Name"]
                            if "Date_of_Issue" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Date_of_Issue"] = passport["data"]["message"]["details"]["data"]["Date_of_Issue"]
                                del passport["data"]["message"]["details"]["data"]["Date_of_Issue"]
                            if "Nationality" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Nationality"] = passport["data"]["message"]["details"]["data"]["Nationality"]
                                del passport["data"]["message"]["details"]["data"]["Nationality"]
                            if "Date_of_Birth" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Date_of_Birth"] = passport["data"]["message"]["details"]["data"]["Date_of_Birth"]
                                del passport["data"]["message"]["details"]["data"]["Date_of_Birth"]
                            if "Gender" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Gender"] = passport["data"]["message"]["details"]["data"]["Gender"]
                                del passport["data"]["message"]["details"]["data"]["Gender"]
                            if "Date_of_Expiry" in passport["data"]["message"]["details"]["data"].keys():
                                passport_details["pass_Date_of_Expiry"] = passport["data"]["message"]["details"]["data"]["Date_of_Expiry"]
                                del passport["data"]["message"]["details"]["data"]["Date_of_Expiry"]
                            # aadhar_front["data"]["message"]["details"]["front_image"] = aadhar_front["data"]["message"]["aadhar_details"]["base64_string"]
                            # del passport["data"]["message"]["details"]["base64_string"]
                            passport_details.update(passport["data"]["message"]["details"]["data"])
                        passport_details["image_1"] = pre_checkins.image_1
                    
                if file_path2:
                    if pre_checkins.guest_id_type == "passport":
                        visa_details = helper_utility({"api":"passportvisadetails", "Passport_Image":convert2["data"], "scan_type":"web"})
                        if visa_details["data"]["message"]["success"] == False:
                            passport_details["image_2"] = pre_checkins.image_2
                            passport_details.update(visa_details["data"]["message"])
                            del passport_details["success"]
                            passport_details["id_type"] = "Foreign"
                            return {"success": True,"data":passport_details}
                        passport_details.update(visa_details["data"]["message"]["details"]["data"])
                    else:
                        visa_details = helper_utility({"api":"passport_address", "Passport_Image":convert2["data"]})
                        if visa_details["data"]["message"]["success"] == False:
                            passport_details["image_2"] = pre_checkins.image_2
                            passport_details.update(visa_details["data"]["message"])
                            del passport_details["success"]
                            passport_details["id_type"] = pre_checkins.guest_id_type
                            return {"success": True,"data":passport_details}
                        passport_details.update(visa_details["data"]["message"]["data"])
                    # aadhar_back["data"]["message"]["details"]["back_image"] = aadhar_back["data"]["message"]["aadhar_details"]["base64_string"]
                    # del visa_details["data"]["message"]["details"]["data"]["base64_string"]
                    passport_details["image_2"] = pre_checkins.image_2  
                passport_details["id_type"] = pre_checkins.guest_id_type if pre_checkins.guest_id_type == "indianPassport" else "Foreign"
                return {"success": True,"data":passport_details}
            if pre_checkins.guest_id_type == "OCI":
                pass
            if pre_checkins.guest_id_type == "other" or pre_checkins.guest_id_type == "others":
                other_details = {}
                if file_path1:
                    driving_license = helper_utility({"api":"other_images", "image":convert1["data"]})
                    if driving_license["data"]["message"]["success"] == False:
                        other_details["image_1"] = pre_checkins.image_1
                        other_details["image_2"] = pre_checkins.image_2
                        other_details.update(driving_license["data"]["message"])
                        del other_details["success"]
                        other_details["id_type"] = "other"
                        return {"success": False,"data":other_details}
                        # return driving_license["data"]["message"]
                    if driving_license["data"]["message"]["otherimage_details"]["base64_string"]:
                        base_image = convert_base64_to_image(driving_license["data"]["message"]["otherimage_details"]["base64_string"],name,site_folder_path,company_doc)
                        if "file_url" in  base_image["message"].keys():
                            other_details["image_1"] = base_image["message"]["file_url"]
                            del driving_license["data"]["message"]["otherimage_details"]["base64_string"]
                if file_path2:
                    back2 = helper_utility({"api":"other_images", "image":convert2["data"]})
                    if back2["data"]["message"]["success"] == False:
                        other_details["image_2"] = pre_checkins.image_2
                        other_details.update(driving_license["data"]["message"])
                        del other_details["success"]
                        other_details["id_type"] = "other"
                        return {"success": False,"data":other_details}
                        return back2["data"]["message"]
                    if back2["data"]["message"]["otherimage_details"]["base64_string"]:
                        base_image = convert_base64_to_image(back2["data"]["message"]["otherimage_details"]["base64_string"],name,site_folder_path,company_doc)
                        if "file_url" in  base_image["message"].keys():
                            other_details["image_2"] = base_image["message"]["file_url"]
                            del back2["data"]["message"]["otherimage_details"]["base64_string"]
                other_details["id_type"] = "other"
                if company_doc.scan_ezy_module == 1:
                    other_details["scan_ezy"] = True
                else:
                    other_details["scan_ezy"] = False
                print("===========================")
                return {"success":True, "data":other_details}
        else:
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists({"doctype":"Precheckins",'name': name}):
                    guest_details = frappe.db.get_value("Precheckins",name,["guest_first_name","guest_last_name","guest_last_name","no_of_adults","no_of_children","confirmation_number","address1","address2","zip_code","guest_city","guest_state","guest_country","guest_dob","guest_age","guest_nationality","gender","arrival_date","coming_from","departure_date","company","guest_id_type","image_1","image_2","going_to"], as_dict=1)
                    guest_details["id_type"] = guest_details.guest_id_type if guest_details.guest_id_type != "passport" else "Foreign" 
                    guest_details["reference"] = "No-Vision"
                    return {"success":True, "data":guest_details}
                else:
                    return {"success":False,"message":"Confirmation Number not found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def add_guest_details():
    try:
        data=json.loads(frappe.request.data)
        data = data["data"]
        pre_checkins_count = 0
        company_doc = frappe.get_last_doc("company")
        if company_doc.scan_ezy_module == 1:
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = folder_path+'/sites/'+company_doc.site_name
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists({"doctype":'Precheckins', "confirmation_number":data["confirmation_number"]}):
                    pre_checkins_count = frappe.db.get_value('Precheckins', {"confirmation_number":data["confirmation_number"]}, "no_of_adults")
            # if company_doc.ezy_checkins_module == 0 and company_doc.scan_ezy_module == 1:
            #     pre_checkins_count = frappe.db.get_value('Arrival Information',{"confirmation_number":data["confirmation_number"]},"no_of_adults")
            pre_arrival_confi = data["confirmation_number"]
            if "-" in data["confirmation_number"]:
                data["confirmation_number"] = data["confirmation_number"].split("-")[0]
            scan_guest_details = frappe.db.count('Guest Details', {'confirmation_number': data["confirmation_number"]})
            if frappe.db.exists('Arrival Information', data["confirmation_number"]):
                arrival_doc = frappe.get_doc("Arrival Information",data["confirmation_number"])
                if frappe.db.exists({'doctype': 'Precheckins','confirmation_number': data["confirmation_number"]}):
                    if (scan_guest_details+1) == pre_checkins_count:
                        arrival_doc.status = "Scanned"
                        arrival_doc.booking_status = "CHECKED IN"
                    else:
                        if (scan_guest_details+1) < pre_checkins_count:
                            arrival_doc.status = "Partial Scanned"
                            arrival_doc.booking_status = "CHECKED IN"
                else:
                    if arrival_doc.no_of_adults:
                        pre_checkins_count = arrival_doc.no_of_adults
                    if pre_checkins_count == 0:
                        arrival_doc.status = "Scanned"
                        arrival_doc.booking_status = "CHECKED IN"
                    else:
                        if (scan_guest_details+1) == pre_checkins_count:
                            arrival_doc.status = "Scanned"
                        else:
                            if (scan_guest_details+1) < pre_checkins_count:
                                arrival_doc.status = "Partial Scanned"
                                arrival_doc.booking_status = "CHECKED IN"
                arrival_doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
            else:
                arrival_date = datetime.datetime.now().date()
                arrival_info_doc = frappe.get_doc({"doctype":"Arrival Information","confirmation_number":data["confirmation_number"],"status":"Scanned","booking_status":"CHECKED IN","arrival_date":arrival_date,"company":company_doc.name,"virtual_checkin_status":"Yes","guest_first_name":data["given_name"]})
                arrival_info_doc.insert(ignore_permissions=True, ignore_links=True)
            name = data["given_name"]+data["confirmation_number"]+data["id_type"]
            if data["id_image1"]:
                if "private" not in data["id_image1"] and "/files/" not in data["id_image1"]:
                    image_1 = convert_base64_to_image(data["id_image1"],name,site_folder_path,company_doc)
                    if image_1["message"] == False:
                        return image_1
                    data["id_image1"] = image_1["message"]["file_url"]
            if data["id_image2"]:
                if "private" not in data["id_image2"] and "/files/" not in data["id_image2"]:
                    image_2 = convert_base64_to_image(data["id_image2"],name,site_folder_path,company_doc)
                    if image_2["message"] == False:
                        return image_2
                    data["id_image2"] = image_2["message"]["file_url"]
            if data["face_image"] != "":
                if "private" not in data["face_image"] and "/files/" not in data["face_image"]:
                    face = convert_base64_to_image(data["face_image"],name,site_folder_path,company_doc)
                    if face["message"] == False:
                        return face
                    data["face_image"] = face["message"]["file_url"]
            data["doctype"] = "Guest Details"
            data["id_type"] = "Foreigner" if data["id_type"] == "Foreign" else data["id_type"]
            if company_doc.ezy_checkins_module == 1:
                if frappe.db.exists({'doctype': 'Precheckins','confirmation_number': data["confirmation_number"]}) and data["guest_id"]:
                    pre_doc = frappe.get_doc("Precheckins",data["guest_id"])
                    pre_doc.opera_scanned_status = "Scanned"
                    arrival_doc.booking_status = "CHECKED IN"
                    pre_doc.guest_first_name = data["given_name"]
                    if "sur_name" in data.keys():
                        pre_doc.guest_last_name = data["sur_name"] if data["sur_name"] else ""
                    else:
                        pre_doc.guest_last_name = data["surname"] if data["surname"] else ""
                    pre_doc.save(ignore_permissions=True,ignore_version=True)
                    del data["guest_id"]
            if "address1" in data.keys():
                data["address"] = data["address1"]
                del data["address1"]
            if "address2" in data.keys():
                if data["address2"] != "":
                    if re.search("\d{6}",data["address2"]):
                        postal_code = re.match('^.*(?P<zipcode>\d{6}).*$', data["address2"]).groupdict()['zipcode']
                        data["postal_code"] = postal_code if len(postal_code) == 6 else ''
            doc = frappe.get_doc(data)
            doc.insert(ignore_permissions=True, ignore_links=True)
            return {"success":True, "message":"Guest added successfully"}
        else:
            return {"success":False, "message":"Scan-Ezy module is not enabled"}
    except Exception as e:
        print(str(e),"====================")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Add Guest Details","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def process_cform():
    try:
        # data=json.loads(frappe.request.data)
        # data = data["data"]
        company = frappe.get_last_doc('company')
        if company.cform_session == 1:
            return {"success":False,"message":"Already cform inpogress"}
        # if len(data)>0:
        #     company_doc = frappe.get_doc('company',company.name)
        #     company_doc.cform_session = 1
        #     company_doc.save(ignore_permissions=True,ignore_version=True)
        #     for index, each in enumerate(data):
        #         each_data = frappe.db.get_value("Guest Details",each,["surname","given_name","gender","date_of_birth","select_category",
        #         "nationality","address","city","country","passport_number","passport_place_of_issued_city",
        #         "passport_place_of_issued_country","passport_date_of_issue","passport_valid_till","visa_number","visa_place_of_issued_city","visa_place_of_issued_country",
        #         "visa_date_of_issue","visa_valid_till","visa_type","visa_sub_type","arrival_from_country","arrival_from_city","arrival_place",
        #         "date_of_arrival_in_india","checkin_date","checkin_time","no_of_nights","whether_employed_in_india","purpose_of_visit","next_destination","next_destination_place",
        #         "next_destination_state","next_destination_city","next_destination_country","contact_phone_no","contact_mobile_no","permanent_phone_no","permanent_mobile_no","remarks","face_image","name"], as_dict=1)
        #         each_data["hotelAddress"] = company.address_1+" ,"+company.address_2
        #         each_data["hote_state"] = company.state
        #         each_data["hotel_city"] = company.city
        #         each_data["hotel_pincode"] = company.pincode
        #         if each_data["date_of_birth"]:
        #             each_data["date_of_birth"] = each_data["date_of_birth"].strftime("%d/%m/%Y")
        #         if each_data["passport_date_of_issue"]:
        #             each_data["passport_date_of_issue"] = each_data["passport_date_of_issue"].strftime("%d%m%Y")
        #         if each_data["passport_valid_till"]:
        #             each_data["passport_valid_till"] = each_data["passport_valid_till"].strftime("%d%m%Y")
        #         if each_data["visa_date_of_issue"]:
        #             each_data["visa_date_of_issue"] = datetime.datetime.strptime(each_data["visa_date_of_issue"], '%Y-%m-%d').strftime("%d%m%Y")
        #         if each_data["visa_valid_till"]:
        #             each_data["visa_valid_till"] = datetime.datetime.strptime(each_data["visa_valid_till"], '%Y-%m-%d').strftime("%d%m%Y")
        #         if each_data["date_of_arrival_in_india"]:
        #             each_data["date_of_arrival_in_india"] = each_data["date_of_arrival_in_india"].strftime("%d/%m/%Y")
        #         if each_data["checkin_date"]:
        #             each_data["checkin_date"] = each_data["checkin_date"].strftime("%d/%m/%Y")
        #         if each_data["checkin_time"]:
        #             each_data["checkin_time"] = str(each_data["checkin_time"])
        #         each_data = {k: "" if not v else v for k, v in each_data.items()}
        cform = intiate()
        return {"success": True,"message":"cform"}
            # company_doc.cform_session = 0
            # company_doc.save(ignore_permissions=True,ignore_version=True)
    except Exception as e:
        print(str(e),"====================")
        # company_doc = frappe.get_doc('company',company.name)
        # company_doc.cform_session = 0
        # company_doc.save(ignore_permissions=True,ignore_version=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Process Cform","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

