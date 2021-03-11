# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import json
import traceback

def execute(filters=None):
	try:
		total_data = []
		columns = [ "Deleted On", "Deleted By", "Invoice Number", "Room Number", "Guest Name", "Invoice Date"]
		doc = frappe.db.get_list("Deleted Document",filters={'creation': ['Between',(filters['from_date'],filters['to_date'])],"deleted_doctype":"Invoices"},fields=["deleted_name","creation","owner","data"],order_by="creation desc")
		for each in doc:
			removed_milliseconds = str(each["creation"]).split(".")[0]
			invoice_data = json.loads(each["data"])
			values_list = [removed_milliseconds, each["owner"], each["deleted_name"], invoice_data["room_number"], invoice_data["guest_name"], invoice_data["invoice_date"]]
			total_data.append(values_list)
		columns, data = columns, total_data
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}