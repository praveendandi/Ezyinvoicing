import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import re
import json
import traceback
import sys
import frappe
import itertools
import io, os
from PIL import Image
import pytesseract
from wand.image import Image as wi
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import *
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()
os.environ['OMP_THREAD_LIMIT'] = '1'
cid_issue = True

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"
@frappe.whitelist(allow_guest=True)
def cidToChar(cidx):
    return chr(int(re.findall(r'\(cid\:(\d+)\)',cidx)[0]) + 29) 




@frappe.whitelist(allow_guest=True)
def reinitiateInvoice(data):
    try:
        imgBlobs=[]
        extracted_text=[]
        filepath = data['filepath']
        reupload_inv_number = data['invoice_number']
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("HEHHC-01")
        site_folder_path = companyCheckResponse['data'].site_name
        file_path = folder_path+'/sites/'+site_folder_path+filepath
        today = date.today()
        invoiceDate = today.strftime("%Y-%m-%d")
        content = []
        with pdfplumber.open(file_path) as pdf:
            count = len(pdf.pages)
            for index in range(count):
                first_page = pdf.pages[index]
                print(first_page.extract_text())
                if cid_issue == True:
                    cid_text = first_page.extract_text()
                    final_data = ''
                    for x in cid_text.split('\n'):
                        if x != '' and x != '(cid:3)':         # merely to compact the output
                            abc = re.findall(r'\(cid\:\d+\)',x)
                            if len(abc) > 0:
                                for cid in abc: x=x.replace(cid, cidToChar(cid))
                            final_data += repr(x).strip("'") + "\n"
                    content.append(final_data)
                else:
                    content.append(first_page.extract_text())

        raw_data = []
        for i in content:
            for j in i.splitlines():
                raw_data.append(j)
        # pdf=wi(filename=file_path,resolution=300)
        # pdfImg=pdf.convert('jpeg')
        # raw_data = []
        # # for i in content:
        # imgBlobs=[]
        # # extracted_text=[]
        # for img in pdfImg.sequence:
        #     page=wi(image=img)
        #     imgBlobs.append(page.make_blob('jpeg'))

        # for imgBlob in imgBlobs:
        #     im=Image.open(io.BytesIO(imgBlob))
        #     text=pytesseract.image_to_string(im,lang='eng',config='--psm 6')
        #     extracted_text.append(text)


        # for i in extracted_text:
        #     for j in i.splitlines():
        #         raw_data.append(j)

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
        for i in raw_data:
            print(i,"///////////")
            if "Conf. No." in i:
                confirmation_number = i.split(" ")
                conf_number = confirmation_number[-1].replace(" ", "")
            if "Total" in i and "Total Value" not in i and "INR" not in i:
                total_invoice = i.split(" ")
                total_invoice_amount = float(total_invoice[-2].replace(",", ""))
            if "Invoice Date" in i:
                depatureDateIndex = i.index('Invoice Date')
                date_time_obj = ((i[depatureDateIndex:]).replace("Invoice Date","")).strip()
                date_time_obj = datetime.datetime.strptime(date_time_obj, '%Y-%m-%d').strftime("%d-%b-%y %H:%M:%S")
            if "Room No." in i:
                i = i.strip()
                room = i.split(" ")
                roomNumber = room[-1]
                # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
            if "GSTIN / UIN:" in i or "GSTIN/UIN:" in i:
                i = i.replace("GST ","")
                gstNumber = (i.split(':')[1]).split(" ")[1]
                gstNumber = (gstNumber.replace("Arrival","")).strip()
                gstNumber = gstNumber.replace('@','')
                gstNumber = gstNumber.replace("Departure","")
                # if len(gstNumber) > 0:
                #     if gstNumber[0]=='o' or gstNumber[0]=='O':
                #         gstNumber = '0'+gstNumber[1:]
                # if len(gstNumber) == 15:
                #     gstNumber = gstNumber
                #     if re.match("^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",gstNumber):
                #         gstNumber = gstNumber
                #     else:
                #         gstNumber = ""
                # else:
                #     gstNumber = ""
                gstNumber = gstNumber.strip()
                if len(gstNumber) == 15:
                    gstNumber = gstNumber
                    state_code = gstNumber[:2]
                    pan_char = gstNumber[2:7].replace("0","Q")
                    pan_num = gstNumber[7:11]
                    single_char = gstNumber[11].replace("0","Q")
                    remaining_str = gstNumber[12:]
                    gstNumber = state_code+pan_char+pan_num+single_char+remaining_str
                    if re.match("\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}",gstNumber):
                        gstNumber = gstNumber
                    else:
                        gstNumber = ""
                else:
                    gstNumber = ""
            if "Invoice No." in i:
                invoiceNumber = (i.split(' ')[-1]).replace(" ", "")
                if "l" in invoiceNumber:
                    invoiceNumber = invoiceNumber.replace("l","")
                if "--" in invoiceNumber:
                    invoiceNumber = invoiceNumber.replace("--","-I-")
                # invoiceNumber = invoiceNumber.replace("O","")
                # invoiceNumber = invoiceNumber.replace("|","I")
                # invoiceNumber = invoiceNumber.replace("o","")

            if "Bill To" in i:
                guestDetailsEntered = True
            if "Checkout By:" in i:
                guestDetailsEntered = False
            if guestDetailsEntered == True:
                guestDeatils.append(i)
            if i in "Date Description Reference Debit Credit":
                entered = True
            entered = True	
            if 'CGST 6%=' in i:
                entered = False
            if 'Billing' in i:
                entered = False
            if 'Total' in i:
                entered = False
            if entered == True:
                data.append(i)
            if "GUEST NAME:" in i:
                guestDeatils.append(i)
            if "Membership" in i:
                Membership = i.split(":")
                membership = Membership[-1].replace(" ", "")
            if "Cashier" in i and "GSA/Cashier" not in i:
                p = i.index('Cashier')
                print_by = ((i[p:]).replace("Cashier","")).strip()

        check_invoice = check_invoice_exists(invoiceNumber)
        if check_invoice['success']==True:
            inv_data = check_invoice['data']
            invoiceNumber = inv_data.name
            if inv_data.change_gst_number == "No" and inv_data.invoice_type=="B2B":
                gstNumber = inv_data.gst_number
            if inv_data.change_gst_number == "No" and inv_data.invoice_type=="B2C":
                gstNumber = ''
        if invoiceNumber != reupload_inv_number:
            return {"success":False,"message":"Incorrect Invoice Attempted"}

        items = [] 
        itemsort = 0
        for i in data:
            i = i.strip()
            pattern = re.compile("^([0-9]{4}|[0-9]{2})[./-]([0]?[1-9]|[1][0-2])[./-]([0]?[1-9]|[1|2][0-9]|[3][0|1])+")
            check_date = re.findall(pattern, i)
            if len(check_date) > 0 and "CGST" not in i and "SGST" not in i and "CESS" not in i and "VAT" not in i and "Cess" not in i and "Vat" not in i and "IGST" not in i:
                item = dict()
                item_value = ""
                dt = i.strip()
                items_split = dt.split(" ")
                if len(items_split)>4 and "." in items_split[-1]:
                    item['date'] = items_split[0]
                    item['item_value'] = float(items_split[-1].replace(",",""))
                    item["name"] = (' '.join(items_split[1:-2])).strip()
                    if "#" in item["name"]:
                        item["name"] = (item["name"].split("#")[0]).strip()
                    if "Check" in item["name"]:
                        item["name"] = (item["name"].split("Check")[0]).strip()
                    # if "-FO" in item["name"]:
                    #     name_index = item["name"].index("-FO")
                    #     item["name"] = item["name"][:name_index]
                    if "SIN" in item["name"]:
                        name_index = item["name"].index("SIN")
                        item["name"] = item["name"][:name_index]
                    if "Ref" in item["name"]:
                        name_index = item["name"].index("Ref")
                        item["name"] = item["name"][:name_index]
                    if "..." in item["name"]:
                        name_index = item["name"].index("...")
                        item["name"] = item["name"][:name_index]
                    if "LOCAL" in item["name"]:
                        name_index = item["name"].index("LOCAL")
                        item["name"] = item["name"][:name_index]
                    if "discount" in item["name"]:
                        name_index = item["name"].index("discount")
                        item["name"] = item["name"][:name_index]
                    if "MOBILE" in item["name"]:
                        name_index = item["name"].index("MOBILE")
                        item["name"] = item["name"][:name_index]
                    # if "-Rebate" in item["name"]:
                    #     name_index = item["name"].rindex("-Rebate")
                    #     item["name"] = item["name"][:name_index]
                    if "Transfer Debit" in item["name"]:
                        if "(Amt" in i:
                            name_index = item["name"].rindex("(Amt")
                            item["name"] = item["name"][:name_index]
                    if len(items_split[-2]) == 6 or len(items_split[-2]) == 8:
                        if items_split[-2].isdigit():
                            item['sac_code'] = items_split[-2]
                        else:
                            item["sac_code"] = "No Sac"
                    else:
                        item["sac_code"] = "No Sac"
                    # if "Accommodation" in item['name'] or "accommodation" in item['name']:
                    #     if "Rebate" not in item['name']:
                    #         item['name'] = "Accommodations Charge"    
                    item['sort_order'] =  itemsort+1
                itemsort+=1
                if item !={}:
                    items.append(item)

        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types  = ' '.join([''.join(ele) for ele in paymentTypes['data']])
        payment = [''.join(ele) for ele in paymentTypes['data']]
        for each in items:
            if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"]:
                if each["name"] not in payment_Types:
                    res = [ele for ele in payment if(ele in each["name"] and "Paid Out" not in each["name"])]
                    if not res:
                        total_items.append(each)

        guest = dict()
        for index, i in enumerate(guestDeatils):
            if "Folio No." in i:
                guest['name'] = i.split('Folio No.')[0]    
            if "Departure" in i:        
                guest['name'] = i.split('Departure')[0]
            if "Page 1 of 1" in i:
                guest['name'] = i.split('Page 1 of 1')[0] 
            if "Page 1 of 2" in i:
                guest['name'] = i.split('Page 1 of 1')[0]       
            # print(guest,i)    
            guest["name"] = (guest["name"].replace("GUEST NAME:","")).strip()
            guest['name'] = guest['name'].replace("Page 1 of 1","")
            guest['name'] = guest['name'].replace("Page 1 of 2","")
        guest['invoice_number'] = invoiceNumber.replace(' ', '')

        guest['membership'] = membership
        guest['invoice_date'] = date_time_obj
        guest['items'] = total_items
        guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
        guest['gstNumber'] = gstNumber
        guest['room_number'] = int(roomNumber) if roomNumber != "" else 0
        guest['company_code'] = "HEHHC-01"
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

        company_code = {"code":"HEHHC-01"}
        error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"HEHHC-01","invoice_date":date_time_obj}
        error_data['invoice_file'] = filepath
        error_data['guest_name'] = guest['name']
        error_data['gst_number'] = gstNumber
        if guest['invoice_type'] == "B2C":
            error_data['gst_number'] == " "
        error_data['state_code'] = " "
        error_data['room_number'] = guest['room_number']
        error_data['pincode'] = " "
        error_data['total_invoice_amount'] = total_invoice_amount
        # gstNumber = "12345"

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
