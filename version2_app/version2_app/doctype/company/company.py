# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import shutil
import os
import pdfplumber
from datetime import date, datetime
import requests
import pandas as pd
import re
import json
import sys
import frappe

class company(Document):
	# pass
	def on_update(self):
		if self.name:
			folder_path = frappe.utils.get_bench_path()
			site_folder_path = self.site_name
			folder_path = frappe.utils.get_bench_path()
			path = folder_path + '/sites/' + site_folder_path

			reinitatefilepath = path+self.invoice_reinitiate_parsing_file
			destination_path = folder_path+self.reinitiate_file_path
			# invoice_parser_file_path
			invoicefilepath = path+self.invoice_parser_file
			destination_path2 = folder_path+self.invoice_parser_file_path
			try:
				print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
				
				shutil.copy(reinitatefilepath, destination_path)
				shutil.copy(invoicefilepath,destination_path2)
			except Exception as e:
				# shutil.copy(filepath, destination_path)
				print(str(e),"************on_update company")
				frappe.throw("file updated Failed")




@frappe.whitelist(allow_guest=True)
def getUserRoles():
    if frappe.local.request.method=="GET":
        #data = json.loads(frappe.request.data)
        doc = frappe.get_roles(frappe.session.user)
        # perm = frappe.get_permissions(frappe.session.user)
        # print(doc)
        # frappe.db.commit()
        return {"success":True,"data":doc}
    else:
        return {"success":False, "message":"User doesn't exists! please Register"}

