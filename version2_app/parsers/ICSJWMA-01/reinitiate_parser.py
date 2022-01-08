import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import re
import json
import sys
import frappe
import traceback
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def reinitiateInvoice(data):
	try:
		filepath = data['filepath']
		reupload_inv_number = data['invoice_number']
		start_time = datetime.datetime.utcnow()
		companyCheckResponse = check_company_exist("ICSJWMA-01")
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
		for i in raw_data:
			if "CREDIT TAX INVOICE" in i:
				invoice_category = "Credit Invoice"
			if "Confirmation No" in i:
				confirmation_number = i.split(":")
				conf_number = confirmation_number[-1].replace(" ", "")
			if "Total" in i:
				total_invoice = i.split(" ")
				total_invoice_amount = float(total_invoice[-2].replace(",", ""))
			if "Departure" in i and date_time_obj == "":
				depatureDateIndex = i.index('Departure')
				date_time_obj = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
			if "Bill Generation Date" in i:
				date_time_obj = (i.split(":")[-1]).strip()
				date_time_obj = datetime.datetime.strptime(date_time_obj,'%d-%m-%y').strftime('%d-%b-%y %H:%M:%S')
			if "Room" in i and "CHECK#" not in i and "Rooms" not in i and "GST" not in i and "Room No" not in i:
				room = i.split(":")
				roomNumber = room[-1]
				# roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
			if "GST ID" in i:
				gstNumber = i.split(':')[1].replace(' ', '')
				# if "ConfirmationNo." in gstNumber:
				gstNumber = gstNumber.replace("ConfirmationNo.","")
				gstNumber = gstNumber.replace("Membership","")
			if "Invoice No" in i:
				invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "")
			if "Bill To" in i:
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
			if "Company Name" in i:
				guestDeatils.append(i)
			if "Membership" in i:
				Membership = i.split(":")
				membership = Membership[-1].replace(" ", "")
			if "Cashier" in i:
				p = i.split(":")
				print_by = p[1].replace(" ","")
				
		check_invoice = check_invoice_exists(invoiceNumber)
		if check_invoice['success']==True:
			inv_data = check_invoice['data']
			invoiceNumber = inv_data.name
		if invoiceNumber != reupload_inv_number:
			return {"success":False,"message":"Incorrect Invoice Attempted"}
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
					ele = j[0]
					if "~" not in j[1]:
						ele = ele+" "+j[1]
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
			if len(check_date) > 0 and "IGST" not in i and "CGST" not in i and "SGST" not in i and "CESS" not in i and "VAT" not in i and "Cess" not in i and "Vat" not in i and "VAT" not in i:
				item = dict()
				item_value = ""
				dt = i.strip()
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

		guest = dict()		
		if "Confirmation" in confirmation_number[0]: 
			name = confirmation_number[0].strip().split("Confirmation No")
			if len(name[0])>0:
				guest['name'] = confirmation_number[0].split("Confirmation No ")[0].strip(" ").replace(",","")
			else:
				guest['name'] = room[0].split("Room")[0]	
		else:
			guest['name'] = room[0].split("Room")[0]


		guest['invoice_number'] = invoiceNumber.replace(' ', '')

		guest['membership'] = membership
		guest['invoice_date'] = date_time_obj
		guest['items'] = items
		guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
		guest['gstNumber'] = gstNumber
		guest['room_number'] = int(roomNumber) if roomNumber != "" else 0
		guest['company_code'] = "ICSJWMA-01"
		guest['confirmation_number'] = conf_number
		guest['start_time'] = str(start_time)
		guest['print_by'] = print_by
		guest['invoice_category'] = invoice_category

		check_invoice = check_invoice_exists(guest['invoice_number'])
		if check_invoice['success']==True:
			inv_data = check_invoice['data']
			if inv_data.docstatus==2:
				amened='Yes'
				invoiceNumber = inv_data.name
				guest['invoice_number'] = inv_data.name
			else:
				invoiceNumber = inv_data.name
				guest['invoice_number'] = inv_data.name
				amened='No'
		
		company_code = {"code":"ICSJWMA-01"}
		error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"ICSJWMA-01","invoice_date":date_time_obj}
		error_data['invoice_file'] = filepath
		error_data['guest_name'] = guest['name']
		error_data['gst_number'] = gstNumber
		if guest['invoice_type'] == "B2C":
			error_data['gst_number'] == " "
		error_data['state_code'] = "36"
		error_data['room_number'] = guest['room_number']
		error_data['total_invoice_amount'] = total_invoice_amount
		# gstNumber = "12345"
		# print(guest['invoice_number'])

		if len(gstNumber) < 15 and len(gstNumber)>0:
			error_data['invoice_file'] = filepath
			error_data['error_message'] = "Invalid GstNumber"
			error_data['amened'] = amened
			
			errorcalulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format})
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
						sez = 1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
						calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"sez":sez})
						if calulateItemsApiResponse['success'] == True:
							guest['invoice_file'] = filepath
							insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"sez":sez})
							if insertInvoiceApiResponse['success']== True:
								print("Invoice Created",insertInvoiceApiResponse)
								return {"success":True,"message":"Invoice Created"}
							else:
								
								error_data['error_message'] = insertInvoiceApiResponse['message']
								error_data['amened'] = amened
								error_data["sez"] = sez
								errorInvoice = Error_Insert_invoice(error_data)
								print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
								return {"success":False,"message":insertInvoiceApiResponse['message']}
						else:
							
							error_data['error_message'] = calulateItemsApiResponse['message']
							error_data['amened'] = amened
							error_data["sez"] = sez
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
				calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"sez":0})
				if calulateItemsApiResponse['success'] == True:
					guest['invoice_file'] = filepath
					insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer,"sez":0})
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