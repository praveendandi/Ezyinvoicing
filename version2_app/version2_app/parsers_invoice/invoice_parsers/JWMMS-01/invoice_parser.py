import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import re
import json
import sys
import frappe
import itertools
import traceback,os
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *
from version2_app.version2_app.doctype.invoices.invoice_helpers import update_document_bin


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def file_parsing(filepath):
    invoiceNumber = ''
    print_by = ''
    document_type = ""
    try:
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("JWMMS-01")
        company = frappe.get_doc("company","JWMMS-01")
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
        checkout_date = ''
        informationInvoice = "No"
        reupload = False
        invoice_category = "Tax Invoice"
        for i in raw_data:
            # print(i,"++++++++++")
            if "INFORMATION INVOICE" in i or "I NFORMATION INVOICE" in i:
                informationInvoice = "Yes"
            if "CREDIT TAX INVOICE" in i or "CREDIT INVOICE" in i:
                invoice_category = "Credit Invoice"
            if "Confirmation No" in i or "Confirmation no.  " in i or "Confirmation No  " in i:
                confirmation_number = i.split(":")
                conf_number = confirmation_number[-1].replace(" ", "")
            if "Total" in i:
                total_invoice = i.split(" ")
                total_invoice_amount = float(total_invoice[-2].replace(",", ""))
                if "-" in total_invoice[-2]:
                    invoice_category = "Credit Invoice"
            # if "JW Marriott Hotel Mumbai Sahar" in i:
            #     ind = raw_data.index(i)
            #     dateobj = raw_data[ind-1]
            #     date_time_obj = datetime.datetime.strptime(dateobj,'%d-%b-%y').strftime('%d-%b-%y %H:%M:%S')
            if  "JW Marriott Hotel Mumbai Sahar" in i:
                ind = raw_data.index(i)
                dateobj = raw_data[ind-1]
                try:
                    date_time_obj = datetime.datetime.strptime(dateobj, '%d-%m-%y').strftime('%d-%b-%y %H:%M:%S')
                except ValueError:
                    try:
                        date_time_obj = datetime.datetime.strptime(dateobj, '%d-%b-%y').strftime('%d-%b-%y %H:%M:%S')
                    except ValueError:
                        # Handle the case when both formats fail to parse the date
                        print("Invalid date format:", dateobj)
                        date_time_obj = None
                        
            if "Departure   :" in i:
                depatureDateIndex = i.index('Departure')
                checkout_date = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
                if checkout_date == '':
                    checkout_date = None
                else:
                    checkout_date = datetime.datetime.strptime(checkout_date,'%d-%m-%y').strftime('%d-%b-%y %H:%M:%S')
            if "Room  :" in i and "Room  :" in i:
                room = i.split(":")
                roomNumber = room[-1]
                # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
            
            # if "GST No." in i and "Hotel" not in i and "PAN" not in i:
            #     if company.only_b2c == "No":
            #         gstNumber = i.split(':')[-1].replace(' ', '')
            #         # if "ConfirmationNo." in gstNumber:
            #         gstNumber = gstNumber.replace("ConfirmationNo.","")
            #         gstNumber = gstNumber.replace("Membership","")
            #     else:
            #         gstNumber = ""
            
            if "GST No.   :" in i or "GST No.               :" in i and "Hotel" not in i and "PAN" not in i:
                gstNumber = i.split(':')[1].replace(' ', '')
                gstNumber = gstNumber.replace("ConfirmationNo.","")
                gstNumber = gstNumber.replace("Membership","").replace("WindowNo.","").strip()
            if "Invoice No  :" in i:
                invoiceNumber = i.split(':')[-1].replace(" ","")
                invoiceNumber = invoiceNumber.strip()
            if "Bill To" in i:
                guestDetailsEntered = True
            if "Checkout By:" in i:
                guestDetailsEntered = False
            if guestDetailsEntered == True:
                guestDeatils.append(i)
            entered = True
            if 'CGST 6%=' in i:
                entered = False
            if 'Billing' in i:
                entered = False
            if 'Total' in i:
                entered = False
            if entered == True:
                data.append(i)
            if "Guest Name         :" in i or "Guest Name " in i:
                guestDeatils.append(i)
            if "Membership" in i:
                Membership = i.split(":")
                membership = Membership[-1].replace(" ", "")
            if "Cashier" in i:
                p = i.split(":")
                print_by = p[1].replace(" ","")


        items = [] 
        itemsort = 0
        for i in data:
            i = i.replace("  "," ")
            pattern = re.compile("^([0-9]{2}\-[0-9]{2}\-[0-9]{2})+")
            check_date = re.findall(pattern, i)
            dt = i.strip()
            split_str = dt.split(" ")[-1]
            if len(check_date) > 0 and "." in split_str:
                item = dict()
                item_value = ""
                for index, j in enumerate(i.split(' ')):
                    if index == 0:
                        item['date'] = j
                    val = dt.split(" ")
                    if val != "":
                        item_value = val[-1]
                        item['item_value'] = float(item_value.replace(',', ''))
                    else:
                        item_value = val[-2]
                        item['item_value'] = float(item_value.replace(',', ''))
                    if index == 1:
                        starting_index = i.index(j)
                        if "~" in i:
                            ending_index = i.find("~")
                            item["name"] = (i[starting_index:ending_index]).strip()
                        else:
                            ending_index = i.find(item_value)
                            item["name"] = (i[starting_index:ending_index]).strip()
                    if 'SAC' in j:
                        item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                    else:
                        item['sac_code'] = "No Sac"
                    item['sort_order'] =  itemsort+1
                itemsort+=1
                items.append(item)

        # total_items = []
        # paymentTypes = GetPaymentTypes()
        # payment_Types  = [''.join(each) for each in paymentTypes['data']]
        # company = frappe.get_doc("company","JWMMS-01")
        # for each in items:
        #     if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"]:
        #         if company.only_b2c == "No":
        #             if each["name"] not in payment_Types:
        #                 total_items.append(each)
        #         else:
        #             items = {'date':each["date"],'item_value':each['item_value'],'item_name':each['name'],'sort_order':each["sort_order"],"sac_code":"No Sac","doctype":"Items","item_type":"SAC","cgst": 0,"sgst": 0,
        #                 "igst": 0,"item_taxable_value":each["item_value"],"gst_rate":0,"item_value_after_gst":each["item_value"],"cess":0,"cess_amount":0,"state_cess":0,"state_cess_amount":0,"cgst_amount":0,"sgst_amount":0,"igst_amount":0,"parent":invoiceNumber,
        #                 "parentfield":"items","parenttype":"invoices","sac_code_found":"Yes","other_charges":0,"vat_amount":0,"vat":0.0,"unit_of_measurement":"OTH","quantity":1,"unit_of_measurement_description":"OTHERS",
        #                 "is_service_charge_item":"No","sac_index":"1","line_edit_net":"No","item_reference":"","other_charges":0,"taxable":"No","item_mode":"Debit" if "-" not in str(each["item_value"]) else "Credit","item_type":"SAC","description":each['name'],"type":"Non-Gst"}
        #             total_items.append(items)
        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types  = [''.join(each) for each in paymentTypes['data']]
        for each in items:
            if each["name"] != "":
                if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"] and "UTGST" not in each["name"] and "[Add: udf.]" not in each["name"]:
                    if each["name"] not in payment_Types:
                        total_items.append(each)

        guest = dict()		
        for index, i in enumerate(guestDeatils):
            if index == 0:
                guest['name'] = i.split(':')[1].replace("Guest Name :","")
                guest['name'] = i.split(':')[1].replace("Cashier","").strip()
                guest['name'] = guest['name'].replace("InvoiceNo","").strip()
            if index == 1:
                guest['address1'] = i
            if index == 2:
                guest['address2'] = i

        


        guest['invoice_number'] = invoiceNumber.replace(' ', '')

        guest['membership'] = membership
        guest['invoice_date'] = date_time_obj
        guest['items'] = total_items
        guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
        guest['gstNumber'] = gstNumber
        guest['room_number'] = int(roomNumber) if roomNumber != "" else 0
        guest['company_code'] = "JWMMS-01"
        guest['confirmation_number'] = conf_number
        guest['start_time'] = str(start_time)
        guest['print_by'] = print_by
        guest['invoice_category'] = invoice_category
        guest['checkout_date'] = checkout_date if checkout_date != '' else None

        if companyCheckResponse['data'].pms_information_invoice_for_payment_qr == "Yes" and informationInvoice == "Yes":
            if informationInvoice == "Yes":
                information_data={"confirmation_no":guest['confirmation_number'],"room_no":guest["room_number"],"guest_name":guest['name'].strip(),"doctype":"Information Invoices","document":filepath}
                doc = frappe.get_doc(information_data)
                doc.insert(ignore_permissions=True, ignore_links=True)
                socket = frappe.publish_realtime("custom_socket", {'message':'Information Invoice Created','data':information_data,"company":"WMGC-01"})
                return {"success": True,"data":information_data}
                
        else:
            if informationInvoice == "No":
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


                company_code = {"code":"JWMMS-01"}
                error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"JWMMS-01","invoice_date":date_time_obj,"checkout_date":checkout_date if checkout_date != '' else None}
                error_data['invoice_file'] = filepath
                error_data['guest_name'] = guest['name']
                error_data['gst_number'] = gstNumber
                if guest['invoice_type'] == "B2C":
                    error_data['gst_number'] == " "
                error_data['state_code'] = " "
                error_data['room_number'] = guest['room_number']
                error_data['pincode'] = ""
                error_data['total_invoice_amount'] = total_invoice_amount
                # gstNumber = "12345"
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
                # if company.only_b2c == "Yes":
                #     taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
                #     if reupload == False:
                #         guest['invoice_file'] = filepath
                #         insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":total_items,"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer,"sez":0})
                #         if insertInvoiceApiResponse['success']== True:
                #             print("B2C Invoice Created",insertInvoiceApiResponse)
                #             return {"success":True,"message":"Invoice Created"}
                #         else:
                #             return {"success":False,"message":"Invoice"}
                #     else:
                #         guest['invoice_file'] = filepath
                #         insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":total_items,"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer,"sez":0})
                #         if insertInvoiceApiResponse['success']== True:
                #             print("B2C Invoice Created",insertInvoiceApiResponse)
                #             return {"success":True,"message":"Invoice Created"}
                #         else:
                #             return {"success":False,"message":"Invoice"}
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
                                            error_data["sez"] = sez
                                            error_data["items_data"]=calulateItemsApiResponse['data']
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
            else:
                return {"success":False,"message":"Dont have rights to print Information Invoice"}
    except Exception as e:
        print(traceback.print_exc())
        update_document_bin(print_by,document_type,"",str(e),filepath)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoice_parser","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def invoiceNumberMethod(invoiceNumber):
    invoiceNumber = "3967-"+invoiceNumber
    return invoiceNumber