# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
import requests
import os
import pandas as pd
import os.path
import sys
from frappe.utils import cstr

class Items(Document):
	pass
	



@frappe.whitelist()
def updateitems(data):
	try:
		for each in data['items']:
			itemdoc = frappe.db.get_list("Items",filters={'parent': ['=',data['invoice_number']],'item_name':['=',each['name']]},fields=['name'])
			if len(itemdoc)>0:
				doc = frappe.get_doc("Items",itemdoc[0]['name'])
				doc.referrence = each['referrence']
				doc.save()
		frappe.db.commit()
		return {"success":True}
	except Exception as e:
		print(str(e))	
		return {"success":False,"message":str(e)}	


@frappe.whitelist()
def invoice_items(filters=[]):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        invoice_data = frappe.db.get_list("Items",filters=filters,fields=['date as Date', 'item_name as ItemName', 'sac_code as SacCode', 'discount_value as Discount','item_value as ItemValue', 'cgst as CGSTRate','cgst_amount as CGST','sgst as SSTRate','sgst_amount as SGST','igst as IGSTRate','igst_amount as IGST', 'vat as VATRate','vat_amount as VAT','state_cess as StateCESSRate','state_cess_amount as StateCESSAmount','cess as CentralCESSRate','cess_amount as CentralCESSAmount','item_value_after_gst as TotalItemValue'])
        if len(invoice_data) > 0:
            company = frappe.get_last_doc("company")
            cwd = os.getcwd()
            site_name = cstr(frappe.local.site)
            file_path = cwd + "/" + site_name + "/public/files/items_export.xlsx"
            df = pd.DataFrame.from_records(invoice_data)
            df.to_excel(file_path, index=False)
            files_new = {"file": open(file_path, 'rb')}
            payload_new = {'is_private': 1, 'folder': 'Home'}
            file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                          data=payload_new, verify=False).json()
            if "file_url" in file_response["message"].keys():
                os.remove(file_path)
                return {"success": True, "file_url": file_response["message"]["file_url"]}
            return {"success": False, "message": "something went wrong"}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("export_invoices", "line No:{}\n{}".format(
            exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}



@frappe.whitelist()
def get_items_for_pos_checks(name):
    try:
        itemdoc = frappe.db.get_list("Items",filters=[["pos_check","=",name]],fields=['*'])
        return {"success": True, "data": itemdoc}
    except Exception as e:
        print(str(e))
        return {"success":False,"message":str(e)}
