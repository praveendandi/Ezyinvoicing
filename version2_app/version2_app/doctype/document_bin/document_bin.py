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

@frappe.whitelist(allow_guest=True)
def deletedocument(filepath):
	try:
		docname = frappe.get_list('Document Bin', {'invoice_file': filepath})
		frappe.db.delete('Document Bin',docname[0])
		frappe.db.commit()
		print("doneeeeeeeee")
		return True
	except Exception as e:

		print(str(e),"/a/a/a/a///////////////////")
		return False


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
