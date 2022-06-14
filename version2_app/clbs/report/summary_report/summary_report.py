# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import traceback
import pandas as pd
# import frappe

def execute(filters=None):
    try:
        columns, data = ["Summary ID", "Summary Name", "GST Number", "Generated Date", "Status", "Dispatch Date", "Total Value", "Emails", "Email Send Time"], []
        if 'tax_payer_details' in filters:
            filters = {'creation': ['Between',(filters['from_date'],filters['to_date'])],'tax_payer_details':['like',"%"+filters['tax_payer_details']+"%"]}
        else:
            filters = {'creation': ['Between',(filters['from_date'],filters['to_date'])]}
        summary_details = frappe.db.get_list("Summaries",filters=filters, fields=["name","reference","summary_title","tax_payer_details","DATE(creation)", "status"], as_list=False)
        if len(summary_details)>0:
            for each in summary_details:
                each["DATE(creation)"] = str(each["DATE(creation)"])
                get_dispatch_details = frappe.db.get_value("Dispatch Details", {"summaries":each["name"]}, "dispatch_date")
                if get_dispatch_details:
                    each["dispatch_date"] = get_dispatch_details
                else:
                    each["dispatch_date"] = None
                get_total_amount = frappe.db.get_list("Summary Breakups", filters=[["summaries","=",each["name"]]], fields=["sum(Amount) as amount"],group_by='summaries')
                each["total_amount"] = get_total_amount[0]["amount"] if len(get_total_amount) > 0 else ""    
                each["emails"] = None
                each["email_send_time"] = None
                if each["name"]:
                    get_emails = frappe.db.get_list("Summary Email Tracking", filters=[["summary","=",each["name"]]],pluck="emails")
                    emails = [email for each in get_emails for email in json.loads(each)]
                    if len(emails) > 0:
                        emails = list(set(emails))
                        each["emails"] = ",".join(emails)
                    creation_date = frappe.db.get_list("Summary Email Tracking", filters=[["summary","=",each["name"]]],pluck="creation")
                    if len(creation_date)>0:
                        each["email_send_time"] = str(creation_date[0])  
                del each["name"]
            for each in summary_details:
                data.append(list(each.values()))
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}
