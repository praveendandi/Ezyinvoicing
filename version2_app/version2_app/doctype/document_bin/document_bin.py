# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,glob
import datetime,os,sys,traceback
from datetime import timedelta,date
from frappe.utils import cstr
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
        cwd=cwd = os.getcwd() 
        site_name = cstr(frappe.local.site)
        list_files=glob.glob(cwd+"/"+site_name+"/public/files/*.gz")
        for each_file in list_files:
            os.remove(each_file)
        return {"success":True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing dailyDeletedocumentBin","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}	
