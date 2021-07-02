# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from re import T
import frappe
from frappe.model.document import Document
import traceback,os,sys
import datetime
class InvoicePayments(Document):
    pass


@frappe.whitelist(allow_guest=True)
def insert_invoice_payments(data):
    try:
        frappe.db.delete('Invoice Payments', {'invoice_number': data['invoice_number']})
        frappe.db.commit()
        company = frappe.get_last_doc('company')
        if len(data['items'])>0:
            for item in data['items']:
                print(item,"---------")
                date_time_obj = datetime.datetime.strptime(item['date'],company.invoice_item_date_format).strftime('%Y-%m-%d')
                doc = frappe.get_doc({"doctype":"Invoice Payments","invoice_number":data['invoice_number'],"date":date_time_obj,"payment":item['name'],'item_value':item['item_value']})
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
        return {"sucess": True, "data": 'doc'}

    except Exception as e:
        print(traceback.print_exc(),"**********  insert_invoice_payments")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_invoice_payments","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}