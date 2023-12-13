import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import traceback,sys,os
import re,os
import json
import sys
import frappe
import itertools
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *
from version2_app.version2_app.doctype.invoices.invoice_helpers import update_document_bin


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist()
def file_parsing(filepath):
    invoiceNumber = ''
    print_by = ''
    document_type = ""
    try:
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("BHGCCH-01")
        site_folder_path = companyCheckResponse['data'].site_name
        file_path = folder_path+'/sites/'+site_folder_path+filepath
        today = date.today()
        invoiceDate = today.strftime("%Y-%m-%d")
        content = []
        with pdfplumber.open(file_path) as pdf:
            count = len(pdf.pages)
            for index in range(count):
                first_page = pdf.pages[index]
                content.append(first_page.extract_text())

        raw_data = []
        for i in content:
            for j in i.splitlines():
                raw_data.append(j)
        reupload= False
        data = []
        amened = ''
        entered = False
        guestDetailsEntered = False
        guestDeatils = []
        invoiceNumber = ''
        gstNumber = ''
        date_time_obj = ''
        total_invoice_amount = ''
        conf_number = ''
        membership = ''
        print_by = ''
        roomNumber = ""
        invoice_category = "Tax Invoice"
        guest = dict()
        start_ind = 0
        end_index = 0
        itemdate = ""
        for ind,i in enumerate(raw_data):
            if "Item Description" in i:
                start_ind = ind
            if "Sub Total" in i:
                end_index = ind    
            if "Total Amount" in i:
                total_invoice = i.split(" ")
                total_invoice_amount = float(total_invoice[-1].replace(",", ""))

            if "Course :" in i:
                dateobj = i.split(' ')[-3].strip()
                itemdate = dateobj
                date_time_obj = datetime.datetime.strptime(dateobj,'%d/%m/%Y').strftime('%d-%b-%y %H:%M:%S')
            if "Ref :" in i:
                invoiceNumber = i.split(' ')[2] 
            if "User :" in i:
                name = i.split(':')[-1]
                guest['name'] = name
                guest['address1'] = ""
                guest['address2'] = ""
            if ind>start_ind and start_ind!=0:
                data.append(i)
            
        # print(start_ind,end_index,data)
        print(itemdate)
        items = [] 
        itemsort = 0
        for i in data:
            item={}
            if "Sub Total" in i:
                break
            else: 
                i = i.split(" ")
                print(i)  
                item['date'] = itemdate
                item['name'] = " ".join(i[0:len(i)-3])
                item['item_value'] = float(i[-1].replace(",", ""))
                item['sac_code'] = "No Sac"
                item['sort_order'] =  itemsort+1
                itemsort+=1
                items.append(item)
        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types  = [''.join(each) for each in paymentTypes['data']]
        for each in items:
            if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"]:
                if each["name"] not in payment_Types:
                    total_items.append(each)

        guest['invoice_number'] = invoiceNumber.replace(' ', '')

        guest['membership'] = membership
        guest['invoice_date'] = date_time_obj
        guest['items'] = total_items
        guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
        guest['gstNumber'] = gstNumber
        guest['room_number'] = int(roomNumber) if roomNumber != "" else 0
        guest['company_code'] = "BHGCCH-01"
        guest['confirmation_number'] = conf_number
        guest['start_time'] = str(start_time)
        guest['print_by'] = print_by
        guest['invoice_category'] = invoice_category


        check_invoice = check_invoice_exists(guest['invoice_number'])
        if check_invoice['success']==True:
            inv_data = check_invoice['data']
            # print(inv_data.__dict__)
            if inv_data.docstatus==2:
                amened='Yes'
            else:
                invoiceNumber = inv_data.name
                guest['invoice_number'] = inv_data.name
                amened='No'
                if inv_data.invoice_type == "B2B":
                    if inv_data.irn_generated=="Pending" or inv_data.irn_generated == "Error":
                        reupload = True
                    else:
                        frappe.publish_realtime("custom_socket", {'message':'Duplicate Invoice','type':"Duplicate Invoice","invoice_number":inv_data.name,"company":inv_data.company})
                        update_document_bin(print_by,document_type,"","Duplicate",filepath)
                        return {"Success": False,"Message":"Invoice Already Printed"}		
                else:
                    frappe.publish_realtime("custom_socket", {'message':'Duplicate Invoice','type':"Duplicate Invoice","invoice_number":inv_data.name,"company":inv_data.company})
                    update_document_bin(print_by,document_type,"","Duplicate",filepath)
                    # if inv_data.qr_generated=="Pending" or inv_data.irn_generated=="Error":
                    reupload = True

        company_code = {"code":"BHGCCH-01"}
        error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"BHGCCH-01","invoice_date":date_time_obj}
        error_data['invoice_file'] = filepath
        error_data['guest_name'] = guest['name']
        error_data['gst_number'] = gstNumber
        if guest['invoice_type'] == "B2C":
            error_data['gst_number'] == " "
        error_data['state_code'] = "36"
        error_data['room_number'] = guest['room_number']
        error_data['pincode'] = "500082"
        error_data['total_invoice_amount'] = total_invoice_amount
        # print(guest['invoice_number'])

        if len(gstNumber) < 15 and len(gstNumber)>0:
            error_data['invoice_file'] = filepath
            error_data['error_message'] = "Invalid GstNumber"
            error_data['amened'] = amened
            
            errorcalulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format})
            if errorcalulateItemsApiResponse['success'] == True:
                error_data['items_data'] = errorcalulateItemsApiResponse['data']
            errorInvoice = Error_Insert_invoice(error_data)
            print("Error:  *******The given gst number is not a vaild one**********")
            return {"success":False,"message":"Invalid GstNumber"}



        


        print(json.dumps(guest, indent = 1))
        gspApiDataResponse = gsp_api_data({"code":company_code['code'],"mode":companyCheckResponse['data'].mode,"provider":companyCheckResponse['data'].provider})
        if gspApiDataResponse['success'] == True:
            if guest['invoice_type'] == 'B2B':
                checkTokenIsValidResponse = check_token_is_valid({"code":company_code['code'],"mode":companyCheckResponse['data'].mode})
                if checkTokenIsValidResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":guest['gstNumber'],"code":company_code['code'],"invoice":guest['invoice_number'],"apidata":gspApiDataResponse['data']})
                    if getTaxPayerDetailsResponse['success'] == True:
                        sez = 1 if getTaxPayerDetailsResponse["data"].tax_type in ["SEZ","SEZ Developer","SEZ Unit"] else 0
                        calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"sez":sez})
                        if calulateItemsApiResponse['success'] == True:
                            guest['invoice_file'] = filepath
                            if reupload == False:
                                insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"sez":sez})
                                if insertInvoiceApiResponse['success']== True:
                                    print("Invoice Created",insertInvoiceApiResponse)
                                    return {"success":True,"message":"Invoice Created"}
                        
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['amened'] = amened
                                    error_data["items_data"]=calulateItemsApiResponse['data']
                                    error_data["sez"] = sez
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                                    update_document_bin(print_by,document_type,"",error_data['error_message'],filepath)
                                    return {"success":False,"message":insertInvoiceApiResponse['message']}
                            else:
                                insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"sez":sez})
                                if insertInvoiceApiResponse['success']== True:
                                    print("Invoice Created",insertInvoiceApiResponse)
                                    return {"success":True,"message":"Invoice Created"}
                        
                                else:
                                    error_data['error_message'] = insertInvoiceApiResponse['message']
                                    error_data['amened'] = amened
                                    error_data["sez"] = sez
                                    error_data["items_data"]=calulateItemsApiResponse['data']
                                    errorInvoice = Error_Insert_invoice(error_data)
                                    print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                                    update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                                    return {"success":False,"message":insertInvoiceApiResponse['message']}

                        else:
                            
                            error_data['error_message'] = calulateItemsApiResponse['message']
                            error_data['amened'] = amened
                            error_data["sez"] = sez
                            errorInvoice = Error_Insert_invoice(error_data)
                            print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
                            update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                            return {"success":False,"message":calulateItemsApiResponse['message']}
                    else:
                        # print(error_data)
                        error_data['error_message'] = getTaxPayerDetailsResponse['message']
                        error_data['amened'] = amened
                        errorInvoice = Error_Insert_invoice(error_data)
                        update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                        return {"success":False,"message":getTaxPayerDetailsResponse['message']}                        
                else:
                    # itsindex = checkTokenIsValidResponse['message']['message'].index("'")
                    error_data['error_message'] = checkTokenIsValidResponse['message']
                    error_data['amened'] = amened
                    errorInvoice = Error_Insert_invoice(error_data)
                    update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                    return {"success":False,"message":checkTokenIsValidResponse['message']} 
            else:
                taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}


                calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"sez":0})
                if calulateItemsApiResponse['success'] == True:
                    guest['invoice_file'] = filepath
                    if reupload == False:
                        insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer,"sez":0})
                        if insertInvoiceApiResponse['success']== True:
                            print("B2C Invoice Created",insertInvoiceApiResponse)
                            return {"success":True,"message":"Invoice Created"}
                        else:
                            
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['amened'] = amened
                            errorInvoice = Error_Insert_invoice(error_data)
                            print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                            update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                            return {"success":False,"message":insertInvoiceApiResponse['message']}
                    else:
                        insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer,"sez":0})
                        if insertInvoiceApiResponse['success']== True:
                            print("B2C Invoice Created",insertInvoiceApiResponse)
                            return {"success":True,"message":"Invoice Created"}
                        else:
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            error_data['amened'] = amened
                            errorInvoice = Error_Insert_invoice(error_data)
                            print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                            update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                            return {"success":False,"message":insertInvoiceApiResponse['message']}

                else:
                            
                    error_data['error_message'] = calulateItemsApiResponse['message']
                    error_data['amened'] = amened
                    errorInvoice = Error_Insert_invoice(error_data)
                    print("B2C calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
                    update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
                    return {"success":False,"message":calulateItemsApiResponse['message']}		
        else:
            error_data['error_message'] = gspApiDataResponse['message']
            error_data['amened'] = amened
            errorInvoice = Error_Insert_invoice(error_data)
            print("gspApiData fialed:  ",gspApiDataResponse['message'])
            update_document_bin(print_by,document_type,invoiceNumber,error_data['error_message'],filepath)
            return {"success":False,"message":gspApiDataResponse['message']}
    except Exception as e:
        print(traceback.print_exc())
        update_document_bin(print_by,document_type,"",str(e),filepath)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoice_parser","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
        


