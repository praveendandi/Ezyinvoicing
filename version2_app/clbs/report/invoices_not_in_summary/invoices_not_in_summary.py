# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import traceback

def execute(filters=None):
    try:
        columns, data = ["Invoice Number","Guest Name","Confirmation Number","GST Number","Room Number","Invoice Category","ACK Date","Checkout Date","Printed Date","Summary","Total Invoice Amount"], []
        if 'tax_payer_details' in filters:
            filters={'creation': ['Between',(filters['from_date'],filters['to_date'])], "invoice_type": "B2B", "summary":["=",""],'gst_number':['like',"%"+filters['tax_payer_details']+"%"]}
        else:
            filters={'creation': ['Between',(filters['from_date'],filters['to_date'])], "invoice_type": "B2B", "summary":["=",""]}
        data = frappe.db.get_list('Invoices', filters=filters, fields=["invoice_number","guest_name","confirmation_number","gst_number","room_number","invoice_category","DATE_FORMAT(ack_date, '%d-%m-%Y %H:%i:%S') as ack_date","DATE_FORMAT(invoice_date, '%d-%m-%Y') as checkout_date","DATE_FORMAT(creation, '%d-%m-%Y') as printed_date","summary","sales_amount_after_tax as total_invoice_amount"], order_by="invoice_number")
        return columns, data
    except Exception as e:
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}
