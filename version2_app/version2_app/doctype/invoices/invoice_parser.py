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
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import *
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def file_parsing(filepath):
	start_time = datetime.datetime.utcnow()
	companyCheckResponse = check_company_exist("HICC-01")
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
	for i in raw_data:
		if "Confirmation No." in i:
			confirmation_number = i.split(":")
			conf_number = confirmation_number[-1].replace(" ", "")
		if "Total" in i:
			total_invoice = i.split(" ")
			total_invoice_amount = float(total_invoice[-2].replace(",", ""))
		if "Departure :" in i:
			depatureDateIndex = i.index('Departure')
			date_time_obj = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
		if "Room No." in i:
			room = i.split(":")
			roomNumber = room[-1]
			# roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
		if "Guest GST ID" in i:
			gstNumber = i.split(':')[1].replace(' ', '')
			gstNumber = gstNumber.replace("ConfirmationNo.","")
			print(gstNumber)
		if "Bill  No." in i:
			invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "")
			# if "-" in invoiceNumber:
			# 	invoiceNumber = invoiceNumber.replace("-"," ")
		if "Bill To" in i:
			guestDetailsEntered = True
		if "Checkout By:" in i:
			guestDetailsEntered = False
		if guestDetailsEntered == True:
			guestDeatils.append(i)
		if i in "Date Description Reference Debit Credit":
			entered = True
		if 'CGST 6%=' in i:
			entered = False
		if 'Billing' in i:
			entered = False
		if 'Total' in i:
			entered = False
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

	
	paymentTypes = GetPaymentTypes()
	paymentTypes  = ' '.join([''.join(ele) for ele in paymentTypes['data']])
	original_data = []
	for index, i in enumerate(data):
	
		
		if 'XX/XX' in i:
			i = " "
		if i !=" ":
			j = i.split(' ')
			j = j[1:-1]
			if len(j)>1:
				ele = j[0]+" "+j[1]
				if ele not in paymentTypes:
					original_data.append(i)
			elif len(j) == 1:
				if j[0] not in paymentTypes:
					original_data.append(i)



		

	items = [] 
	itemsort = 0
	for i in original_data:
		pattern = re.compile(
		 "^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})+"
		)
		check_date = re.findall(pattern, i)
		if len(check_date) > 0:
			item = dict()
			for index, j in enumerate(i.split(' ')):
				# print(index,j)
				if index == 0:
					item['date'] = j
				if index == 1:
					starting_index = i.index(j)
					if "~" in i:
						ending_index = i.find("~")
						item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ")
					else:
						ending_index = i.find(item_value)
						item["name"] = ((i[starting_index:ending_index]).strip()).replace("  "," ")
						
				if 'SAC' in j:
					item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
				if index == len(i.split(' ')) - 1:
					if index != 0:
						item['item_value'] = float(j.replace(',', ''))
				item['sort_order'] =  itemsort+1
			itemsort+=1
			items.append(item)

	total_items = []
	for each in items:
		if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Allow " not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"]:
			total_items.append(each)

	finalData = []
	for item in items:

		if len(item) > 1:

			if 'CGST' not in item['name'] and 'SGST' not in item['name'] and 'CESS' not in item['name'] and "Allow " not in item["name"]:

				if 'sac_code' in item:
					item['sac_code'] = item['sac_code']
				else:
					item['sac_code'] = 'No Sac'
				finalData.append(item)
			else:
				itemToUpdate = finalData[len(finalData) - 1]
				# itemToUpdate[item['name']] = item['TotAmt']
				if 'SGST' in item['name']:
					itemToUpdate['sgst'] = int(item['percentage'].replace(',', ''))
					itemToUpdate['sgstAmount'] = item['item_value']
				elif 'CGST' in item['name']:
					itemToUpdate['cgst'] = int(item['percentage'].replace(',', ''))
					itemToUpdate['cgstAmount'] = item['item_value']
				elif 'IGST' in item['name']:
					itemToUpdate['igst'] = int(item['percentage'].replace(',', ''))
					itemToUpdate['igstAmount'] = item['item_value']
				elif 'CESS' in item['name']:
					itemToUpdate['cess'] = int(item['percentage'].replace(',', ''))
					itemToUpdate['cessAmount'] = item['item_value']
				elif 'Allow ' in item["name"]:
					if "sgst" in itemToUpdate:
						itemToUpdate['cgst'] = 9
						itemToUpdate['cgstAmount'] = item['item_value']
					else:
						itemToUpdate['sgst'] = 9
						itemToUpdate['sgstAmount'] = item['item_value']


	invoiceItems = []
	for index, i in enumerate(finalData):
		# i['name']=i['name']+"99999"
		if 'cgstAmount' not in i:
			i['cgst'] = 0
			i['cgstAmount'] = float(0)
		if 'sgstAmount' not in i:
			i['sgst'] = 0
			i['sgstAmount'] = float(0)
		if 'igstAmount' not in i:
			i['igst'] = 0
			i['igstAmount'] = float(0)
		if 'cessAmount' not in i:
			i['cess'] = 0
			i['cessAmount'] = float(0)    
		# i['total_item_value'] = float(i['sgstAmount'])+float(i['cgstAmount'])+float(i['item_value'])+float(i['igstAmount'])
		invoiceItems.append(i)

		# print(i)
	guest = dict()
	# print(guestDeatils)
	for index, i in enumerate(guestDeatils):
		if index == 0:
			guest['name'] = i.split(':')[1]
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
	guest['room_number'] = int(roomNumber)
	guest['company_code'] = "HICC-01"
	guest['confirmation_number'] = conf_number
	guest['start_time'] = str(start_time)
	guest['print_by'] = print_by

	# check_invoice_exists
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

	company_code = {"code":"HICC-01"}
	error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"JP-2022","invoice_date":date_time_obj}
	error_data['invoice_file'] = filepath
	error_data['guest_name'] = guest['name']
	error_data['gst_number'] = gstNumber
	if guest['invoice_type'] == "B2C":
		error_data['gst_number'] == " "
	error_data['state_code'] = "36"
	error_data['room_number'] = guest['room_number']
	error_data['pincode'] = "500082"
	# gstNumber = "12345"
	# print(guest['invoice_number'])

	if len(gstNumber) < 15 and len(gstNumber)>0:
		error_data['invoice_file'] = filepath
		error_data['error_message'] = "The given gst number is not a vaild one"
		error_data['amened'] = amened
		errorInvoice = Error_Insert_invoice(error_data)
		print("Error:  *******The given gst number is not a vaild one**********")
		return {"success":False,"message":"The given gst number is not a vaild one"}



	   


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
						insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
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
						print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
						return {"success":False,"message":calulateItemsApiResponse['message']}
				else:
					# print(error_data)
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
				insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer})
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
	

