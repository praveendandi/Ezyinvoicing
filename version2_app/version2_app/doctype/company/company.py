# -*- coding: utf-8 -*-
# Copyright (c) 2020, Caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
from subprocess import Popen, PIPE, STDOUT
import shutil,shlex
from pathlib import Path
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
import os, importlib.util
# from version2_app.version2_app.doctype.invoices.reinitiate_parser import reinitiateInvoice
#funnnnnnnnnnn
#sample=---=

abs_path = os.path.dirname(os.getcwd())
module_name = 'reinitiateInvoice'



class company(Document):
	# pass
	def on_update(self):
		if self.name:
			folder_path = frappe.utils.get_bench_path()
			site_folder_path = self.site_name
			folder_path = frappe.utils.get_bench_path()
			path = folder_path + '/sites/' + site_folder_path
			if self.invoice_reinitiate_parsing_file:
				reinitatefilepath = path + self.invoice_reinitiate_parsing_file
				destination_path = folder_path + self.reinitiate_file_path
				try:
					print(self.name, "$$$$$$$$$$$$$$$$$$$$$$$")
					shutil.copy(reinitatefilepath, destination_path)
				except Exception as e:
					print(str(e), "************on_update company")
					frappe.throw("file updated Failed")
			if self.invoice_parser_file:
				# invoice_parser_file_path
				invoicefilepath = path + self.invoice_parser_file
				destination_path2 = folder_path + self.invoice_parser_file_path
				try:
					print(self.name, "$$$$$$$$$$$$$$$$$$$$$$$")
					shutil.copy(invoicefilepath, destination_path2)
				except Exception as e:
					print(str(e), "************on_update company")
					frappe.throw("file updated Failed")


@frappe.whitelist(allow_guest=True)
def getUserRoles():
	if frappe.local.request.method == "GET":
		#data = json.loads(frappe.request.data)
		doc = frappe.get_roles(frappe.session.user)
		# perm = frappe.get_permissions(frappe.session.user)
		# print(doc)
		# frappe.db.commit()
		return {"success": True, "data": doc}
	else:
		return {
			"success": False,
			"message": "User doesn't exists! please Register"
		}


@frappe.whitelist(allow_guest=True)
def createError(title, error):
	frappe.log_error(error)


@frappe.whitelist(allow_guest=True)
def getPrinters():
	raw_printers = os.popen("lpstat -p -d")    
	print(raw_printers.__dict__)
	printers = []
	for index, i in enumerate(raw_printers):
		print(index, i)
		if 'system default destination' not in i and 'ezy' not in i and 'EZY' not in i and "reason unknown" not in i:
			printers.append(i.split('is')[0].split('printer')[1].strip())

	return {
		'success': True,
		"data": printers,
		"message": "list of avaliable printers"
	}


@frappe.whitelist(allow_guest=True)
def givePrint(invoiceNumber, printer):

	# get invoice details
	invoice = frappe.get_doc('Invoices', invoiceNumber)

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
	os.system("lpr -P " + printer + " " + path)
	return {
		"success": "True",
		"Data": {},
		"message": "Job Issued to Printer " + printer
	}


@frappe.whitelist(allow_guest=True)
def gitCurrentBranchCommit():
	try:
		folder_path = frappe.utils.get_bench_path()
		b = os.popen("git --git-dir=" + folder_path +
					 "/apps/version2_app/.git rev-parse HEAD")
		return {"success": True, "message": b}
	except Exception as e:
		print("git branch commit id:  ", str(e))
		return {"success": False, "message": str(e)}
# angular_project_production_path

