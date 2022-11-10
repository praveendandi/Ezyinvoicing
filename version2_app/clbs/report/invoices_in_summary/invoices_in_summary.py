# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import traceback


def execute(filters=None):
    try:
        columns, data = ["Invoice Number","Guest Name","GST Number","Invoice Category","ACK Date","Printed Date","Summary","Total Invoice Amount", "Emails", "Email Send Time"], []
        if 'tax_payer_details' in filters:
            filters={'creation': ['Between',(filters['from_date'],filters['to_date'])], "invoice_type": "B2B", "summary":["!=",""],'gst_number':['like',"%"+filters['tax_payer_details']+"%"]}
        else:
            filters={'creation': ['Between',(filters['from_date'],filters['to_date'])], "invoice_type": "B2B", "summary":["!=",""]}
        data = frappe.db.get_list('Invoices', filters=filters, fields=["invoice_number","guest_name","gst_number","invoice_category","DATE_FORMAT(ack_date, '%d-%m-%Y %H:%i:%S') as ack_date","DATE_FORMAT(creation, '%d-%m-%Y') as printed_date","summary","sales_amount_after_tax as total_invoice_amount"], order_by="invoice_number")
        for each in data:
            if each["summary"]:
                get_emails = frappe.db.get_list("Summary Email Tracking", filters=[["summary","=",each["summary"]]],pluck="emails")
                emails = [email for each in get_emails for email in json.loads(each)]
                if len(emails) > 0:
                    emails = list(set(emails))
                    each["emails"] = ",".join(emails)
                creation_date = frappe.db.get_list("Summary Email Tracking", filters=[["summary","=",each["summary"]]],pluck="creation")
                if len(creation_date)>0:
                    each["email_send_time"] = str(creation_date[0])
        return columns, data
    except Exception as e:
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}
