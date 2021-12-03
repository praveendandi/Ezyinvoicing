# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime, os, sys, traceback,json
from datetime import date
from frappe.model.document import Document
from frappe.utils import logger


frappe.utils.logger.set_log_level("DEBUG")

class ArrivalInformation(Document):
    pass


@frappe.whitelist(allow_guest=True)
def arrivalActivity(company,file_url,source):
    try:
        company_doc = frappe.get_doc("company",company)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company_doc.site_name
        if not company_doc.arrival_report:
            return {"success":False,"message":"Please upload the arrival json file."}
        json_file_path = folder_path+'/sites/'+site_folder_path+company_doc.arrival_report
        with open(json_file_path) as f:
            column_indexs = json.load(f)
        file_path = folder_path+'/sites/'+site_folder_path+file_url
        with open(file_path) as file:
            data = file.readlines()[3:]
        total_data = []
        processedCount = 0
        duplicateCount = 0
        alreadyCheckinCount = 0
        total_count = 0
        for each_reservation in data:
            split_line = each_reservation.split("|")
            replace_new = [x.replace("\n","") for x in split_line]
            if len(replace_new)>4:
                confirmation_number = ""
                IS_GROUP_CODE = ""
                print(len(replace_new), column_indexs["GROUP_CODE"])
                if column_indexs["GROUP_CODE"] <= len(replace_new):
                    if replace_new[column_indexs["GROUP_CODE"]] != "":
                        confirmation_number = replace_new[column_indexs["GROUP_CODE"]]
                        IS_GROUP_CODE = "Yes"
                    else:
                        confirmation_number = replace_new[column_indexs["CONFIRMATION_NO"]]
                        IS_GROUP_CODE = "No"
                else:
                    confirmation_number = replace_new[column_indexs["CONFIRMATION_NO"]]
                    IS_GROUP_CODE = "No"
                reservation = {"guest_title":replace_new[column_indexs["GUEST_TITLE"]],
                    "guest_first_name":replace_new[column_indexs["GUEST_FIRST_NAME"]],
                    "guest_last_name":replace_new[column_indexs["GUEST_LAST_NAME"]],
                    "guest_email_address":replace_new[column_indexs["GUEST_EMAIL_ADDRESS"]],
                    "room_type": replace_new[column_indexs["ROOM_TYPE"]],
                    "guest_phone_no":replace_new[column_indexs["GUEST_PHONE_NO"]],
                    "travel_agent_name":replace_new[column_indexs["TRAVEL_AGENT_NAME"]],
                    "no_of_adults":replace_new[column_indexs["NO_OF_ADULTS"]],
                    "no_of_children":replace_new[column_indexs["NO_OF_CHILDREN"]],
                    "no_of_nights":replace_new[column_indexs["NO_OF_NIGHTS"]],
                    "billing_instructions":replace_new[column_indexs["BILLING_INSTRUCTIONS"]],
                    "no_of_rooms":replace_new[column_indexs["NO_OF_ROOMS"]],
                    "confirmation_number":confirmation_number,
                    "csr_id":replace_new[column_indexs["CRS_ID"]],
                    "print_rate":"Yes" if replace_new[column_indexs["PRINT_RATE_YN"]] == "Y" else "No",
                    "room_rate":replace_new[column_indexs["ROOM_RATE"]],
                    "reservation_clerk":replace_new[column_indexs["RESERVATION_CLERK"]],
                    "membership_no":replace_new[column_indexs["MEMBERSHIP_NO"]],
                    "membership_type":replace_new[column_indexs["MEMBERSHIP_TYPE"]],
                    "total_visits":replace_new[column_indexs["TOTAL_VISITS"]],
                    "cc_number":replace_new[column_indexs["CC_NUMBER"]],
                    "company_name":replace_new[column_indexs["COMPANY_NAME"]],
                    "booking_status":replace_new[column_indexs["BOOKING_STATUS"]],
                    "is_group_code": IS_GROUP_CODE,
                    "number_of_guests": str(int(replace_new[column_indexs["NO_OF_ADULTS"]])+int(replace_new[column_indexs["NO_OF_CHILDREN"]])),
                    "virtual_checkin_status":"No",
                    "company":company,
                    "cc_exp_date":replace_new[column_indexs["CC_EXP_DATE"]]
                }
                arrival_date = datetime.datetime.strptime(replace_new[column_indexs["ARRIVAL_DATE"]], "%d-%b-%y").date()
                today = date.today()
                process = False
                if arrival_date >= today:
                    process = True
                reservation["arrival_date"]=datetime.datetime.strptime(replace_new[column_indexs["ARRIVAL_DATE"]],"%d-%b-%y").strftime('%Y-%m-%d %H:%M:%S') if replace_new[column_indexs["ARRIVAL_DATE"]] != "" else None
                reservation["departure_date"]=datetime.datetime.strptime(replace_new[column_indexs["DEPARTURE_DATE"]],"%d-%b-%y").strftime('%Y-%m-%d %H:%M:%S') if replace_new[column_indexs["DEPARTURE_DATE"]] != "" else None
                if frappe.db.exists('Arrival Information', reservation["confirmation_number"]):
                    arrival_info_doc = frappe.get_doc('Arrival Information',reservation["confirmation_number"])
                    if reservation["booking_status"] != "CANCELLED":
                        if (arrival_info_doc.virtual_checkin_status == "No" and process == True):
                            duplicateCount += 1
                            if(reservation["booking_status"] == "CHECKED IN"):
                                reservation['checkin_date'] = reservation["arrival_date"]
                            if(reservation["booking_status"] == "CHECKED OUT"):
                                reservation['checkout_date'] = reservation["departure_date"]
                            frappe.db.set_value('Arrival Information', reservation["confirmation_number"], reservation)
                        else:
                            alreadyCheckinCount += 1
                            if(reservation["booking_status"] == "CHECKED IN" or reservation["booking_status"] == "CHECKED OUT"):
                                update_reservation = {"booking_status":reservation["booking_status"]}
                                if(reservation["booking_status"] == "CHECKED IN"):
                                    update_reservation['checkin_date'] = reservation["arrival_date"]
                                if(reservation["booking_status"] == "CHECKED OUT"):
                                    update_reservation['checkout_date'] = reservation["departure_date"]
                                frappe.db.set_value('Arrival Information', reservation["confirmation_number"],update_reservation)
                    else:
                        alreadyCheckinCount += 1
                        duplicateCount += 1
                        if (arrival_info_doc.booking_status == "DUE IN" or arrival_info_doc.booking_status == "RESERVED") and (arrival_info_doc.arrival_date >= arrival_date):
                            frappe.db.set_value('Arrival Information', reservation["confirmation_number"], reservation)
                        if arrival_info_doc.booking_status == "CANCELLED":
                            frappe.db.set_value('Arrival Information', reservation["confirmation_number"], reservation)
                else:
                    if process:
                        processedCount += 1
                        reservation["doctype"]="Arrival Information"
                        arrival_info = frappe.get_doc(reservation)
                        arrival_info.insert(ignore_permissions=True, ignore_links=True)
                        frappe.db.commit()
                    else:
                        pass
                total_count += 1
        if total_count > 0:
            arrival_activity = {
                "file_name":os.path.basename(file_url),
                "source":source,
                "file_path":file_url,
                "processed_count":processedCount,
                "duplicate_count":duplicateCount,
                "already_checkin_count":alreadyCheckinCount,
                "total_count":total_count,
                "doctype":"Arrival Activities",
                "status":"CSV import Done"
            }
            arrival_act = frappe.get_doc(arrival_activity)
            arrival_act.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.commit()
            date_time = datetime.datetime.now()
            user_name =  frappe.session.user 
            activity_data = {"doctype":"Activity Logs","datetime":date_time,"module":"Scanezy","event":"PreArrivals","user":user_name,"activity":"Arrivals added successfully"}
            event_doc=frappe.get_doc(activity_data)
            event_doc.insert()
            frappe.db.commit()
        return {"success": True,"message":"Arrivals added successfully"}
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Arrivals arrivalActivity","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def updateEmail(confirmation=None,mobile=None,email=None):
    try:
        if frappe.db.exists("Arrival Information",confirmation):
            arrival_doc = frappe.get_doc("Arrival Information",confirmation)
            arrival_doc.guest_eamil2 = email
            arrival_doc.guest_mobile_no2 = mobile
            arrival_doc.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
            return {"success":True, "message":"email updated"}
        return {"success":False, "message":"Reservation not found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("updateEmail","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}