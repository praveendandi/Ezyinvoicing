import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import traceback
import re
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


@frappe.whitelist(allow_guest = True)
def file_parsing(filepath):
    invoiceNumber = ''
    print_by = ''
    document_type = ""
    try:
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("TPV-01")
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
        reupload = False
        invoice_category = "Tax Invoice"
        for i in raw_data:
            # print(i,"*********")
            if "Account Id  " in i or "Account Id" in i and "Name" not in i:
                confirmation_number = i.split(" ")
                conf_number = confirmation_number[2]
                conf_number = conf_number.replace('PageNo','').strip()
            if "Grand Total" in i:
                total_invoice = i.split(" ")
                total_invoice_amount = float(total_invoice[-1].replace(",", ""))
                if "-" in total_invoice[-1]:
                    invoice_category = "Credit Invoice"
            # if "DEPARTURE DATE " in i:
            #     depatureDateIndex = i.split(":")[-1]
            #     depatureDate= "".join(re.findall("[0-9]{2}\/[0-9]{2}\/[0-9]{2}",depatureDateIndex))
            #     date_time_obj = datetime.datetime.strptime(depatureDate,'%d/%m/%y').strftime('%d-%b-%y %H:%M:%S')
            if "Date" in i or "Date " in i and "Invoice No" not in i:
                date_time_obj = i.split(" ")[-1].strip()
                date_time_obj = datetime.datetime.strptime(date_time_obj,'%d/%m/%Y').strftime('%d-%b-%y %H:%M:%S')
                date_time_obj = date_time_obj.strip()
            if "Room No   " in i or "Room No   " in i or "Room No   " in i:
                room = re.sub(r'[0-9]{2}\/[0-9]{2}\/[0-9]{4}','',i)
                room = room.replace("Date","")
                roomNumber = room.split()[-1]
                roomNumber = roomNumber.replace('Date','')
            # if "Room No   " in i or "Room No   " in i or "Room No   " in i:
            #     if "Date" in i:
            #         i = i.strip()
            #         room = i.split()
            #         roomNumber = room[2].strip()
            #         # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
            if "GSTIN No." in i or "GSTIN No" in i or "GSTIN No" in i:
                gstNumber = i.split(' ')[-1].replace(' ', '').replace(".","")
                gstNumber = gstNumber.replace("TAXINVOICE","").replace("No","")
            if "Invoice No " in i or "Invoice No" in i and "Date" not in i :
                inv_no = re.sub(r'[0-9]{2}\/[0-9]{2}\/[0-9]{4}','',i)
                inv_no = inv_no.replace("Date","")
                invoiceNumber = inv_no.split()[-1]
                invoiceNumber = invoiceNumber.replace('Date','').lstrip("-")
            if "Bill to" in i:
                guestDetailsEntered = True
            if "Checkout By:" in i: 
                guestDetailsEntered = False
            if guestDetailsEntered == True:
                guestDeatils.append(i)
            # if i in "Date Description Reference Debit Credit":
            entered = True
            if 'CGST 6%=' in i:
                entered = False
            if 'Billing' in i:
                entered = False
            if 'Total' in i:
                entered = False
            if entered == True:
                data.append(i)
            if "Guest Name " in i or "Guest Name " in i or "Name" in i:
                guestDeatils.append(i)
            if "Membership" in i:
                Membership = i.split(":")
                membership = Membership[-1].replace(" ", "")
            if "Printed By / On" in i:
                p = i.split(":")
                print_by = p[1].replace(" ","")

        items = [] 
        itemsort = 0
        for i in data:
            i = i.replace("  "," ")
            pattern = re.compile("^([0-9]{2}\/[0-9]{2}\/[0-9]{4})")
            check_date = re.findall(pattern, i)
            if len(check_date) > 0 and "CGST" not in i and "SGST" not in i and "CESS" not in i and "VAT" not in i and "Cess" not in i and "cess" not in i and "Vat" not in i and "IGST" not in i and "STATE GST" not in i and "CENTRAL GST" not in i and "Central GST" not in i and "State GST" not in i and "GST" not in i:
                item = dict()
                item_value = ""
                dt = i.strip()                
                for index, j in enumerate(i.split(' ')):
                    val = dt.split(" ")
                    if index == 0 and len(val)>1:
                        item['date'] = j
                    if len(val)>1:
                        item_value = val[-1]
                        item['item_value'] = float(item_value.replace(',', ''))
                    # else:
                    # 	item_value = val[-2]
                    # 	item['item_value'] = float(item_value.replace(',', ''))
                    if index == 1 and len(val)>1:
                        starting_index = i.index(j)
                        if "~" in i:
                            ending_index = i.find("~")
                            item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ").strip()
                            item["name"] = item["name"].replace("/"," ").strip()
                            item["name"] = item["name"].replace("#"," ").strip()
                            item["name"] = item["name"].replace("*"," ").strip()
                        else:
                            ending_index = i.find(item_value)
                            replace_to_one_space = i.replace("  "," ")
                            item_split = replace_to_one_space.split(" ")
                            date_index = replace_to_one_space.index(item_split[1])
                            credit_index = replace_to_one_space.index(item_split[-1])
                            item_name = replace_to_one_space[date_index+len(item_split[2]):credit_index]
                            new_item = item_name.split(" ")
                            item_name = " ".join(new_item[1:])
                            for i, c in enumerate(item_name):
                                if c.isdigit():
                                    item_name = item_name[i:]
                                    item["name"] = item_name.strip()
                                    item["name"] = item["name"].replace("/"," ").strip()
                                    item["name"] = item["name"].replace("#"," ").strip()
                                    item["name"] = item["name"].replace("*"," ").strip()
                                    result = re.sub(r'[0-9]+', '', item["name"])
                                    item["name"] = result.strip()
                                    break
                                else:
                                    item_name = item_name
                                    item["name"] = item_name.strip()
                                    item["name"] = item["name"].replace("/"," ").strip()
                                    item["name"] = item["name"].replace("#"," ").strip()
                                    item["name"] = item["name"].replace("*"," ").strip()
                                    result = re.sub(r'[0-9]+', '', item["name"])
                                    item["name"] = result.strip()

                        # else:
                        #     start_ind = i.index(val[2])
                        #     end_ind = i.index(val[-1])
                        #     name_item = i[start_ind:end_ind]
                        #     print(name_item,"?/////////////")
                        #     if val[-3].isnumeric():
                        #         name_item = name_item.replace(val[-3],"")
                        #     item["name"] = name_item.strip()
                        #     result = re.sub(r'[0-9]+','', item["name"])
                        #     item["name"] = result.strip()
                        #     item["name"] = item["name"].replace("/"," ").strip()
                        #     item["name"] = item["name"].replace("#"," ").strip()
                        #     item["name"] = item["name"].replace("*"," ").strip()
                        #     print(item["name"],"/////////////////")
                        #     # print(item["name"],":::::::::::")
                        # else:
                        #     ending_index = i.find(item_value)
                        #     name_item = i.split(" ")
                        #     if len(name_item)>6:
                        #         print(name_item,";;;;;;;;;;")
                        #         name_item = name_item[1]
                        #         item["name"] = name_item
                        #         print(item["name"],";;;;;;;;;")
                        #     # item_split = item_split.
                        #     # print(item_split,"/////////")

                    if len(val)>1:		
                        if 'SAC' in j:
                            item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                        else:
                            item['sac_code'] = "No Sac"
                    if len(val)>1:		
                        item['sort_order'] =  itemsort+1
                itemsort+=1
                if item !={}:
                    items.append(item)

        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types  = [''.join(each) for each in paymentTypes['data']]
        for each in items:
            if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "cess" not in each['name'] and "Vat" not in each["name"] and "IGST" not in each["name"] and "STATE GST" not in each["name"] and "CENTRAL GST" not in each["name"] and "Central GST" not in each["name"] and "State GST" not in each["name"] and "GST" not in each["name"]:
                if each["name"] not in payment_Types:
                    total_items.append(each)
        
        guest = dict()
        for index, i in enumerate(guestDeatils):
            if index == 0: 
                guest['name'] = i.split(':')[-1]
                guest['name'] = guest['name'].replace("PAN No.","")
                guest['name'] = guest['name'].replace("Guest Name","").replace("Name","")
                guest['name'] = guest['name'].replace("*","").strip()
                # guest['name'] = re.sub('[0-9]|[-:,]',' ',guest['name']).replace("Bill Date","").strip()
                # # guest['name'] = i.replace("BILL No.","").strip(",")
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
        guest['room_number'] = int(roomNumber) if roomNumber != '' else 0
        guest['company_code'] = "TPV-01"
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
                        update_document_bin(print_by,document_type, invoiceNumber,"Duplicate",filepath)
                        return {"Success": False,"Message":"Invoice Already Printed"}		
                else:
                    frappe.publish_realtime("custom_socket", {'message':'Duplicate Invoice','type':"Duplicate Invoice","invoice_number":inv_data.name,"company":inv_data.company})
                    update_document_bin(print_by,document_type, invoiceNumber,"Duplicate",filepath)
                    # if inv_data.qr_generated=="Pending" or inv_data.irn_generated=="Error":
                    reupload = True

        company_code = {"code":"TPV-01"}
        error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"TPV-01","invoice_date":date_time_obj}
        error_data['invoice_file'] = filepath
        error_data['guest_name'] = guest['name']
        error_data['gst_number'] = gstNumber
        if guest['invoice_type'] == "B2C":
            error_data['gst_number'] == " "
        error_data['state_code'] = ""
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
        gspApiDataResponse = gsp_api_data({"code":company_code['code'],"mode":companyCheckResponse['data'].mode,"provider":companyCheckResponse['data'].provider})
        if gspApiDataResponse['success'] == True:
            if guest['invoice_type'] == 'B2B':
                checkTokenIsValidResponse = check_token_is_valid({"code":company_code['code'],"mode":companyCheckResponse['data'].mode})
                if checkTokenIsValidResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":guest['gstNumber'],"code":company_code['code'],"invoice":guest['invoice_number'],"apidata":gspApiDataResponse['data']})
                    if getTaxPayerDetailsResponse['success'] == True:
                        sez = 1  if getTaxPayerDetailsResponse["data"].tax_type in ["SEZ","SEZ Developer","SEZ Unit"] else 0
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