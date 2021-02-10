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
import random, string
import re
import json
import sys
import frappe
import os
# from version2_app.version2_app.doctype.invoices.reinitiate_parser import reinitiateInvoice

class company(Document):
<<<<<<< HEAD
        #  pass
	def on_update(self):
		if self.name:
			folder_path = frappe.utils.get_bench_path()
			site_folder_path = self.site_name
			folder_path = frappe.utils.get_bench_path()
			path = folder_path + '/sites/' + site_folder_path
			if self.invoice_reinitiate_parsing_file:
				reinitatefilepath = path+self.invoice_reinitiate_parsing_file
				destination_path = folder_path+self.reinitiate_file_path
				try:
					print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
					shutil.copy(reinitatefilepath, destination_path)
				except Exception as e:
					print(str(e),"************on_update company")
					frappe.throw("file updated Failed")
			if self.invoice_parser_file:
				# invoice_parser_file_path
				invoicefilepath = path+self.invoice_parser_file
				destination_path2 = folder_path+self.invoice_parser_file_path
				try:
					print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
					shutil.copy(invoicefilepath,destination_path2)
				except Exception as e:
					print(str(e),"************on_update company")
					frappe.throw("file updated Failed")
=======
    # pass
    def on_update(self):
        if self.name:
            folder_path = frappe.utils.get_bench_path()
            site_folder_path = self.site_name
            folder_path = frappe.utils.get_bench_path()
            path = folder_path + '/sites/' + site_folder_path
            if self.invoice_reinitiate_parsing_file:
                reinitatefilepath = path+self.invoice_reinitiate_parsing_file
                destination_path = folder_path+self.reinitiate_file_path
                try:
                    print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
                    shutil.copy(reinitatefilepath, destination_path)
                except Exception as e:
                    print(str(e),"************on_update company")
                    frappe.throw("file updated Failed")
            if self.invoice_parser_file:
                # invoice_parser_file_path
                invoicefilepath = path+self.invoice_parser_file
                destination_path2 = folder_path+self.invoice_parser_file_path
                try:
                    print(self.name,"$$$$$$$$$$$$$$$$$$$$$$$")
                    shutil.copy(invoicefilepath,destination_path2)
                except Exception as e:
                    print(str(e),"************on_update company")
                    frappe.throw("file updated Failed")
>>>>>>> 32488ebc62a4f94233d4f35054d771c8a792c800





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

@frappe.whitelist(allow_guest=True)
def createError(title,error):
    frappe.log_error(error)

@frappe.whitelist(allow_guest=True)
def getPrinters():
    raw_printers = os.popen("lpstat -p -d")
    print(raw_printers.__dict__)
    printers = []
    for index,i in enumerate(raw_printers):
        print(index,i)
        if 'system default destination' not in i and 'ezy' not in i and 'EZY' not in i and "reason unknown" not in i:
            printers.append(i.split('is')[0].split('printer')[1].strip())

    return {'success':True,"data":printers,"message":"list of avaliable printers"}

@frappe.whitelist(allow_guest=True)
def givePrint(invoiceNumber,printer):

    # get invoice details
    invoice = frappe.get_doc('Invoices',invoiceNumber)
    
    invoice_file = invoice.invoice_file
    if invoice.invoice_type == 'B2B':
        if invoice.irn_generated == 'Success':
            invoice_file = invoice.invoice_with_gst_details
        else:
            invoice_file = invoice.invoice_file
    else:
        invoice_file = invoice.invoice_file

    
    # get invoice file path 
    folder_path = frappe.utils.get_bench_path()
    company = frappe.get_last_doc('company')
    site_folder_path = company.site_name
    path = folder_path + '/sites/' + site_folder_path + invoice_file

    # invoicefile = invoice.invoice_file
    os.system("lpr -P " +printer+" "+path)
    return {"success":"True","Data":{},"message":"Job Issued to Printer "+printer}




@frappe.whitelist(allow_guest=True)
def gitCurrentBranchCommit():
    try:
        folder_path = frappe.utils.get_bench_path()
        b = os.popen("git --git-dir="+folder_path+"/apps/version2_app/.git rev-parse HEAD")
        return {"success":True,"message":b} 
    except Exception as e:
        print("git branch commit id:  ", str(e))
        return {"success":False,"message":str(e)}	


