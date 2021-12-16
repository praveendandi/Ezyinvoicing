# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os,sys,traceback
class SocketNotification(Document):
    pass


@frappe.whitelist()
def DeleteNotifications():
    try:
        deleteb2b = frappe.db.delete('Socket Notification', {'invoice_type': 'B2B'})
        deleteb2c = frappe.db.delete('Socket Notification', {'invoice_type': 'B2C'})
        frappe.db.commit()
        return {"success":True,"message":"Successfully Deleted"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing DeleteNotifications Socket","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}	

