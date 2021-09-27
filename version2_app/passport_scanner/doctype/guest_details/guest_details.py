# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import sys,traceback
from frappe.model.document import Document

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
        frappe.log_error("Ezy-invoicing guest update attachment logs","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}