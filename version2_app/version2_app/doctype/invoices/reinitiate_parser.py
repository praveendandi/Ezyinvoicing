import pdfplumber
# from datetime import datetime
from datetime import date
import datetime
import requests
import re
import string
import json
import sys
import os
import itertools
from json import dumps
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import *
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *
start_time=str(datetime.datetime.utcnow()) 
# sys.exit()
#hi
site_folder_path = "version2_app.com/"
host = "http://localhost:8000/api/method/"
folder_path = frappe.utils.get_bench_path()
path = folder_path + '/sites/' + site_folder_path


def fileUploadfunction(files,invoice_number,payload):
    filecheck = requests.post(host+companyApis['check_invoice_file_exists_api'],headers=headers,json={"data":{"invoice":invoice_number}}).json()
    if filecheck['message']['success']==False:
        file_response = requests.post(host+companyApis['file_upload_api'],
                                files=files, data=payload, verify=False).json()
        file_response = {"message":{"data":file_response['message']}}
        return file_response
    else:
        file_response = filecheck
        return file_response

headers = {
    'Content-Type': 'application/json'
} 
@frappe.whitelist(allow_guest=True)
def reinitiateInvoice(data):
    companyCheckResponse = check_company_exist("JP-2022")
    
    invoicepath = data['filepath']
    file_path=path+data['filepath']
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
    entered = False
    guestDetailsEntered = False

    guestDeatils = []
    invoiceNumber = ''
    gstNumber = ''
    date_time_obj = ''
    total_invoice_amount = ''
    conformation_number = ''
    for i in raw_data:
        if "Total" in i:
            total_invoice = i.split(" ")
            
            total_invoice_amount = float(total_invoice[-1].replace(",",""))
        if "Confirmation No." in i:
            conformation_number = i.split(" ")[-1]
        if "Departure :" in i:
            depatureDateIndex = i.index('Departure')
            date_time_obj = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
        if "Room No " in i:
            roomNumber = ''.join(filter(lambda j: j.isdigit(), i)) 
        if "GST ID  :" in i:
            gstNumber = i.split(':')[1].replace(' ', '')
        if "Invoice No." in i:
            invoiceNumber = i.split(':')[len(i.split(':'))-1]
        if "Billing" in i:
            guestDetailsEntered = True
        if "Checkout By" in i:
            guestDetailsEntered = False
        if guestDetailsEntered == True:
            guestDeatils.append(i)
        if "Guest Name" in i:
            guestDeatils.append(i)  
        if i in "Date Description Reference Debit Credit":
            entered = True
        if 'CGST 6%=' in i:
            entered = False
        if 'Billing  :' in i:
            entered = False
        if 'Total' in i:
            entered = False
        if entered == True:
            data.append(i)


    paymentTypes = GetPaymentTypes()

    paymentTypes  = list(itertools.chain(*paymentTypes['data']))
    # print(paymentTypes)


    original_data = []
    for i in data:
        pattern = re.compile("([0-9])\/([0-9])")
        check_date = re.findall(pattern, i)
        if len(check_date) > 0:
            
            split = i.split(" ")
            split.pop(0)
            split.pop(-1)
            payment = split[0]+" "+split[1]+" "+split[2]  
            
            if "XXXXXX"  in i:
                i = " "
            elif "XX/XX" in i:
                i = " " 
                
            elif payment not in paymentTypes:
                # print(i.split(" "))
                original_data.append(i)
            elif len(split)>3:
                payment2 = payment+" "+split[3]      
                if payment2 not in paymentTypes:
                    original_data.append(i)   
            else:
                pass

    items = []
    # print(companyApis['calculation_by'])
    # if companyApis['calculation_by'] == "Description":
    itemsort = 0
    for i in original_data:
        pattern = re.compile("([0-9])\/([0-9])")
        check_date = re.findall(pattern, i)
        if len(check_date) > 0:
            item = dict() 
            for index, j in enumerate(i.split(' ')):
                # print(j,index)
                if "CHECK" in j:
                    pass
                if "Food" in j:
                    item['sac_code'] = "996331"
                if index == 0:
                    itemDate = j.split('/')
                    item['date'] = "20"+itemDate[2]+"-"+itemDate[1]+"-"+itemDate[0]
                if index == 1:
                    item['name'] = j
                if index == 2 and "CHECK" not in j:
                    item['name'] = item['name']+' '+j
                if index == 3 and "CHECK" not in j and "." not in j:
                    if type(j) is str and len(j)>3 and '%' not in j and j[0]!='#':
                        item['name'] = item['name']+' '+j
                    if '%' in j:
                        item['percentage'] = ''.join(filter(lambda j: j.isdigit(), j))
                        item['name'] = item['name']+' '+j
                    
                    if 'sac_code' in item and item['sac_code'] != '':
                        if 'SAC' in j:
                            item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                if j=="Bevg" and index==4:

                    item['name'] = item['name']+' '+j 
                if index==4 and j==")" and "Telephone" in i:
                    item['name'] = item['name']+' '+j 

                if ("SGST" in j) or ("CGST" in j):
                    item['name'] = item['name']+' '+j 

                if "INR" in j:
                    item['name'] = item['name']+' '+j
                if '%' in j and len(j)==2 and index!=3:
                    item['percentage'] = ''.join(filter(lambda j: j.isdigit(), j))
                    item['name'] = item['name']+' '+j   

                if j=="9":
                    item['percentage'] = '9'
                    item['name'] = item['name']+' '+'9%'  

                if 'SAC' in j:
                    item['name'] = item['name']+' '+j

                if len(j) is 6 and j.isdigit():
                    item['sac_code'] = j  
                    item['name'] = item['name']+' '+j 
                if "#" in j:
                    pass
                if index == len(i.split(' '))-1:
                    item['item_value'] = float(j.replace(',', ''))
                item['sort_order'] =  itemsort+1
            itemsort+=1    
                    
            items.append(item) 
    
    files = {'file': open(
        file_path, 'rb')}


    finalData = []
    for index, item in enumerate(items):

        if 'CGST' not in item['name'] and 'SGST' not in item['name']:
            if 'sac_code' in item:
                item['sac_code']=item['sac_code']
            else:
                item['sac_code']='No Sac'
            finalData.append(item)
        else:
            itemToUpdate = finalData[len(finalData)-1]
            if 'SGST' in item['name']:
                itemToUpdate['sgst'] = int(item['percentage'].replace(',',''))
                itemToUpdate['sgstAmount'] = item['item_value']
            elif 'CGST' in item['name']:
                itemToUpdate['cgst'] = int(item['percentage'].replace(',',''))
                itemToUpdate['cgstAmount'] = item['item_value']
            elif 'IGST' in item['name']:
                itemToUpdate['igst'] = int(item['percentage'].replace(',',''))
                itemToUpdate['igstAmount'] = item['item_value']

    invoiceItems = []
    for index, i in enumerate(finalData):
        # i['SlNo'] = index+1
        if 'cgstAmount' not in i:
            i['cgst'] = 0
            i['cgstAmount'] = float(0)
        if 'sgstAmount' not in i:
            i['sgst'] = 0
            i['sgstAmount'] = float(0)
        if 'igstAmount' not in i:
            i['igst'] = 0
            i['igstAmount'] = float(0)
        # i['total_item_value'] = float(i['sgstAmount'])+float(i['cgstAmount'])+float(i['item_value'])+float(i['igstAmount'])
        invoiceItems.append(i)




    guest = dict()
    guest['start_time'] = start_time
    # print(guestDeatils)
    for index, i in enumerate(guestDeatils):
        if index == 0:
            guest['name'] = i.split(':')[1]
            if "Guests" in guest['name']:
                guest['name'] = guest['name'].replace("Guests"," ")
        if index == 1:
            guest['address1'] = i
        if index == 2:
            guest['address2'] = i


    guest['invoice_number'] = invoiceNumber.replace(' ', '')
 
    guest['invoice_date'] = date_time_obj
    guest['items'] = invoiceItems
    guest['invoice_type'] = 'B2B'if gstNumber != '' else 'B2C'
    guest['gstNumber'] = gstNumber
    guest['room_number'] = int(roomNumber)
    guest['company_code'] = "JP-2022"
    guest['conformation_number'] = conformation_number


    

    payload = {
        'is_private': 1,
        'folder': 'Home',
        'doctype': 'invoices',
        'docname': guest['invoice_number'],
        # 'file_name':
        'fieldname': 'invoice'}

    company_code = {"code":guest['company_code']}


    


    error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"JP-2022","invoice_date":date_time_obj}
    error_data['invoice_file'] = invoicepath
    error_data['guest_name'] = guest['name']
    error_data['gst_number'] = gstNumber
    error_data['state_code'] = "7"
    error_data['room_number'] = guest['room_number']
    error_data['pincode'] = "110008"



    # gstNumber = "123456"
    if len(gstNumber)<15:
        error_data['invoice_file'] = invoicepath
        error_data['error_message'] = "The given gst number is not a vaild one"
        errorInvoice = Error_Insert_invoice(error_data)
        return {"success":False,"message":"The given gst number is not a vaild one"}
     


    gspApiDataResponse = gsp_api_data({"code":company_code['code'],"mode":companyCheckResponse['data'].mode,"provider":companyCheckResponse['data'].provider})
    if gspApiDataResponse['success'] == True:
        if guest['invoice_type'] == 'B2B':
            checkTokenIsValidResponse = check_token_is_valid({"code":company_code['code'],"mode":companyCheckResponse['data'].mode})
            if checkTokenIsValidResponse['success'] == True:
                getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":guest['gstNumber'],"code":company_code['code'],"invoice":guest['invoice_number'],"apidata":gspApiDataResponse['data']})
                if getTaxPayerDetailsResponse['success'] == True:
                    calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code']})
                    if calulateItemsApiResponse['success'] == True:
                        # print(calulateItemsApiResponse)
                        guest['invoice_file'] = invoicepath
                        insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number']})
                        if insertInvoiceApiResponse['success']== True:
                            print("Invoice Created",insertInvoiceApiResponse)
                            return {"success":True,"message":"Invoice updated"}
                        else:
                            # print(insertInvoiceApiResponse)
                            # itsindex = insertInvoiceApiResponse['message']['message'].index("'")
                            error_data['error_message'] = insertInvoiceApiResponse['message']
                            errorInvoice = Error_Insert_invoice(error_data)
                            print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                            return {"success":False,"message":insertInvoiceApiResponse['message']}
                    else:
                        # itsindex = calulateItemsApiResponse['message']['message'].index("'")
                        error_data['error_message'] = calulateItemsApiResponse['message']
                        # print("*****",error_data)
                        errorInvoice = Error_Insert_invoice(error_data)
                        print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'],"***********")
                        print(errorInvoice)
                        return {"success":False,"message":calulateItemsApiResponse['message']}
                else:
                    # itsindex = getTaxPayerDetailsResponse['message']['message'].index("'")
                    print(error_data)
                    error_data['error_message'] = getTaxPayerDetailsResponse['message']
                    errorInvoice = Error_Insert_invoice(error_data)
                    return {"success":False,"message":getTaxPayerDetailsResponse['message']}                        
            else:
                # itsindex = checkTokenIsValidResponse['message']['message'].index("'")
                error_data['error_message'] = checkTokenIsValidResponse['message']
                errorInvoice = Error_Insert_invoice(error_data)
                return {"success":False,"message":checkTokenIsValidResponse['message']} 
        else:
            error_data['error_message'] = "Your Invoice is in B2C Format"
            error_data['invoice_type'] = "B2C"
            errorInvoice = Error_Insert_invoice(error_data)
            return {"success":False,"message":"Your Invoice is in B2C Format"}
            print("B2C")
    else:
        error_data['error_message'] = gspApiDataResponse['message']
        errorInvoice = Error_Insert_invoice(error_data)
        print("gspApiData fialed:  ",gspApiDataResponse['message'])
        return {"success":False,"message":gspApiDataResponse['message']}
    

