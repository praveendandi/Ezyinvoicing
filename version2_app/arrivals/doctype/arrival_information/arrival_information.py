# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime, os, sys, traceback
from datetime import date
from frappe.model.document import Document
from frappe.utils import logger


frappe.utils.logger.set_log_level("DEBUG")

class ArrivalInformation(Document):
    pass


@frappe.whitelist(allow_guest=True)
def arrivalActivity(company,file_url):
    try:
        company_doc = frappe.get_doc("company",company)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company_doc.site_name
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
                if len(replace_new) >= 27:
                    if replace_new[26] != "":
                        confirmation_number = replace_new[26]
                        IS_GROUP_CODE = "Yes"
                    else:
                        confirmation_number = replace_new[12]
                        IS_GROUP_CODE = "No"
                else:
                    confirmation_number = replace_new[12]
                    IS_GROUP_CODE = "No"
                reservation = {"guest_title":replace_new[0],
                    "guest_first_name":replace_new[1],
                    "guest_last_name":replace_new[2],
                    "guest_email_address":replace_new[3],
                    "room_type": replace_new[4],
                    "guest_phone_no":replace_new[5],
                    "travel_agent_name":replace_new[6],
                    "no_of_adults":replace_new[7],
                    "no_of_children":replace_new[8],
                    "no_of_nights":replace_new[9],
                    "billing_instructions":replace_new[10],
                    "no_of_rooms":replace_new[11],
                    "confirmation_number":confirmation_number,
                    "csr_id":replace_new[13],
                    "print_rate":"Yes" if replace_new[14] == "Y" else "No",
                    "room_rate":replace_new[15],
                    "reservation_clerk":replace_new[16],
                    "membership_no":replace_new[19],
                    "membership_type":replace_new[20],
                    "total_visits":replace_new[21],
                    "cc_number":replace_new[22],
                    "company_name":replace_new[24],
                    "booking_status":replace_new[25],
                    "is_group_code": IS_GROUP_CODE,
                    "virtual_checkin_status":"No",
                    "cc_exp_date":replace_new[23]
                }
                arrival_date = datetime.datetime.strptime(replace_new[17], "%d-%b-%y").date()
                today = date.today()
                process = False
                if arrival_date >= today:
                    process = True
                reservation["arrival_date"]=datetime.datetime.strptime(replace_new[17],"%d-%b-%y").strftime('%Y-%m-%d %H:%M:%S') if replace_new[17] != "" else None
                reservation["departure_date"]=datetime.datetime.strptime(replace_new[18],"%d-%b-%y").strftime('%Y-%m-%d %H:%M:%S') if replace_new[18] != "" else None
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
                        if (arrival_info_doc.booking_status == "DUE IN" or arrival_info_doc.booking_status == "RESERVED") and (arrival_info_doc.checkin_date >= arrival_date):
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
                "source":"",
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
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Arrivals arrivalActivity","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}