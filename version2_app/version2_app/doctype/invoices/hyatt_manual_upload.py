from __future__ import unicode_literals
import frappe
# from frappe import enqueue
from frappe.model.document import Document
from datetime import date
import requests
import datetime
import random
import traceback,os,sys
import string
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
import time
import json
from frappe.utils.background_jobs import enqueue
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice



@frappe.whitelist()
def hyattbulkupload(data):
    try:
        print("startt--------------------------")
        start_time = datetime.datetime.now()
        folder_path = frappe.utils.get_bench_path()
        items_data_file = data['invoice_file']

        companyData = frappe.get_doc('company',data['company'])
        site_folder_path = companyData.site_name
        items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
        items_dataframe = pd.read_csv(items_file_path)

        columnslist = items_dataframe.columns.values.tolist()
        columnslist = columnslist[0].split("|")
        check_columns = companyData.bulk_import_invoice_headers
        company_check_columns = check_columns.split(",")
        if company_check_columns != columnslist:
            frappe.db.delete('File', {'file_url': data['invoice_file']})
            frappe.db.commit()
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":"Invoice data File mismatch","company":data['company']})
            return {"success":False,"message":"Invoice data File mismatch"}
        listdata = items_dataframe.head(3)
        valuesdata = items_dataframe.values.tolist()
        list_data={}
        input_data = []
        invoice_referrence_objects = {}
        for each in valuesdata:
            each[0]="|".join([str(i) for i in each ])
            # ['Satoshi Inatomi', '', 'HIGH', '0809', '1762', '01-APR-2021', 'CREDIT INVOICE', '5301', '999712', 'Guest Laundry', 'N', '-237.01', '', '226.85', '0.00', '0.00', '0.00', '0.00', '0.00', '', '', '', '', 'NONTAX']
            val = each[0].split("|")
            print(val[7],"////////////////////////////////////////////////")
            
            if len(val[1])>5:
                invoice_type = "B2B"
            else:
                val[1] = "empty"	
                invoice_type = "B2C"
            if val[13]=='':
                continue
            if companyData.name == "GHM-01":
                inv_date = datetime.datetime.strptime(val[6],'%d-%m-%Y').strftime("%d-%b-%Y")
                each = {"invoicedate":inv_date,"taxinvnum":val[5],"invoice_category":val[4],"room_number":1,"taxid":val[7],"goods_desc":val[33],"guestname":val[8],"invoiceamount":float(val[44]) if float(val[44]) != 0.00 else float(val[-14]),"taxcode_dsc":val[35],"sgst":val[46],"cgst":val[47],"igst":val[48],"cess":val[49]}
                # time.sleep(2)
                print(each,"-------------------------")
            else:
                each = {"invoicedate":val[5],"taxinvnum":"HRC"+val[4],"invoice_category":val[6],"room_number":val[3],"taxid":val[1],"goods_desc":val[9],"guestname":val[0],"invoiceamount":float(val[13]),"taxcode_dsc":val[8],"sgst":val[14],"cgst":val[15],"igst":val[16],"cess":val[17]}
            if frappe.db.exists("SAC HSN CODES",each['goods_desc']):
                sac_desc = frappe.get_doc("SAC HSN CODES",each['goods_desc'])
                if sac_desc.bulk_upload_service_charge ==1:
                    if sac_desc.one_sc_applies_to_all == 1:
                        # vatamount = (vat_rate_percentage * scharge_value) / 100.0
                        itemcharge = (each['invoiceamount']*companyData.service_charge_percentage)/(100.0+companyData.service_charge_percentage)
                    else:
                        itemcharge = (each['invoiceamount']*sac_desc.service_charge_rate)/(100.0+sac_desc.service_charge_rate)

                    each['invoiceamount'] = each['invoiceamount'] - itemcharge    
            if each['invoice_category'] == "CREDIT INVOICE":
                each['invoice_category'] = "Credit Invoice"
            if each['invoice_category'] == "TAX INVOICE":
                each['invoice_category'] = "Tax Invoice"
            if each['invoice_category'] == "DEBIT INVOICE":
                each['invoice_category'] = "Debit Invoice"        
            # total_invoice_amount = float(val[-1])+float(val[])
            if companyData.name == "GHM-01":
                sgst = 0 if val[-9]!="" else float(val[46])
                cgst = 0 if val[-8]!="" else float(val[47])
                igst = 0 if val[-7]!="" else float(val[48])
                cess = 0 if val[-6]!="" else float(val[49])
                # total_invoice_amount = 0 if val[11]=="" else float(val[-1]) 
                total_invoice_amount = float(val[-1])
            else:
                sgst = 0 if val[14]!="" else float(val[14])
                cgst = 0 if val[15]!="" else float(val[15])
                igst = 0 if val[16]!="" else float(val[16])
                cess = 0 if val[17]!="" else float(val[17])
                total_invoice_amount = 0 if val[11]=="" else float(val[11])
            # total_invoice_amount = float(val[11]) 
            each["total_invoice_amount"] = total_invoice_amount
            if each['taxinvnum'] not in invoice_referrence_objects:
                    
                invoice_referrence_objects[each['taxinvnum']] = []
                invoice_referrence_objects[each['taxinvnum']].append(each)
            else:
                invoice_referrence_objects[each['taxinvnum']].append(each)
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            each['invoicedate'] = str(each['invoicedate'])
            if each['goods_desc'] not in payment_Types:
                
                
                item_date = datetime.datetime.strptime(each['invoicedate'],'%d-%b-%Y').strftime(companyData.invoice_item_date_format)
                if 'invoice_number' not in list_data:
                    list_data['invoice_category'] = each['invoice_category']
                    list_data['invoice_number'] = each['taxinvnum']
                    list_data['invoice_date'] = each['invoicedate']
                    list_data['room_number'] = 1
                    list_data['guest_name'] = each['guestname']
                    # amount = each['invoiceamount']+each['sgstamount']+each['sgstamount']+each['ngstamount']
                    list_data['total_invoice_amount'] = each['total_invoice_amount']
                    list_data['gstNumber'] = each['taxid']
                    item_list = {'date':item_date,'item_value':each['invoiceamount'],'name':each['goods_desc'],'sort_order':1,"sac_code":str(each['taxcode_dsc'])}
                    items = []
                    items.append(item_list)
                    list_data['items'] = items
                    list_data['company_code'] = data['company']
                    list_data['invoice_number'] = each['taxinvnum']
                    list_data['place_of_supply'] = companyData.state_code
                    list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
                    list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
                else:
                    if list_data['invoice_number'] == each['taxinvnum'] :
                        # amount = list_data['invoiceamount']+list_data['sgstamount']+list_data['sgstamount']+list_data['ngstamount']
                        list_data['total_invoice_amount'] = each['total_invoice_amount']
                        items = {'date':item_date,"sac_code":str(each['taxcode_dsc']),'item_value':each['invoiceamount'],'name':each['goods_desc'],'sort_order':1}
                        list_data['items'].extend([items])
                    else:
                        input_data.append(list_data)
                        list_data = {}
                        list_data['invoice_category'] = each['invoice_category']
                        list_data['invoice_number'] = each['taxinvnum']
                        list_data['invoice_date'] = each['invoicedate']
                        list_data['room_number'] = 1
                        list_data['guest_name'] = each['guestname']
                        # amount = each['invoiceamount']+each['sgstamount']+each['sgstamount']+each['ngstamount']
                        list_data['total_invoice_amount'] = each['total_invoice_amount']
                        list_data['gstNumber'] = each['taxid']
                        # list_data['total_invoice_amount'] = each['SUMFT_DEBITPERtaxinvnum']
                        item_list = {'date':item_date,"sac_code":str(each['taxcode_dsc']),'item_value':each['invoiceamount'],'name':each['goods_desc'],'sort_order':1}
                        items = []
                        items.append(item_list)
                        list_data['items'] = items
                        list_data['company_code'] = data['company']
                        list_data['invoice_number'] = each['taxinvnum']
                        list_data['place_of_supply'] = companyData.state_code
                        list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
                        list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
        output_date = []
        # print(len(input_data),"lemnnnnnn output")
        taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
        frappe.publish_realtime("custom_socket", {'message':'Bulk Upload Invoices Count','type':"Bulk_upload_invoice_count","count":len(input_data),"company":data['company']})
        countIn = 1
        print(len(input_data),"count")

        for each in input_data:
            each['gstNumber'] = str(each['gstNumber'])
            
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
            
            each['invoice_from'] = "File"
            each['company_code'] = data['company']
            
            each['invoice_date'] = each['invoice_date'].replace(" 00:00:00","")
            
            date_time_obj = datetime.datetime.strptime(each['invoice_date'],'%d-%b-%Y').strftime('%d-%b-%y %H:%M:%S')
            each['invoice_date'] = date_time_obj
            each['mode'] = companyData.mode
            each['invoice_file'] = ""
            each['gstNumber'] = each['gstNumber'].strip()
            if each['gstNumber'] == "empty":
                each['invoice_type'] = "B2C"
                each['gstNumber']=""
            else:
                each['invoice_type'] = "B2B"
                invoice_referrence_objects[each['invoice_number']][0]['gstNumber'] = each['gstNumber']
            each['confirmation_number'] = each['invoice_number']
            each['print_by'] = "System"
            each['start_time'] = str(datetime.datetime.utcnow())
            each['name'] = each['guest_name']
            error_data = {"invoice_type":'B2B' if each['gstNumber'] != '' else 'B2C',"invoice_number":each['invoice_number'],"company_code":data['company'],"invoice_date":each['invoice_date']}
            error_data['invoice_file'] = ""
            error_data['guest_name'] = each['guest_name']
            error_data['gst_number'] = ''
            if each['invoice_type'] == "B2C":
                error_data['gst_number'] == " "
            error_data['state_code'] =  " "
            error_data['room_number'] = each['room_number']
            error_data['pincode'] = ""
            error_data['total_invoice_amount'] = each['total_invoice_amount']
            error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
            error_data['sez'] = 0
            error_data['invoice_from'] = "File"
            each['sez'] = 0
            sez = 0
            # print(len(each['gstNumber']),"lennn",each['gstNumber'],each['invoice_type'])
            taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
            if len(each['gstNumber']) < 15 and len(each['gstNumber'])>0:
                error_data['error_message'] = each['gstNumber']+" "+"Invalid GstNumber"
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
                                    # print(error_data['error_message'])
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
                        error_data['error_message'] = each['gstNumber']+" "+"Invalid GstNumber"
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
                    print(errorInvoice)
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoice Created','type':"Bulk_file_invoice_created","invoice_number":str(each['invoice_number']),"company":data['company'], "count":len(invoice_number_list), "invoice_count":countIn})
            countIn+=1
        df = pd.DataFrame(output_date)
        df = df.groupby('date').count().reset_index()
        output_data = df.to_dict('records')
        InsertExcelUploadStats({"data":output_data,"uploaded_by":data['username'],"start_time":str(start_time),"referrence_file":data['invoice_file']})
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Completed','type':"Bulk_upload_data","data":output_data,"company":data['company']})
        # return {"success":True,"message":"Successfully Uploaded Invoices","data":output_data}		
        return {"success":True,"message":"Successfully Uploaded"}
    except Exception as e:
        print(str(e),"   Opera manual ")
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing hyattbulkupload Bulk upload","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":str(e),"company":data['company']})
        return {"success":False,"message":str(e)}    