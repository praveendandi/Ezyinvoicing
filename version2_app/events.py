import frappe

from version2_app.parsers import *
import json, shlex, time, re
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import datetime
import importlib.util
import traceback
# from version2_app.version2_app.doctype.invoices import *
#===============================
#===================================



def invoice_created(doc, method=None):
    print("Invoice Created",doc.name)



def invoiceCreated(doc):
    try:
        # frappe.publish_realtime("invoice_created", "message")
        frappe.publish_realtime("custom_socket", {'message':'Invoices Created','data':{"name":doc.name, "irn_generated":doc.irn_generated,"invoice_type":doc.invoice_type,"invoice_from":doc.invoice_from,"guest_name":doc.guest_name,"invoice_file":doc.invoice_file,"print_by":doc.print_by,"creation":doc.creation,"invoice_category":doc.invoice_category}})
        soc_doc = frappe.new_doc("Socket Notification")
        soc_doc.invoice_number = doc.name
        soc_doc.guest_name = doc.guest_name
        soc_doc.invoice_type = doc.invoice_type
        soc_doc.room_number = doc.room_number
        soc_doc.confirmation_number = doc.confirmation_number
        soc_doc.print_by = doc.print_by
        soc_doc.invoice_category = doc.invoice_category
        soc_doc.insert(ignore_permissions=True)
        filename = doc.invoice_file
        bin_name = frappe.db.get_value('Document Bin',{'invoice_file': filename})
               
        bin_doc = frappe.get_doc("Document Bin",bin_name)
        bin_doc.print_by = doc.print_by
        bin_doc.document_printed = "Yes"
        bin_doc.invoice_type = doc.invoice_type
        bin_doc.invoice_number = doc.invoice_number
        bin_doc.save(ignore_permissions=True,ignore_version=True)
    except Exception as e:
        print(str(e), "Invoice Created Socket Method")
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}


    # frappe.subscriber.on("invoice_created", function (channel, message) {  etc, etc })
def update_documentbin(filepath, error_log):
    try:
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
                file_path = abs_path + '/apps/version2_app/version2_app/parsers/'+doc.attached_to_name+'/invoice_parser.py'
                module_name = 'file_parsing'
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.file_parsing(doc.file_url)
        else:
            print('Normal File')
    except Exception as e:
        print(str(e), "fileCreated")
        update_documentbin(doc.file_url,str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}

def emitsocket(doc,method=None):
    frappe.log_error("trigger socket bench update", " {'message':'bench  update started','type':'bench update'}")
    frappe.publish_realtime("custom_socket", {'message':'bench  update started','type':"bench update"})

#-----------------


def updateManager(doc, method=None):
  
    if doc.status!="Ongoing":
        #==========
        # commands = ['git pull','service nginx reload','service nginx restart']
        commands = ['git pull']
        console_dump = ''
        # cwd = '/home/caratred/Desktop/ezy-invoice-production'
        # company = frappe.get_last_doc('company')
        # cwd = company.angular_project_production_path
        # cwd = '/home/caratred/Documents/angular/ezy-invoice-production'
        cwd = '/home/frappe/ezy-invoice-production'
        key = str(time.time())
        # count = 0
        for command in commands:
            terminal = Popen(shlex.split(command),
                            stdin=PIPE,
                            stdout=PIPE,
                            stderr=STDOUT,
                            cwd=cwd)
            # frappe.log_error("log error", terminal.stdout.read(1))
            for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
                console_dump += c
        logged_command = " && ".join(commands)
        frappe.publish_realtime("custom_socket", {'message':'bench update completed','type':"bench completed"})
        # frappe.log_error("Angular project pull", console_dump)
        frappe.log_error("Angular project pull data","sample")

        

def safe_decode(string, encoding='utf-8'):
    try:
        string = string.decode(encoding)
    except Exception:
        pass
    return string

