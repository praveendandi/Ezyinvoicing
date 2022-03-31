from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import time
import traceback,sys
import os,re
import datetime
import json
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.hyatt_mumbai import hyatt_mumbai
from version2_app.version2_app.doctype.invoices.hyatt_bulk import hyatt_bulkupload


 

@frappe.whitelist(allow_guest=True)
def BulkUploadReprocess(data):
    try:
        invoice_number = data['invoice_number']
        invoice_data = frappe.get_doc('Invoices',invoice_number)
        line_items = json.loads(invoice_data.invoice_object_from_file)
        if "data" not in line_items.keys():
            line_items = {"data": line_items}
            invoice_data.invoice_object_from_file = json.dumps(line_items)
        if isinstance(line_items["data"], dict):
            if "data" in line_items["data"].keys():
                line_items = line_items["data"]
                invoice_data.invoice_object_from_file = json.dumps(line_items)
        invoice_total_amount = invoice_data.total_invoice_amount
        print(invoice_total_amount)
        print(invoice_data.gst_number,"=-=-=-=-=-=-")
        company = frappe.get_doc('company',invoice_data.company)
        gstNumber = (invoice_data.gst_number).strip() 
        invoiceType = invoice_data.invoice_type
        error_data ={}
        error_data['room_number'] = invoice_data.room_number
        error_data['total_invoice_amount'] = invoice_total_amount
        error_data['invoice_number'] = invoice_number
        error_data['gst_number'] = invoice_data.gst_number
        error_data['company_code'] = invoice_data.company
        each = {}
        # if company.bulk_excel_upload_type=="Hyatt Bulkupload":
        #     data.update(invoice_data.company)
        #     output=hyatt_bulkupload(data)
        #     if output['success'] == False:
        #         frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
        #     return output
        if company.bulk_excel_upload_type == "HolidayIn":
            # line_items = json.loads(invoice_data.invoice_object_from_file)
            invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            items = []
            sort_order = 1
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            if invoice_data.change_gst_number=="Yes" and invoice_data.converted_from_b2c=="No":
                if line_items['data'][0]['taxid'] == "empty" or line_items['data'][0]['taxid'] == "":
                    gstNumber == ""
                    invoiceType = "B2C"
                else:
                    gstNumber = line_items['data'][0]['taxid']
                    invoiceType = "B2B"
                    error_data['gst_number'] = gstNumber
                    error_data['invoice_type'] = "B2B"

            for each in line_items['data']:
                each = each
                if each['goods_desc'] not in payment_Types:
                    item_dict = {}
                    if "00:00:00" in each['invoicedate']:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
                    else:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d').strftime(company.invoice_item_date_format)
                    item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
                    item_dict['item_value'] = round(each['invoiceamount'],2)
                    item_dict['sac_code'] = str(each["taxcode_dsc"])
                    item_dict['name'] = each['goods_desc']
                    item_dict['sort_order'] = sort_order
                    sort_order+=1
                    items.append(item_dict)
        elif company.bulk_excel_upload_type == "Marriot":
            # line_items = json.loads(invoice_data.invoice_object_from_file)
            
            # invoice_date = invoice_data.invoice_date
            invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            items = []
            sort_order = 1
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            if invoice_data.change_gst_number=="No" and invoice_data.converted_from_b2c=="No":
                if not invoice_data.converted_from_b2b == "Yes":
                    if line_items['data'][0]['taxid'] == "empty":
                        gstNumber == ""
                        invoiceType = "B2C"
                    else:
                        gstNumber = line_items['data'][0]['taxid']
                        invoiceType = "B2B"
                        error_data['gst_number'] = gstNumber
                        error_data['invoice_type'] = "B2B"
                else:
                    gstNumber == ""
                    invoiceType = "B2C"
            for each in line_items['data']['items']:

                if each['name'] not in payment_Types:
                    if  "CGST" in each["name"] or "SGST" in each["name"] or "IGST" in each["name"] or "VAT" in each["name"]  or "Cess" in each["name"] or "CESS" in each["name"]:
                        continue
                    item_dict = {}
                    date_time_obj = datetime.datetime.strptime(each['date'],'%d-%m-%y').strftime(company.invoice_item_date_format)
                    item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
                    item_dict['item_value'] = each['item_value']
                    item_dict['sac_code'] = "No Sac"
                    item_dict['name'] = each['name']
                    item_dict['sort_order'] = sort_order
                    sort_order+=1
                    items.append(item_dict)	
        elif company.bulk_excel_upload_type == "Hyatt Mumbai" or company.bulk_excel_upload_type=="Hyatt Bulkupload" or company.bulk_excel_upload_type == "Hyatt Hyderabad" or company.bulk_excel_upload_type=="Grand" or company.bulk_excel_upload_type=="Novotel Vijayawada" or company.bulk_excel_upload_type == "Hyatt Hyderabad" or company.bulk_excel_upload_type=="Grand" or company.bulk_excel_upload_type=="Bulkupload Without Headers" or companyData.bulk_excel_upload_type=="Bulkupload With Headers":
            # line_items = json.loads(invoice_data.invoice_object_from_file)
            
            # invoice_date = invoice_data.invoice_date
            # output = hyatt_mumbai(data)
            # if output['success'] == False:
            #     frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            # return output
            invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            items = []
            sort_order = 1
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            if invoice_data.change_gst_number=="No" and invoice_data.converted_from_b2c=="No":
                if line_items['data']['gstNumber'] == "" or line_items['data']['gstNumber'].strip() == "0" or len(line_items['data']['gstNumber']) != 15:
                    print("----===================")
                    gstNumber == ""
                    invoiceType = "B2C"
                else:
                    print("||||||||||||||||||||||||||||||||||||||",line_items['data']['gstNumber'])
                    gstNumber = line_items['data']['gstNumber']
                    invoiceType = "B2B"
                    error_data['gst_number'] = gstNumber
                    error_data['invoice_type'] = "B2B"
            for each in line_items['data']['items']:
                if each['name'] not in payment_Types:
                    if  "CGST" in each["name"] or "SGST" in each["name"] or "Service Charge " in each["name"] or "VAT" in each["name"]  or "Cess" in each["name"] or "CESS" in each["name"] or ("IGST" in each["name"] and "Debit Note - IGST" not in each["name"]):
                        continue
                    item_dict = {}
                    if company.name=="TGND-01":
                        date_time_obj = datetime.datetime.strptime(each['date'],'%d-%m-%y').strftime(company.invoice_item_date_format)
                    else:
                        date_time_obj = datetime.datetime.strptime(each['date'],company.invoice_item_date_format).strftime(company.invoice_item_date_format)
                    item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
                    if "item_value" not in each:
                        item_dict["item_value"]=each["FT_CREDIT"]
                    else:
                        item_dict['item_value'] = each['item_value']
                    item_dict['sac_code'] = "No Sac"
                    item_dict['name'] = each['name']
                    item_dict['sort_order'] = sort_order
                    sort_order+=1
                    items.append(item_dict)	
        elif company.bulk_excel_upload_type == "Opera":
            # line_items = json.loads(invoice_data.invoice_object_from_file)
            # invoice_date = invoice_data.invoice_date
            invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            items = []
            sort_order = 1
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            for each in line_items['data']:
                if each['goods_desc'] not in payment_Types:
                    item_dict = {}
                    if "00:00:00" in each['invoicedate']:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%d/%m/%Y %H:%M:%S').strftime(company.invoice_item_date_format)
                    else:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%d/%m/%Y').strftime(company.invoice_item_date_format)
                    # date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
                    item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
                    item_dict['item_value'] = each['invoiceamount']
                    item_dict['sac_code'] = str(each["taxcode_dsc"])
                    item_dict['name'] = each['goods_desc']
                    item_dict['sort_order'] = sort_order
                    sort_order+=1
                    items.append(item_dict)
        elif company.bulk_excel_upload_type == "Hyatt":
            # line_items = json.loads(invoice_data.invoice_object_from_file)
            # invoice_date = invoice_data.invoice_date
            invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            items = []
            sort_order = 1
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            for each in line_items['data']:
                if each['goods_desc'] not in payment_Types:
                    item_dict = {}
                    if "00:00:00" in each['invoicedate']:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%d-%b-%Y %H:%M:%S').strftime(company.invoice_item_date_format)
                    else:
                        date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%d-%b-%Y').strftime(company.invoice_item_date_format)
                    # date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
                    item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
                    item_dict['item_value'] = each['invoiceamount']
                    item_dict['sac_code'] = str(each["taxcode_dsc"])
                    item_dict['name'] = each['goods_desc']
                    item_dict['sort_order'] = sort_order
                    sort_order+=1
                    items.append(item_dict)				
        else:
            pass
        # print(items)
        calculate_data = {}
        calculate_data['items'] = items
        calculate_data['invoice_number'] = invoice_number
        calculate_data['company_code'] = invoice_data.company 
        calculate_data['invoice_item_date_format'] = company.invoice_item_date_format
        calculate_data['sez'] = invoice_data.sez	
        # calculate_items_data = calulate_items(calculate_data)
        # print(calculate_items_data)
        print(items,"//////////////////////////////////////////////////")
        if invoiceType=="B2B":
            print("'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''",gstNumber)
            gspApiDataResponse = gsp_api_data({"code":company.name,"mode":company.mode,"provider":company.provider})
            if gspApiDataResponse['success']==True:
                checkTokenIsValidResponse = check_token_is_valid({"code":company.name,"mode":company.mode})
                if checkTokenIsValidResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":gstNumber,"code":company.name,"invoice":invoice_number,"apidata":gspApiDataResponse['data']})
                    if getTaxPayerDetailsResponse['success'] == True:
                        sez = 1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        calculate_data['sez']=1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        taxpayer=getTaxPayerDetailsResponse['data'].__dict__
                    
                        calculate_items_data = calulate_items(calculate_data)
                        print(calculate_items_data,"////////>>>>>>>>>>>>>>>>>>>>>>")
                        if calculate_items_data['success']==True:
                            guest_data = {'items':calculate_items_data['data'],'name':invoice_data.guest_name,"invoice_number":invoice_data.name,"membership":"","invoice_date":invdate,"invoice_type":invoiceType,
                                            "gstNumber":invoice_data.gst_number,"room_number":invoice_data.room_number,"company_code":company.name,"confirmation_number":invoice_data.confirmation_number,"start_time":str(datetime.datetime.now()),"print_by":invoice_data.print_by,"invoice_category":invoice_data.invoice_category,"invoice_file":invoice_data.invoice_file}
                            reinitiate_data = {"company_code":company.name,"items_data":calculate_items_data['data'],"total_invoice_amount":invoice_total_amount,"invoice_number":invoice_data.name,"amened":"No","sez":invoice_data.sez}
                            taxpayer_details = {"gst_number":invoice_data.gst_number,"legal_name":invoice_data.legal_name,"email":invoice_data.email,"address_1":invoice_data.address_1,"address_2":invoice_data.address_1,"trade_name":invoice_data.trade_name,"location":invoice_data.location,"pincode":invoice_data.pincode,"phone_number":invoice_data.phone_number,"state_code":invoice_data.state_code}
                            reinitiate_data['taxpayer']= taxpayer
                            reinitiate_data['guest_data'] = guest_data
                            reinitiate_data['invoice_object_from_file'] = json.loads(invoice_data.invoice_object_from_file)
                            
                            invoicereinitiate = Reinitiate_invoice(reinitiate_data)
                            return invoicereinitiate
                        else:
                            error_data['error_message'] = calculate_items_data['message']
                            errorInvoice = Error_Insert_invoice(error_data)
                            return errorInvoice
                    else:
                        calculate_items_data = calulate_items(calculate_data)
                        # print(calculate_items_data,">>>>>>>>>>>>>>>>>>>>>>")
                        if calculate_items_data['success'] == True:
                            error_data['items_data'] = calculate_items_data['data']
                        error_data['error_message'] = getTaxPayerDetailsResponse['message']
                        errorInvoice = Error_Insert_invoice(error_data)	
                        return errorInvoice	
                else:
                    error_data['error_message'] = checkTokenIsValidResponse['message']
                    errorInvoice = Error_Insert_invoice(error_data)	
                    return errorInvoice
            else:
                error_data['error_message'] = checkTokenIsValidResponse['message']
                errorInvoice = Error_Insert_invoice(error_data)	
                return errorInvoice
        else:	
            calculate_items_data = calulate_items(calculate_data)
            if calculate_items_data['success']==True:
                guest_data = {'items':calculate_items_data['data'],'name':invoice_data.guest_name,"invoice_number":invoice_data.name,"membership":"","invoice_date":invdate,"invoice_type":invoiceType,
                                "gstNumber":invoice_data.gst_number,"room_number":invoice_data.room_number,"company_code":company.name,"confirmation_number":invoice_data.confirmation_number,"start_time":str(datetime.datetime.now()),"print_by":invoice_data.print_by,"invoice_category":invoice_data.invoice_category,"invoice_file":invoice_data.invoice_file}
                reinitiate_data = {"company_code":company.name,"items_data":calculate_items_data['data'],"total_invoice_amount":invoice_total_amount,"invoice_number":invoice_data.name,"amened":"No","sez":invoice_data.sez}
                taxpayer_details = {"gst_number":invoice_data.gst_number,"legal_name":invoice_data.legal_name,"email":invoice_data.email,"address_1":invoice_data.address_1,"address_2":invoice_data.address_1,"trade_name":invoice_data.trade_name,"location":invoice_data.location,"pincode":invoice_data.pincode,"phone_number":invoice_data.phone_number,"state_code":invoice_data.state_code}
                reinitiate_data['taxpayer']= taxpayer_details
                reinitiate_data['guest_data'] = guest_data
                reinitiate_data['invoice_object_from_file'] = json.loads(invoice_data.invoice_object_from_file)
                invoicereinitiate = Reinitiate_invoice(reinitiate_data)
                return invoicereinitiate
            else:
                error_data['error_message'] = calculate_items_data['message']
                errorInvoice = Error_Insert_invoice(error_data)
                return errorInvoice	
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing BulkUploadReprocess Bulk upload","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}  				
