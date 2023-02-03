# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import sys,traceback

class POSPrintSettings(Document):
	pass


@frappe.whitelist()
def pos_printer_settings(data):
	try:
		total_data = []
		if data["type"] == "all":
			doc = frappe.db.get_list("POS Print Settings",fields=["name","outlet","printer"],start=data['start'],page_length=data['end'])
			if len(doc)>0:			
				for each in doc:
					outlet_doc = frappe.get_doc("Outlets",each["outlet"])
					printer_doc = frappe.get_doc("POS Printers", each["printer"])
					total_data.append({"name":each["name"],"outlet":outlet_doc.outlet_name,"printer":printer_doc.printer_ip,"printer_name":printer_doc.printer_name})
			else:
				return {"success":False,"message":"No data found"}
		else:
			doc = frappe.db.get_list("Outlets",filters = {'outlet_name': ['like', '%'+data["value"]+'%']})
			outlet_values = [j for each in doc for j in each.values()]
			if len(doc)>0:
				setting_doc = frappe.db.get_list("POS Print Settings",filters={"outlet":["in",outlet_values]},fields=["name","outlet","printer"],start=data['start'],page_length=data['end'])
				for each in setting_doc:
					outlet_doc = frappe.get_doc("Outlets",each["outlet"])
					printer_doc = frappe.get_doc("POS Printers", each["printer"])
					total_data.append({"name":each["name"],"outlet":outlet_doc.outlet_name,"printer":printer_doc.printer_ip,"printer_name":printer_doc.printer_name})
			else:
				return {"success":False,"message":"No data found"}
		
		return {"success":True,"data":total_data,"count":len(total_data)}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing pos printer settings","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}
