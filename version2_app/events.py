import frappe, requests, json

from version2_app.parsers import *
import json
import shlex
import time
import re
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import datetime
import importlib.util
import traceback
from datetime import date, timedelta

import shutil
from frappe.utils import logger
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)


def invoice_created(doc, method=None):
    print("Invoice Created",doc.name)
    if frappe.db.exists('Invoice Reconciliations', doc.name):
        reconciliations_doc = frappe.get_doc('Invoice Reconciliations', doc.name)
        reconciliations_doc.invoice_found = "Yes"
        reconciliations_doc.save(ignore_permissions=True,ignore_version=True)
    if doc.invoice_from=="Pms":
        if frappe.db.exists({"doctype":'Document Bin', 'invoice_file': doc.invoice_file}):
            bin_name = frappe.db.get_value('Document Bin',{'invoice_file': doc.invoice_file})
            bin_doc = frappe.get_doc("Document Bin",bin_name)
            bin_doc.print_by = doc.print_by
            bin_doc.document_type = doc.invoice_category
            bin_doc.invoice_number = doc.name
            # bin_doc.error_log = error_log
            bin_doc.document_printed = "Yes"
            bin_doc.save(ignore_permissions=True,ignore_version=True)

def company_created(doc,method=None):
    doc = frappe.db.get_list('company',filters={"docstatus":0},fields=["name","company_name","company_code","phone_number","gst_number","provider","ip_address","port"])
    api="http://"+doc[0]["ip_address"]+":"+doc[0]["port"]+"/api/resource/Properties"
    adequare_doc=frappe.get_doc("GSP APIS",doc[0]["provider"])
    insert_dict={"doctype":"Properties","property_name":doc[0]["company_name"],"property_code":doc[0]["company_code"],"contact_number":doc[0]["phone_number"],"gst_number":doc[0]["gst_number"],"gsp_provider":doc[0]["provider"],"api_key":adequare_doc.gsp_prod_app_secret,"api_secret":adequare_doc.gsp_prod_app_id,"gsp_test_app_id":adequare_doc.gsp_test_app_id,"gsp_test_app_secret":adequare_doc.gsp_test_app_secret}
    headers = {'content-type': 'application/json'}
    r = requests.post(api,headers=headers,json=insert_dict)

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
        if frappe.db.exists({"doctype":'Document Bin', 'name': bin_name}):   
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
            if '@' in filepath:
                systemName = re.search('@(.*)@', filepath)
                systemName = systemName.group(1)
            else:
                systemName = "NA"    
            bin_doc = frappe.new_doc("Document Bin")
            bin_doc.system_name = systemName
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
				frappe.log_error(traceback.print_exc())
				logger.error(f"fileCreated,   {traceback.print_exc()}")
		else:
			if ".pdf" in doc.file_url and "with-qr" not in doc.file_url:
				update_documentbin(doc.file_url,"")

			print('Normal File')
		logger.error(f"fileCreated,   {traceback.print_exc()}")
	except Exception as e:
		frappe.log_error(traceback.print_exc())
		logger.error(f"fileCreated,   {traceback.print_exc()}")
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


def information_folio_created(doc, method=None):
    try:
        print(doc.invoice_file, "heeloo hiee")
        print(doc.name, "hello hiee")
        # if
        frappe.publish_realtime(
            "custom_socket", {'message': 'information Invoices Created', 'data': doc.__dict__})

        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def tablet_mapping(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        # if
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Mapped', 'data': doc.__dict__})
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def remove_mapping(doc, method=None):
    try:
        print(doc.__dict__, "hello hiee removing mapping &&&&&&&77")
        # if
        frappe.publish_realtime(
            "custom_socket", {'message': 'Remove Tablet config', 'data': doc.__dict__})
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Config Disconnected', 'data': doc.__dict__})
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def tablet_connected(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        # if
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Connected', 'data': doc.__dict__})
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def tablet_disconnected(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        # if
        # config_doc = frappe.db.exists({
        #     'doctype': 'Tablet Config',
        #     'tablet': doc.name,
        # })
        # print(config_doc,"hello*************8")
        # if True:
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Config Disconnected', 'data': doc.__dict__})
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Disconnected', 'data': doc.__dict__})
        # else:
        #     frappe.publish_realtime(
        #         "custom_socket", {'message': 'Tablet Disconnected', 'data': doc.__dict__})
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def workstation_disconnected(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        # frappe.publish_realtime(
        #     "custom_socket", {'message': 'station_disconnected', 'data': doc.__dict__})
    except Exception as e:
        print(e)


def update_tablet_status(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Status Updated', 'data': doc.__dict__})
    except Exception as e:
        print(e)


def create_redg_card(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Redg Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)
        
        
def create_paidout_receipt(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Paidout Receipt Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)
        
def create_advance_deposits(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Advance Deposits Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)
        
def create_encashment_certificates(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Encashment Certifcates Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)
        
def create_payment_receipts(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Payment Receipts Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)
        
def create_pos_bill(doc, method=None):
    try:
        print(doc.name, "hello hiee")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Pos Bills Created', 'data': doc.__dict__})
    except Exception as e:
        print(e)


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
        lastdate = date.today() - timedelta(days=6)
        data = frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""",lastdate)
        print(data)
        frappe.db.commit()
        return {"success":True}
    except Exception as e:
        return {"success":False,"message":str(e)}

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

def dailyIppprinterFiles():
    try:
        company = frappe.get_last_doc('company')
        shutil.rmtree(company.ipp_printer_file_path)
        os.mkdir(company.ipp_printer_file_path)
    except Exception as e:
        print(str(e))
