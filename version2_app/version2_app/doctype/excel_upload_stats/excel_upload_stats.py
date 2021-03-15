# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from datetime import date
import requests
import datetime
import random
import traceback
import string
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
import time
# from version2_app.version2_app.doctype.invoices.invoices import *
# from version2_app.version2_app.doctype.payment_types.payment_types import *
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
import math



class ExceluploadStats(Document):
	pass

@frappe.whitelist()
def InsertExcelUploadStats(data):
	try:
		for each in data['data']:
			if "Pending" not in each:
				each['Pending'] = 0
			if "Success" not in each:
				each['Success'] = 0
			if "Error" not in each:
				each['Error'] = 0
			if "B2B" not in each:
				each['B2B'] = 0
			if "B2C" not in each:
				each['B2C'] = 0				
			process_time = datetime.datetime.now() - datetime.datetime.strptime(data['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
			doc_data = {"doctype":"Excel upload Stats","invoice_date":each['date'],"invoices_count":each['invoice_number'],"pending":each['Pending'],"success":each['Success'],"error":each['Error'],"b2b":each['B2B'],"b2c":each['B2C'],"uploaded_by":data['uploaded_by'],"process_time":process_time,"referrence_file":data['referrence_file'],"gst_file":data['gst_file']}
			doc = frappe.get_doc(doc_data)
			doc.insert(ignore_permissions=True, ignore_links=True)
		return {"success":True,"message":"Done"}
	except Exception as e:
		print(str(e),"     InsertExcelUploadStats  ")
		return {"message":str(e),"success":False}		
