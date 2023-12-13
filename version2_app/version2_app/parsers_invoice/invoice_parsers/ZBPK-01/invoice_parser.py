import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import traceback,sys,os
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
from version2_app.pos_bills.doctype.pos_checks.pos_checks import create_pos_bills


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
        companyCheckResponse = check_company_exist("ZBPK-01")
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
                # print(raw_data,"rowwwwwwww")

        data = []
        amened = ''
        entered = False
        guestDetailsEntered = False
        informationInvoice = "No"
        guestDeatils = []
        invoiceNumber = ''
        gstNumber = ''
        date_time_obj = ''
        total_invoice_amount = ''
        conf_number = ''
        membership = ''
        item_date = ''
        print_by = ''
        roomNumber = ""
        reupload = False
        invoice_category = "Tax Invoice"
        banquet = False
        laundary = False
        posbill = False
        B2B_pos = False
        B2C_pos = False
        taxinvoice = False
        if "LAUNDRY BILL O" in raw_data or "LAUNDRY BILL" in raw_data:
            laundary = True
        elif "Function Details" in raw_data:
            banquet = True
        elif "RESTAURANTS PVT LTD" in raw_data or "RESAURANTS PVT LTD" in raw_data:
            posbill = True
            for each in raw_data:
                if "Guest GSTIN" in each:
                    B2B_pos = True
                else:
                    B2C_pos = True    
        else:
            taxinvoice = True

        
        print(banquet, taxinvoice, laundary, posbill, B2B_pos, B2C_pos)        
        if banquet:
            for i in raw_data:
                # print(i,"++++++++++++++")
                if "Bill Date" in i:
                    date_time_obj = re.split(r" ",i)[-2]
                    inv_date = date_time_obj.replace("/","").strip("0")
                    date_time_obj = datetime.datetime.strptime(date_time_obj,'%d/%m/%Y').strftime('%d-%b-%y %H:%M:%S')
                    item_date = datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%Y-%m-%d')
                    invoiceNumber = inv_date+invoiceNumber
                if "Res No #" in i:
                    confirmation_number = i.split()
                    conf_number = confirmation_number[-1].replace(" ", "")
                if "Net. Amount" in i or "Net. Amount" in i:
                    advance = ''
                    ind = raw_data.index(i)
                    advance = raw_data[ind-2]
                    if advance == 'Advances':
                        ind = raw_data.index(i)
                        advance_amount = raw_data[ind-3]
                        advance = float(advance_amount.replace(",",""))
                        ind = raw_data.index(i)
                        total_invoice_amount = raw_data[ind-1]
                        # total_invoice_amount=i.split(" ")
                        total_invoice_amount_diff = float(total_invoice_amount.replace(",",""))
                        # print(total_invoice_amount_diff,">>>>>>>>>>>>>>>>>>>>>>>>>")
                        total_invoice_amount = total_invoice_amount_diff + advance
                    else:
                        ind = raw_data.index(i)
                        total_invoice_amount = raw_data[ind-1]
                        # total_invoice_amount=i.split(" ")
                        total_invoice_amount = float(total_invoice_amount.replace(",",""))
                # if "Total Amount with Taxes" in i or "Total Amount with Taxes" in i: 
                #     print(i.split(),"////////////")
                #     total_invoice_amount=i.split(" ")
                #     total_invoice_amount = float(total_invoice_amount[-1].replace(",", ""))
                #     print(total_invoice_amount,"amounttttttt")
                # if "Room No" in i:
                #     room = i.split(":")
                #     roomNumber = room[-1]
                    # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
                if "GST No. " in i or "GST No." in i:
                    gstNumber = i.split(' ')[-1].replace(' ', '')
                    gstNumber = gstNumber.replace("GSTNBillNo","").replace("No.","")
                if "Bill No" in i:
                    invoiceNumber = (i.split(' '))
                    invoiceNumber = invoiceNumber[-1]
                if "Bill To" in i:
                    guestDetailsEntered = True
                if "Checkout By:" in i:
                    guestDetailsEntered = False
                if guestDetailsEntered == True:
                    guestDeatils.append(i)
                if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit":
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
                if "Guest Name" in i:
                    guestDeatils.append(i)
                if "Membership" in i:
                    Membership = i.split(":")
                    membership = Membership[-1].replace(" ", "")
                if "Printed By / On" in i:
                    print_by = i.split(":")
                    print_by = print_by[1].replace(" ","")
        if laundary:
            for i in raw_data:       
                if "Bill Date :" in i:
                        date_time_obj = (i.split(":")[-2]).strip()
                        date_time_obj = re.split(r" ",date_time_obj)[0].replace("  "," ")
                        item_date =  date_time_obj
                        date_time_obj = datetime.datetime.strptime(date_time_obj,'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
                if "Reg No :" in i:
                    confirmation_number = i.split(":")
                    conf_number = confirmation_number[-1].replace(" ", "")
                if "NETT AMOUNT" in i or "Net Amount :" in i:
                    total_invoice = i.split()
                    total_invoice_amount = float(total_invoice[-1])
                    print(total_invoice_amount,"amounttttttt")
                if "Room Number :" in i:
                    room = i
                    room = re.findall(r'[0-9]+',room)
                    roomNumber = room[0]
                if "GSTIN "  in i:
                    gstNumber = i.split(':')[1].replace(' ', '')
                    gstNumber = gstNumber.replace("GSTNBillNo","")
                if "Bill No " in i:
                    invoiceNumber = (i.split(':')[1]).replace("Bill Date", "").strip()
                    date_inv = (datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%d%m%Y')).strip("0")
                    invoiceNumber = date_inv+invoiceNumber
                if "Bill To" in i:
                    guestDetailsEntered = True
                if "Checkout By:" in i:
                    guestDetailsEntered = False
                if guestDetailsEntered == True:
                    guestDeatils.append(i)
                if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit":
                    entered = True
                if 'CGST 6%=' in i:
                    entered = False
                if 'Billing' in i:
                    entered = False
                if 'NETT AMOUNT' in i:
                    entered = False
                entered = True    
                if entered == True:
                    data.append(i)
                if "Guest Name :" in i:
                    guestDeatils.append(i)
                if "Membership" in i:
                    Membership = i.split(":")
                    membership = Membership[-1].replace(" ", "")
                if "Printed By / On" in i:
                    print_by = i.split(":")
                    print_by = print_by[1].replace(" ","")
        if posbill:
            if B2B_pos and B2C_pos:
                for i in raw_data:
                    print(i)
                    if "Table #" in i:
                        index_val = raw_data.index(i)+1
                        date_time_obj=raw_data[index_val]
                        date_time_obj = re.split(r" ",date_time_obj)[1]
                        date_time_obj = datetime.datetime.strptime(date_time_obj,'%d/%m/%y').strftime('%d-%b-%y %H:%M:%S')
                        item_date = datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%d/%m/%y')
                    if "Table #:" in i:
                        index_val = raw_data.index(i)
                        invoiceNumber=raw_data[index_val]
                        invoiceNumber = invoiceNumber.split(":")[0].replace("Table #","").replace("Bill No","").strip()
                        date_inv = (datetime.datetime.strptime(date_time_obj,'%d-%b-%y %H:%M:%S').strftime('%d%m%y')).strip("0")
                        invoiceNumber = date_inv+invoiceNumber
                    if "Net Amount " in i:
                        total_invoice_amount=i.split(" ")
                        total_invoice_amount = float(total_invoice_amount[-1].replace(",", ""))
                    if "Guest GSTIN"  in i or "Guest GSTIN" in i:
                        gstNumber = i.replace(" ","")
                        gstNumber = gstNumber.split()[-1].replace(' ', '').strip()
                        gstNumber = gstNumber.replace("GSTNBillNo","").replace("GuestGSTIN","").strip()
                        check_date = re.compile("\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}")
                        # if(re.search(check_date, gstNumber)):
                        #     pass
                        # else:
                        #     B2B_pos = False
                        #     break
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
                    if 'Total' in i:
                        entered = False
                    entered = True 
                    if entered == True:
                        data.append(i)
                    if "Guest Name     " in i or "Guest Name" in i or "Guest Name" in i:
                        guestDeatils.append(i)
                    if "Membership" in i:
                        Membership = i.split(":")
                        membership = Membership[-1].replace(" ", "")
                    if "Printed By / On" in i:
                        print_by = i.split(":")
                        print_by = print_by[1].replace(" ","")

            # text = "".join(content)
            # pos_data = {
            #         "payload": text,
            #         "outlet": "In Room Dinning",
            #         "check_type": "closed check",
            #         "company": "ZBPK-01",
            #         "pos_bill": filepath
            #     }
            # pos_bill = create_pos_bills(pos_data)
            # if not B2B_pos:
            #     return {"success": True}

        if taxinvoice:
            for i in raw_data:
                # print(i,"taxxxxxxxxxxx")
                if "Bill Date :" in i:
                    date_time_obj = (i.split(":")[-1]).strip()
                    date_time_obj = re.split(r" ",date_time_obj)[0]
                    inv_date = datetime.datetime.strptime(date_time_obj,'%d/%m/%y').strftime('%d%m%Y').strip("0")
                    date_time_obj = datetime.datetime.strptime(date_time_obj,'%d/%m/%y').strftime('%d-%b-%y %H:%M:%S')
                    invoiceNumber = inv_date + invoiceNumber
                if "Reg No :" in i:
                    confirmation_number = i.split(":")
                    conf_number = confirmation_number[-1].replace(" ", "")
                if ("Net Amount:" in i or "Net Amount :" in i or "Net Amount:" in i) and ("Total:" not in i):
                    total_invoice = i.split()
                    total_invoice_amount = float(total_invoice[-2].replace(",", ""))                    
                if "Room No" in i:
                    room = i.split(":")
                    roomNumber = room[-1]
                    # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
                if "GSTN Number " in i:
                    gstNumber = i.split(':')[1].replace(' ', '')
                    gstNumber = gstNumber.replace("GSTNBillNo","")
                if "Bill Number: " in i or "Bill Number: :" in i or "Bill #:" in i:
                    invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "")
                    # invoiceNumber = ''.join(filter(lambda i: i.isdigit(), invoiceNumber))
                if "Bill To" in i:
                    guestDetailsEntered = True
                if "Checkout By:" in i:
                    guestDetailsEntered = False
                if guestDetailsEntered == True:
                    guestDeatils.append(i)
                if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit" or i in "Date Ref No Description GSTN SAC# Credit Debit Amount":
                    entered = True
                if 'CGST 6%=' in i:
                    entered = False
                if 'Billing' in i:
                    entered = False
                if 'Net Amount' in i :
                    entered = False
                # entered = True    
                if entered == True:
                    data.append(i)
                if "Guest Name" in i or "Guest Name :" in i:
                    guestDeatils.append(i)
                if "Membership" in i:
                    Membership = i.split(":")
                    membership = Membership[-1].replace(" ", "")
                if "Printed By / On" in i:
                    print_by = i.split(":")
                    print_by = print_by[1].replace(" ","")
        

        items = [] 
        itemsort = 0
        data_list = []
        item_ind = ""
        total_ind = ""
        for i in data:
            if not B2B_pos:
                i = i.replace("  "," ")
                if "Total" not in i and "Room No " not in i and "Central GS" not in i and "State GS" not in i:
                    pattern = re.compile("^([0-9]{2}\/[0-9]{2}\/[0-9]{2})+")
                    check_date = re.findall(pattern, i)
                    item = dict()
                    if len(check_date) > 0 : 
                        item_value = ""
                        dt = i.strip()
                        i=i.strip()
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
                                    item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ")
                                else:
                                    ending_index = i.find(item_value)
                                    replace_to_one_space = i.replace("  "," ")
                                    item_split = replace_to_one_space.split(" ")
                                    date_index = replace_to_one_space.index(item_split[0])
                                    credit_index = replace_to_one_space.index(item_split[-2])
                                    item_name = replace_to_one_space[date_index+len(item_split[0]):credit_index-len(item_split[-2])]
                                    result = re.sub(r'[0-9]+', '', item_name)
                                    item["name"] = result.strip()
                                    print(item["name"],"///////////")

                            if len(val)>1:		
                                if 'SAC' in j:
                                    item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
                                else:
                                    item['sac_code'] = "No Sac"
                            if len(val)>1:		
                                item['sort_order'] =  itemsort+1.
                                
            
                    else:
                        split_i = i.split(" ")
                        if len(split_i)>0:
                            print(i)
                            pattern = re.compile("^([0-9])+")
                            check_date = re.findall(pattern, split_i[0])
                            if len(check_date) > 0  and "GST No." not in i:
                                split_str = i.split(" ")
                                if len(split_str)>3:	
                                    item['date'] = datetime.datetime.strptime(item_date,'%Y-%m-%d').strftime(companyCheckResponse['data'].invoice_item_date_format)
                                    item_value  = split_str[-1]
                                    item['item_value'] = float(item_value.replace(',', ''))
                                    if laundary:
                                        item["name"] = split_str[1]
                                    # elif posbill in "SAC":
                                    #     item["name"] = split_str[-1] 
                                    else:
                                        start_ind = i.index(split_str[1])
                                        end_ind = i.index(split_str[-2])
                                        name_item = i[start_ind:end_ind]
                                        if split_str[-3].isnumeric():
                                            name_item = name_item.replace(split_str[-3],"")
                                        item["name"] = name_item.strip()
                                    item['sac_code'] = "No Sac"
                                    item['sort_order'] =  itemsort+1
                    
                        
                    itemsort+=1
                    if item !={}:
                        if len(item)>1:
                            items.append(item)
            else:
                # split_str = i.split(" ")
                # regnumber = re.compile(r'\d+(?:,\d*)?')
                # if regnumber.match(split_str[-1]):
                #     print(i,"///////////////////")
                if "Item Name" in i:
                    item_ind = data.index(i)
                if "Total Amoun" in i:
                    total_ind = data.index(i)
                if item_ind != "" and total_ind != "" :
                    data_list = data[item_ind+1:total_ind]
                    break

        if len(data_list) > 0:
            finallist = []
            first_line = None
            second_line = None
            for count, each in enumerate(data_list):
                split_str = each.split(" ")
                regnumber = re.compile(r'\d+(?:,\d*)?')
                if regnumber.match(split_str[-1]) and "SAC" not in each and "." in split_str[-1]:
                    first_line = count     
                if "SAC" in each:
                    second_line = count
                    if str(first_line) and str(second_line):
                        finallist.append(data_list[first_line:second_line+1])
                        first_line = None
                        second_line = None

            itemsort = 0
            for i in finallist:
                item = dict()
                item['date'] = item_date
                item_value = i[0].split(" ")
                item['item_value'] = float(item_value[-1].replace(',', ''))
                join_list = " ".join(i)
                pattern=re.findall("[A-Za-z]+",join_list)
                join_pattern=' '.join(pattern)
                item_name = join_pattern.replace("SAC","")
                item["name"] = item_name.strip()
                item['sac_code'] = "No Sac"
                item['sort_order'] =  itemsort+1
                itemsort += 1
                items.append(item)    


        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types  = [''.join(each) for each in paymentTypes['data']]
        for each in items:
            if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"] and "Central GST" not in each["name"] and "State GST" not in each["name"] and "Central GS":
                if each["name"] not in payment_Types:
                    total_items.append(each)

        guest = dict()
        # print(guestDeatils)
        for index, i in enumerate(guestDeatils):
            if index == 0:
                if laundary:
                    guest['name'] = i.split(':')[1].replace("Delivery Date","").strip()
                elif banquet:
                    ind = i.index("Bill No")
                    i = i[:ind]
                    guest['name'] = i.replace("Guest Name","").strip()
                elif posbill:
                    guest['name'] = i.replace("Guest Name","").strip() 
                    if not guest['name']:
                        guest['name'] = "Guest"
                else:
                    guest['name'] = i.split(':')[1].replace("Bill Number","").strip()
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
        guest['company_code'] = "ZBPK-01"
        guest['confirmation_number'] = conf_number
        guest['start_time'] = str(start_time)
        guest['print_by'] = print_by
        guest['invoice_category'] = invoice_category
        if  taxinvoice:
            guest['pos_checks'] = 0
        elif banquet:
            guest['pos_checks'] = 0
        elif laundary:
            guest['pos_checks'] = 0
        else:
            guest['pos_checks'] = 1


        if companyCheckResponse['data'].pms_information_invoice_for_payment_qr == "Yes" and informationInvoice == "Yes":
            if informationInvoice == "Yes":
                information_data={"confirmation_no":guest['confirmation_number'],"room_no":guest["room_number"],"guest_name":guest['name'].strip(),"doctype":"Information Invoices","document":filepath}
                doc = frappe.get_doc(information_data)
                doc.insert(ignore_permissions=True, ignore_links=True)
                socket = frappe.publish_realtime("custom_socket", {'message':'Information Invoice Created','data':information_data,"company":"ZBPK-01"})
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

                company_code = {"code":"ZBPK-01"}
                error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"ZBPK-01","invoice_date":date_time_obj}
                error_data['invoice_file'] = filepath
                error_data['guest_name'] = guest['name']
                error_data['gst_number'] = gstNumber
                if guest['invoice_type'] == "B2C":
                    error_data['gst_number'] == " "
                error_data['state_code'] = "36"
                error_data['room_number'] = guest['room_number']
                error_data['pincode'] = "500082"
                error_data['total_invoice_amount'] = total_invoice_amount
                error_data["pos_checks"] = guest['pos_checks']
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
            else:
                return {"success":False,"message":"Dont have rights to print Information Invoice"}
    except Exception as e:
        print(traceback.print_exc())
        update_document_bin(print_by,document_type,"",str(e),filepath)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoice_parser","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
        
def invoiceNumberMethod(invoiceNumber):
    invoiceNumber = "TWM"+invoiceNumber
    return invoiceNumber 


