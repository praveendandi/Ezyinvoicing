import frappe
import json
import requests
from datetime import date
import requests
import datetime
import random
import traceback
from frappe.utils import get_site_name
import pandas as pd
import numpy as np

@frappe.whitelist(allow_guest=True)
def getUserRoles():
	if frappe.local.request.method == "POST":
		data = json.loads(frappe.request.data)
		print(data,"etst")
		for i in data['role']:
			doc = frappe.get_doc({
				"docstatus": 0,
				"doctype": "Has Role",
				"modified_by": "Administrator",
				"owner": "Administrator",
				"parent": data['parent'],
				'parentfield': "roles",
				"parenttype": "User",
				"role": i,
				})
			doc.save()
			frappe.db.commit()
			
		return {"success":True}
	if frappe.local.request.method=="PUT":
		data = json.loads(frappe.request.data)
		par = frappe.db.delete('Has Role', {'parent': data['parent']})
		# frappe.db.commit()
		for i in data['role']:
			doc = frappe.get_doc({
				"docstatus": 0,
				"doctype": "Has Role",
				 # "idx": 1,
				"modified_by": "Administrator",
				"owner": "Administrator",
				"parent": data['parent'],
				'parentfield': "roles",
				"parenttype": "User",
				"role": i,
				})
			doc.save()
			frappe.db.commit()
		return {"success":True}
		
@frappe.whitelist(allow_guest=True)
def samplebulk():
	folder_path = frappe.utils.get_bench_path()
	items_data_file = "/private/files/EINVOICE 01.03.2021 to 01.03.2021.xlsx"
	company = "TLND-01"
	companyData = frappe.get_doc('company',company)
	site_folder_path = companyData.site_name
	items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
	items_dataframe = pd.read_excel(items_file_path)
	# print(items_dataframe[''])
	# list(dataPd['2'])
	columnslist = items_dataframe.columns.values.tolist()
	columnslist = columnslist[0].split("|")
	print(columnslist,len(columnslist))
	listdata = items_dataframe.head(3)
	# print(listdata)
	valuesdata = items_dataframe.values.tolist()
	print(valuesdata[0],len(valuesdata),type(valuesdata))
	print("--------")
	val = valuesdata[0][0].split("|")
	print(val,len(val))
	return True		
	# apps/version2_app/version2_app/version2_app/doctype/getUserRoles.py