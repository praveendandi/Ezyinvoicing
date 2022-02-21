from dataclasses import asdict
from requests.exceptions import RetryError
import frappe, requests, json

from version2_app.parsers import *
import json
import shlex
import time
import re
from subprocess import Popen, PIPE, STDOUT
import os,glob
import sys
import datetime
import importlib.util
from frappe.utils import cstr
import traceback
import requests
from datetime import date, timedelta

import shutil
from frappe.utils import logger
from frappe.utils.data import money_in_words

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)

@frappe.whitelist(allow_guest=True)
def num_to_words(num):
    try:
        given_num = abs(float((num)))
        num_in_word = money_in_words(given_num)
        text=str(num_in_word).strip("INR")
        return {"success":True, "data":text.strip()}
    except:
        frappe.log_error(frappe.get_traceback(),"num_to_words Error")
        return {"success":False}


def invoice_update(doc,method=None):
    try:
        if doc.sales_amount_after_tax:
            total_amount_in_words=num_to_words(doc.sales_amount_after_tax)
            if total_amount_in_words["success"] == True:
                doc.amount_in_word = total_amount_in_words["data"]
                # doc.save(ignore_permissions=True,ignore_version=True)
        # frappe.db.commit()
    except:
        frappe.log_error(frappe.get_traceback(),"invoice_update Error")
        

def invoice_created(doc, method=None):
    try:
        if doc.sales_amount_after_tax:
            total_amount_in_words=num_to_words(doc.sales_amount_after_tax)
            if total_amount_in_words["success"] == True:
                doc.amount_in_word = total_amount_in_words["data"]
                # print(doc.amount_in_word,"===============")
                # doc.save(ignore_permissions=True)
                # frappe.db.commit()
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
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoice_created Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))            
        return {"success":False,"message":str(e)}

def company_created(doc,method=None):
    try:
        doc = frappe.db.get_list('company',filters={"docstatus":0},fields=["name","company_name","company_code","phone_number","gst_number","provider","ip_address","port"])
        api="http://"+doc[0]["ip_address"]+":"+doc[0]["port"]+"/api/resource/Properties"
        adequare_doc=frappe.get_doc("GSP APIS",doc[0]["provider"])
        insert_dict={"doctype":"Properties","property_name":doc[0]["company_name"],"property_code":doc[0]["company_code"],"contact_number":doc[0]["phone_number"],"gst_number":doc[0]["gst_number"],"gsp_provider":doc[0]["provider"],"api_key":adequare_doc.gsp_prod_app_secret,"api_secret":adequare_doc.gsp_prod_app_id,"gsp_test_app_id":adequare_doc.gsp_test_app_id,"gsp_test_app_secret":adequare_doc.gsp_test_app_secret}
        headers = {'content-type': 'application/json'}
        r = requests.post(api,headers=headers,json=insert_dict,verify=False)
        folder_path = frappe.utils.get_bench_path()
        if doc.pms_property_logo != "":
            file_path = folder_path+'/sites/'+doc.site_name+doc.pms_property_logo
            status = upload_propery_logo_pms({"file_path":file_path,"company":doc.name})
            if status["success"] == False:
                return status 
            frappe.db.set_value('company', doc.name, {"pms_property_url":status["data"]})
            frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing company_created Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))   
        return {"success":False,"message":str(e)}

def invoice_deleted(doc,method=None):
    try:
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
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoice_deleted Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoiceCreated Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}



def update_documentbin(filepath, error_log):
    try:
        bin_data = frappe.db.get_list('Document Bin', filters={'invoice_file': ['=', filepath]})
        print(bin_data)
        if len(bin_data)>0:
            pass
        else:
            systemName = "NA"
            if filepath.count("@") == 2:
                if '@' in filepath:
                    systemName = re.search('@(.*)@', filepath)
                    systemName = systemName.group(1)
            bin_doc = frappe.new_doc("Document Bin")
            bin_doc.system_name = systemName
            bin_doc.invoice_file = filepath
            bin_doc.error_log =  error_log
            bin_doc.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        print(str(e), "update_documentbin")
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing update_documentbin Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def fileCreated(doc, method=None):
    try:
        if 'job-' in doc.file_name:
            if not frappe.db.exists({'doctype': 'Document Bin','invoice_file': doc.file_url}):
                update_documentbin(doc.file_url,"")
                abs_path = os.path.dirname(os.getcwd())
                company_doc = frappe.get_doc("company",doc.attached_to_name)
                new_parsers = company_doc.new_parsers
                if company_doc.block_print == "True":
                    return {"success":False,"message":"Print has been Blocked"}
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
            company = frappe.get_last_doc("company")
            if company.block_print == "True":
                return {"success":False,"message":"Print has been Blocked"}
            if ".pdf" in doc.file_url and "with-qr" not in doc.file_url:
                update_documentbin(doc.file_url,"")

            print('Normal File')
        logger.error(f"fileCreated,   {traceback.print_exc()}")
    except Exception as e:
        # frappe.log_error(traceback.print_exc())
        logger.error(f"fileCreated,   {traceback.print_exc()}")
        print(str(e), "fileCreated")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing fileCreated Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        update_documentbin(doc.file_url,str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}

