# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe
import os,sys,traceback
class PaymentTypes(Document):
    pass

@frappe.whitelist(allow_guest=True)
def GetPaymentTypes():
    try:
        doc = frappe.db.get_list("Payment Types",filters={
        'status': 'Active'},fields=['payment_type'],as_list=True)
        # print(doc)
        return {"success":True,"data":doc}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing GetPaymentTypes","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":e}