@frappe.whitelist(allow_guest=True)
def gitUiBranchCommit(company):
	try:
		company = frappe.get_doc('company',company)
		# folder_path = frappe.utils.get_bench_path()
		b = os.popen("git --git-dir=" + company.angular_project_production_path+"/.git rev-parse HEAD")
		return {"success": True, "message": b}
	except Exception as e:
		print("git branch commit id:  ", str(e))
		return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def gitpull():
	try:
		# company = frappe.get_doc('company',company)
		# folder_path = frappe.utils.get_bench_path()
		b = os.popen("git --git-dir=/home/caratred/frappe_projects/Einvoice_Bench/apps/version2_app/.git pull origin git-pull-check")
		return {"success": True, "message": b}
	except Exception as e:
		print("git branch commit id:  ", str(e))
		return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def b2cstatusupdate():
	try:
		data = frappe.db.get_list('Invoices',
								  filters={'invoice_type': 'B2C'},
								  fields=[
									  "name", "invoice_number", "qr_generated",
									  "irn_generated", "b2c_qrimage"
								  ])
		for each in data:
			print(each)
			if each["irn_generated"] == "NA" and each[
					"qr_generated"] == "Pending":
				doc = frappe.get_doc("Invoices", each["name"])
				doc.qr_generated = "Success"
			elif each["irn_generated"] == "Zero Invoice" and each[
					"qr_generated"] == "Pending":
				doc = frappe.get_doc("Invoices", each["name"])
				doc.qr_generated = "Zero Invoice"
				doc.irn_generated = "NA"
				# update = "Update tabInvoices set qr_generated = 'Zero Invoice', irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each["irn_generated"] == "Error" and each[
					"qr_generated"] == "Pending":
				doc = frappe.get_doc("Invoices", each["name"])
				doc.qr_generated = "Error"
				doc.irn_generated = "NA"
				# update = "Update tabInvoices set qr_generated = 'Error', irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each["irn_generated"] == "Error" and each[
					"qr_generated"] == "Success":
				doc = frappe.get_doc("Invoices", each["name"])
				doc.irn_generated = "NA"
				# update = "Update tabInvoices set irn_generated = 'NA' where name = '"+each[0]+"';"
			elif each["irn_generated"] == "Zero Invoice" and each[
					"qr_generated"] == "Success":
				doc = frappe.get_doc("Invoices", each["name"])
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
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def addsacindex():
	try:
		data = frappe.db.get_all('SAC HSN CODES',
								 fields=["name", "sac_index"],
								 order_by='modified')
		if len(data) > 0:
			for index, j in enumerate(data):
				if j["sac_index"] == None:
					doc = frappe.get_doc("SAC HSN CODES", j["name"])
					doc.sac_index = ''.join(
						random.choice(string.digits) for _ in range(7))
					doc.save()
					frappe.db.commit()
			return {"success": True}
		else:
			return {"success": False, "message": "no data found"}
	except Exception as e:
		print("addsacindex", str(e))
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def qr_generatedtoirn_generated():
	try:
		data = frappe.db.get_list('Invoices',
								  filters={'invoice_type': 'B2C'},
								  fields=[
									  "name", "invoice_number", "qr_generated",
									  "irn_generated", "b2c_qrimage"
								  ])
		if len(data) > 0:
			for each in data:
				doc = frappe.get_doc("Invoices", each["name"])
				doc.irn_generated = each["qr_generated"]
				doc.save()
				frappe.db.commit()
			return {"success": True}
		else:
			return {"success": False, "message": "no data found"}
	except Exception as e:
		print("addsacindex", str(e))
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def errorInvoicesList():
	try:
		doc = frappe.db.get_list('company',fields=['name'])
	   
		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Error'},fields=["name","invoice_number","guest_name","irn_generated"])
		if len(data)>0:
			return {"success":True,"data":data}
		else:
			return {"success":False,"message":"No data"} 
	except Exception as e:
		return {"success":False,"mesasge":str(e)}

@frappe.whitelist(allow_guest=True)
def reprocess_error_inoices():
	try:
		doc = frappe.db.get_list('company',fields=['name',"new_parsers"])
		if doc[0]["new_parsers"] == 0:
			file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc[0]["name"]+'/reinitiate_parser.py'
		else:
			file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoices/invoice_parsers/'+doc[0]["name"]+'/reinitiate_parser.py'
		spec = importlib.util.spec_from_file_location(module_name, file_path)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Error'},fields=["name","invoice_number","invoice_file"])
		if len(data)>0:
			# frappe.publish_realtime("custom_socket", {'data':reinitiate,'message':reinitiate,'type':"reprocess pending invoicess","invoice_number":each['name'],"status":doc.irn_generated,"guest_name":doc.guest_name})
			for each in data:
				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
				reinitiate = module.reinitiateInvoice(obj)
				doc = frappe.get_doc("Invoices",each['name'])
				frappe.publish_realtime("custom_socket", {'data':reinitiate,'message':reinitiate,"invoice_number":each['name'],'type':"redo error","status":doc.irn_generated,"guest_name":doc.guest_name})
			return {"success":True}
		else:
			return {"success":False, "message":"no data found"}
	except Exception as e:
		print("reprocess_error_inoices", str(e))
		return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def reprocess_pending_inoices():
	try:
		doc = frappe.db.get_list('company',fields=['name',"new_parsers"])
		if doc[0]["new_parsers"] == 0:
			file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc[0]["name"]+'/reinitiate_parser.py'
		else:
			file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoices/invoice_parsers/'+doc[0]["name"]+'/reinitiate_parser.py'
		spec = importlib.util.spec_from_file_location(module_name, file_path)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		data = frappe.db.get_list('Invoices',filters={'irn_generated': 'Pending'},fields=["name","invoice_number","invoice_file"])
		if len(data)>0:
			for each in data:
				obj = {"filepath":each["invoice_file"],"invoice_number":each["name"]}
				reinitiate = module.reinitiateInvoice(obj)
				doc = frappe.get_doc("Invoices",each['name'])
				frappe.publish_realtime("custom_socket", {'data':reinitiate,'message':reinitiate,'type':"reprocess pending invoicess","invoice_number":each['name'],"status":doc.irn_generated,"guest_name":doc.guest_name})
			return {"success":True}
		else:
			return {"success":False, "message":"no data found"}
	except Exception as e:
		print("reprocess_pending_inoices", str(e))
		return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def manual_to_pms():
	try:
		data = frappe.db.get_list('Invoices',
								  filters={'invoice_from': 'Manual'},
								  fields=["name", "invoice_number"])
		if len(data) > 0:
			updatePms = frappe.db.sql(
				"""update tabInvoices set invoice_from='Pms' where invoice_from='Manual'"""
			)
		updatecategory = frappe.db.sql(
			"""update tabInvoices set invoice_category='Tax Invoice' where invoice_category is NULL"""
		)
		frappe.db.commit()
		return True
	except Exception as e:
		return {"success": False}



