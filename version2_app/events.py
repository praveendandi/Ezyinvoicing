import frappe

from version2_app.parsers import *
import json, shlex, time, re
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import datetime
import importlib.util
import traceback
from datetime import date, timedelta



def invoice_created(doc, method=None):
    print("Invoice Created",doc.name)
    if frappe.db.exists('Invoice Reconciliations', doc.name):
        reconciliations_doc = frappe.get_doc('Invoice Reconciliations', doc.name)
        reconciliations_doc.invoice_found = "Yes"
        reconciliations_doc.save(ignore_permissions=True,ignore_version=True)
    if doc.invoice_from=="Pms":
        bin_name = frappe.db.get_value('Document Bin',{'invoice_file': doc.invoice_file})
        bin_doc = frappe.get_doc("Document Bin",bin_name)
        bin_doc.print_by = doc.print_by
        bin_doc.document_type = doc.invoice_category
        bin_doc.invoice_number = doc.name
        # bin_doc.error_log = error_log
        bin_doc.document_printed = "Yes"
        bin_doc.save(ignore_permissions=True,ignore_version=True)



def invoice_deleted(doc,method=None):
    frappe.publish_realtime("custom_socket", {'message':'Invoice deleted','type':"Delete invoice","invoice_number":doc.name,"company":doc.company})
    soc_doc = frappe.new_doc("Socket Notification")
    soc_doc.invoice_number = doc.name
    soc_doc.guest_name = doc.guest_name
    soc_doc.document_type = doc.invoice_category
    soc_doc.room_number = doc.room_number
    soc_doc.confirmation_number = doc.confirmation_number
    soc_doc.print_by = doc.print_by
    soc_doc.invoice_category = doc.invoice_category
    soc_doc.record_type = "Delete"
    soc_doc.insert(ignore_permissions=True)

def invoiceCreated(doc):
    try:
        # frappe.publish_realtime("invoice_created", "message")
        print("=================---------------000000000000")       
        frappe.publish_realtime("custom_socket", {'message':'Invoices Created','data':doc.__dict__,"company":doc.company})
        soc_doc = frappe.new_doc("Socket Notification")
        soc_doc.invoice_number = doc.name
        soc_doc.guest_name = doc.guest_name
        soc_doc.document_type = doc.invoice_category
        soc_doc.room_number = doc.room_number
        soc_doc.confirmation_number = doc.confirmation_number
        soc_doc.print_by = doc.print_by
        soc_doc.invoice_category = doc.invoice_category
        soc_doc.record_type = "Create"
        soc_doc.insert(ignore_permissions=True)
        
        filename = doc.invoice_file
        bin_name = frappe.db.get_value('Document Bin',{'invoice_file': filename})
               
        bin_doc = frappe.get_doc("Document Bin",bin_name)
        bin_doc.print_by = doc.print_by
        bin_doc.document_printed = "Yes"
        bin_doc.document_type = doc.invoice_category
        bin_doc.invoice_number = doc.invoice_number
        bin_doc.save(ignore_permissions=True,ignore_version=True)
    except Exception as e:
        print(str(e), "Invoice Created Socket Method")
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}



def update_documentbin(filepath, error_log):
    try:
        bin_data = frappe.db.get_list('Document Bin', filters={'invoice_file': ['=', filepath]})
        print(bin_data)
        if len(bin_data)>0:
            pass
        else:
            bin_doc = frappe.new_doc("Document Bin")
            bin_doc.invoice_file = filepath
            bin_doc.error_log =  error_log
            bin_doc.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        print(str(e), "update_documentbin")
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}


def fileCreated(doc, method=None):
    try:
        if 'job-' in doc.file_name:
            if not frappe.db.exists({'doctype': 'Document Bin','invoice_file': doc.file_url}):
                update_documentbin(doc.file_url,"")
                abs_path = os.path.dirname(os.getcwd())
                company_doc = frappe.get_doc("company",doc.attached_to_name)
                new_parsers = company_doc.new_parsers
                if new_parsers == 0:
                    file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc.attached_to_name+'/invoice_parser.py'
                else:
                    file_path = abs_path + '/apps/version2_app/version2_app/parsers_invoice/invoice_parsers/'+doc.attached_to_name+'/invoice_parser.py'
                module_name = 'file_parsing'
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.file_parsing(doc.file_url)
        else:
            if ".pdf" in doc.file_url and "with-qr" not in doc.file_url:
                update_documentbin(doc.file_url,"")

            print('Normal File')
    except Exception as e:
        print(str(e), "fileCreated")
        update_documentbin(doc.file_url,str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}

def Updateemitsocket(doc,method=None):
    if doc.status=="Success":
        company = frappe.get_last_doc('company')
        frappe.log_error("trigger socket bench update", " {'message':'bench  update started','type':'bench update'}")
        frappe.publish_realtime("custom_socket", {'message':'bench  update started','type':"bench update","company":company.name})


def DocumentBinSocket(doc,method=None):
    company = frappe.get_last_doc('company')
    frappe.log_error("Document Bin Insert", " {'message':'Docuemnt Bin Insert'}")
    frappe.publish_realtime("custom_socket", {'message':'Document Bin Insert','type':"document_bin_insert","data":doc.__dict__,"company":company.name})

def updateManager(doc, method=None):
    try:
        if doc.status!="Ongoing":
            print("==========")
            commands = ['git pull origin updates','systemctl nginx reload','systemctl nginx restart']
            console_dump = ''
            company = frappe.get_last_doc('company')
            print(company)
            # cwd = '/home/caratred/Documents/angular/ezy-invoice-production'
            # cwd = '/home/frappe/ezy-invoice-production'
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
                print(terminal,"//////////")                
                # frappe.log_error("log error", terminal.stdout.read(1))
                for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                    console_dump += c
            logged_command = " && ".join(commands)
            frappe.publish_realtime("custom_socket", {'message':'bench update completed','type':"bench completed","company":company.name})
            # frappe.log_error("Angular project pull", console_dump)
            frappe.log_error("Angular project pull data","update manager")
    except Exception as e:
        print(str(e),"    updateManager")

        

def safe_decode(string, encoding='utf-8'):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string

def deleteemailfilesdaily():
	try:
		company = frappe.get_last_doc('company')
		lastdate = date.today() - timedelta(days=1)
		print(lastdate)
		emaildata = frappe.db.get_list('Email Queue',filters={'creation': ['>',lastdate],'status':"Sent"},fields=['name', 'attachments'])
		print(emaildata)
		filelist = []
		for each in emaildata:
			value = json.loads(each.attachments)
			filelist.append(value[0]['fid'])
			delete = frappe.delete_doc("File",value[0]['fid'])
			print(delete)

		return {"success":True}
	except Exception as e:
		return {"success":False,"message":str(e)}
