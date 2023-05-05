from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import sys,traceback
import frappe
import os, importlib.util


@frappe.whitelist()
def get_parser_filePath(company):
    try:
        folder_path = frappe.utils.get_bench_path()
        path = folder_path+"/apps/version2_app/version2_app/parsers/"+company+"/invoice_parser.py"
        return {"success":True,"data":path}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing get_parser_filePath","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return{"success":False,"message":str(e)}
