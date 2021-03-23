from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import time
import traceback
import os
import datetime
import json

# {'items': [{'date': '11-12-19', 'item_value': 222000.0, 'sac_code': 'No Sac', 'sort_order': 1, 'name': 'BQT (OC) Lunch'}], 'invoice_number': '303698', 'company_code': 'ICSJWMA-01', 'invoice_item_date_format': '%d-%m-%y', 'sez': 0}


@frappe.whitelist(allow_guest=True)
def BulkUploadReprocess(invoice_number):
	try:
		invoice_data = frappe.get_doc('Invoices',invoice_number)
		company = frappe.get_doc('company',invoice_data.company)
		line_items = json.loads(invoice_data.invoice_object_from_file)
		print(line_items)
		items = []:
		sort_order = 1
		for each in line_items:
			item_dict = {}
			item_dict['date'] = each['BILL_GENERATION_DATE']
			item_dict['item_value'] = each['FT_DEBIT']
			item_dict['sac_code'] = "No Sac"
			item_dict['name'] = each['TRANSACTION_DESCRIPTION']
			item_dict['sort_order'] = sort_order
			sort_order+=1
			items.append(item_dict)
		calculate_data = {}
		calculate_data['items'] = items
		calculate_data['invoice_number'] = invoice_number
		calculate_data['company_code'] = invoice_data.company 
		calculate_data['invoice_item_date_format'] = company.invoice_item_date_format
		calculate_data['sez'] = invoice_data.sez	
		return {"success":True,"data":line_items}
	except Exception as e:
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}    
