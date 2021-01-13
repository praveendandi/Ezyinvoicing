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
import mysql.connector as mysql
import requests
import pandas as pd
import re
import json
import sys
import frappe
import os

class company(Document):
	pass
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
		db = mysql.connect(
			host = "127.0.0.1",
			user = "root",
			passwd = "root",
			database = "_ae17eaceb43e7f9c"
		)
		cursor = db.cursor()
		query = "SELECT name,invoice_number,qr_generated,irn_generated,b2c_qrimage FROM tabInvoices where invoice_type='B2C';"
		cursor.execute(query)
		records = cursor.fetchall()
		for each in records:
			if each[3] == "NA" and each[2] == "Pending":
				print(1)
				update = "Update tabInvoices set qr_generated = 'Success' where name = '"+each[0]+"';"
			elif each[3] == "Zero Invoice" and each[2] == "Pending":
				print(2)
				update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each[3] == "Error" and each[2] == "Pending":
				print(2)
				update = "Update tabInvoices set qr_generated = 'Error', irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each[3] == "Error" and each[2] == "Success":
				print(4)
				update = "Update tabInvoices set irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each[3] == "Zero Invoice" and each[2] == "Success":
				update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
			else:
				update = ""
			cursor.execute(update)
			commit_changes = db.commit()
			print(commit_changes)
		return True
	except Exception as e:
		print("b2cstatusupdate", str(e))
		return {"success":False,"message":str(e)}