def Updateemitsocket(doc,method=None):
    try:
        if doc.status=="Success":
            company = frappe.get_last_doc('company')
            frappe.log_error("trigger socket bench update", " {'message':'bench  update started','type':'bench update'}")
            frappe.publish_realtime("custom_socket", {'message':'bench  update started','type':"bench update","company":company.name})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Updateemitsocket Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def DocumentBinSocket(doc,method=None):
    try:
        company = frappe.get_last_doc('company')
        frappe.log_error("Document Bin Insert", " {'message':'Docuemnt Bin Insert'}")
        frappe.publish_realtime("custom_socket", {'message':'Document Bin Insert','type':"document_bin_insert","data":doc.__dict__,"company":company.name})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing DocumentBinSocket Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing updateManager Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
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
        print(doc.name, "hello hiee","$$$$$$$$$$$$$$$$")
        workstation = frappe.get_doc("Active Work Stations",doc.work_station)
        workstation.username = doc.username
        workstation.save(ignore_permissions=True,ignore_version=True)
        frappe.publish_realtime("custom_socket", {'message': 'Tablet Mapped', 'data': doc.__dict__})
        # frappe.publish_realtime("custom_socket", {'message':'information Folio','type':"bench completed"})
    except Exception as e:
        print(e)


def remove_mapping(doc, method=None):
    try:
        print(doc.__dict__, "hello hiee removing mapping &&&&&&&77")
        tablet = frappe.db.get_value("Active Tablets",doc.tablet,"tablet")
        frappe.publish_realtime(
            "custom_socket", {'message': 'Remove Tablet config', 'data': doc.__dict__})
        frappe.publish_realtime(
            "custom_socket", {'message': 'Tablet Config Disconnected', 'data': doc.__dict__,"tablet":tablet})
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
        # if
        # config_doc = frappe.db.exists({
        #     'doctype': 'Tablet Config',Tablet Map
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
        table_config = frappe.db.get_value("Tablet Config",{"tablet":doc.name},["work_station","username","tablet"])
        tablet = frappe.get_doc("Active Tablets",table_config[2])
        table_config_doc = frappe.get_doc("Tablet Config",table_config.name)
        table_config_doc.tablet_socket_id = tablet.socket_id
        table_config_doc.save(ignore_permissions=True,ignore_version=True)
        workstation = frappe.get_doc("Active Work Stations",table_config[0])
        workstation.username = table_config[1]
        workstation.save(ignore_permissions=True,ignore_version=True)
        data = doc.__dict__
        data["workstation"] = workstation.work_station
        data["workstation_status"] = workstation.status
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing deletemailfilesdaily Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def gspmeteringhook(doc,method=None):
    try: 
        company = frappe.get_last_doc('company')
        inputData = {"data":{"doctype":"Gsp Metering","property_code":company.name,'tax_payer_details':doc.tax_payer_details,'login':doc.login,'generate_irn':doc.generate_irn,'get_irn_details_by_doc':doc.get_irn_details_by_doc,'cancel_irn':doc.cancel_irn,'invoice_by_irn':doc.invoice_by_irn,'create_qr_image':doc.create_qr_image,'status':doc.status}}
        print(inputData)
        headers = {'Content-Type': 'application/json'}
        if company.mode == "Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                                'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
                                    }
                json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",headers=headers,json=inputData,proxies=proxies,verify=False)
            else:
                if company.skip_ssl_verify == 1:
                    json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",headers=headers,json=inputData,verify=False)
                else:
                    json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.getcount.gspmetering_post",headers=headers,json=inputData,verify=False)
            print(json_response,"/////////")
            return json_response
        print("Property is in Testing Mode gspmeteringhook")         
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing gspmeteringhook Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))    

