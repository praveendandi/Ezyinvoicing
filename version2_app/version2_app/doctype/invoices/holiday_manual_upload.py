import frappe
# from frappe import enqueue
from frappe.model.document import Document
from datetime import date
import requests
import datetime,ast
import random, re
import traceback,os,sys
import xmltodict
import time
import string
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice,b2b_success_to_credit_note

pd.set_option("display.max_rows", None, "display.max_columns", None)

from os.path import expanduser
home = expanduser("~")

@frappe.whitelist(allow_guest=True)
def holidayinManualupload(data):
    try:
        # data={"invoice_file":"/private/files/3340 report.xlsx","company":"HIEHH-01"}
        companyData = frappe.get_doc('company',data['company'])
        start_time = datetime.datetime.now()
        company = data['company']
        if "error_upload" in data and data["error_upload"] == "yes":
            newoutput = data["total_data"]
        else:
            print("startt--------------------------",data)
            folder_path = frappe.utils.get_bench_path()
            items_data_file = data['invoice_file']
            folioid=""
            site_folder_path = companyData.site_name
            items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
            if ".csv" in items_file_path:
                try:
                    items_dataframe = pd.read_csv(items_file_path,error_bad_lines=False,delimiter='|')
                except UnicodeDecodeError:
                    items_dataframe = pd.read_csv(items_file_path,encoding ='latin1',error_bad_lines=False,delimiter='|')
            elif ".xml" in items_file_path:
                with open(items_file_path) as xml_file:
                    items_dataframe = xmltodict.parse(xml_file.read())
            else:
                items_dataframe = pd.read_excel(items_file_path,error_bad_lines=False,delimiter='|')

            # items_dataframe = pd.read_excel(items_file_path)
            if ".xml" not in items_file_path:
                items_dataframe = items_dataframe.fillna('empty')
                items_dataframe = items_dataframe.sort_values("taxinvnum")
                invoice_columns = list(items_dataframe.columns.values)
                invoice_num = list(set(items_dataframe['taxinvnum']))
                company_check_columns = companyData.bulk_import_invoice_headers
                company_check_columns = company_check_columns.split(",")
                if company_check_columns != invoice_columns:
                    frappe.db.delete('File', {'file_url': data['invoice_file']})
                    frappe.db.commit()
                    frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk Invoices Exception","message":"Invoice data File mismatch","company":data['company']})
                    return {"success":False,"message":"Invoice data File mismatch"}
                newoutput = items_dataframe.to_dict('records')
            else:
                output=[]
                for item in items_dataframe["data"]["records"]["row"]:
                    data1=dict((each["@name"],each["#text"]) if "#text" in  each else (each["@name"],"") for each in item["column"])
                    data1["invoiceamount"]=float(data1["invoiceamount"])
                    data1["sgstamount"]=float(data1["sgstamount"])
                    data1["ngstamount"]=float(data1["ngstamount"])
                    if "folioid" in data1:
                        # global folioid
                        folioid=data1["folioid"]
                    output.append(ast.literal_eval(json.dumps(data1)))
                df = pd.DataFrame(output)
                dfoutput = df.sort_values(by='taxinvnum')
                newoutput = dfoutput.T.to_dict().values()
        list_data={}
        item_taxable = ""
        line_item_type = ""
        input_data = []
        invoice_referrence_objects = {}
        for each in newoutput:
            total_invoice_amount = each['invoiceamount']
            totalitemAmount = each['invoiceamount']
            each['invoiceamount'] = each['invoiceamount']-each['sgstamount']-each['sgstamount']-each['ngstamount']
            each['invoiceamount'] = round(each['invoiceamount'],2)
            each['taxcode_dsc'] = str(each['taxcode_dsc'])
            # print(each['taxinvnum'],len(each['taxinvnum']))
            del each['accountdate']# = str(each['accountdate'])
            del each['arrdate']# = str(each['arrdate'])
            del each['depdate']# = str(each['depdate'])
            del each['org_invoicedate']
                
            if each['taxinvnum'] not in invoice_referrence_objects:
                
                invoice_referrence_objects[each['taxinvnum']] = []
                invoice_referrence_objects[each['taxinvnum']].append(each)
            else:
                invoice_referrence_objects[each['taxinvnum']].append(each)
            
            paymentTypes = GetPaymentTypes()
            payment_Types  = [''.join(each) for each in paymentTypes['data']]
            each['invoicedate'] = str(each['invoicedate'])
            csi = total_invoice_amount-each['sgstamount']-each['sgstamount']-each['ngstamount']
            if csi != 0:
                gst_percentage = round((each['sgstamount']/csi)*100,1)
            else:
                gst_percentage = 0
            if each['goods_desc'] not in payment_Types:
                # totalitemAmount = each['invoiceamount']-each['sgstamount']-each['sgstamount']-each['ngstamount']
                if "00:00:00" in each['invoicedate']:
                    item_date = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d %H:%M:%S').strftime(companyData.invoice_item_date_format)
                else:
                    item_date = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d').strftime(companyData.invoice_item_date_format)
                # if frappe.db.exists('SAC HSN CODES', each['goods_desc']):
                #     sac_doc = frappe.get_doc('SAC HSN CODES',each['goods_desc'])
                #     list_data["sac_desc"] = each['goods_desc']
                #     list_data["sac_code"] = "Found"
                # else:
                #     list_data["sac_desc"] = each['goods_desc']
                #     list_data["sac_code"] = "NOT Found"
                #     break
                if (each['sgstamount'] != 0 or each['ngstamount'] != 0):
                    line_item_type = "Included"
                    item_taxable = "Yes"
                elif str(each['taxcode_dsc']) == "996311" and each['sgstamount'] == 0 and each['ngstamount'] == 0:
                    line_item_type = "Excempted"
                    item_taxable = "Yes"
                else:
                    if str(each['taxcode_dsc']) != "996311" and each['sgstamount'] == 0 and each['ngstamount'] == 0:
                        line_item_type = "Non-Gst"
                        item_taxable = "No"
                item_date = datetime.datetime.strptime(item_date,companyData.invoice_item_date_format)
                if 'invoice_number' not in list_data:
                    list_data['invoice_category'] = "Tax Invoice"
                    list_data['invoice_number'] = each['taxinvnum']
                    list_data['invoice_date'] = each['invoicedate']
                    list_data['room_number'] = 0
                    list_data['guest_name'] = each['guestname']
                    # amount = #+each['sgstamount']+each['sgstamount']+each['ngstamount']
                    list_data['total_invoice_amount'] = totalitemAmount
                    list_data['gstNumber'] = each['taxid'].strip()
                    item_list = {'date':item_date,'item_value':each['invoiceamount'],'item_name':each['goods_desc'],'sort_order':1,"sac_code":str(each['taxcode_dsc']),"doctype":"Items","item_type":"SAC" if len(each['taxcode_dsc']) == 6 else "HSN","cgst": gst_percentage if each['sgstamount'] else 0,"sgst": gst_percentage if each['sgstamount'] else 0,
                        "igst": gst_percentage if each['ngstamount'] else 0,"item_taxable_value":csi,"gst_rate":gst_percentage*2,"item_value_after_gst":total_invoice_amount,"cess":0,"cess_amount":0,"state_cess":0,"state_cess_amount":0,"cgst_amount":each['sgstamount'],"sgst_amount":each['sgstamount'],"igst_amount":each["ngstamount"],"parent":each["taxinvnum"],
                        "parentfield":"items","parenttype":"invoices","sac_code_found":"Yes","other_charges":0,"vat_amount":0,"vat":0.0,"unit_of_measurement":"OTH","quantity":1,"unit_of_measurement_description":"OTHERS",
                        "is_service_charge_item":"No","sac_index":"1","line_edit_net":"No","item_reference":"","other_charges":0,"taxable":item_taxable,"item_mode":"Debit" if "-" not in str(each['invoiceamount']) else "Credit","item_type":"SAC" if len(str(each['taxcode_dsc'])) == 6 else "HSN","description":each['goods_desc'],"type":line_item_type
                    }
                    items = []
                    items.append(item_list)
                    list_data['items'] = items
                    list_data['company_code'] = data['company']
                    list_data['invoice_number'] = each['taxinvnum']
                    list_data["folioid"] = each["folioid"]
                    list_data['place_of_supply'] = companyData.state_code
                    list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
                    list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
                else:
                    if list_data['invoice_number'] == each['taxinvnum'] :
                        # amount = list_data['invoiceamount']+list_data['sgstamount']+list_data['sgstamount']+list_data['ngstamount']
                        list_data['total_invoice_amount'] = list_data['total_invoice_amount']+totalitemAmount #+each['sgstamount']+each['sgstamount']+each['ngstamount']
                        list_data["folioid"] = each["folioid"]
                        items = {'date':item_date,'item_value':each['invoiceamount'],'item_name':each['goods_desc'],'sort_order':1,"sac_code":str(each['taxcode_dsc']),"doctype":"Items","item_type":"SAC" if len(each['taxcode_dsc']) == 6 else "HSN","cgst": gst_percentage if each['sgstamount'] else 0,"sgst": gst_percentage if each['sgstamount'] else 0,
                        "igst": gst_percentage if each['ngstamount'] else 0,"item_taxable_value":csi,"gst_rate":gst_percentage*2,"item_value_after_gst":total_invoice_amount,"cess":0,"cess_amount":0,"state_cess":0,"state_cess_amount":0,"cgst_amount":each['sgstamount'],"sgst_amount":each['sgstamount'],"igst_amount":each["ngstamount"],"parent":each["taxinvnum"],
                        "parentfield":"items","parenttype":"invoices","sac_code_found":"Yes","other_charges":0,"vat_amount":0,"vat":0.0,"unit_of_measurement":"OTH","quantity":1,"unit_of_measurement_description":"OTHERS",
                        "is_service_charge_item":"No","sac_index":"1","line_edit_net":"No","item_reference":"","other_charges":0,"taxable":item_taxable,"item_mode":"Debit" if "-" not in str(each['invoiceamount']) else "Credit","item_type":"SAC" if len(str(each['taxcode_dsc'])) == 6 else "HSN","description":each['goods_desc'],"type":line_item_type}
                        list_data['items'].extend([items])
                    else:
                        input_data.append(list_data)
                        list_data = {}
                        list_data['invoice_category'] = "Tax Invoice"
                        list_data["folioid"] = each["folioid"]
                        list_data['invoice_number'] = each['taxinvnum']
                        list_data['invoice_date'] = each['invoicedate']
                        list_data['room_number'] = 0
                        list_data['guest_name'] = each['guestname']
                        # amount = each['invoiceamount']#+each['sgstamount']+each['sgstamount']+each['ngstamount']
                        list_data['total_invoice_amount'] = totalitemAmount
                        list_data['gstNumber'] = each['taxid'].strip()
                        # list_data['total_invoice_amount'] = each['SUMFT_DEBITPERtaxinvnum']
                        item_list = {'date':item_date,'item_value':each['invoiceamount'],'item_name':each['goods_desc'],'sort_order':1,"sac_code":str(each['taxcode_dsc']),"doctype":"Items","item_type":"SAC" if len(each['taxcode_dsc']) == 6 else "HSN","cgst": gst_percentage if each['sgstamount'] else 0,"sgst": gst_percentage if each['sgstamount'] else 0,
                        "igst": gst_percentage if each['ngstamount'] else 0,"item_taxable_value":csi,"gst_rate":gst_percentage*2,"item_value_after_gst":total_invoice_amount,"cess":0,"cess_amount":0,"state_cess":0,"state_cess_amount":0,"cgst_amount":each['sgstamount'],"sgst_amount":each['sgstamount'],"igst_amount":each["ngstamount"],"parent":each["taxinvnum"],
                        "parentfield":"items","parenttype":"invoices","sac_code_found":"Yes","other_charges":0,"vat_amount":0,"vat":0.0,"unit_of_measurement":"OTH","quantity":1,"unit_of_measurement_description":"OTHERS",
                        "is_service_charge_item":"No","sac_index":"1","line_edit_net":"No","item_reference":"","other_charges":0,"taxable":item_taxable,"item_mode":"Debit" if "-" not in str(each['invoiceamount']) else "Credit","item_type":"SAC" if len(str(each['taxcode_dsc'])) == 6 else "HSN","description":each['goods_desc'],"type":line_item_type}
                        items = []
                        items.append(item_list)
                        list_data['items'] = items
                        list_data['company_code'] = data['company']
                        list_data['invoice_number'] = each['taxinvnum']
                        list_data['place_of_supply'] = companyData.state_code
                        list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
                        list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
                # else:
                #     list_data['invoice_category'] = "Tax Invoice"
                #     list_data['invoice_number'] = each['taxinvnum']
                #     list_data['invoice_date'] = each['invoicedate']
                #     list_data['room_number'] = 1
                #     list_data['guest_name'] = each['guestname']
                #     # amount = #+each['sgstamount']+each['sgstamount']+each['ngstamount']
                #     list_data['total_invoice_amount'] = totalitemAmount
                #     list_data['gstNumber'] = each['taxid']
                #     item_list={}
                #     items = []
                #     items.append(item_list)
                #     list_data['items'] = items
                #     list_data['company_code'] = data['company']
                #     list_data['invoice_number'] = each['taxinvnum']
                #     list_data['place_of_supply'] = companyData.state_code
                #     list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
                #     list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
        gstNumber = ''
        output_date = []
        # print(len(input_data),"lemnnnnnn output")
        taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
        frappe.publish_realtime("custom_socket", {'message':'Bulk Upload Invoices Count','type':"Bulk_upload_invoice_count","count":len(input_data),"company":company})
        countIn = 1
        print(len(input_data),"count")
        if input_data == [] and len(list_data)>0:
            input_data.append(list_data)
        for each in input_data:
            each['gstNumber'] = str(each['gstNumber'])
            # each['total_invoice_amount']= 10000
            print(each['invoice_number'],"       invoice Number ",countIn)
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
            
            each['invoice_date'] = each['invoice_date'].replace(" 00:00:00","")
            
            date_time_obj = datetime.datetime.strptime(each['invoice_date'],'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            each['invoice_date'] = date_time_obj
            each['mode'] = companyData.mode
            each['invoice_file'] = ""
            each['gstNumber'] = each['gstNumber'].strip()
            if each['gstNumber'] == "empty" or len(each['gstNumber']) != 15:
                each['invoice_type'] = "B2C"
                each['gstNumber']=""
            else:
                if re.match("^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",each['gstNumber']):
                    each['invoice_type'] = "B2B"
                    each['gstNumber'] = each['gstNumber']
                    invoice_referrence_objects[each['invoice_number']][0]['gstNumber'] = each['gstNumber']
                else:
                    each['invoice_type'] = "B2C"
                    each['gstNumber']=""
            each['confirmation_number'] = ""
            each['print_by'] = "System"
            each['start_time'] = str(datetime.datetime.utcnow())
            each['name'] = each['guest_name']
            error_data = {"invoice_type":'B2B' if gstNumber != "" else 'B2C',"invoice_number":each['invoice_number'],"company_code":data['company'],"invoice_date":each['invoice_date']}
            error_data['invoice_file'] = ""
            error_data['guest_name'] = each['guest_name']
            error_data['gst_number'] = each['gstNumber']
            if each['invoice_type'] == "B2C":
                error_data['gst_number'] == ""
            error_data['state_code'] =  " "
            error_data['room_number'] = each['room_number']
            error_data['pincode'] = ""
            error_data['total_invoice_amount'] = each['total_invoice_amount']
            error_data['sez'] = 0
            error_data['invoice_from'] = "File"
            each['sez'] = 0
            sez = 0
            taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
            if len(each['gstNumber']) < 15 and len(each['gstNumber'])>0:
                error_data['error_message'] = "Invalid GstNumber "+each['gstNumber']
                error_data['amened'] = 'No'
                error_data['invoice_type'] = "B2B"
                error_data['gst_number'] = each['gstNumber']
                # errorcalulateItemsApiResponse = calulate_items(each)
                error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                # if errorcalulateItemsApiResponse['success'] == True:
                error_data['items_data'] = each['items']
                errorInvoice = Error_Insert_invoice(error_data)
                print("Error:  *******The given gst number is not a vaild one")
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
                        # calulateItemsApiResponse = calulate_items(each)
                        # if calulateItemsApiResponse['success'] == True:
                        # for sac_items in each['items']:
                        #     if frappe.db.exists('SAC HSN CODES', each['goods_desc']):
                        #         sac_doc = frappe.get_doc('SAC HSN CODES',each['goods_desc'])
                        #         list_data["sac_code"] = "Found"
                        #     else:
                        #         list_data["sac_code"] = "NOT Found"
                        #         break
                        # if each["sac_code"] == "Found":
                        if reupload==False:
                            insertInvoiceApiResponse = insert_invoice({"folioid":each["folioid"],"guest_data":each,"company_code":data['company'],"items_data":each['items'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
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
                            insertInvoiceApiResponse = Reinitiate_invoice({"folioid":each["folioid"],"guest_data":each,"company_code":data['company'],"items_data":each['items'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
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
                        # else:
                        #     error_data['error_message'] = "SAC Code "+ each["sac_desc"] +" not found"
                        #     error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                        #     errorInvoice = Error_Insert_invoice(error_data)
                        #     B2B = "B2B"
                        #     B2C = np.nan
                            
                        #     output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    else:
                        error_data['error_message'] = "Invalid GstNumber "+each['gstNumber']
                        error_data['amened'] = 'No'
                        error_data['invoice_type'] = "B2B"
                        error_data['gst_number'] = each['gstNumber']
                        errorcalulateItemsApiResponse = calulate_items(each)
                        error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
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
                    error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                    if errorcalulateItemsApiResponse['success'] == True:
                        error_data['items_data'] = errorcalulateItemsApiResponse['data']
                    errorInvoice = Error_Insert_invoice(error_data)
                    B2B = "B2B"
                    B2C = np.nan
                    
                    output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    print("Error:  *******The given gst number is not a vaild one**********")		
            else:
                taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}

                # calulateItemsApiResponse = calulate_items(each)
                # if each["sac_code"] == "Found":
                if reupload==False:
                    insertInvoiceApiResponse = insert_invoice({"folioid":each["folioid"],"guest_data":each,"company_code":data['company'],"items_data":each['items'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
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
                    insertInvoiceApiResponse = Reinitiate_invoice({"folioid":each["folioid"],"guest_data":each,"company_code":data['company'],"items_data":each['items'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":{"data":invoice_referrence_objects[each['invoice_number']]}})
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
                # else:
                        
                #     error_data['error_message'] = "SAC Code "+ each["sac_desc"] +" not found"
                #     error_data['invoice_object_from_file'] = {"data":invoice_referrence_objects[each['invoice_number']]}
                #     errorInvoice = Error_Insert_invoice(error_data)
                #     B2C = "B2C"
                #     B2B = np.nan
                    
                #     output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
                    # print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
            frappe.publish_realtime("custom_socket", {'message':'Bulk Invoice Created','type':"Bulk_file_invoice_created","invoice_number":str(each['invoice_number']),"company":company})
            countIn+=1
        df = pd.DataFrame(output_date)
        df = df.groupby('date').count().reset_index()
        output_data = df.to_dict('records')
        InsertExcelUploadStats({"data":output_data,"uploaded_by":data['username'] if "username" in data else "","start_time":str(start_time),"referrence_file":data['invoice_file']})
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Created','type':"Bulk_upload_data","data":output_data,"company":company})
        # return {"success":True,"message":"Successfully Uploaded Invoices","data":output_data}		
        return {"success":True,"message":"Successfully Uploaded"}
    except Exception as e:
        print(traceback.print_exc())
        frappe.db.delete('File', {'file_url': data['invoice_file']})
        # frappe.db.delete('File',{'file_url': data['gst_file']})
        frappe.db.commit()
        print(str(e),"   manual_upload")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing holidayinManualupload Bulk upload","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        frappe.publish_realtime("custom_socket", {'message':'Bulk Invoices Exception','type':"Bulk_upload_data","message":str(e),"company":data['company']})
        return {"success":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def testsample(file_path,company): 
    companyData = frappe.get_doc('company',company)
    site_folder_path = companyData.site_name
    folder_path = frappe.utils.get_bench_path()
    items_file_path = folder_path+'/sites/'+site_folder_path+file_path
    with open(items_file_path) as xml_file:
        items_dataframe = xmltodict.parse(xml_file.read())
    output=[]
    for item in items_dataframe["data"]["records"]["row"]:
        data1=dict((each["@name"],each["#text"]) if "#text" in  each else (each["@name"],"") for each in item["column"])
        data1["invoiceamount"]=float(data1["invoiceamount"])
        data1["sgstamount"]=float(data1["sgstamount"])
        if "ngstamount" not in data1:
            data1["ngstamount"]=float(data1["igstamount"])
        else:
            data1["ngstamount"]=float(data1["ngstamount"])
        if "folioid" in data1:
            # global folioid
            folioid=data1["folioid"]
        output.append(ast.literal_eval(json.dumps(data1)))
    df = pd.DataFrame(output)
    group = df.groupby(['taxinvnum'])['taxinvnum'].count()
    find = group.to_dict()
    error_invoice_numbers = []
    for key,value in find.items():
        if frappe.db.exists("Invoices",key):
            invoice_doc = frappe.get_doc("Invoices",key)
            items_count = frappe.db.count('Items', {'parent': key})
            if items_count == value:
                print("------------------------------------")
            else:
                if invoice_doc.invoice_type == "B2B":
                    error_invoice_numbers.append({"invoice_number":key,"GST Number":invoice_doc.gst_number,"Legal Name":invoice_doc.legal_name,"Guest Name":invoice_doc.guest_name,"item_count_in_xml":value,"item_count_in_ezy":items_count})
    if len(error_invoice_numbers) > 0:
        ts = time.time()
        folder_path = frappe.utils.get_bench_path()
        items_file_path = home+'/'+str(ts).replace('.',"")+".xlsx"
        df2 = pd.DataFrame(error_invoice_numbers)
        df2.to_excel(items_file_path,index=False)
        files_new = {"file": open(items_file_path, 'rb')}
        payload_new = {
            "is_private": 1,
            "folder": "Home"
        }
        upload_report = requests.post(
            companyData.host + "api/method/upload_file",
            files=files_new,
            data=payload_new).json()
        url = upload_report['message']['file_url']
        return url
    else:
        return {"success": True,"message": "No data found"}


@frappe.whitelist(allow_guest=True)
def holidayinnerrorbulkreprocess(file_path,company):
    try:
        companyData = frappe.get_doc('company',company)
        site_folder_path = companyData.site_name
        folder_path = frappe.utils.get_bench_path()
        items_file_path = folder_path+'/sites/'+site_folder_path+file_path
        newData = pd.read_excel(items_file_path)
        # data = newData.T.to_dict().values()
        data = newData.to_dict('records')
        cn_data = []
        for each in data:
            if frappe.db.exists("Invoices",each["invoice_number"]):
                invoice_doc = frappe.get_doc("Invoices",each["invoice_number"])
                
                raise_credit = b2b_success_to_credit_note({"invoice_number":each["invoice_number"],"taxinvoice":"No","invoice_date":invoice_doc.invoice_date,"holiday":"Yes"})
                if raise_credit["success"] == False:
                    return raise_credit
                if frappe.db.exists("Invoices",each["invoice_number"]+"CN"):
                    credit_invoice_doc = frappe.get_doc("Invoices",each["invoice_number"]+"CN")
                    sales_amount_after_tax = str(credit_invoice_doc.sales_amount_after_tax)
                else:
                    sales_amount_after_tax = ""
                cn_data.append({"Tax Invoice Number":each["invoice_number"],"Credit Invoice Number":each["invoice_number"]+"CN","GST Number":invoice_doc.gst_number,"Trade Name":invoice_doc.trade_name,"Sales Tax Amount":sales_amount_after_tax})
        if len(cn_data) > 0:
            ts = time.time()
            folder_path = frappe.utils.get_bench_path()
            items_file_path = home+'/'+str(ts).replace('.',"")+".xlsx"
            df2 = pd.DataFrame(cn_data)
            df2.to_excel(items_file_path,index=False)
            files_new = {"file": open(items_file_path, 'rb')}
            payload_new = {
                "is_private": 1,
                "folder": "Home"
            }
            upload_report = requests.post(
                companyData.host + "api/method/upload_file",
                files=files_new,
                data=payload_new).json()
            url = upload_report['message']['file_url']
            return url
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing holidayinnerrorbulkreprocess","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def holidayinnreprocesserrorbulkupload(file_path,company,xml_file):
    # try:
        companyData = frappe.get_doc('company',company)
        site_folder_path = companyData.site_name
        folder_path = frappe.utils.get_bench_path()
        items_file_path = folder_path+'/sites/'+site_folder_path+file_path
        newData = pd.read_excel(items_file_path)
        # data = newData.T.to_dict().values()
        data = newData['invoice_number'].tolist()
        xml_file_path = folder_path+'/sites/'+site_folder_path+xml_file
        with open(xml_file_path) as xml_files:
            items_dataframe = xmltodict.parse(xml_files.read())
        output=[]
        for item in items_dataframe["data"]["records"]["row"]:
            data1=dict((each["@name"],each["#text"]) if "#text" in  each else (each["@name"],"") for each in item["column"])
            data1["invoiceamount"]=float(data1["invoiceamount"])
            data1["sgstamount"]=float(data1["sgstamount"])
            data1["ngstamount"]=float(data1["ngstamount"])
            if "folioid" in data1:
                # global folioid
                folioid=data1["folioid"]
            output.append(ast.literal_eval(json.dumps(data1)))
        df = pd.DataFrame(output)
        dfoutput = df.sort_values(by='taxinvnum')
        newoutput = dfoutput.T.to_dict().values()
        total_data = [y for x in data for y in newoutput if y["taxinvnum"] == x]
        for each in total_data:
            each["taxinvnum"] = each["taxinvnum"]+"-"
        tax_invoice = holidayinManualupload({"total_data":total_data,"company":company,"error_upload":"yes","invoice_file":xml_file})
        if tax_invoice["success"]==False:
            return tax_invoice
        cn_data = []
        for number in data:
            if frappe.db.exists("Invoices",number+"-"):
                invoice_doc = frappe.get_doc("Invoices",number+"-")
                cn_data.append({"Tax Invoice Number":number,"New Invoice Number":number+"-","GST Number":invoice_doc.gst_number,"Trade Name":invoice_doc.trade_name,"Sales Tax Amount":invoice_doc.pms_invoice_summary_without_gst})
        if len(cn_data) > 0:
            ts = time.time()
            folder_path = frappe.utils.get_bench_path()
            items_file_path = home+'/'+str(ts).replace('.',"")+".xlsx"
            df2 = pd.DataFrame(cn_data)
            df2.to_excel(items_file_path,index=False)
            files_new = {"file": open(items_file_path, 'rb')}
            payload_new = {
                "is_private": 1,
                "folder": "Home"
            }
            upload_report = requests.post(
                companyData.host + "api/method/upload_file",
                files=files_new,
                data=payload_new).json()
            url = upload_report['message']['file_url']
            return url
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     frappe.log_error("Ezy-invoicing holidayinnerrorbulkreprocess","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
    #     return {"success":False,"message":str(e)}   