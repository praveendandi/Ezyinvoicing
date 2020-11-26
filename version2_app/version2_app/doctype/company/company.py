# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import shutil
import os
site_folder_path = "version2_app.com"
# host = "http://localhost:8000/api/method/"
folder_path = frappe.utils.get_bench_path()
path = folder_path + '/sites/' + site_folder_path
class company(Document):
	def on_update(self):
		if self.name:
			filepath = path+self.invoice_parsing_file
			destination_path = folder_path+self.reinitiate_file_path
			# print(filepath,destination_path,"/./////////")
			try:
				print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
				
				shutil.copy(filepath, destination_path)
			except Exception as e:
				# shutil.copy(filepath, destination_path)
				print(str(e),"************on_update company")
				frappe.throw("file updated Failed")



			