@frappe.whitelist(allow_guest=True)
def manulaTax_credit_to_debit():
	try:
		data = frappe.db.get_list('Items',
								  filters={
									  'item_mode': 'Credit',
									  'is_credit_item': 'Yes'
								  },
								  fields=["name", "parent"])
		if len(data) > 0:
			updatetax = frappe.db.sql(
				"""update tabItems set item_mode='Debit' where item_mode='credit' and is_credit_item='No'"""
			)
			frappe.db.commit()
		# print(data)
		return True
	except Exception as e:
		return {"success": False, "message": str(e)}


import time


# from bench_manager.bench_manager.utils import run_command
@frappe.whitelist(allow_guest=True)
def console_command(key=None,
					caller='bench_update_pull',
					app_name=None,
					branch_name=None):
	company = frappe.get_last_doc("company")                
	commands = {
		"bench_update": ["bench update"],
		"switch_branch": [""],
		"get-app": ["bench get-app {app_name}".format(app_name=app_name)],
		"bench_update_pull": ["git pull origin "+company.backend_git_branch, "bench migrate"]
	}
	run_command(commands=commands[caller],
				doctype='Bench Settings',
				key=str(time.time()),
				docname='Bench Settings')
	# frappe.publish_realtime("custom_socket", {'message':'bench update completed','type':"bench completed"})            
	return True


# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappé and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from subprocess import Popen, PIPE, STDOUT
import re, shlex





def run_command(commands,
				doctype,
				key,
				cwd='..',
				docname=' ',
				after_command=None):
	verify_whitelisted_call()
	start_time = frappe.utils.time.time()
	console_dump = ""
	logged_command = " && ".join(commands)
	logged_command += " "  #to make sure passwords at the end of the commands are also hidden
	sensitive_data = [
		"--mariadb-root-password", "--admin-password", "--root-password"
	]
	for password in sensitive_data:
		logged_command = re.sub("{password} .*? ".format(password=password),
								'',
								logged_command,
								flags=re.DOTALL)
	doc = frappe.get_doc({
		'doctype': 'Bench Manager Command',
		'key': key,
		'source': doctype + ': ' + docname,
		'command': logged_command,
		'console': console_dump,
		'status': 'Ongoing'
	})
	doc.insert()
	frappe.db.commit()
	print(doc.name, '----------------------')

	try:
		for command in commands:
			print(command)
			terminal = Popen(shlex.split(command),
							 stdin=PIPE,
							 stdout=PIPE,
							 stderr=STDOUT,
							 cwd='/home/caratred/frappe_projects/Einvoice_Bench/apps/version2_app')
			print(terminal._waitpid_lock,"terminal") 
		 
		if terminal.wait():
			_close_the_doc(start_time,
						   key,
						   console_dump,
						   status='Failed',
						   user=frappe.session.user)
		else:
			_close_the_doc(start_time,
						   key,
						   console_dump,
						   status='Success',
						   user=frappe.session.user)
		terminal = Popen(shlex.split("bench migrate"),
							 stdin=PIPE,
							 stdout=PIPE,
							 stderr=STDOUT,
							 cwd=cwd)    
		common_site = frappe.utils.get_bench_path()    
		with open(common_site+"/sites/common_site_config.json", "r") as jsonFile:
			data = json.load(jsonFile)
		data["maintenance_mode"] = 0
		data["pause_scheduler"] = 0

		with open(common_site+"/sites/common_site_config.json", "w") as jsonFile:
			json.dump(data, jsonFile)                     
	except Exception as e:
		print(str(e),"  excep")
		_close_the_doc(start_time,
					   key,
					   "{} \n\n{}".format(e, console_dump),
					   status='Failed',
					   user=frappe.session.user)
	finally:
		frappe.db.commit()
		_refresh(doctype=doctype, docname=docname, commands=commands)

