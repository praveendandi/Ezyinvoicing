# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import datetime
import json,xmltodict
from regex import P
import os
import sys
import traceback
from datetime import date

import frappe
from frappe.model.document import Document
from frappe.utils import logger

frappe.utils.logger.set_log_level("DEBUG")


class ArrivalInformation(Document):
    pass


@frappe.whitelist(allow_guest=True)
def arrivalActivity(company, file_url, source):
    try:
        company_doc = frappe.get_doc("company", company)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company_doc.site_name
        # if company_doc.arrival_information_file_type != "Xml":
        if not company_doc.arrival_report:
            return {"success": False, "message": "Please upload the arrival json file."}
        json_file_path = (
            folder_path + "/sites/" + site_folder_path + company_doc.arrival_report
        )
        with open(json_file_path) as f:
            column_indexs = json.load(f)
        file_path = folder_path + "/sites/" + site_folder_path + file_url
        with open(file_path) as file:
            data = file.readlines()[3:]
        processedCount = 0
        duplicateCount = 0
        alreadyCheckinCount = 0
        total_count = 0
        check_len = 0
        # print(company_doc.arrival_information_file_type)
        if company_doc.arrival_information_file_type == "Xml":
            with open(file_path) as xml_file:
                arrivals = json.loads(json.dumps(xmltodict.parse(xml_file.read())))
            for arival in arrivals['MODULE1']['LIST_G_C9']['G_C9']:
                replace_new = list(arival.keys())
                IS_GROUP_CODE = 'No'
                if len(replace_new)>=60:
                    IS_GROUP_CODE = 'Yes'
                # print(replace_new,column_indexs)
                # print(arival,"hello")
                # print(replace_new[column_indexs["NO_OF_ADULTS"]],
                # replace_new[column_indexs["NO_OF_CHILDREN"]],"hello")
                reservation = {
                        "guest_title": arival[replace_new[column_indexs["GUEST_TITLE"]]],
                        "guest_first_name": arival[replace_new[column_indexs["GUEST_FIRST_NAME"]]],
                        "guest_last_name": arival[replace_new[column_indexs["GUEST_LAST_NAME"]]],
                        "guest_email_address": arival[replace_new[
                            column_indexs["GUEST_EMAIL_ADDRESS"]
                        ]]
                        if company != "GMM-01"
                        else "susmitha@caratred.com",
                        "room_type": arival[replace_new[column_indexs["ROOM_TYPE"]]],
                        "guest_phone_no": arival[replace_new[column_indexs["GUEST_PHONE_NO"]]],
                        "travel_agent_name": arival[replace_new[
                            column_indexs["TRAVEL_AGENT_NAME"]]
                        ],
                        "no_of_adults": arival[replace_new[column_indexs["NO_OF_ADULTS"]]],
                        "no_of_children": arival[replace_new[column_indexs["NO_OF_CHILDREN"]]],
                        "no_of_nights": arival[replace_new[column_indexs["NO_OF_NIGHTS"]]],
                        "billing_instructions": arival[replace_new[
                            column_indexs["BILLING_INSTRUCTIONS"]]
                        ],
                        "no_of_rooms": arival[replace_new[column_indexs["NO_OF_ROOMS"]]],
                        "confirmation_number": arival[replace_new[column_indexs["CONFIRMATION_NO"]]],
                        "csr_id": arival[replace_new[column_indexs["CRS_ID"]]],
                        "print_rate": "Yes"
                        if arival[replace_new[column_indexs["PRINT_RATE_YN"]]] == "Y"
                        else "No",
                        "room_rate": arival[replace_new[column_indexs["ROOM_RATE"]]],
                        "reservation_clerk": arival[replace_new[
                            column_indexs["RESERVATION_CLERK"]]
                        ],
                        "membership_no": arival[replace_new[column_indexs["MEMBERSHIP_NO"]]],
                        "membership_type": arival[replace_new[column_indexs["MEMBERSHIP_TYPE"]]],
                        "total_visits": arival[replace_new[column_indexs["TOTAL_VISITS"]]],
                        "cc_number": arival[replace_new[column_indexs["CC_NUMBER"]]],
                        "company_name": arival[replace_new[column_indexs["COMPANY_NAME"]]],
                        "booking_status": arival[replace_new[column_indexs["BOOKING_STATUS"]]],
                        "is_group_code": IS_GROUP_CODE,
                        "number_of_guests": str(
                            int(arival[replace_new[column_indexs["NO_OF_ADULTS"]]])
                            + int(arival[replace_new[column_indexs["NO_OF_CHILDREN"]]])
                        ),
                        "virtual_checkin_status": "No",
                        "company": company,
                        "cc_exp_date": arival[replace_new[column_indexs["CC_EXP_DATE"]]],
                        "room_number": str(arival[replace_new[column_indexs["room_number"]]]),
                        "checkin_time": arival[replace_new[column_indexs["checkin_time"]]].replace("*", "")
                        if arival[replace_new[column_indexs["checkin_time"]]] != None
                        else "00:00:00",
                        "checkout_time": arival[replace_new[column_indexs["checkout_time"]]].replace("*", "")
                        if arival[replace_new[column_indexs["checkout_time"]]] != None
                        else "00:00:00",
                    }
                for key in reservation.keys():
                    if reservation[key]== None and key!='checkin_time': 
                        reservation[key] = ''

                print(reservation)
                arrival_date = datetime.datetime.strptime(
                        arival[replace_new[column_indexs["ARRIVAL_DATE"]]], "%d-%b-%y"
                    ).date()
                today = date.today()
                process = False
                if arrival_date >= today:
                    process = True
                reservation["arrival_date"] = (
                    datetime.datetime.strptime(
                        arival[replace_new[column_indexs["ARRIVAL_DATE"]]], "%d-%b-%y"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    if arival[replace_new[column_indexs["ARRIVAL_DATE"]]] != ""
                    else None
                )
                reservation["departure_date"] = (
                    datetime.datetime.strptime(
                        arival[replace_new[column_indexs["DEPARTURE_DATE"]]], "%d-%b-%y"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    if arival[replace_new[column_indexs["DEPARTURE_DATE"]]] != ""
                    else None
                )
                if reservation["booking_status"] != 'PROSPECT':
                    if frappe.db.exists(
                        "Arrival Information", reservation["confirmation_number"]
                    ):
                        arrival_info_doc = frappe.get_doc(
                            "Arrival Information", reservation["confirmation_number"]
                        )
                        if reservation["booking_status"] != "CANCELLED":
                            if (
                                arrival_info_doc.virtual_checkin_status == "No"
                                and process is True
                            ):
                                duplicateCount += 1
                                if reservation["booking_status"] == "CHECKED IN":
                                    reservation["checkin_date"] = reservation[
                                        "arrival_date"
                                    ]
                                if reservation["booking_status"] == "CHECKED OUT":
                                    reservation["checkout_date"] = reservation[
                                        "departure_date"
                                    ]
                                frappe.db.set_value(
                                    "Arrival Information",
                                    reservation["confirmation_number"],
                                    reservation,
                                )
                            else:
                                alreadyCheckinCount += 1
                                if (
                                    reservation["booking_status"] == "CHECKED IN"
                                    or reservation["booking_status"] == "CHECKED OUT"
                                ):
                                    update_reservation = {
                                        "booking_status": reservation["booking_status"]
                                    }
                                    if reservation["booking_status"] == "CHECKED IN":
                                        update_reservation["checkin_date"] = reservation[
                                            "arrival_date"
                                        ]
                                    if reservation["booking_status"] == "CHECKED OUT":
                                        update_reservation["checkout_date"] = reservation[
                                            "departure_date"
                                        ]
                                    frappe.db.set_value(
                                        "Arrival Information",
                                        reservation["confirmation_number"],
                                        update_reservation,
                                    )
                        else:
                            alreadyCheckinCount += 1
                            duplicateCount += 1
                            if (
                                arrival_info_doc.booking_status == "DUE IN"
                                or arrival_info_doc.booking_status == "RESERVED"
                            ) and (arrival_info_doc.arrival_date >= arrival_date):
                                frappe.db.set_value(
                                    "Arrival Information",
                                    reservation["confirmation_number"],
                                    reservation,
                                )
                            if arrival_info_doc.booking_status == "CANCELLED":
                                frappe.db.set_value(
                                    "Arrival Information",
                                    reservation["confirmation_number"],
                                    reservation,
                                )
                    else:
                        if process:
                            processedCount += 1
                            reservation["doctype"] = "Arrival Information"
                            arrival_info = frappe.get_doc(reservation)
                            arrival_info.insert(ignore_permissions=True, ignore_links=True)
                            frappe.db.commit()
                        else:
                            pass
                    total_count += 1
                else:
                    print("booking_status is PROSPECT")

        else:
            for each_reservation in data:
                split_line = each_reservation.split("|")
                replace_new = [x.replace("\n", "") for x in split_line]
                if len(replace_new) > 4:
                    confirmation_number = ""
                    IS_GROUP_CODE = ""
                    if company_doc.name in ["RDV-01", "HRDR-01", "GMM-01"]:
                        if check_len != 0:
                            if check_len != len(replace_new):
                                find_index = data.index(each_reservation)
                                if len(data[find_index + 1]) < check_len:
                                    new_split_line = data[find_index + 1].split("|")
                                    update_data = [
                                        x.replace("\n", "") for x in new_split_line
                                    ]
                                    if company_doc.name in ["HRDR-01", "GMM-01"]:
                                        if len(update_data) > 0:
                                            if update_data[0] == "":
                                                del update_data[0]
                                    replace_new.extend(update_data)
                                    del data[find_index + 1]
                        else:
                            check_len = len(replace_new)
                    if check_len == len(replace_new) or check_len == 0:
                        check_len = len(replace_new)
                    if column_indexs["GROUP_CODE"] <= len(replace_new):
                        if replace_new[column_indexs["GROUP_CODE"]] != "":
                            confirmation_number = replace_new[column_indexs["GROUP_CODE"]]
                            IS_GROUP_CODE = "Yes"
                        else:
                            confirmation_number = replace_new[
                                column_indexs["CONFIRMATION_NO"]
                            ]
                            IS_GROUP_CODE = "No"
                    else:
                        confirmation_number = replace_new[column_indexs["CONFIRMATION_NO"]]
                        IS_GROUP_CODE = "No"
                    reservation = {
                        "guest_title": replace_new[column_indexs["GUEST_TITLE"]],
                        "guest_first_name": replace_new[column_indexs["GUEST_FIRST_NAME"]],
                        "guest_last_name": replace_new[column_indexs["GUEST_LAST_NAME"]],
                        "guest_email_address": replace_new[
                            column_indexs["GUEST_EMAIL_ADDRESS"]
                        ]
                        if company != "GMM-01"
                        else "susmitha@caratred.com",
                        "room_type": replace_new[column_indexs["ROOM_TYPE"]],
                        "guest_phone_no": replace_new[column_indexs["GUEST_PHONE_NO"]],
                        "travel_agent_name": replace_new[
                            column_indexs["TRAVEL_AGENT_NAME"]
                        ],
                        "no_of_adults": replace_new[column_indexs["NO_OF_ADULTS"]],
                        "no_of_children": replace_new[column_indexs["NO_OF_CHILDREN"]],
                        "no_of_nights": replace_new[column_indexs["NO_OF_NIGHTS"]],
                        "billing_instructions": replace_new[
                            column_indexs["BILLING_INSTRUCTIONS"]
                        ],
                        "no_of_rooms": replace_new[column_indexs["NO_OF_ROOMS"]],
                        "confirmation_number": confirmation_number,
                        "csr_id": replace_new[column_indexs["CRS_ID"]],
                        "print_rate": "Yes"
                        if replace_new[column_indexs["PRINT_RATE_YN"]] == "Y"
                        else "No",
                        "room_rate": replace_new[column_indexs["ROOM_RATE"]],
                        "reservation_clerk": replace_new[
                            column_indexs["RESERVATION_CLERK"]
                        ],
                        "membership_no": replace_new[column_indexs["MEMBERSHIP_NO"]],
                        "membership_type": replace_new[column_indexs["MEMBERSHIP_TYPE"]],
                        "total_visits": replace_new[column_indexs["TOTAL_VISITS"]],
                        "cc_number": replace_new[column_indexs["CC_NUMBER"]],
                        "company_name": replace_new[column_indexs["COMPANY_NAME"]],
                        "booking_status": replace_new[column_indexs["BOOKING_STATUS"]],
                        "is_group_code": IS_GROUP_CODE,
                        "number_of_guests": str(
                            int(replace_new[column_indexs["NO_OF_ADULTS"]])
                            + int(replace_new[column_indexs["NO_OF_CHILDREN"]])
                        ),
                        "virtual_checkin_status": "No",
                        "company": company,
                        "cc_exp_date": replace_new[column_indexs["CC_EXP_DATE"]],
                        "room_number": str(replace_new[column_indexs["room_number"]]),
                        "checkin_time": replace_new[column_indexs["checkin_time"]].replace("*", "")
                        if replace_new[column_indexs["checkin_time"]] != ""
                        else "00:00:00",
                        "checkout_time": replace_new[column_indexs["checkout_time"]].replace("*", "")
                        if replace_new[column_indexs["checkout_time"]] != ""
                        else "00:00:00",
                    }
                    arrival_date = datetime.datetime.strptime(
                        replace_new[column_indexs["ARRIVAL_DATE"]], "%d-%b-%y"
                    ).date()
                    today = date.today()
                    process = False
                    if arrival_date >= today:
                        process = True
                    reservation["arrival_date"] = (
                        datetime.datetime.strptime(
                            replace_new[column_indexs["ARRIVAL_DATE"]], "%d-%b-%y"
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        if replace_new[column_indexs["ARRIVAL_DATE"]] != ""
                        else None
                    )
                    reservation["departure_date"] = (
                        datetime.datetime.strptime(
                            replace_new[column_indexs["DEPARTURE_DATE"]], "%d-%b-%y"
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        if replace_new[column_indexs["DEPARTURE_DATE"]] != ""
                        else None
                    )
                    if reservation["booking_status"] != 'PROSPECT':
                        if frappe.db.exists(
                            "Arrival Information", reservation["confirmation_number"]
                        ):
                            arrival_info_doc = frappe.get_doc(
                                "Arrival Information", reservation["confirmation_number"]
                            )
                            if reservation["booking_status"] != "CANCELLED":
                                if (
                                    arrival_info_doc.virtual_checkin_status == "No"
                                    and process is True
                                ):
                                    duplicateCount += 1
                                    if reservation["booking_status"] == "CHECKED IN":
                                        reservation["checkin_date"] = reservation[
                                            "arrival_date"
                                        ]
                                    if reservation["booking_status"] == "CHECKED OUT":
                                        reservation["checkout_date"] = reservation[
                                            "departure_date"
                                        ]
                                    frappe.db.set_value(
                                        "Arrival Information",
                                        reservation["confirmation_number"],
                                        reservation,
                                    )
                                else:
                                    alreadyCheckinCount += 1
                                    if (
                                        reservation["booking_status"] == "CHECKED IN"
                                        or reservation["booking_status"] == "CHECKED OUT"
                                    ):
                                        update_reservation = {
                                            "booking_status": reservation["booking_status"]
                                        }
                                        if reservation["booking_status"] == "CHECKED IN":
                                            update_reservation["checkin_date"] = reservation[
                                                "arrival_date"
                                            ]
                                        if reservation["booking_status"] == "CHECKED OUT":
                                            update_reservation["checkout_date"] = reservation[
                                                "departure_date"
                                            ]
                                        frappe.db.set_value(
                                            "Arrival Information",
                                            reservation["confirmation_number"],
                                            update_reservation,
                                        )
                            else:
                                alreadyCheckinCount += 1
                                duplicateCount += 1
                                if (
                                    arrival_info_doc.booking_status == "DUE IN"
                                    or arrival_info_doc.booking_status == "RESERVED"
                                ) and (arrival_info_doc.arrival_date >= arrival_date):
                                    frappe.db.set_value(
                                        "Arrival Information",
                                        reservation["confirmation_number"],
                                        reservation,
                                    )
                                if arrival_info_doc.booking_status == "CANCELLED":
                                    frappe.db.set_value(
                                        "Arrival Information",
                                        reservation["confirmation_number"],
                                        reservation,
                                    )
                        else:
                            if process:
                                processedCount += 1
                                reservation["doctype"] = "Arrival Information"
                                arrival_info = frappe.get_doc(reservation)
                                arrival_info.insert(ignore_permissions=True, ignore_links=True)
                                frappe.db.commit()
                            else:
                                pass
                        total_count += 1
                    else:
                        print("booking_status is PROSPECT")
                
        if total_count > 0:
            arrival_activity = {
                "file_name": os.path.basename(file_url),
                "source": source,
                "file_path": file_url,
                "processed_count": processedCount,
                "duplicate_count": duplicateCount,
                "already_checkin_count": alreadyCheckinCount,
                "total_count": total_count,
                "doctype": "Arrival Activities",
                "status": "CSV import Done",
            }
            arrival_act = frappe.get_doc(arrival_activity)
            arrival_act.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.commit()
            date_time = datetime.datetime.now()
            user_name = frappe.session.user
            activity_data = {
                "doctype": "Activity Logs",
                "datetime": date_time,
                "module": "Scanezy",
                "event": "PreArrivals",
                "user": user_name,
                "activity": "Arrivals added successfully",
            }
            event_doc = frappe.get_doc(activity_data)
            event_doc.insert()
            frappe.db.commit()

        
        return {"success": True, "message": "Arrivals added successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Arrivals arrivalActivity",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


def create_arrival_info_based_on_status(reservation):
    '''
    create arrival info 
    '''
    try:
        pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Create Arrival information",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def updateEmail(confirmation="", mobile="", email=""):
    try:
        if frappe.db.exists("Arrival Information", confirmation):
            arrival_doc = frappe.get_doc("Arrival Information", confirmation)
            arrival_doc.guest_eamil2 = email
            arrival_doc.guest_mobile_no2 = mobile
            if email != "":
                arrival_doc.send_invoice_mail = 1
            arrival_doc.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
            return {"success": True, "message": "email updated"}
        return {"success": False, "message": "Reservation not found"}
    except Exception as e:
        print(str(e), "//////////////")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "updateEmail",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_arrival_info(confirmation, company):
    try:
        check_confirmation = frappe.db.sql(
            """SELECT * FROM `tabArrival Information` where (name = '{}' or csr_id = '{}') and booking_status in ('RESERVED','DUE IN') and status = 'Pending' and company = '{}'""".format(
                confirmation, confirmation, company
            ),
            as_dict=1,
        )
        if len(check_confirmation) > 0:
            return {"success": True, "data": check_confirmation}
        return {"success": False, "message": "Invalid confirmation number or csr id"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "get_arrival_info",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def autocomplete_arrival_info(confirmation_number: str, company: str):
    """
    get arrival information by confirmation
    :param confirmation_number: confirmation number
    :param company: company code
    :param fields: list of fields to be returned
    """
    try:
        auto_complete_data = frappe.db.get_list(
            "Arrival Information",
            filters={
                "name": ["like", "%" + confirmation_number + "%"],
                "company": company,
            },
            fields=[
                "name",
                "guest_first_name",
                "no_of_adults",
                "no_of_children",
                "booking_status",
                "virtual_checkin_status",
                "status",
            ],
        )
        return {"success": True, "data": auto_complete_data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "autocomplete_arrival_info",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}