@frappe.whitelist(allow_guest=True)
def b2cstatusupdate():
    try:
        data = frappe.db.get_list('Invoices',filters={'invoice_type': 'B2C'},fields=["name","invoice_number","qr_generated","irn_generated","b2c_qrimage"])
        for each in data:
            print(each)
            if each["irn_generated"] == "NA" and each["qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices",each["name"])
                doc.qr_generated = "Success"
            elif each["irn_generated"] == "Zero Invoice" and each["qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices",each["name"])
                doc.qr_generated = "Zero Invoice"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Error" and each["qr_generated"] == "Pending":
                doc = frappe.get_doc("Invoices",each["name"])
                doc.qr_generated = "Error"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Error', irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Error" and each["qr_generated"] == "Success":
                doc = frappe.get_doc("Invoices",each["name"])
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set irn_generated = 'NA' where name = '"+each[0]+"';"
            elif each["irn_generated"] == "Zero Invoice" and each["qr_generated"] == "Success":
                doc = frappe.get_doc("Invoices",each["name"])
                doc.qr_generated = "Zero Invoice"
                doc.irn_generated = "NA"
                # update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
            else:
                doc = None
            if doc == None:
                continue
            doc.save()
            frappe.db.commit()
        return True
    except Exception as e:
        print("b2cstatusupdate", str(e))
        return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def addsacindex():
    try:
        data = frappe.db.get_all('SAC HSN CODES',fields=["name","sac_index"], order_by = 'modified')
        if len(data)>0:
            for index, j in enumerate(data):
                if j["sac_index"] == None:
                    doc = frappe.get_doc("SAC HSN CODES",j["name"])
                    doc.sac_index = ''.join(random.choice(string.digits) for _ in range(7))
                    doc.save()
                    frappe.db.commit()
            return {"success":True}
        else:
            return {"success":False, "message":"no data found"}
    except Exception as e:
        print("addsacindex", str(e))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def qr_generatedtoirn_generated():
    try:
        data = frappe.db.get_list('Invoices',filters={'invoice_type': 'B2C'},fields=["name","invoice_number","qr_generated","irn_generated","b2c_qrimage"])
        if len(data)>0:
            for each in data:
                doc = frappe.get_doc("Invoices",each["name"])
                doc.irn_generated = each["qr_generated"]
                doc.save()
                frappe.db.commit()
            return {"success":True}
        else:
            return {"success":False, "message":"no data found"}
    except Exception as e:
        print("addsacindex", str(e))
        return {"success":False,"message":str(e)}


# @frappe.whitelist(allow_guest=True)
# def reprocess_error_inoices():
# 	try:
# 		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Error'},fields=["name","invoice_number","invoice_file"])
# 		print(data)
# 		if len(data)>0:
# 			for each in data:
# 				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
# 				reinitiate = reinitiateInvoice(obj)
# 			return {"success":True}
# 		else:
# 			return {"success":False, "message":"no data found"}
# 	except Exception as e:
# 		print("reprocess_error_inoices", str(e))
# 		return {"success":False,"message":str(e)}


# @frappe.whitelist(allow_guest=True)
# def reprocess_pending_inoices():
# 	try:
# 		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Pending'},fields=["name","invoice_number","invoice_file"])
# 		if len(data)>0:
# 			for each in data:
# 				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
# 				reinitiate = reinitiateInvoice(obj)
# 			return {"success":True}
# 		else:
# 			return {"success":False, "message":"no data found"}
# 	except Exception as e:
# 		print("reprocess_pending_inoices", str(e))
# 		return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def manual_to_pms():
    try:
        data = frappe.db.get_list('Invoices',filters={'invoice_from': 'Manual'},fields=["name","invoice_number"])
        if len(data)>0:
            updatePms = frappe.db.sql("""update tabInvoices set invoice_from='Pms' where invoice_from='Manual'""")
        updatecategory = frappe.db.sql("""update tabInvoices set invoice_category='Tax Invoice' where invoice_category is NULL""")
        frappe.db.commit()
        return True
    except Exception as e:
        return{"success":False}

