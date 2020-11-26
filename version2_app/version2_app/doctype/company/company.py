# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
site_folder_path = "version2_app.com"
# host = "http://localhost:8000/api/method/"
folder_path = frappe.utils.get_bench_path()
path = folder_path + '/sites/' + site_folder_path
class company(Document):
	def on_update(self):
		if self.name:
			try:
				print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
				filepath = path+self.invoice_parsing_file
				destination_path = folder_path+self.reinitiate_file_path
				print(filepath,destination_path)
				# with open(filepath) as f:
				a_file = open(filepath, "r")

				lines = a_file.readlines()
				a_file.close()

				new_file = open("destination_path", "w+")
				for line in lines:
					print("/111111111111")
					new_file.write(line)

				new_file.close()
				# frappe.throw("file updated successfully")
			except Exception as e:
				print(str(e),"************8")
				frappe.throw("file updated Failed")



			# frappe.th
# apps/version2_app/version2_app/version2_app/doctype/invoices/reinitiate_parser.py