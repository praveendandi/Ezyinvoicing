# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import logger
import traceback, sys
import os
from escpos.printer import Network
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)

class POSChecks(Document):
	pass


@frappe.whitelist(allow_guest=True)
def create_pos_bills(data):
	try:
		company_doc = frappe.get_doc("company",data["company"])
		data["mode"] = company_doc.mode
		data["doctype"] = "POS Checks"
		outlet_doc = frappe.get_doc("Outlets",data["outlet"])
		outlet_printer = frappe.db.get_value("POS Print Settings",{"outlet":outlet_doc.name},"printer")	
		if outlet_doc.print == "Yes":
			folder_path = frappe.utils.get_bench_path()
			path = folder_path + '/sites/' + company_doc.site_name +"/public"
			logopath = path+outlet_doc.outlet_logo
			qrpath = path+outlet_doc.static_payment_qr_code
			print(logopath, qrpath)
			give_print(data["payload"],outlet_printer,logopath,qrpath)
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True,ignore_links=True)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing create pos bills","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}


def give_print(text, ip, logo_path, qr_path):
	try:
		b = text.encode('utf-8')
		kitchen = Network(ip)  # Printer IP Address
		kitchen.set("CENTER", "A", "B")
		kitchen.image(img_source=logo_path)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		kitchen.text('\n')
		kitchen._raw(b)
		kitchen.hw('INIT')
		kitchen.set("CENTER", "A", "B")
		# kitchen.qr("https://caratred.com")
		kitchen.image(qr_path)
		kitchen.hw('INIT')
		kitchen.cut()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing give print","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}