# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Items(Document):
	pass
	



@frappe.whitelist(allow_guest=True)
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