@frappe.whitelist(allow_guest=True)
def update_parsers():
	try:
		company = frappe.get_last_doc('company')
		if company.parsers_branch_name:
			command = "git pull origin "+company.parsers_branch_name
			abs_path = os.path.dirname(os.getcwd())
			cwd = abs_path+'/apps/version2_app/version2_app/parsers_invoices/invoice_parsers/'
			check_folder = abs_path+'/apps/version2_app/version2_app/parsers_invoices'
			if not os.path.exists(check_folder):
				os.mkdir(check_folder)
				clone_command = "git clone https://prasanthvajja:foQJihWZhufdixW43yCs@gitlab.caratred.com/prasanthvajja/invoice_parsers.git"
				Popen(shlex.split(clone_command),stdin=PIPE,stdout=PIPE,stderr=STDOUT,cwd=check_folder)
			# token = "foQJihWZhufdixW43yCs"
			terminal = Popen(shlex.split(command),stdin=PIPE,stdout=PIPE,stderr=STDOUT,cwd=cwd)
			return{"success":True,"message":"Parsers Updated Successfully"}
		else:
			return{"success":False,"message":"Please add branch name in Company"}
	except Exception as e:
		return{"success":False,"message":str(e)}



@frappe.whitelist(allow_guest=True)
def diskspace():
	b = os.popen(" df -h /dev/sda1")
	print(b)
	# print(b.encoding)
	return b

@frappe.whitelist(allow_guest=True)
def bench_migrate():
	try:
		terminal = Popen(shlex.split("bench migrate"),
								stdin=PIPE,
								stdout=PIPE,
								stderr=STDOUT,
								cwd="..")
		return {"success":True,"message":"Bench Migrate Done"} 
	except Exception as e:
		print(str(e),"      bench_migrate")
		return {"success":False,"messgae":str(e)}                                


def _close_the_doc(start_time, key, console_dump, status, user):
	time_taken = frappe.utils.time.time() - start_time
	final_console_dump = ''
	console_dump = console_dump.split('\n\r')
	for i in console_dump:
		i = i.split('\r')
		final_console_dump += '\n' + i[-1]
	frappe.set_value('Bench Manager Command', key, 'console',
					 final_console_dump)
	frappe.set_value('Bench Manager Command', key, 'status', status)
	frappe.set_value('Bench Manager Command', key, 'time_taken', time_taken)
	frappe.publish_realtime(key,
							'\n\n' + status + '!\nThe operation took ' +
							str(time_taken) + ' seconds',
							user=user)


def _refresh(doctype, docname, commands):
	frappe.get_doc(doctype, docname).run_method('after_command',
												commands=commands)



@frappe.whitelist()
def verify_whitelisted_call():
	if 'bench_manager' not in frappe.get_installed_apps():
		raise ValueError("This site does not have bench manager installed.")


def safe_decode(string, encoding='utf-8'):
	try:
		string = string.decode(encoding)
	except Exception:
		pass
	return string



@frappe.whitelist(allow_guest=True)
def updateUiProd(company):
	try:
		print("==========")
		company = frappe.get_doc('company',company)
		commands = ['git pull origin '+company.ui_git_branch,'systemctl reload nginx','systemctl restart nginx']
		
		console_dump = ''
		
		cwd = company.angular_project_production_path
		key = str(time.time())
		# count = 0
		for command in commands:
			print(command,"    command")
			terminal = Popen(shlex.split(command),
							stdin=PIPE,
							stdout=PIPE,
							stderr=STDOUT,
							cwd=cwd)
			for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
				console_dump += c
		logged_command = " && ".join(commands)
		frappe.publish_realtime("custom_socket", {'message':'system_reload','type':"system_reload"})
		frappe.log_error("Angular project pull data","updateUiProd")
	except Exception as e:
		print(str(e),"    updateUiProd")
