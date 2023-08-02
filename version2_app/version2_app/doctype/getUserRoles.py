import frappe
import json
import requests
from datetime import date
import requests
import datetime
import random
import traceback,os,sys
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice


@frappe.whitelist()
def getUserRoles():
    try:
        if frappe.local.request.method == "POST":
            data = json.loads(frappe.request.data)
            print(data,"etst")
            for i in data['role']:
                if i == 'ezy-admin' or i=='ezy-Admin':
                    return {"success": False, "message": "Cannot assign 'ezy-admin' role."}
                doc = frappe.get_doc({
                    "docstatus": 0,
                    "doctype": "Has Role",
                    "modified_by": "Administrator",
                    "owner": "Administrator",
                    "parent": data['parent'],
                    'parentfield': "roles",
                    "parenttype": "User",
                    "role": i,
                    })
                doc.save()
                frappe.db.commit()
                
            return {"success":True}
        if frappe.local.request.method=="PUT":
            data = json.loads(frappe.request.data)
            par = frappe.db.delete('Has Role', {'parent': data['parent']})
            # frappe.db.commit()
            for i in data['role']:
                if i == 'ezy-admin'or i=='ezy-Admin':
                    return {"success": False, "message": "Cannot assign 'ezy-admin' role."}
                doc = frappe.get_doc({
                    "docstatus": 0,
                    "doctype": "Has Role",
                    # "idx": 1,
                    "modified_by": "Administrator",
                    "owner": "Administrator",
                    "parent": data['parent'],
                    'parentfield': "roles",
                    "parenttype": "User",
                    "role": i,
                    })
                doc.save(ignore_permissions=True, ignore_version=True)
                frappe.db.commit()
            return {"success":True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing getUserRoles","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False, "message": str(e)}		
