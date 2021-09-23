from __future__ import unicode_literals
import frappe
# from frappe import enqueue
from frappe.model.document import Document
from datetime import date
# import async
# import asyncio
import requests
import datetime
import random
import traceback,os,sys
import string
import xmltodict
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
import time
import json
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.holiday_manual_upload import holidayinManualupload
from version2_app.version2_app.doctype.invoices.opera_manula_bulkupload import operabulkupload
from version2_app.version2_app.doctype.invoices.hyatt_manual_upload import hyattbulkupload
from frappe.utils.background_jobs import enqueue
from version2_app.version2_app.doctype.invoices.hyatt_mumbai import hyatt_mumbai
from version2_app.version2_app.doctype.invoices.grand_newdelhi import grand_newdelhi





# @frappe.whitelist(allow_guest=True)
# def manual_upload(data):
# 	# try:
# 	frappe.enqueue("version2_app.version2_app.doctype.invoices.manual_upload.manualuploadEnqueue",queue='default', timeout=None, event="BulkUpload", is_async=True, job_name="samplefunforqueue", now=True,arg1=data)
# 	# data = frappe.enqueue("version2_app.version2_app.doctype.invoices.manual_upload.samplefunforqueue",queue='default', timeout=None, event=None, is_async=True, job_name="samplefunforqueue", now=True)
# 	# print(data,type(data))
# 	return {"success":True}
# 	# except Exception as e:
# 	# 	logger.error(f"manual upload queue  {str(e)}")
# 	# 	return {"success":False,"message":str(e)}


# def samplefunforqueue():
# 	doc = frappe.get_doc("company","MJH-01")
# 	doc.merchant_name = "sample"
# 	doc.save()


# @frappe.whitelist(allow_guest=True)
# def manual_upload1(data):
# 	return await manual_upload1(data).start()
# 	# return True


@frappe.whitelist(allow_guest=True)
def manual_upload(data):
    enqueue(
            manual_upload_data,
            queue="default",
            timeout=800000,
            event="data_import",
            now=False,
            data = data,
            is_async = False,
            )		
    return True    

