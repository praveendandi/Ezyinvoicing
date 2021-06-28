# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import logger
import traceback, sys
import os,re
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
			give_print(data["payload"],outlet_printer,logopath,qrpath)
		# extract_bills = extract_data(data["payload"],outlet_doc)
		# if extract_bills["success"] == False:
		# 	return extract_bills["message"]
		# data.update(extract_bills["data"])
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True,ignore_links=True)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing create pos bills","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}


# def extract_data(payload,outlet_doc):
# 	try:
# 		data={}
# 		raw_data = payload.split("\n")
# 		total_amount = ""
# 		for line in raw_data:
# 			if outlet_doc.closed in payload and outlet_doc.void not in payload:
# 				data["check_type"] = "Check Closed"
# 				total_amount = "0.00"
# 			elif outlet_doc.void in payload:
# 				data["check_type"] = "Closed Void Check"
# 				if re.match("[ChangeDue\s]+[A-Za-z.0-9]+",line.strip()):
# 					total_amount_regex = re.findall("\d.+",line.replace(" ",""))
# 					total_amount = total_amount_regex[0] if len(total_amount_regex) > 0 else ""
# 			else:
# 				data["check_type"] = "Normal Check"
# 				if re.match("[TotalDue\s]+[A-Za-z.0-9]+",line.strip()):
# 					total_amount_regex = re.findall("\d.+",line.replace(" ",""))
# 					total_amount = total_amount_regex[0] if len(total_amount_regex) > 0 else ""
# 			if "CHK" in line and "TBL" in line:
# 				check_no = re.search('CHK(.*)TBL', line.strip())
# 				data["check_no"] = (check_no.group(1)).strip()
# 			if "TBL" in line and "GST" in line:
# 				table_no = re.search('TBL(.*)GST', line.strip())
# 				data["table_number"] = (table_no.group(1)).strip()
# 			if "GST" in line and "GST No." not in line and "%" not in line:
# 				guest_count = line.split(" ")[-1]
# 				data["no_of_guests"] = guest_count
# 			if "TBL" in line and "GST" not in line:
# 				table_no = line.split(" ")[-1]
# 				data["table_number"] = table_no
# 		data["total_amount"] = str(total_amount)
# 		return {"success":True, "data":data}
# 	except Exception as e:
# 		print(str(e))
# 		exc_type, exc_obj, exc_tb = sys.exc_info()
# 		frappe.log_error("Ezy-invoicing extract data","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
# 		return {"success":False,"message":str(e)}

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