def taxpayerhook(doc,method=None):
    try:
        company = frappe.get_doc('company',doc.company)
        headers = {'Content-Type': 'application/json'}
        
        inputData = {'doctype':'TaxPayerDetail','gst_number':doc.gst_number,'legal_name':doc.legal_name,'email':doc.email,'address_1':doc.address_1,'address_2':doc.address_2,'location':doc.location,'pincode':doc.pincode,'gst_status':doc.gst_status,'tax_type':doc.tax_type,'trade_name':doc.trade_name,'phone_number':doc.phone_number,'state_code':doc.state_code,'address_floor_number':doc.address_floor_number,'address_street':doc.address_street,'status':doc.status,'block_status':doc.block_status}
        if company.mode =="Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                                'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
                                    }
                insertTaxpayer = requests.post(company.licensing_host+"/api/resource/TaxPayerDetail",headers=headers,json=inputData,proxies=proxies,verify=False)
            else:
                if company.skip_ssl_verify == 1:
                    insertTaxpayer = requests.post(company.licensing_host+"/api/resource/TaxPayerDetail",headers=headers,json=inputData,verify=False)
                else:
                    insertTaxpayer = requests.post(company.licensing_host+"/api/resource/TaxPayerDetail",headers=headers,json=inputData,verify=False)
            if insertTaxpayer.status_code==200:
                print("--------- Taxpayer hook")
            return insertTaxpayer
        print("Property is in Testing Mode taxpayerhook")                 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing taxpayerhook Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))  



def InvoiceDataTolicensing():
    try:
        company = frappe.get_last_doc('company')
        if company.mode == "Production":
            today = date.today()# - timedelta(days=43)
            Invoice_count = frappe.db.get_list('Invoices',filters={'creation':["Between",[today, today]],'mode':'Testing'},fields=['count(name) as count','invoice_category','mode'],group_by='invoice_category')
            Invoice_count2 = frappe.db.get_list('Invoices',filters={'creation':["Between",[today, today]],'mode':'Production'},fields=['count(name) as count','invoice_category','mode'],group_by='invoice_category')
            print(Invoice_count,".a.a.a.a.a.")
            print(Invoice_count2)
            headers = {'Content-Type': 'application/json'}
            
            if len(Invoice_count)>0:
                inputData = {"data":{"date":str(today),"property_code":company.name,"mode":"Testing"}}
                for each in Invoice_count:
                    if each['invoice_category'] == "Tax Invoice":
                        inputData['data']['taxinvoices'] = each['count']
                    if each['invoice_category'] == "Debit Invoice":
                        inputData['data']['debitinvoices'] = each['count']
                    if each['invoice_category'] == "Credit Invoice":
                        inputData['data']['creditinvoices'] = each['count']        
                json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.getcount.invoice_post",headers=headers,json=inputData,verify=False)
            
            if len(Invoice_count2)>0:
                inputData = {"data":{"date":str(today),"property_code":company.name,"mode":"Production"}}
                for each in Invoice_count2:
                    if each['invoice_category'] == "Tax Invoice":
                        inputData['data']['taxinvoices'] = each['count']
                    if each['invoice_category'] == "Debit Invoice":
                        inputData['data']['debitinvoices'] = each['count']
                    if each['invoice_category'] == "Credit Invoice":
                        inputData['data']['creditinvoices'] = each['count']
                json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.getcount.invoice_post",headers=headers,json=inputData,verify=False)         
        print("Property is in Testing Mode InvoiceDataTolicensing")
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing InvoiceDataToLicensing Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))



def dailyDeletedocumentBin():
    try:
        company = frappe.get_last_doc('company')
        lastdate = date.today() - timedelta(days=6)
        data = frappe.db.sql("""DELETE FROM `tabDocument Bin` WHERE creation < %s""",lastdate)
        print(data)
        frappe.db.commit()
        return {"success":True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing dailyDeletedocumentBin Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}	

def dailyIppprinterFiles():
    try:
        company = frappe.get_last_doc('company')
        shutil.rmtree(company.ipp_printer_file_path)
        os.mkdir(company.ipp_printer_file_path)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing dailyIppprinterFiles Event","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(str(e))


@frappe.whitelist(allow_guest=True)
def updatepropertiesdetails():
    try: 
        gspdetails = frappe.get_last_doc('GSP APIS')
        company = frappe.get_last_doc("company")
        inputData = {"data":{"doctype":"Properties","company_code":company.name,"api_key":gspdetails.gsp_prod_app_id,'api_secret':gspdetails.gsp_prod_app_secret,'gst_prod_username':gspdetails.gst__prod_username,'gst_prod_password':gspdetails.gst_prod_password,"gsp_test_app_id":gspdetails.gsp_test_app_id,"gsp_test_app_secret":gspdetails.gsp_test_app_secret,"gst_test_username":gspdetails.gst__test_username,"gst_test_password":gspdetails.gst_test_password,"groups":company.property_group,"mode":company.mode}}
        headers = {'Content-Type': 'application/json'}
        if company.mode == "Production":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                                'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
                                    }
                json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",headers=headers,json=inputData,proxies=proxies,verify=False)
            else:
                if company.skip_ssl_verify == 1:
                    json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",headers=headers,json=inputData,verify=False)
                else:
                    json_response = requests.post(company.licensing_host+"/api/method/ezylicensing.ezylicensing.doctype.properties.properties.update_property_status",headers=headers,json=inputData,verify=False)
            return json_response.json()
        return {"success":True, "message":"Property is in Testing Mode"}         
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-updatepropertiesdetails","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def promotionsSocket(doc,method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {'message': 'Promotions Created', 'data': doc.__dict__})
    except Exception as e:
        print(str(e))