@frappe.whitelist(allow_guest=True)
def manual_upload_data(data):
    try:
        print("startt--------------------------",data)
        start_time = datetime.datetime.now()
        folder_path = frappe.utils.get_bench_path()
        items_data_file = data['invoice_file']
        company = data['company']
        companyData = frappe.get_doc('company',data['company'])
        if companyData.bulk_excel_upload_type=="Grand" or companyData.bulk_excel_upload_type=="Novotel Vijayawada":
            output=grand_newdelhi(data)
            if output['success'] == False:
                frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            return output
        if companyData.bulk_excel_upload_type == "HolidayIn":
            output = holidayinManualupload(data)
            if output['success'] == False:
                frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            return output
        if companyData.bulk_excel_upload_type == "Opera":
            output = operabulkupload(data)
            if output['success'] ==False:
                frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            return output	
        if companyData.bulk_excel_upload_type == "Hyatt":
            output = hyattbulkupload(data)
            if output['success'] ==False:
                frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            return output
        if companyData.bulk_excel_upload_type == "Hyatt Mumbai" or companyData.bulk_excel_upload_type == "Hyatt Hyderabad":
            output = hyatt_mumbai(data)
            if output['success'] == False:
                frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","messagedata":output['message'],"company":company})
            return output
        site_folder_path = companyData.site_name
        items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
        paymentTypes = GetPaymentTypes()
        paymentTypes  = [''.join(each) for each in paymentTypes['data']]
        input_data = []
        invoice_referrence_objects = {}
        with open(items_file_path) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
        for each in data_dict['FOLIO_DETAILS']['LIST_G_BILL_NO']['G_BILL_NO']:

            # item_date = datetime.datetime.strptime(each['BILL_GENERATION_DATE'],'%Y-%m-%d %H:%M:%S').strftime(companyData.invoice_item_date_format)
            if each['SUMFT_DEBITPERBILL_NO'] is None:
                each['SUMFT_DEBITPERBILL_NO'] = each['SUMFT_CREDITPERBILL_NO']
            list_data={'invoice_category':each['FOLIO_TYPE'],'invoice_number':each['BILL_NO'],'invoice_date':each['BILL_GENERATION_DATE'],
                    'room_number':each['ROOM'],'guest_name':each['DISPLAY_NAME'],'total_invoice_amount':float(each['SUMFT_DEBITPERBILL_NO']),
                    'gstNumber':'empty','company_code':companyData.name,'place_of_supply':companyData.state_code,'invoice_item_date_format':companyData.invoice_item_date_format,
                    'guest_data':{'invoice_category':each['FOLIO_TYPE']}}
            
            items = []
            items_pdf = []
            if isinstance(each['LIST_G_TRX_NO']['G_TRX_NO'], list):
                for y,x in enumerate(each['LIST_G_TRX_NO']['G_TRX_NO']):
                    items_pdf_dict={}
                    item_date = datetime.datetime.strptime(x['TRX_DATE'],'%d-%b-%y').strftime(companyData.invoice_item_date_format)
                    if x['TRANSACTION_DESCRIPTION'] in paymentTypes:# 
                        if x['FT_CREDIT'] is None:
                            x['FT_CREDIT'] = x['FT_DEBIT']
                        items_pdf_dict = {'date':item_date,'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac',"FT_CREDIT":float(x['FT_CREDIT'])}
                        # continue
                    elif "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION'] or 'VAT' in x['TRANSACTION_DESCRIPTION'] or "Cess" in x['TRANSACTION_DESCRIPTION'] or "CESS" in x['TRANSACTION_DESCRIPTION']:
                        items_pdf_dict = {'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac'}
                    
                    # if x['FT_DEBIT'] is None:
                    #     x['FT_DEBIT'] = x['FT_CREDIT']
                    else:
                        if x['FT_DEBIT'] is None:
                            x['FT_DEBIT'] = x['FT_CREDIT']
                        items_dict = {'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],'sort_order':int(y)+1,"sac_code":'No Sac'}
                        # print(dict(x))
                        items.append(items_dict)
                        items_pdf.append(items_dict)
                    if len(items_pdf_dict)>0:
                        items_pdf.append(items_pdf_dict) 
            else:
                items_pdf_dict={}
                x = dict(each['LIST_G_TRX_NO']['G_TRX_NO'])
                item_date = datetime.datetime.strptime(x['TRX_DATE'],'%d-%b-%y').strftime(companyData.invoice_item_date_format)
                
                if x['TRANSACTION_DESCRIPTION'] in paymentTypes:# or "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION']:
                    if x['FT_CREDIT'] is None:
                        x['FT_CREDIT'] = x['FT_DEBIT']
                    items_pdf_dict = {'date':item_date,'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac',"FT_CREDIT":float(x['FT_CREDIT'])}
                # if x['FT_DEBIT'] is None:
                #     x['FT_DEBIT'] = x['FT_CREDIT']    
                elif "CGST" in x['TRANSACTION_DESCRIPTION'] or "SGST" in x['TRANSACTION_DESCRIPTION'] or 'IGST' in x['TRANSACTION_DESCRIPTION'] or 'VAT' in x['TRANSACTION_DESCRIPTION'] or "Cess" in x['TRANSACTION_DESCRIPTION'] or "CESS" in x['TRANSACTION_DESCRIPTION']:
                    items_pdf_dict = {'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],"sac_code":'No Sac'}
                else:
                    items.append({'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],'sort_order':1,"sac_code":'No Sac'})
                    items_pdf.append({'date':item_date,'item_value':float(x['FT_DEBIT']),'name':x['TRANSACTION_DESCRIPTION'],'sort_order':1,"sac_code":'No Sac'})


            list_data['items'] = items
            refobj = list_data.copy()
            del refobj['items']
            refobj['items'] = items_pdf
            invoice_referrence_objects[each['BILL_NO']] = refobj
            input_data.append(list_data)
        # if company_check_columns != invoice_columns:
        #     frappe.db.delete('File', {'file_url': data['invoice_file']})
        #     frappe.db.delete('File',{'file_url': data['gst_file']})
        #     frappe.db.commit()
        #     frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":"Invoice data mismatch","company":company})
        #     return {"success":False,"message":"Invoice data mismatch"}
        print("[===============[===================")
        gst_data_file = data['gst_file']
        gst_file_path = folder_path+'/sites/'+site_folder_path+gst_data_file
        gst_dataframe = pd.read_csv(gst_file_path)
        columns = list(gst_dataframe.columns.values)
        gst_data = gst_dataframe.values.tolist()
        gst_data.insert(0,columns)
        gst_dict = {}
        count = gst_data[0][0].split("|")
        if companyData.bulk_import_gst_count != len(count):
            # frappe.db.delete('File', {'file_url': data['invoice_file']})
            # frappe.db.delete('File',{'file_url': data['gst_file']})
            frappe.db.commit()
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk_upload_data","message":"Gst data mismatch","company":company})
            return {"success":False,"message":"Gst data mismatch"}
        for each in gst_data:
            if each[0][0]=="|":
                # inv = each[0].split("|")
                pass
            else:
                inv = each[0].split("|")                
                inv[0] = inv[0].replace("\t\t\t","")
                gst_dict[inv[1]] = inv[0]

        
        
        output_date = []
        # print(len(input_data),"lemnnnnnn output")
        taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
        frappe.publish_realtime("custom_socket", {'message':'Bulk Upload Invoices Count','type':"Bulk_upload_invoice_count","count":len(input_data),"company":company})
        countIn = 1
        for each in input_data:
            print(invoice_referrence_objects[each['invoice_number']],"--------")
            if each['invoice_category'] == "CREDIT TAX INVOICE":
                each['invoice_category'] = "Credit Invoice"
            elif each['invoice_category'] == "CREDIT INVOICE":
                each['invoice_category'] = "Credit Invoice"
            elif each['invoice_category'] == "TAX INVOICE":
                each['invoice_category'] = "Tax Invoice"
            else:
                each['invoice_category'] = "Tax Invoice"
            # print(each)
            if each['invoice_number'] in gst_dict:
                each['invoice_type'] = "B2B"
                invoice_referrence_objects[each['invoice_number']]['gstNumber'] = gst_dict[each['invoice_number']]
                each['gstNumber'] = gst_dict[each['invoice_number']]
            else:
                each['invoice_type'] = "B2C"
                each['gstNumber'] = ""

            # print(each['invoice_number'],"ionvvvvvvvvvnum")
            check_invoice = check_invoice_exists(str(each['invoice_number']))
            if check_invoice['success']==True:
                inv_data = check_invoice['data']
                if inv_data.docstatus!=2 and inv_data.irn_generated!="Success" and inv_data.invoice_type=="B2B":
                    reupload = True
                elif inv_data.invoice_type == "B2C":
                    reupload = True
                else:
                    reupload = False	
            else:
                reupload = False	
            if each['invoice_category'] == "empty":
                each['invoice_category'] = "Tax Invoice"
            each['invoice_from'] = "File"
            each['company_code'] = data['company']
            
            each['invoice_date'] = each['invoice_date'].replace("/","-")
            each['invoice_date'] = each['invoice_date'].replace("00:00:00","")
            date_time_obj = (each['invoice_date'].split(":")[-1]).strip()
            date_time_obj = datetime.datetime.strptime(date_time_obj,'%d-%b-%y').strftime('%d-%b-%y %H:%M:%S')
            each['invoice_date'] = date_time_obj
            each['mode'] = companyData.mode
            each['invoice_file'] = ""
            
            each['confirmation_number'] = each['invoice_number']
            each['print_by'] = "System"
            each['start_time'] = str(datetime.datetime.utcnow())
            each['name'] = each['guest_name']
            error_data = {"invoice_type":'B2B' if each['gstNumber'] != '' else 'B2C',"invoice_number":each['invoice_number'],"company_code":data['company'],"invoice_date":each['invoice_date']}
            error_data['invoice_file'] = ""
            error_data['guest_name'] = each['guest_name']
            error_data['gst_number'] = each['gstNumber']
            if each['invoice_type'] == "B2C":
                error_data['gst_number'] == ""
            error_data['state_code'] =  " "
            error_data['room_number'] = each['room_number']
            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
            error_data['pincode'] = ""
            error_data['total_invoice_amount'] = each['total_invoice_amount']
            error_data['sez'] = 0
            error_data['invoice_from'] = "File"
            each['sez'] = 0
            sez = 0
            # print(len(each['gstNumber']),"lennn",each['gstNumber'],each['invoice_type'])
            taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}

            if len(each['gstNumber']) < 15 and len(each['gstNumber'])>0:
                error_data['error_message'] = "Invalid GstNumber " + each['gstNumber']
                error_data['amened'] = 'No'
                
                errorcalulateItemsApiResponse = calulate_items(each)
                if errorcalulateItemsApiResponse['success'] == True:
                    error_data['items_data'] = errorcalulateItemsApiResponse['data']
                errorInvoice = Error_Insert_invoice(error_data)
                print("Error:  *******The given gst number is not a vaild one**********")
                B2B = "B2B"
                B2C = np.nan
                output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                # continue
            
            elif each['invoice_type']=="B2B":
                gspApiDataResponse = gsp_api_data({"code":data['company'],"mode":companyData.mode,"provider":companyData.provider})
                checkTokenIsValidResponse = check_token_is_valid({"code":data['company'],"mode":companyData.mode})
                if checkTokenIsValidResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":each['gstNumber'],"code":data['company'],"invoice":str(each['invoice_number']),"apidata":gspApiDataResponse['data']})
                    if getTaxPayerDetailsResponse['success'] == True:
                        sez = 1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        each['sez']=1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
                        taxpayer=getTaxPayerDetailsResponse['data'].__dict__
                        
                        calulateItemsApiResponse = calulate_items(each)

                        if calulateItemsApiResponse['success'] == True:
                            if reupload==False:
                                insertInvoiceApiResponse = insert_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
                                if insertInvoiceApiResponse['success']== True:
                                    
                                    B2B = "B2B"
                                    B2C = np.nan
                                        
                                    if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    else:
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    B2B = "B2B"
                                    B2C = np.nan
                                    
                                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    # print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                            else:
                                insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
                                if insertInvoiceApiResponse['success']== True:
                                    
                                    B2B = "B2B"
                                    B2C = np.nan
                                            
                                    if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    else:
                                        output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    B2B = "B2B"
                                    B2C = np.nan
                                    
                                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                                    # print("B2B insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                        else:
                        
                            error_data['error_message'] = calulateItemsApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)
                            B2B = "B2B"
                            B2C = np.nan
                            
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
                    else:
                        error_data['error_message'] = "Invalid GstNumber " + each['gstNumber']
                        error_data['amened'] = 'No'
                        
                        errorcalulateItemsApiResponse = calulate_items(each)
                        if errorcalulateItemsApiResponse['success'] == True:
                            error_data['items_data'] = errorcalulateItemsApiResponse['data']
                        errorInvoice = Error_Insert_invoice(error_data)
                        B2B = "B2B"
                        B2C = np.nan
                        
                        output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        print("Error:  *******The given gst number is not a vaild one**********")
                else:
                    error_data['error_message'] = "Login gsp error"
                    error_data['amened'] = 'No'
                    
                    errorcalulateItemsApiResponse = calulate_items(each)
                    if errorcalulateItemsApiResponse['success'] == True:
                        error_data['items_data'] = errorcalulateItemsApiResponse['data']
                    errorInvoice = Error_Insert_invoice(error_data)
                    B2B = "B2B"
                    B2C = np.nan
                    frappe.log_error(errorInvoice, 'enques')
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    print("Error:  *******The given gst number is not a vaild one**********")		
            else:
                taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}

                calulateItemsApiResponse = calulate_items(each)

                if calulateItemsApiResponse['success'] == True:
                    if reupload==False:
                        insertInvoiceApiResponse = insert_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
                        if insertInvoiceApiResponse['success']== True:
                            B2B=np.nan
                            B2C = "B2C"	 
                            if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            else:
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        else:
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)

                            B2B=np.nan
                            B2C = "B2C"
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                    else:
                        insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
                        if insertInvoiceApiResponse['success']== True:
                            B2B=np.nan
                            B2C = "B2C"	 
                            if insertInvoiceApiResponse['data'].irn_generated == "Success":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            else:
                                output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                        else:
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                            errorInvoice = Error_Insert_invoice(error_data)
                            
                            B2B=np.nan
                            B2C = "B2C"
                            output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                            # print("B2B insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                else:
                        
                    error_data['error_message'] = calulateItemsApiResponse['message']
                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                    errorInvoice = Error_Insert_invoice(error_data)
                    B2C = "B2C"
                    B2B = np.nan
                    
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoice Created','type':"Bulk_file_invoice_created","invoice_number":str(each['invoice_number']),"company":company})
            countIn+=1
        df = pd.DataFrame(output_date)
        df = df.groupby('date').count().reset_index()
        output_data = df.to_dict('records')
        # data['UserName'] = "Ganesh"
        InsertExcelUploadStats({"data":output_data,"uploaded_by":data['username'],"start_time":str(start_time),"referrence_file":data['invoice_file'],"gst_file":data['gst_file']})
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Created','type':"Bulk_upload_data","data":output_data,"company":company})
        # return {"success":True,"message":"Successfully Uploaded Invoices","data":output_data}		
        return {"success":True,"message":"Successfully Uploaded"}
    except Exception as e:
        print(traceback.print_exc())
        # frappe.db.delete('File', {'file_url': data['invoice_file']})
        # if "gst_file" in data:
        #     frappe.db.delete('File',{'file_url': data['gst_file']})
        frappe.db.commit()
        print(str(e),"   manual_upload")
        # frappe.log_error(frappe.get_traceback(), 'enques')
        # make_error_snapshot(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing manual_upload_data Bulk upload","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":str(e),"company":data['company']})
        return {"success":False,"message":str(e)}