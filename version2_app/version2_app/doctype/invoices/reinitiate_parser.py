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
# from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "HICC_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def reinitiateInvoice(data):
	filepath = data['filepath']
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
		if "GST ID" in i and "Telangana" not in i:
			gstNumber = i.split(':')[1].replace(' ', '')
			gstNumber = gstNumber.replace(" ","")
			gstNumber = gstNumber[:15]
		if "Bill  No." in i:
			invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "")
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



		# if 'Deposit Bank' not in i and 'Amex Card' not in i and 'Deposit Transfer at' not in i and 'Other Credit Cards' not in i and "Date Description Reference Debit Credit" not in i and 'City Ledger' not in i and 'Visa Card' not in i and 'Cash' not in i and 'Bill To Company' not in i and i not in payment_list and 'Master' not in i and 'ZZZ POS Visa Card' not in i and 'Debit Cards (ALL)' not in i and "Refund Back to Guest" not in i:
		# 	original_data.append(i)
		# if 'XX/XX' in i and i in payment_list:
		# 	original_data.pop(len(original_data) - 1)
		# 	original_data.pop(len(original_data) - 1)

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
					item['name'] = j
				if index == 2:
					if len(i.split(" "))>3:
						item['name'] = item['name'] + ' ' + j
				if index == 3:
					if "#" not in j and '[' not in j and ']' not in j and '.' not in j and ',' not in j and 'Pkg.' not in j:
						item["name"] = item["name"] + ' ' + j
				if index == 4:
					if ".00" in j:
						pass
					else:
						if re.fullmatch('[A-Za-z]+', j) and '#' not in j and '[' not in j and "Room" not in j and ']' not in j and 'Pkg.' not in j and 'Split' not in j:
							item["name"] = item["name"] + ' ' + j
				if j == "Dinner" and "Dinner" not in item['name']:
					item["name"] = item["name"] + ' ' + j

				if '%' in j:
					if j not in item['name']:
						v = re.findall("\d+\.\d+\%", j)
						if len(v)==1:
							item['percentage'] = v[0][:-1]

						if "(" not in j and "." not in j:
							
							item['percentage'] = ''.join(filter(lambda j: j.isdigit(), j))
							item["name"] = item["name"] + ' ' + j
				if '%' in j:
					
					v = re.findall("\d+\.\d+\%", j)
					if len(v)==1:
						item['percentage'] = v[0][:-1]
					if "(" not in j and "." not in j:
						item['percentage'] = ''.join(filter(lambda j: j.isdigit(), j))

				
				if index == 5:
					if "CompBreakfast" in j or "Beverage" in j:
						item["name"] = item["name"] + ' ' + j
				
				if "SGST" in j:
					item['name'] = item['name'] + ' SGST'
				if "CGST" in j:
					item['name'] = item['name'] + ' CGST'
				if "IGST" in j:
					item['name'] = item['name'] + ' IGST'
				# if "Cess" in j:
				# 	print(i,j)
					# item['name'] = item['name'] + ' Cess'
				if "HICC" in j:
					if "HICC" not in item['name']:
						item['name'] = item['name']+' HICC'
				if 'SAC' in j:
					item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
					if "SAC" not in item['name']:
						item['name'] = item['name']+ ' SAC'
					if item['sac_code'].isdigit():
						item['name'] = item['name']+' '+item['sac_code']
				if len(j)==6 and j.isdigit():
					item['name'] = item['name']+' '+j
					item['sac_code'] = j
				if len(j)==8 and j.isdigit():
					item['name'] = item['name']+' '+j
					item['sac_code'] = j	
				if index == len(i.split(' ')) - 1:
					if index != 0:
						item['item_value'] = float(j.replace(',', ''))
				item['sort_order'] =  itemsort+1
			itemsort+=1
			items.append(item)


	finalData = []
	for item in items:
		# print(item)
		if len(item) > 1:

			if 'CGST' not in item['name'] and 'SGST' not in item['name'] and 'CESS' not in item['name'] and "Allow " not in item["name"] and 'Cess' not in item['name']:# and "Service Charge" not in item['name'] and "Utility Charge" not in item['name']:
				# print(item)
				if 'sac_code' in item:
					if item['sac_code']== '':
						item['sac_code'] = 'No Sac'
					else:
						item['sac_code'] = item['sac_code']
				else:
					item['sac_code'] = 'No Sac'
				finalData.append(item)
			else:
				itemToUpdate = finalData[len(finalData) - 1]
				if 'SGST' in item['name']:
					if "." in item['percentage']:
						itemToUpdate['sgst'] = float(item['percentage'])
						itemToUpdate['sgstAmount'] = item['item_value']
					else:
						itemToUpdate['sgst'] = int(item['percentage'].replace(',', ''))
						itemToUpdate['sgstAmount'] = item['item_value']
				elif 'CGST' in item['name']:
					if "." in item['percentage']:
						itemToUpdate['cgst'] = float(item['percentage'])
						itemToUpdate['cgstAmount'] = item['item_value']
					else:
						print(item)
						itemToUpdate['cgst'] = int(item['percentage'].replace(',', ''))
						itemToUpdate['cgstAmount'] = item['item_value']
				elif 'IGST' in item['name']:
					if "." in item['percentage']:
						itemToUpdate['igst'] = float(item['percentage'])
						itemToUpdate['igstAmount'] = item['item_value']
					else:
						itemToUpdate['igst'] = int(item['percentage'].replace(',', ''))
						itemToUpdate['igstAmount'] = item['item_value']
				elif 'CESS' in item['name']:
					if "." in item['percentage']:
						itemToUpdate['cess'] = float(item['percentage'])
						itemToUpdate['cessAmount'] = item['item_value']
					else:
						itemToUpdate['cess'] = int(item['percentage'].replace(',', ''))
						itemToUpdate['cessAmount'] = item['item_value']	
				elif 'Cess' in item['name']:
					if "." in item['percentage']:
						itemToUpdate['cess'] = float(item['percentage'])
						itemToUpdate['cessAmount'] = item['item_value']
					else:
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
		# i['SlNo'] = index+1
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
	guest['items'] = invoiceItems
	guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
	guest['gstNumber'] = gstNumber
	guest['room_number'] = int(roomNumber)
	guest['company_code'] = "HICC-01"
	guest['confirmation_number'] = conf_number
	guest['start_time'] = str(start_time)
	
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
	if len(gstNumber) < 15 and len(gstNumber)>0:
		error_data['invoice_file'] = filepath
		error_data['error_message'] = "The given gst number is not a vaild one"
		errorInvoice = Error_Insert_invoice(error_data)
		print("Error:  *******The given gst number is not a vaild one**********")
		return {"success":False,"message":"The given gst number is not a vaild one"}



	# check_invoice_exists
	check_invoice = check_invoice_exists(guest['invoice_number'])
	if check_invoice['success']==True:
		inv_data = check_invoice['data']
		if inv_data.docstatus==2:
			amened='Yes'
		else:
			amened='No'    
	# print(json.dumps(guest, indent = 1))
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
							errorInvoice = Error_Insert_invoice(error_data)
							print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
							return {"success":False,"message":insertInvoiceApiResponse['message']}
					else:
						
						error_data['error_message'] = calulateItemsApiResponse['message']
						errorInvoice = Error_Insert_invoice(error_data)
						print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'],"***********")
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
					errorInvoice = Error_Insert_invoice(error_data)
					print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
					return {"success":False,"message":insertInvoiceApiResponse['message']}
			else:
						
				error_data['error_message'] = calulateItemsApiResponse['message']
				errorInvoice = Error_Insert_invoice(error_data)
				print("B2C calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
				return {"success":False,"message":calulateItemsApiResponse['message']}	
	else:
		error_data['error_message'] = gspApiDataResponse['message']
		errorInvoice = Error_Insert_invoice(error_data)
		print("gspApiData fialed:  ",gspApiDataResponse['message'])
		return {"success":False,"message":gspApiDataResponse['message']}
	

