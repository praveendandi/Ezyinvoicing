import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import re
import json
import sys
import frappe
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist()
def reinitiateInvoice(data):
    try:
        filepath = data['filepath']
        reupload_inv_number = data['invoice_number']
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("HPHYD-01")
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
        invoice_category = "Tax Invoice"
        banquet = False
        taxinvoice = False
        if "BANQUET INVOICE" in raw_data or " B A N Q U E T  B I L L" in raw_data or "B A N Q U E T  INVOICE" in i:
            banquet = True   
        else:
            taxinvoice = True
            
        if banquet:
            for i in raw_data:
                # print(i,"++++++++++++")
                if "Bill Date :" in i:
                    date_time_obj = i.split(":")[-1].strip()
                    # date_time_obj = re.split(r" ",date_time_obj)[0]
                    date_time_obj = datetime.datetime.strptime(date_time_obj,'%d/%m/%y').strftime('%d-%b-%y %H:%M:%S')
                    item_date = datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%Y-%m-%d')
                    invoice_date = item_date
                    invoice_date = datetime.datetime.strptime(invoice_date,'%Y-%m-%d').strftime('%y%m')
                    invoiceNumber = invoice_date + invoiceNumber
                if "Reservation No " in i or "Reservation No :" in i:
                    confirmation_number = i.split(":")
                    conf_number = confirmation_number[1].replace(" ", "").replace("BillNo","")
                    # conf_number = confirmation_number[-2].replace(" ", "").replace("Bill No","")
                if "Net Amount :" in i or "Net Amount " in i:
                    # print(i.split(" "))
                    total_invoice = i.split(":")
                    total_invoice_amount = float(total_invoice[-1].strip().replace(",", ""))

                if "Room No" in i or "Res No #" in i or "Room No. " in i:
                    room = i.split(":")
                    roomNumber = room[-1]
                    # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
                if "Guest GSTN # " in i or "Guest GSTN # :" in i:
                    gstNumber = i.split(':')[1].replace(' ', '')
                    gstNumber = gstNumber.replace("GSTNBillNo","")
                    gstNumber = gstNumber.replace("FSSAINO","").strip()
                    print(gstNumber)
                if "Bill No " in i or "Bill No :" in i:
                    invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "").strip()
                    
                if "Bill To" in i:
                    guestDetailsEntered = True
                if "Checkout By:" in i:
                    guestDetailsEntered = False
                if guestDetailsEntered == True:
                    guestDeatils.append(i)
                # if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit":
                entered = True
                if 'CGST 6%=' in i:
                    entered = False
                if 'Billing' in i:
                    entered = False
                if 'Sub Total ' in i:
                    entered = False
                entered = True    
                if entered == True:
                    data.append(i)
                if "Guest Name " in i:
                    guestDeatils.append(i)
                if "Membership" in i:
                    Membership = i.split(":")
                    membership = Membership[-1].replace(" ", "")
                if "Printed By / On" in i:
                    print_by = i.split(":")
                    print_by = print_by[1].replace(" ","")
                    
        if taxinvoice:     
            for i in raw_data:
                # print(i,"*********")
                if "REG NO. " in i:
                    confirmation_number = i.split(":")
                    conf_number = confirmation_number[-1].replace(" ", "").strip()
                    conf_number = conf_number.replace('PageNo','').strip()
                if ("GRAND TOTAL" in i and "GRAND TOTAL" in i ) and "DAY TOTAL" not in i:
                    # print(i.split(),"///////")
                    total_invoice = i.split()
                    total_invoice_amount = float(total_invoice[2].replace(",", ""))
                    print(total_invoice_amount,"totallllllllll")
                if "Departure:" in i:
                    depatureDateIndex = i.split()[-2]
                    date_time_obj = datetime.datetime.strptime(depatureDateIndex,'%d/%m/%Y').strftime('%d-%b-%y %H:%M:%S')
                if "ROOM NO  " in i or "ROOM NO  :" in i:
                    if ":" in i:
                        room = i.split(":")
                        roomNumber = room[-1].strip()
                        # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
                    else:
                        room = i.split(" ")
                        roomNumber = room[-1].strip()
                if "GSTIN NO " in i:
                    gstNumber = i.split(':')[1].replace(' ', '')
                    gstNumber = gstNumber.replace("TAXINVOICE","")
                if "Bill No  " in i:
                    invoiceNumber = i.split(":")
                    invoiceNumber = invoiceNumber[-1].replace('/','').strip()
                    item_date = datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%y%m')
                    invoiceNumber = item_date + invoiceNumber
                if "Bill to" in i:
                    guestDetailsEntered = True
                if "Folio No." in i:
                    guestDetailsEntered = False
                # if guestDetailsEntered == True:
                #     guestDeatils.append(i)
                # if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit":
                entered = True
                if 'CGST 6%=' in i:
                    entered = False
                if 'Billing' in i:
                    entered = False
                if 'Total' in i:
                    entered = False
                entered = True
                if entered == True:
                    data.append(i)
                if "ROOM NO  " in i:
                    guestDeatils.append(i)
                if "Membership" in i:
                    Membership = i.split(":")
                    membership = Membership[-1].replace(" ", "")
                if "Printed By / On" in i:
                    print_by = i.split(":")
                    print_by = print_by[1].replace(" ","")


        check_invoice = check_invoice_exists(invoiceNumber)
        if check_invoice['success']==True:
            inv_data = check_invoice['data']
            invoiceNumber = inv_data.name
            if inv_data.change_gst_number == "No":
                gstNumber = inv_data.gst_number
        if invoiceNumber != reupload_inv_number:
            return {"success":False,"message":"Incorrect Invoice Attempted"}

        items = [] 
        itemsort = 0
        for i in data:
            if not banquet:
                # i = i.replace("  "," ")
                i =i.strip()
                pattern = re.compile("^([0-9]{2}\/[0-9]{2}\/[0-9]{2})")
                check_date = re.findall(pattern, i)
                if len(check_date) > 0 and "DAY TOTAL" not in i:
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
                            else:
                                ending_index = i.find(item_value)
                                item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ").strip() 
                            test_val=re.sub("[0-9]|[.,]","", item["name"])
                            if test_val:
                                item["name"]=test_val.strip()
                            # else:
                            #     item["name"]=item["name"].strip()
                        if len(val)>1:		
                            if 'SAC' in j:
                                item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                            else:
                                item['sac_code'] = "No Sac"
                        if len(val)>1:		
                            item['sort_order'] =  itemsort+1       
                    if item !={}:
                        items.append(item)
                        
            else:
                # print(i,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                split_i = i.split(" ")
                if len(split_i)>0:
                    pattern = re.compile("^([0-9])+")
                    check_date = re.findall(pattern, split_i[0])
                    if len(check_date) > 0:
                        item = dict()
                        item_value = ""
                        dt = i.strip()                
                        for index, j in enumerate(i.split(' ')):
                            val = dt.split(" ")
                            split_str = i.split(" ")
                            if len(split_str)>1:	
                                item['date'] = datetime.datetime.strptime(item_date,'%Y-%m-%d').strftime(companyCheckResponse['data'].invoice_item_date_format) 
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
                                    else:
                                        ending_index = i.find(item_value)
                                        item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ").strip() 
                                    test_val=re.sub("[0-9]|[.,]","", item["name"])
                                    if test_val:
                                        item["name"]=test_val.strip()
                                    # else:
                                    #     item["name"]=item["name"].strip()
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
            if each["name"] != "":
                if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "cess" not in each['name'] and "Vat" not in each["name"] and "IGST" not in each["name"] and "STATE GST" not in each["name"] and "CENTRAL GST" not in each["name"] and "Central GST" not in each["name"] and "State GST" not in each["name"]:
                    if each["name"] not in payment_Types:
                        total_items.append(each)
        guest = dict()
        # print(guestDeatils)
        for index, i in enumerate(guestDeatils):
            if index == 0:
                if banquet:
                    # guest['name'] = i.split(':')[1].replace("Bill Date & Time ","").strip()
                    guest['name'] = i.split(':')[1].replace("Bill Date ","").strip()
                else:
                    guest['name'] = i.split(':')[0]
                    # guest['name'] = re.sub('[0-9]|[-:,]',' ',guest['name']).replace("BILL No.","").strip()
                    guest['name'] = guest['name'].replace("ROOM NO","").strip()
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
        guest['company_code'] = "HPHYD-01"
        guest['confirmation_number'] = conf_number
        guest['start_time'] = str(start_time)
        guest['print_by'] = print_by
        guest['invoice_category'] = invoice_category

        check_invoice = check_invoice_exists(guest['invoice_number'])
        if check_invoice['success']==True:
            inv_data = check_invoice['data']
            if inv_data.docstatus==2:
                amened='Yes'
            else:
                invoiceNumber = inv_data.name
                guest['invoice_number'] = inv_data.name
                amened='No'
        
        company_code = {"code":"HPHYD-01"}
        error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"HPHYD-01","invoice_date":date_time_obj}
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
                        calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format})
                        if calulateItemsApiResponse['success'] == True:
                            guest['invoice_file'] = filepath
                            insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
                            if insertInvoiceApiResponse['success']== True:
                                print("Invoice Created",insertInvoiceApiResponse)
                                return {"success":True,"message":"Invoice Created"}
                            else:
                                
                                error_data['error_message'] = insertInvoiceApiResponse['message']
                                error_data['amened'] = amened
                                errorInvoice = Error_Insert_invoice(error_data)
                                print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                                return {"success":False,"message":insertInvoiceApiResponse['message']}
                        else:
                            
                            error_data['error_message'] = calulateItemsApiResponse['message']
                            error_data['amened'] = amened
                            errorInvoice = Error_Insert_invoice(error_data)
                            print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'],"***********")
                            return {"success":False,"message":calulateItemsApiResponse['message']}
                    else:
                        # itsindex = getTaxPayerDetailsResponse['message']['message'].index("'")
                        error_data['error_message'] = getTaxPayerDetailsResponse['message']
                        error_data['amened'] = amened
                        errorInvoice = Error_Insert_invoice(error_data)
                        return {"success":False,"message":getTaxPayerDetailsResponse['message']}                        
                else:
                    # itsindex = checkTokenIsValidResponse['message']['message'].index("'")
                    error_data['error_message'] = checkTokenIsValidResponse['message']
                    error_data['amened'] = amened
                    errorInvoice = Error_Insert_invoice(error_data)
                    return {"success":False,"message":checkTokenIsValidResponse['message']} 
            else:
                
                taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}


                calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format})
                if calulateItemsApiResponse['success'] == True:
                    guest['invoice_file'] = filepath
                    insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer})
                    if insertInvoiceApiResponse['success']== True:
                        print("B2C Invoice Created",insertInvoiceApiResponse)
                        return {"success":True,"message":"Invoice Created"}
                    else:
                        
                        error_data['error_message'] = insertInvoiceApiResponse['message']
                        error_data['amened'] = amened
                        errorInvoice = Error_Insert_invoice(error_data)
                        print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                        return {"success":False,"message":insertInvoiceApiResponse['message']}
                else:
                            
                    error_data['error_message'] = calulateItemsApiResponse['message']
                    error_data['amened'] = amened
                    errorInvoice = Error_Insert_invoice(error_data)
                    print("B2C calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
                    return {"success":False,"message":calulateItemsApiResponse['message']}	
        else:
            error_data['error_message'] = gspApiDataResponse['message']
            error_data['amened'] = amened
            errorInvoice = Error_Insert_invoice(error_data)
            print("gspApiData fialed:  ",gspApiDataResponse['message'])
            return {"success":False,"message":gspApiDataResponse['message']}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing reinitiate_parser","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
