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
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import *
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def file_parsing(filepath):
	start_time = datetime.datetime.utcnow()
	companyCheckResponse = check_company_exist("MHKCP-01")
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
		if "Cust GSTIN" in i:
			gstNumber = i.split(':')[1].replace(' ', '')
			gstNumber = gstNumber.replace("ConfirmationNo.","")
			print(gstNumber)
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

	

	original_data = []
	payment_list = "Misc Debit','Cash','Cheque ( Do not Use )','City Ledger FO','Refund Back to Guest','Deposits Paid','American Express','Visa Card','Master','Master Card','Citi Bank Diners','JCB','Bob Card','Debit Card Visa','Debit Cards (ALL)','Debit Card Master','Cash POS','POS CIty Ledger','Other Credit Cards','RUPAY CARD','Voucher (TA)','DIGITAL WALLET','Cash (Foreign Exchange)','Advance Deposit Checkin'"
	for index, i in enumerate(data):
	
		if 'Amex Card' not in i and 'Deposit Transfer at' not in i and 'Other Credit Cards' not in i and "Date Description Reference Debit Credit" not in i and 'City Ledger' not in i and 'Visa Card' not in i and 'Cash' not in i and 'Bill To Company' not in i and i not in payment_list and 'Master' not in i and 'ZZZ POS Visa Card' not in i and 'Debit Cards (ALL)' not in i and "Refund Back to Guest" not in i:
			original_data.append(i)
		if 'XX/XX' in i and i in payment_list:
			original_data.pop(len(original_data) - 1)
			original_data.pop(len(original_data) - 1)

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
					if "#" not in j and '[' not in j and ']' not in j:
						item["name"] = item["name"] + ' ' + j		
				if index == 4:
					if ".00" in j:
						pass
						# item['item_value'] = float(j.replace(',', ''))
					else:
						if re.fullmatch('[A-Za-z]+', j) and '#' not in j and '[' not in j and "Room" not in j and ']' not in j:
							item["name"] = item["name"] + ' ' + j
				if '%' in j:
					item['percentage'] = ''.join(
								filter(lambda j: j.isdigit(), j))
					item["name"] = item["name"] + ' ' + j
				if index>4 and index<9:
					
					if ".00" in j:
						pass
						# print(j,"0000000000000000000000")
						# item['item_value'] = float(j.replace(',', ''))

					else:
						if "#" not in j and '[' not in j and "Room" not in j and "615" not in j and ":" not in j and not j.isdigit() and ']' not in j:
							item["name"] = item["name"] + ' ' + j
				
				if "Dry" in j:
					print(j,"*******************888")
				if "SGST" in j:
					item['name'] = item['name'] + ' SGST'
				if "CGST" in j:
					item['name'] = item['name'] + ' CGST'   
				if "IGST" in j:
					item['name'] = item['name'] + ' IGST'      


				if 'SAC' in j:
					item['sac_code'] = ''.join(filter(lambda j: j.isdigit(), j))
				if index == len(i.split(' ')) - 1:
					if index != 0:
						item['item_value'] = float(j.replace(',', ''))
				item['sort_order'] =  itemsort+1
			itemsort+=1			
			items.append(item)


	finalData = []
	for item in items:
		
		if len(item) > 1:

			if 'CGST' not in item['name'] and 'SGST' not in item['name'] and 'CESS' not in item['name']:
				
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
	guest['company_code'] = "MHKCP-01"
	guest['confirmation_number'] = conf_number
	guest['start_time'] = str(start_time)
	
	company_code = {"code":"MHKCP-01"}
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
	# guest['invoice_number'] = guest['invoice_number']+"-A"
	if check_invoice['success']==True:

		# print(check_invoice)
		# guest['invoice_number'] = guest['invoice_number']+"-A"
		inv_data = check_invoice['data']
		# print(inv_data.docstatus)
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
					calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code']})
					if calulateItemsApiResponse['success'] == True:
						guest['invoice_file'] = filepath
						insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
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
						print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
						return {"success":False,"message":calulateItemsApiResponse['message']}
				else:
					# print(error_data)
					error_data['error_message'] = getTaxPayerDetailsResponse['message']
					errorInvoice = Error_Insert_invoice(error_data)
					return {"success":False,"message":getTaxPayerDetailsResponse['message']}                        
			else:
				# itsindex = checkTokenIsValidResponse['message']['message'].index("'")
				error_data['error_message'] = checkTokenIsValidResponse['message']
				errorInvoice = Error_Insert_invoice(error_data)
				return {"success":False,"message":checkTokenIsValidResponse['message']} 
		else:
			# error_data['error_message'] = "Your Invoice is in B2C Format"
			# error_data['invoice_type'] = "B2C"
			# errorInvoice = Error_Insert_invoice(error_data)
			# return {"success":False,"message":"Your Invoice is in B2C Format"}
			# print("B2C")
			calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code']})
			if calulateItemsApiResponse['success'] == True:
				guest['invoice_file'] = filepath
				insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
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
	
