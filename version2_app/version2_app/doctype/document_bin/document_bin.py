# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from datetime import timedelta,date

from frappe.model.document import Document

class DocumentBin(Document):
	pass



def dailyDeletedocumentBin():
	try:
		company = frappe.get_last_doc('company')
		lastdate = date.today() - timedelta(days=6)
		data = frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""",lastdate)
		print(data)
		frappe.db.commit()
		return {"success":True}
	except Exception as e:
		return {"success":False,"message":str(e)}	
