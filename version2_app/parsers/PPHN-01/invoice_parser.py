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
import traceback
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import *
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)


folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist(allow_guest=True)
def file_parsing(filepath):
	try:
		# frappe.log_error(frappe.get_traceback())
		start_time = datetime.datetime.utcnow()
		companyCheckResponse = check_company_exist("PPHN-01")
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
			if "Reservation #" in i:
				confirmation_number = i.split(":")
				conf_number = confirmation_number[-1].replace(" ", "")
			if "Net Amount" in i:
				total_invoice = i.split(":")[-1]
				total_invoice_amount = float(total_invoice.replace(",",""))
			if "Bill Date" in i or "BillDate" in i:
				date_time_obj = i.split(':')[-1]
				date_time_obj = datetime.datetime.strptime(date_time_obj, '%m/%d/%Y').strftime('%d-%b-%y %H:%M:%S')
			if "Room No" in i:
				room = i.split(" ")
				roomNumber = room[-1]
			if "Company GST No." in i:
				gstNumber = i.split(':')[1].replace(' ', '')
				gstNumber = gstNumber.replace("Plan","")
			if "Bill Number" in i or "BillNumber" in i:
				invoiceNumber = (i.split(':')[len(i.split(':')) - 1]).replace(" ", "")
				if "/" in invoiceNumber:
					invoiceNumber = invoiceNumber.replace("/","")
			if "Bill To" in i:
				guestDetailsEntered = True
			if "Check Out by" in i:
				guestDetailsEntered = False
			if guestDetailsEntered == True:
				guestDeatils.append(i)
			entered = True
			if 'CGST 6%=' in i:
				entered = False
			if 'Billing' in i:
				entered = False
			if 'Net Amount' in i:
				entered = False
			if entered == True:
				data.append(i)
			if "Guest Name" in i:
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
			pattern = re.compile(
			"^([0]?[1-9]|[1|2][0-9]|[3][0|1])[./-]([0]?[1-9]|[1][0-2])[./-]([0-9]{4}|[0-9]{2})+"
			)
			check_date = re.findall(pattern, i)
			if len(check_date) > 0 and "Total:" not in i:
				item = dict()
				item_value = ""
				dt = i.strip()
				for index, j in enumerate(i.split(' ')):
					val = dt.split(" ")
					if len(val)>1:
						if index == 0:
							item['date'] = j
						if "~" in i:
							result = re.search("~(.*)~", i)
							item['name'] = (result.group(1)).strip()
						item_value = val[-1]
						item['item_value'] = float(item_value.replace(',', ''))
						item['sac_code'] = "No Sac"	
						item['sort_order'] =  itemsort+1
				itemsort+=1
				if item !={}:
					items.append(item)

		total_items = []
		paymentTypes = GetPaymentTypes()
		payment_Types  = [''.join(each) for each in paymentTypes['data']]
		for each in items:
			print(each)
			if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"] and "Central GST" not in each["name"] and "State GST" not in each["name"]:
				if each["name"] not in payment_Types:
					total_items.append(each)
				else:
					if "-" in str(each["item_value"]):
						total_invoice_amount = total_invoice_amount+abs(each["item_value"])

		guest = dict()
		# print(guestDeatils)
		for index, i in enumerate(guestDeatils):
			if index == 0:
				guest['name'] = i.split(':')[1]
				guest['name'] = (guest["name"].replace("Bill Number","")).strip()
			if index == 1:
				guest['address1'] = ((i.split(':')[1]).replace("Bill Number","")).strip()
			if index == 2:
				guest['address2'] = ((i.split(':')[1]).replace("Room No","")).strip()
				guest["address2"] =  (guest["address2"].replace(roomNumber, "")).strip()

		guest['invoice_number'] = invoiceNumber.replace(' ', '')

		guest['membership'] = membership
		guest['invoice_date'] = date_time_obj
		guest['items'] = total_items
		guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
		guest['gstNumber'] = gstNumber
		guest['room_number'] = int(roomNumber) if roomNumber != "" else 0
		guest['company_code'] = "PPHN-01"
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
				if inv_data.invoice_type == "B2B":
					if inv_data.irn_generated=="Pending" or inv_data.irn_generated == "Error":
						reupload = True
				else:
					reupload = True
		company_code = {"code":"PPHN-01"}
		error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":invoiceNumber.replace(" ",""),"company_code":"PPHN-01","invoice_date":date_time_obj}
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
						calulateItemsApiResponse = calulate_items({'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format})
						if calulateItemsApiResponse['success'] == True:
							guest['invoice_file'] = filepath
							if reupload == False:
								insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
								if insertInvoiceApiResponse['success']== True:
									print("Invoice Created",insertInvoiceApiResponse)
									return {"success":True,"message":"Invoice Created"}
						
								else:
									error_data['error_message'] = insertInvoiceApiResponse['message']
									error_data['amened'] = amened
									error_data["items_data"]=calulateItemsApiResponse['data']
									errorInvoice = Error_Insert_invoice(error_data)
									print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
									return {"success":False,"message":insertInvoiceApiResponse['message']}
							else:
								insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
								if insertInvoiceApiResponse['success']== True:
									print("Invoice Created",insertInvoiceApiResponse)
									return {"success":True,"message":"Invoice Created"}
						
								else:
									error_data['error_message'] = insertInvoiceApiResponse['message']
									error_data['amened'] = amened
									error_data["items_data"]=calulateItemsApiResponse['data']
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
					if reupload == False:
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
						insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":guest,"company_code":company_code['code'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened,"taxpayer":taxpayer})
						if insertInvoiceApiResponse['success']== True:
							print("B2C Invoice Created",insertInvoiceApiResponse)
							return {"success":True,"message":"Invoice Created"}
						else:
							error_data['error_message'] = insertInvoiceApiResponse['message']
							error_data['amened'] = amened
							errorInvoice = Error_Insert_invoice(error_data)
							print("B2C re insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
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
		print(str(e),"       invoice parsing")
		print(traceback.print_exc())
		frappe.log_error(frappe.get_traceback())
		logger.error(str(e))
		return {"success":False,"message":str(e)}