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
from frappe.utils import get_site_name


class company(Document):
	# pass
	def on_update(self):
		if self.name:
			folder_path = frappe.utils.get_bench_path()
			site_folder_path = self.site_name
			folder_path = frappe.utils.get_bench_path()
			path = folder_path + '/sites/' + site_folder_path

			filepath = path+self.invoice_reinitiate_parsing_file
			destination_path = folder_path+self.reinitiate_file_path
			try:
				print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
				
				shutil.copy(filepath, destination_path)
			except Exception as e:
				# shutil.copy(filepath, destination_path)
				print(str(e),"************on_update company")
				frappe.throw("file updated Failed")