def deletePromotionsSocket(doc,method=None):
    try:
        frappe.publish_realtime(
            "custom_socket", {'message': 'Promotions Deleted', 'data': doc.__dict__})
    except Exception as e:
        print(str(e))




@frappe.whitelist(allow_guest=True)
def block_irn():
    try: 
        company = frappe.get_last_doc("company")
        url_property = requests.get(company.licensing_host+"/api/resource/Properties/"+company.company_code)
        json_property = url_property.json()
        if url_property.status_code == 200:
            company.block_irn = json_property["data"]["block_irn"]
            company.block_print = json_property["data"]["block_print"]
            company.save(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-block-IRN","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
        
@frappe.whitelist(allow_guest=True)
def backup_file_perticulerdoctypes(data):
    try:
        get_company=frappe.get_doc("company",data["company_code"],fields=["host","site_name"])
        site_name = cstr(frappe.local.site)
        run_command=os.system('bench --site {} backup --only "company,SAC HSN CODES,Payment Types,GSP APIS"'.format(site_name))
        cwd=cwd = os.getcwd() 
        # site_name = cstr(frappe.local.site)
        mypath = cwd+"/"+site_name+"/private/backups/*.gz"
        filename=max(glob.glob(mypath), key=os.path.getmtime)
        shutil.move(filename,cwd+"/"+site_name+"/public/files")
        return get_company.host+"files/{}".format(os.path.basename(filename))
    except Exception as e:
        frappe.log_error("backupfile:"+str(e))


def upload_propery_logo_pms(data):
    try:
        # headers = {'Content-Type': 'application/json'}
        company = frappe.get_doc('company',data["company"])
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
        files = {'file': open(data["file_path"],'rb')}
        file_name, file_extension = os.path.splitext(data["file_path"])
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addCompanyLogo",
                    data={"company":company.name,"file_extension":file_extension},files = files,verify=False)
            else:
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addCompanyLogo",
                    data={"company":company.name,"file_extension":file_extension},files = files,verify=False)
            response = json_response.json()
            if response["success"] == False:
                return {
                    "success": False,
                    "message": response["message"]
                }
            return response
        else:
            print(proxies, "     proxy console")
            json_response = requests.post(
                "https://gst.caratred.in/ezy/api/addCompanyLogo",
                data={"company":company.name,"file_extension":file_extension},files = files,
                proxies=proxies,verify=False)
            response = json_response.json()
            if response["success"] == False:
                return {
                    "success": False,
                    "message": response["message"]
                }
            return response
    except Exception as e:
        frappe.log_error("upload_propery_logo_pms:"+str(e))
        return {"success":False,"message":str(e)}

def update_company(doc,method=None):
    try:
        folder_path = frappe.utils.get_bench_path()
        if doc.pms_property_logo:
            file_path = folder_path+'/sites/'+doc.site_name+doc.pms_property_logo
            status = upload_propery_logo_pms({"file_path":file_path,"company":doc.name})
            if status["success"] == False:
                return status 
            frappe.db.set_value('company', doc.name, {"pms_property_url":status["data"]})
            frappe.db.commit()
    except Exception as e:
        frappe.log_error("update_company:"+str(e))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def fetch_invoice_details(filters=[]):
    try:
        if len(filters)>0:
            filters=json.loads(filters)
            company = frappe.get_last_doc("company")
            # if filters["company_code"] == company.name:
            filters.extend([["invoice_type","=","B2B"],["irn_generated","=","Success"]])
            fetch_invoice = frappe.db.get_list('Invoices',filters=filters,fields=['igst_amount','sgst_amount','cgst_amount','total_gst_amount','invoice_number','invoice_date','guest_name','room_number','confirmation_number','total_invoice_amount','irn_number','qr_code_image','irn_generated_time','ack_no','invoice_file','gst_number'])
            for x in fetch_invoice:
                items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount','date','item_type','sac_code','item_name']
                items_doc = frappe.db.get_list('Items',filters={'parent':['in',x["invoice_number"]]},fields =items_fields)
                x['items'] = items_doc
                # print(x['items'])
            return fetch_invoice
        else:
            return {"success":False, "message":"filters not be empty"}
    except Exception as e:
        return {"Success":False,"message":str(e)}
       