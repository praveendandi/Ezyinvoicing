# # # -*- coding: utf-8 -*-
# # # Copyright (c) 2020, caratred and contributors
# # # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe.model.document import Document
# import requests
# from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn

# import datetime
# import random
# from frappe.utils import get_site_name
# import time

# from PyPDF2 import PdfFileWriter, PdfFileReader
# import fitz
# site = 'http://0.0.0.0:8000/'
# site_folder_path = 'version2_app.com/'
# fontpath= '/home/caratred/frappe_projects/Einvoice_Bench/apps/version2_app/version2_app/version2_app/doctype/invoices/Roboto-Black.ttf'

# # site = 'http://jps.ezyinvoicing.com/'
# # site_folder_path = 'jps.ezyinvoicing.com/'
# # fontpath = '/home/frappe/invoices/apps/jp_siddharth/jp_siddharth/jp_siddharth/doctype/invoices/Roboto-Black.ttf'

# class Invoices(Document):
# 	def generateIrn(self, invoice_number):
# 		# try:
# 		# get invoice details
# 		start_time = datetime.datetime.utcnow()
# 		invoice = frappe.get_doc('Invoices', invoice_number)
# 		# get seller details
# 		company_details = check_company_exist_for_Irn(invoice.company)
# 		# get gsp_details
# 		credit_note_items = []
# 		companyData = {"code":company_details['data'].name,"mode":company_details['data'].mode,"provider":company_details['data'].provider}
# 		GSP_details = gsp_api_data(companyData)
# 		# print(GSP_details)
# 		# get taxpayer details
# 		GspData = {"gstNumber":invoice.gst_number,"code":invoice.company,"apidata":GSP_details['data']}
# 		taxpayer_details = get_tax_payer_details(GspData)
# 		#gst data
# 		gst_data = {
# 			"Version": "1.1",
# 			"TranDtls": {
# 				"TaxSch": "GST",
# 				"SupTyp": "B2B",
# 				"RegRev": "Y",
# 				"IgstOnIntra": "N"
# 			},
# 			"SellerDtls": {
# 				"Gstin":
# 				GSP_details['data']['gst'],
# 				"LglNm":
# 				company_details['data'].legal_name,
# 				"TrdNm":
# 				company_details['data'].trade_name,
# 				"Addr1":
# 				company_details['data'].address_1,
# 				"Addr2":
# 				company_details['data'].address_2,
# 				"Loc":
# 				company_details['data'].location,
# 				"Pin":
# 				193502 if company_details['data'].mode == "Testing" else
# 				company_details['data'].pincode,
# 				"Stcd":
# 				"01" if company_details['data'].mode == "Testing" else
# 				company_details['data'].state_code,
# 				"Ph":
# 				company_details['data'].phone_number,
# 				"Em":
# 				company_details['data'].email
# 			},
# 			"BuyerDtls": {
# 				"Gstin":
# 				taxpayer_details['data'].gst_number,
# 				"LglNm":
# 				taxpayer_details['data'].legal_name,
# 				"TrdNm":
# 				taxpayer_details['data'].trade_name,
# 				"Pos":
# 				"01" if company_details['data'].mode == "Testing" else
# 				company_details['data'].state_code,
# 				"Addr1":
# 				taxpayer_details['data'].address_1,
# 				"Addr2":
# 				taxpayer_details['data'].address_2,
# 				"Loc":
# 				taxpayer_details['data'].location,
# 				"Pin":
# 				int(taxpayer_details['data'].pincode),
# 				"Stcd":
# 				taxpayer_details['data'].state_code,
# 				# "Ph": taxpayer_details.phone_number,
# 				# "Em": taxpayer_details.
# 			},
# 			"DocDtls": {
# 				"Typ":
# 				"INV",
# 				"No":
# 				invoice.invoice_number + str(random.randint(0, 10000)) +
# 				'T' if company_details['data'].mode == 'Testing' else
# 				invoice.invoice_number,
# 				"Dt":
# 				datetime.datetime.strftime(invoice.invoice_date,
# 											'%d/%m/%Y')
# 			},
# 			"ItemList": [],
# 		}
# 		total_igst_value = 0
# 		total_sgst_value = 0
# 		total_cgst_value = 0
# 		ass_value = 0
# 		for index, item in enumerate(invoice.items):
# 			# print(item.sac_code,"HsnCD")
# 			if item.is_credit_item == "No" and item.taxable=="Yes":
# 				total_igst_value += item.igst_amount
# 				total_sgst_value += item.sgst_amount
# 				total_cgst_value += item.cgst_amount
# 				ass_value += item.item_value
# 				i = {
# 					"SlNo":
# 					str(index + 1),
# 					"PrdDesc":
# 					item.item_name,
# 					"IsServc":
# 					"Y",
# 					"HsnCd":
# 					item.sac_code if item.sac_code != 'No Sac' else '',
# 					"Qty":
# 					1,
# 					"FreeQty":
# 					0,
# 					"UnitPrice":
# 					round(item.item_value, 1),
# 					"TotAmt":
# 					round(item.item_value, 1),
# 					"Discount":
# 					0,
# 					"AssAmt":
# 					0 if item.sac_code == 'No Sac' else round(
# 						item.item_value, 1),
# 					"GstRt":
# 					item.gst_rate,
# 					"IgstAmt":
# 					round(item.igst_amount, 1),
# 					"CgstAmt":
# 					round(item.cgst_amount, 1),
# 					"SgstAmt":
# 					round(item.sgst_amount, 1),
# 					"CesRt":
# 					0,
# 					"CesAmt":
# 					0,
# 					"CesNonAdvlAmt":
# 					0,
# 					"StateCesRt":
# 					0,
# 					"StateCesAmt":
# 					0,
# 					"StateCesNonAdvlAmt":
# 					0,
# 					"OthChrg":
# 					00,
# 					"TotItemVal":
# 					round(item.item_value_after_gst, 2),
# 				}
# 				gst_data['ItemList'].append(i)
# 			else:
# 				credit_note_items.append(item)
# 		gst_data["ValDtls"] = {
# 			"AssVal": ass_value,
# 			"CgstVal": round(total_cgst_value, 2),
# 			"SgstVal": round(total_sgst_value, 2),
# 			"IgstVal": round(total_igst_value, 2),
# 			"CesVal": 0,
# 			"StCesVal": 0,
# 			"Discount": 0,
# 			"OthChrg": 0,
# 			"RndOffAmt": 0,
# 			"TotInvVal": round(invoice.amount_after_gst, 2),
# 			"TotInvValFc": round(invoice.amount_after_gst, 2)
# 		}
# 		response = postIrn(gst_data, GSP_details['data'])
# 		# print(response)
# 		if response['success']:
# 			invoice = frappe.get_doc('Invoices', invoice_number)
# 			invoice.ack_no = response['result']['AckNo']
# 			invoice.irn_number = response['result']['Irn']
# 			invoice.ack_date = response['result']['AckDt']
# 			invoice.signed_invoice = response['result']['SignedInvoice']
# 			invoice.signed_invoice_generated = 'Yes'
# 			invoice.irn_generated = 'Success'
# 			invoice.qr_code = response['result']['SignedQRCode']
# 			invoice.qr_code_generated = 'Success'
# 			invoice.irn_cancelled = 'No'
# 			invoice.irn_process_time = datetime.datetime.utcnow() - start_time
# 			invoice.save(ignore_permissions=True,ignore_version=True)
# 			create_qr = create_qr_image(invoice_number, GSP_details['data'])
# 			if create_qr['success'] == True:
# 				if credit_note_items != []:
# 					CreditgenerateIrn(invoice_number)
# 					invoice = frappe.get_doc('Invoices', invoice_number)
# 					invoice.irn_process_time = datetime.datetime.utcnow() - start_time
# 					invoice.save(ignore_permissions=True,ignore_version=True)
# 			return response
# 		else:
# 			return response
# 		# except Exception as e:
# 		# 	print(e, "generate Irn")

# 	def cancelIrn(self, invoice_number, reason='wrong Entry'):
# 		# try:
# 		# get invoice details
# 		invoice = frappe.get_doc('Invoices', invoice_number)
# 		# get seller details
# 		company_details = check_company_exist_for_Irn(invoice.company)
# 		# get gsp_details
# 		gsp_data = {"mode":company_details['data'].mode,"code":company_details['data'].name,"provider":company_details['data'].provider}
# 		GSP_details = gsp_api_data_for_irn(gsp_data)
# 		# GSP_details = gsp_api_data(company_details.name,
# 		# 						   company_details.mode,
# 		# 						   company_details.provider)
# 		cancel_response = cancel_irn(invoice, GSP_details, reason)
# 		print(cancel_response)
# 		if cancel_response['success']:
# 			invoice.cancelled_on = cancel_response['result']['CancelDate']
# 			invoice.cancel_message = reason
# 			invoice.irn_cancelled = 'Yes'
# 			invoice.irn_generated = 'Cancel'
# 			invoice.save()
# 			return {
# 				"success": True,
# 				"message": "E-Invoice is cancelled successfully"
# 			}
# 		else:
# 			return {"success": False, "message": "Invoice is not active"}

# 		# except Exception as e:
# 		# 	print(e,"cancel irn")

# 	def getTaxPayerDetails(self, gstNumber):
# 		try:
# 			gstDetails = frappe.get_doc('Tax Payer Details', gstNumber)
# 			return {"success": True, "data": gstDetails}
# 		except Exception as e:
# 			print(e, "get tax payer details")

# 	def updateTaxPayerDetails(self,taxPayerDetails):
# 		print(taxPayerDetails)
# 		taxPayerDeatilsData = frappe.get_doc('Tax Payer Details', taxPayerDetails['gst'])
# 		# print(taxPayerDeatils.name)
# 		taxPayerDeatilsData.address_1 = taxPayerDetails['address_1']
# 		taxPayerDeatilsData.address_2 = taxPayerDetails['address_2']
# 		taxPayerDeatilsData.email = taxPayerDetails['email']
# 		taxPayerDeatilsData.phone_number = taxPayerDetails['phone_number']
# 		taxPayerDeatilsData.legal_name= taxPayerDetails['legal_name']
# 		taxPayerDeatilsData.trade_name= taxPayerDetails['trade_name']
# 		taxPayerDeatilsData.location= taxPayerDetails['location']
# 		taxPayerDeatilsData.save()
# 		return True


# def cancel_irn(invoice, gsp, reason):
# 	try:
# 		print(gsp['data'])
# 		# input_file = "/home/caratred/Desktop/frappe/invoice/sites/jp.invoices.local/private/files/296830withQrIrn.pdf"
# 		# output_file = '/home/caratred/Desktop/frappe/invoice/sites/jp.invoices.local/private/files/canc.pdf'
# 		# watermark_file = '/home/caratred/Desktop/frappe/invoice/sites/jp.invoices.local/private/files/cancelled.pdf'
# 		# with open(input_file, "rb") as filehandle_input:
# 		#     pdf = PdfFileReader(filehandle_input)
# 		#     with open(watermark_file, "rb") as filehandle_watermark:
# 		#         watermark = PdfFileReader(filehandle_watermark)
# 		#         first_page = pdf.getPage(0)
# 		#         first_page_watermark = watermark.getPage(0)
# 		#         first_page.mergePage(first_page_watermark)
# 		#         pdf_writer = PdfFileWriter()
# 		#         pdf_writer.addPage(first_page)
# 		#         with open(output_file, "wb") as filehandle_output:
# 		#             pdf_writer.write(filehandle_output)
# 		headers = {
# 			"user_name": gsp['data']['username'],
# 			"password": gsp['data']['password'],
# 			"gstin": gsp['data']['gst'],
# 			"requestid": str(random.randint(0, 1000000000000000000)),
# 			"Authorization": "Bearer " + gsp['data']['token'],
# 		}
# 		payload = {"irn": invoice.irn_number, "cnlrem": reason, "cnlrsn": "1"}

# 		cancel_response = requests.post(gsp['data']['cancel_irn'],
# 										headers=headers,
# 										json=payload)
# 		repsone = cancel_response.json()
# 		return repsone
# 	except Exception as e:
# 		print("cancel irn", e)


# def attach_qr_code(invoice_number, gsp,code):
# 	try:
# 		invoice = frappe.get_doc('Invoices', invoice_number)
# 		company = frappe.get_doc('company',invoice.company)
# 		folder_path = frappe.utils.get_bench_path()
# 		# path = folder_path + '/sites/' + get_site_name(frappe.local.request.host)
# 		path = folder_path + '/sites/' + site_folder_path
# 		src_pdf_filename = path + invoice.invoice_file
# 		dst_pdf_filename = path + "/private/files/" + invoice_number + 'withQr.pdf'
# 		# attaching qr code
# 		img_filename = path + invoice.qr_code_image
# 		# img_rect = fitz.Rect(250, 200, 340, 270)
# 		img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1, company.qr_rect_y0, company.qr_rect_y1)		
# 		document = fitz.open(src_pdf_filename)
# 		page = document[0]
# 		page.insertImage(img_rect, filename=img_filename)
# 		document.save(dst_pdf_filename)
# 		document.close()
# 		# attacing irn an ack
# 		dst_pdf_text_filename = path + "/private/files/" + invoice_number + 'withQrIrn.pdf'
# 		doc = fitz.open(dst_pdf_filename)
# 		text = "IRN: " + invoice.irn_number + "\n" + "ACK NO: " + invoice.ack_no + "\n" + "ACK DATE: " + invoice.ack_date
# 		page = doc[0]
# 		# where = fitz.Point(15, 55)
# 		where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
# 		page.insertText(
# 			where,
# 			text,
# 			fontname="Roboto-Black",  # arbitrary if fontfile given
# 			fontfile=fontpath,  # any file containing a font
# 			fontsize=6,  # default
# 			rotate=0,  # rotate text
# 			color=(0, 0, 0),  # some color (blue)
# 			overlay=True)
# 		doc.save(dst_pdf_text_filename)
# 		doc.close()

# 		files = {"file": open(dst_pdf_text_filename, 'rb')}
# 		payload = {
# 			"is_private": 1,
# 			"folder": "Home",
# 			"doctype": "Invoices",
# 			"docname": invoice_number,
# 			'fieldname': 'invoice_with_gst_details'
# 		}
# 		upload_qr_image = requests.post(site + "api/method/upload_file",
# 										files=files,
# 										data=payload)
# 		response = upload_qr_image.json()
# 		if 'message' in response:
# 			invoice.invoice_with_gst_details = response['message']['file_url']
# 			invoice.save()
# 		return
# 	except Exception as e:
# 		print(e, "attach qr code")


# def create_qr_image(invoice_number, gsp):
# 	try:
# 		invoice = frappe.get_doc('Invoices', invoice_number)
# 		# file_path = frappe.get_site_path('private', 'files',
# 		#                                  invoice.invoice_file)
# 		folder_path = frappe.utils.get_bench_path()
# 		# path = folder_path + '/sites/' + get_site_name(frappe.local.request.host) + "/private/files/"
# 		path = folder_path + '/sites/' + site_folder_path + "/private/files/"
# 		# print(path)
# 		headers = {
# 			"user_name": gsp['username'],
# 			"password": gsp['password'],
# 			"gstin": gsp['gst'],
# 			"requestid": str(random.randint(0, 1000000000000000000)),
# 			"Authorization": "Bearer " + gsp['token'],
# 			"Irn": invoice.irn_number
# 		}
# 		qr_response = requests.get(gsp['generate_qr_code'],
# 								   headers=headers,
# 								   stream=True)
# 		file_name = invoice_number + "qr.png"
# 		full_file_path = path + file_name
# 		with open(full_file_path, "wb") as f:
# 			for chunk in qr_response.iter_content(1024):
# 				f.write(chunk)
# 		files = {"file": open(full_file_path, 'rb')}
# 		payload = {
# 			"is_private": 1,
# 			"folder": "Home",
# 			"doctype": "Invoices",
# 			"docname": invoice_number,
# 			'fieldname': 'qr_code_image'
# 		}
# 		upload_qr_image = requests.post(site + "api/method/upload_file",
# 										files=files,
# 										data=payload)
# 		response = upload_qr_image.json()
# 		if 'message' in response:
# 			invoice.qr_code_image = response['message']['file_url']
# 			invoice.save()
# 			attach_qr_code(invoice_number, gsp,invoice.company)
# 			return {"success":True}
# 		return {"success":True}
# 	except Exception as e:
# 		print(e, "qr image")
# 		return {"success":False}



# def postIrn(gst_data, gsp):
# 	try:
# 		# print(gst_data)
# 		headers = {
# 			"user_name": gsp['username'],
# 			"password": gsp['password'],
# 			"gstin": gsp['gst'],
# 			"requestid": str(random.randint(0, 1000000000000000000)),
# 			"Authorization": "Bearer " + gsp['token']
# 		}
# 		# print(headers)
# 		# print(gst_data)
# 		# print(gsp['generate_irn'])
# 		irn_response = requests.post(gsp['generate_irn'],
# 										headers=headers,
# 										json=gst_data)
# 		# print(irn_response.text)
# 		if irn_response.status_code == 200:
# 			return irn_response.json()
# 		else:
# 			return {"success": False, 'message': irn_response.text}
# 		# print(irn_response.text)
# 	except Exception as e:
# 		print(e, "post irn")



# def create_invoice(data):
# 	try:
		
# 		if data['invoice_type'] == 'B2B':
# 			# check token is valid or not
# 			isValid = check_token_is_valid(company.name, company.mode)
# 			if isValid == True:
# 				# get taxpayer details
# 				tax_payer = get_tax_payer_details(data['gstNumber'],
# 													company_code, api_details)
# 				# insert invoices
# 				a = insert_invoice(data, company_code, tax_payer)
# 			else:
# 				pass
# 		else:
# 			print("b2c")

# 		return True
# 	except Exception as e:
# 		print(e)


# def insert_invoice(data):
# 	'''
# 	insert invoice data     data, company_code, taxpayer,items_data
# 	'''
# 	try:
# 		# print(data)
# 		value_before_gst = 0
# 		value_after_gst = 0
# 		other_charges = 0
# 		credit_value_before_gst = 0
# 		credit_value_after_gst = 0
		
# 		if "legal_name" not in data['taxpayer']:
# 			data['taxpayer']['legal_name'] = " "
# 		# print(data['items_data'])
# 		#calculat items
# 		# items_data = calulate_items(data['items'], data['invoice_number'],company_code)
# 		for item in data['items_data']:
# 			if item['taxable'] == 'No':
# 				other_charges += item['item_value']

# 			elif item['sac_code'].isdigit():  
# 				if "-" not in str(item['item_value']):
# 					# has_cedit_items = Y
# 					value_before_gst += item['item_value']
# 					value_after_gst += item['item_value_after_gst']
# 				else:
# 					credit_value_before_gst += abs(item['item_value'])
# 					credit_value_after_gst  += abs(item['item_value_after_gst'])
# 			else:
# 				pass
# 		print(datetime.datetime.utcnow()-datetime.datetime.strptime(data['guest_data']['start_time'],"%Y-%m-%d %H:%M:%S.%f"))	
# 		if (round(value_after_gst,2) - round(credit_value_after_gst,2)) >0:
# 			ready_to_generate_irn = "Yes"
# 		else:
# 			ready_to_generate_irn = "No"	
# 		if credit_value_after_gst>0:
# 			has_cedit_items = "Yes"
# 		else:
# 			has_cedit_items = "No"	
# 		invoice = frappe.get_doc({
# 			'doctype':
# 			'Invoices',
			
# 			'invoice_number':
# 			data['guest_data']['invoice_number'],
# 			'guest_name':
# 			data['guest_data']['name'],
# 			'invoice_from':"Pms",
# 			'gst_number':
# 			data['guest_data']['gstNumber'],
# 			'invoice_file':
# 			data['guest_data']['invoice_file'],
# 			'room_number':
# 			data['guest_data']['room_number'],
# 			'confirmation_number':data['guest_data']['conformation_number'],
# 			'invoice_type':
# 			data['guest_data']['invoice_type'],
# 			'invoice_date':
# 			datetime.datetime.strptime(data['guest_data']['invoice_date'],
# 										'%d-%b-%y %H:%M:%S'),
# 			'legal_name':
# 			data['taxpayer']['legal_name'],
# 			'address_1':
# 			data['taxpayer']['address_1'],
# 			'email':
# 			data['taxpayer']['email'],
# 			'trade_name':
# 			data['taxpayer']['trade_name'],
# 			'address_2':
# 			data['taxpayer']['address_2'],
# 			'phone_number':
# 			data['taxpayer']['phone_number'],
# 			'location':
# 			data['taxpayer']['location'],
# 			'pincode':
# 			data['taxpayer']['pincode'],
# 			'state_code':
# 			data['taxpayer']['state_code'],
# 			'amount_before_gst':
# 			round(value_before_gst, 2),
# 			"amount_after_gst":
# 			round(value_after_gst, 2),
# 			"other_charges": round(other_charges,2),
# 			"credit_value_before_gst":round(credit_value_before_gst,2),
# 			"credit_value_after_gst":round(credit_value_after_gst,2),
# 			"pms_invoice_summary_without_gst":round(value_before_gst,2) - round(credit_value_before_gst,2),
# 			"pms_invoice_summary": round(value_after_gst,2) - round(credit_value_after_gst,2),
# 			'irn_generated':
# 			'Pending',
# 			'irn_cancelled':
# 			'No',
# 			'qr_code_generated':
# 			'Pending',
# 			'signed_invoice_generated':
# 			'No',
# 			'company':
# 			data['company_code'],
# 			'invoice_process_time': datetime.datetime.utcnow() - datetime.datetime.strptime(data['guest_data']['start_time'],"%Y-%m-%d %H:%M:%S.%f")
# 		})
# 		v = invoice.insert(ignore_permissions=True, ignore_links=True)

# 		# insert items
# 		# items = data['items_data']
# 		# items = [x for x in items if x['sac_code']!="Liquor"]
# 		itemsInsert = insert_items(data['items_data'])
# 		# insert tax summaries
# 		insert_tax_summaries(data['items_data'], data['invoice_number'])
# 		# taxSummariesInsert = insert_tax_summariesd(data['items_data'], data['guest_data']['invoice_number'])
# 		# insert sac code based taxes
# 		hsnbasedtaxcodes = insert_hsn_code_based_taxes(data['items_data'], data['guest_data']['invoice_number'])
# 		# print(itemsInsert,taxSummariesInsert,hsnbasedtaxcodes)
# 		return {"success":True}
# 	except Exception as e:
# 		print(e,"insert invoice")
# 		return {"success":False,"message":e}
		


# def insert_hsn_code_based_taxes(items, invoice_number):
# 	try:
# 		sac_codes = []
# 		for item in items:

# 			if item['sac_code'] not in sac_codes and item['sac_code'].isdigit():
# 				sac_codes.append(item['sac_code'])

# 		tax_data = []
# 		for sac in sac_codes:
# 			sac_tax = {
# 				'cgst': 0,
# 				'sgst': 0,
# 				'igst': 0,
# 				'sac_hsn_code': sac,
# 				'invoice_number': invoice_number,
# 				'doctype': "SAC HSN Tax Summaries",
# 				'parent': invoice_number,
# 				'parentfield': 'sac_hsn_based_taxes',
# 				'parenttype': "invoices"
# 			}
# 			for item in items:
# 				if item['sac_code'] == sac:
# 					sac_tax['cgst'] += item['cgst_amount']
# 					sac_tax['sgst'] += item['sgst_amount']
# 					sac_tax['igst'] += item['igst_amount']
# 			tax_data.append(sac_tax)

# 		for sac in tax_data:
# 			sac['total_amount'] = sac['cgst'] + sac['sgst'] + sac['igst']
# 			doc = frappe.get_doc(sac)
# 			doc.insert(ignore_permissions=True, ignore_links=True)
# 			return {"sucess":True,"data":doc}
# 	except Exception as e:
# 		print(e,"insert hsn")
# 		return {"success":False,"message":e}
		


# def insert_items(items):
# 	try:
# 		for item in items:
# 			print(item)
# 			# if item['sac_code'].isdigit():
# 			if "-" in str(item['item_value']):
# 				item['is_credit_item'] = "Yes"
# 			else:
# 				item['is_credit_item'] = "No"
# 			doc = frappe.get_doc(item)
# 			doc.insert(ignore_permissions=True, ignore_links=True)
# 		return {"sucess":True,"data":doc}
# 			# print(doc)
# 	except Exception as e:
# 		print(e,"********************insert itemns api")
# 		return {"success":False,"message":e}
		


# def calulate_items(data):
# 	#items, invoice_number,company_code
# 	# try:
# 	total_items = []
# 	for item in data['items']:
# 		final_item = {}
# 		calulationType = frappe.get_doc(
# 					'company', data['company_code'])
		 		
# 		if calulationType.calculation_by == "Description":
# 			sac_code_based_gst_rates = frappe.get_doc(
# 				'SAC HSN CODES', item['name'])
# 			SAC_CODE = sac_code_based_gst_rates.code 	
# 			# if sac_code_based_gst_rates.taxble == "Yes":
# 			if item['sac_code']== "No Sac" and SAC_CODE.isdigit():
# 				item['sac_code'] = sac_code_based_gst_rates.code	
# 			if "-" in str(item['item_value']):#and item['sac_code'] == '996311':
# 				final_item['cgst'] = item['cgst']
# 				final_item['cgst_amount'] = round(item['cgstAmount'], 2)
# 				final_item['sgst'] = item['sgst']
# 				final_item['sgst_amount'] = round(item['sgstAmount'], 2)
# 				final_item['igst'] = item['igst']
# 				final_item['igst_amount'] = round(item['igstAmount'], 2)
# 				final_item[
# 					'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
# 				final_item['item_value_after_gst'] = item['item_value'] + item[
# 					'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
# 				final_item['item_value'] = item['item_value']
# 				if item['sac_code'].isdigit():
# 					final_item['sac_code_found'] = 'Yes' 
# 				else:
# 					final_item['sac_code_found'] = 'No'	
# 				final_item['other_charges'] = 0	 
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble

# 			elif item['sac_code'] == '996311':
# 				final_item['cgst'] = item['cgst']
# 				final_item['cgst_amount'] = round(item['cgstAmount'], 2)
# 				final_item['sgst'] = item['sgst']
# 				final_item['sgst_amount'] = round(item['sgstAmount'], 2)
# 				final_item['igst'] = item['igst']
# 				final_item['igst_amount'] = round(item['igstAmount'], 2)
# 				final_item[
# 					'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
# 				final_item['item_value_after_gst'] = item['item_value'] + item[
# 					'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
# 				final_item['item_value'] = item['item_value']
# 				final_item['sac_code_found'] = 'Yes'  
# 				final_item['other_charges'] = 0
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble
# 			elif item['sac_code'] == '998599':	
# 				final_item['cgst'] = item['cgst']
# 				final_item['cgst_amount'] = round(item['cgstAmount'], 2)
# 				final_item['sgst'] = item['sgst']
# 				final_item['sgst_amount'] = round(item['sgstAmount'], 2)
# 				final_item['igst'] = item['igst']
# 				final_item['igst_amount'] = round(item['igstAmount'], 2)
# 				final_item[
# 					'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
# 				final_item['item_value_after_gst'] = item['item_value'] + item[
# 					'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
# 				final_item['item_value'] = item['item_value']
# 				final_item['sac_code_found'] = 'Yes'  
# 				final_item['other_charges'] = 0 
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble 
# 			elif sac_code_based_gst_rates.description == item['name'] and sac_code_based_gst_rates.taxble == "Yes":
# 				final_item['cgst'] = int(sac_code_based_gst_rates.cgst)
# 				final_item['sgst'] = int(sac_code_based_gst_rates.sgst)
# 				gst_percentage = (int(sac_code_based_gst_rates.cgst) +
# 									int(sac_code_based_gst_rates.sgst))
# 				base_value = item['item_value'] * (100 /
# 													(gst_percentage + 100))
# 				gst_value = item['item_value'] - base_value
# 				final_item['cgst_amount'] = gst_value / 2
# 				final_item['sgst_amount'] = gst_value / 2
# 				final_item['other_charges'] = 0
# 				final_item['igst'] = int(sac_code_based_gst_rates.igst)

# 				if int(sac_code_based_gst_rates.igst) <= 0:
# 					final_item['igst_amount'] = 0
# 				else:
# 					gst_percentage = (int(sac_code_based_gst_rates.cgst) +
# 										int(sac_code_based_gst_rates.sgst))
# 					base_value = item['item_value'] * (
# 						100 / (gst_percentage + 100))
# 					final_item[
# 						'igst_amount'] = item['item_value'] - base_value
# 					final_item['other_charges'] = 0
# 				final_item['gst_rate'] = int(
# 					sac_code_based_gst_rates.cgst) + int(
# 						sac_code_based_gst_rates.sgst) + int(
# 							sac_code_based_gst_rates.igst)
# 				final_item['item_value'] = round(
# 					item['item_value'] - final_item['cgst_amount'] -
# 					final_item['sgst_amount'] - final_item['igst_amount'],
# 					2)
# 				final_item['item_value_after_gst'] = item['item_value']
# 				final_item['sac_code_found'] = 'Yes'
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble

# 			else:
# 				item['sac_code'] = 'No Sac'
# 				final_item['sac_code_found'] = 'No'
# 				final_item['cgst'] = 0
# 				final_item['other_charges'] = 0
# 				final_item['cgst_amount'] = 0
# 				final_item['sgst'] = 0
# 				final_item['sgst_amount'] = 0
# 				final_item['igst'] = 0
# 				final_item['igst_amount'] = 0
# 				final_item['gst_rate'] = 0
# 				final_item['item_value_after_gst'] = item['item_value']
# 				final_item['item_value'] = item['item_value']
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble
# 		else:
# 			sac_code_based_gst_rates = frappe.get_doc(
# 				'SAC HSN CODES', item['sac_code'])
# 			if item['sac_code'] == '996311':
# 				final_item['cgst'] = item['cgst']
# 				final_item['cgst_amount'] = round(item['cgstAmount'], 2)
# 				final_item['sgst'] = item['sgst']
# 				final_item['sgst_amount'] = round(item['sgstAmount'], 2)
# 				final_item['igst'] = item['igst']
# 				final_item['igst_amount'] = round(item['igstAmount'], 2)
# 				final_item[
# 					'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
# 				final_item['item_value_after_gst'] = item['item_value'] + item[
# 					'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
# 				final_item['item_value'] = item['item_value']
# 				final_item['sac_code_found'] = 'Yes'
# 				final_item['other_charges'] = 0
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble
# 			elif item['sac_code'] == '998599':	
# 				final_item['cgst'] = item['cgst']
# 				final_item['cgst_amount'] = round(item['cgstAmount'], 2)
# 				final_item['sgst'] = item['sgst']
# 				final_item['sgst_amount'] = round(item['sgstAmount'], 2)
# 				final_item['igst'] = item['igst']
# 				final_item['igst_amount'] = round(item['igstAmount'], 2)
# 				final_item[
# 					'gst_rate'] = item['cgst'] + item['sgst'] + item['igst']
# 				final_item['item_value_after_gst'] = item['item_value'] + item[
# 					'cgstAmount'] + item['sgstAmount'] + item['igstAmount']
# 				final_item['item_value'] = item['item_value']
# 				final_item['sac_code_found'] = 'Yes'  
# 				final_item['other_charges'] = 0	
# 				final_item['taxable'] = sac_code_based_gst_rates.taxble
# 			else:
# 				if item['sac_code'].isdigit():
# 					sac_code_based_gst_rates = frappe.get_doc(
# 						'SAC HSN CODES', item['sac_code'])
# 					final_item['cgst'] = int(sac_code_based_gst_rates.cgst)
# 					final_item['sgst'] = int(sac_code_based_gst_rates.sgst)
# 					gst_percentage = (int(sac_code_based_gst_rates.cgst) +
# 									int(sac_code_based_gst_rates.sgst))
# 					# gst_value = (item['item_value']*100) /(gst_percentage+100)
# 					# print(gst_percentage,"gst percentage")
# 					base_value = item['item_value'] * (100 /
# 													(gst_percentage + 100))
# 					gst_value = item['item_value'] - base_value
# 					final_item['cgst_amount'] = gst_value / 2
# 					final_item['sgst_amount'] = gst_value / 2
# 					final_item['other_charges'] = 0
# 					final_item['igst'] = int(sac_code_based_gst_rates.igst)

# 					if int(sac_code_based_gst_rates.igst) <= 0:
# 						final_item['igst_amount'] = 0
# 					else:
# 						gst_percentage = (int(sac_code_based_gst_rates.cgst) +
# 										int(sac_code_based_gst_rates.sgst))
# 						base_value = item['item_value'] * (
# 							100 / (gst_percentage + 100))
# 						final_item[
# 							'igst_amount'] = item['item_value'] - base_value

# 					final_item['gst_rate'] = int(
# 						sac_code_based_gst_rates.cgst) + int(
# 							sac_code_based_gst_rates.sgst) + int(
# 								sac_code_based_gst_rates.igst)
# 					final_item['item_value'] = round(
# 						item['item_value'] - final_item['cgst_amount'] -
# 						final_item['sgst_amount'] - final_item['igst_amount'],
# 						2)
# 					final_item['item_value_after_gst'] = item['item_value']
# 					final_item['sac_code_found'] = 'Yes'
# 					final_item['other_charges'] = 0
# 					final_item['taxable'] = sac_code_based_gst_rates.taxble
# 				else:
# 					item['sac_code'] = 'No Sac'
# 					final_item['sac_code_found'] = 'No'
# 					final_item['cgst'] = 0
# 					final_item['cgst_amount'] = 0
# 					final_item['sgst'] = 0
# 					final_item['sgst_amount'] = 0
# 					final_item['igst'] = 0
# 					final_item['igst_amount'] = 0
# 					final_item['gst_rate'] = 0
# 					final_item['item_value_after_gst'] = item['item_value']
# 					final_item['item_value'] = item['item_value']
# 					final_item['other_charges'] = 0
# 					final_item['taxable'] = sac_code_based_gst_rates.taxble
# 		total_items.append({
# 			'doctype':
# 			'Items',
# 			'sac_code':
# 			item['sac_code'],
# 			'item_name':
# 			item['name'],
# 			'date':
# 			datetime.datetime.strptime(item['date'], '%Y-%m-%d'),
# 			'cgst':
# 			final_item['cgst'],
# 			'cgst_amount':
# 			round(final_item['cgst_amount'], 2),
# 			'sgst':
# 			final_item['sgst'],
# 			'sgst_amount':
# 			round(final_item['sgst_amount'], 2),
# 			'igst':
# 			final_item['igst'],
# 			'igst_amount':
# 			round(final_item['igst_amount'], 2),
# 			'item_value':
# 			final_item['item_value'],
# 			'description':
# 			item['name'],
# 			'item_taxable_value':
# 			final_item['item_value'],
# 			'gst_rate':
# 			final_item['gst_rate'],
# 			'item_value_after_gst':
# 			round(final_item['item_value_after_gst'], 2),
# 			'parent':
# 			data['invoice_number'],
# 			'parentfield':
# 			'items',
# 			'parenttype':
# 			"invoices",
# 			'sac_code_found':
# 			final_item['sac_code_found'],
# 			'other_charges': final_item['other_charges'],
# 			'taxable':final_item['taxable']
# 		})
# 	return {"success":True,"data":total_items}
# 	# except Exception as e:
# 	# 	print(e, "calculation api")
# 	# 	return {"success":False,"message":e}
		


# def insert_tax_summariesd(items, invoice_number):
# 	try:
# 		tax_list = []
# 		for item in items:
# 			if item['sgst'] > 0:
# 				dup_dict = {
# 					'tax_type': 'SGST',
# 					'tax_percentage': item['sgst'],
# 					'amount': 0
# 				}
# 				if dup_dict not in tax_list:
# 					tax_list.append(dup_dict)
# 			if item['cgst'] > 0:
# 				dup_dict = {
# 					'tax_type': 'CGST',
# 					'tax_percentage': item['cgst'],
# 					'amount': 0
# 				}
# 				if dup_dict not in tax_list:
# 					tax_list.append(dup_dict)
# 			if item['igst'] > 0:
# 				dup_dict = {
# 					'tax_type': 'IGST',
# 					'tax_percentage': item['igst'],
# 					'amount': 0
# 				}
# 				if dup_dict not in tax_list:
# 					tax_list.append(dup_dict)

# 		for tax in tax_list:
# 			for item in items:
# 				# print(item)
# 				if item['sgst'] > 0 and tax['tax_type'] == 'SGST' and item[
# 						'sgst'] == tax['tax_percentage']:
# 					tax['amount'] += item['sgst_amount']
# 				if item['cgst'] > 0 and tax['tax_type'] == 'CGST' and item[
# 						'cgst'] == tax['tax_percentage']:
# 					tax['amount'] += item['cgst_amount']
# 				if item['igst'] > 0 and tax['tax_type'] == 'IGST' and item[
# 						'igst'] == tax['tax_percentage']:
# 					tax['amount'] += item['igst_amount']
# 			# print('*************************************8')

# 		for tax in tax_list:
# 			doc = frappe.get_doc({
# 				'doctype': 'Tax Summaries',
# 				'invoce_number': invoice_number,
# 				'tax_percentage': tax['tax_percentage'],
# 				'amount': tax['amount'],
# 				'tax_type': tax['tax_type'],
# 				'parent': invoice_number,
# 				'parentfield': 'gst_summary',
# 				'parenttype': "Invoices"
# 			})
# 			doc.insert(ignore_permissions=True)
# 		return {"success":True}
# 	except Exception as e:
# 		print('tax', e)
# 		return {'succes':False,"message":e}
		

# def insert_tax_summaries(items, invoice_number):
# 	'''
# 	insert tax_summaries into tax_summaries table
# 	'''
# 	try:
# 		tax_summaries = []
# 		for item in items:
# 			if len(tax_summaries) > 0:
# 				found = False
# 				for tax in tax_summaries:
# 					found = False
# 					if item['sgst'] > 0:
# 						if tax['tax_type'] == 'SGST' and tax[
# 								'tax_percentage'] == item['sgst']:
# 							tax['amount'] += item['sgst_amount']
# 							found = True
# 					if item['cgst'] > 0:
# 						if tax['tax_type'] == 'CGST' and tax[
# 								'tax_percentage'] == item['cgst']:
# 							tax['amount'] += item['cgst_amount']
# 							found = True
# 					if item['igst'] > 0:
# 						if tax['tax_type'] == 'IGST' and tax[
# 								'tax_percentage'] == item['igst']:
# 							tax['amount'] += item['igst_amount']
# 							found = True
# 				if found == False:
# 					if item['sgst'] > 0:
# 						summary = {}
# 						summary['tax_type'] = 'SGST'
# 						summary['tax_percentage'] = item['sgst']
# 						summary['amount'] = item['sgst_amount']
# 						summary['invoice_number'] = invoice_number
# 						tax_summaries.append(summary)
# 					if item['cgst'] > 0:
# 						summary = {}
# 						summary['tax_type'] = 'CGST'
# 						summary['tax_percentage'] = item['cgst']
# 						summary['amount'] = item['cgst_amount']
# 						summary['invoice_number'] = invoice_number
# 						tax_summaries.append(summary)
# 					if item['igst'] > 0:
# 						summary = {}
# 						summary['tax_type'] = 'IGST'
# 						summary['tax_percentage'] = item['igst']
# 						summary['amount'] = item['igst_amount']
# 						summary['invoice_number'] = invoice_number
# 						tax_summaries.append(summary)
# 			else:
# 				if item['sgst'] > 0:
# 					summary = {}
# 					summary['tax_type'] = 'SGST'
# 					summary['tax_percentage'] = item['sgst']
# 					summary['amount'] = item['sgst_amount']
# 					summary['invoice_number'] = invoice_number
# 					tax_summaries.append(summary)
# 				if item['cgst'] > 0:
# 					summary = {}
# 					summary['tax_type'] = 'CGST'
# 					summary['tax_percentage'] = item['cgst']
# 					summary['amount'] = item['cgst_amount']
# 					summary['invoice_number'] = invoice_number
# 					tax_summaries.append(summary)
# 				if item['igst'] > 0:
# 					summary = {}
# 					summary['tax_type'] = 'IGST'
# 					summary['tax_percentage'] = item['igst']
# 					summary['amount'] = item['igst_amount']
# 					summary['invoice_number'] = invoice_number
# 					tax_summaries.append(summary)
# 		actual_summaries = [
# 			tax_summaries[0],
# 		]
# 		for tax in tax_summaries:
# 			found = False
# 			for actual in actual_summaries:
# 				found = False
# 				if tax['tax_type'] == actual['tax_type'] and tax[
# 						'tax_percentage'] == actual['tax_percentage']:
# 					actual['amount'] += tax['amount']
# 					found = True
# 			if found == False:
# 				actual_summaries.append(tax)

# 		for i in actual_summaries:
# 			print(i)

# 		for tax in tax_summaries:
# 			doc = frappe.get_doc({
# 				'doctype': 'Tax Summaries',
# 				'invoce_number': tax['invoice_number'],
# 				'tax_percentage': tax['tax_percentage'],
# 				'amount': tax['amount'],
# 				'tax_type': tax['tax_type'],
# 				'parent': invoice_number,
# 				'parentfield': 'gst_summary',
# 				'parenttype': "Invoices"
# 			})
# 			doc.insert(ignore_permissions=True)

# 	except Exception as e:
# 		print(e,'insert tax summerie')


# def get_tax_payer_details(data):
# 	'''
# 	get tax payer details from gsp   gstNumber, code, apidata
# 	'''
# 	try:

# 		tay_payer_details = frappe.db.get_value('Tax Payer Details', data['gstNumber'])
# 		if tay_payer_details is None:
# 			response = request_get(data['apidata']['get_taxpayer_details'] + data['gstNumber'],
# 									data['apidata'],data['invoice'])
# 			if response['success']:
					
# 				details = response['result']
# 				if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
# 					if (details['AddrBno'] != "") or (details['AddrBno'] != ""):
# 						details['AddrBnm'] = details['AddrBno']
# 				if (details['AddrBno'] == "") or (details['AddrBno'] == None):
# 					if (details['AddrBnm'] != "") or (details['AddrBnm'] != None):
# 						details['AddrBno'] = details['AddrBnm']
# 				if (details['TradeName'] == "") or (details['TradeName'] == None):
# 					if (details['LegalName'] != "") or (details['TradeName'] !=None):
# 						details['TradeName'] = details['LegalName']
# 				if (details['LegalName'] == "") or (details['LegalName'] == None):
# 					if (details['TradeName'] != "") or (details['TradeName'] != None):
# 						details['LegalName'] = details['TradeName']
# 				if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
# 					details['AddrLoc'] = "New Delhi"		
				
# 				if len(details["AddrBnm"]) < 3:
# 					details["AddrBnm"] = details["AddrBnm"]+"    "
# 				if len(details["AddrBno"]) < 3:
# 					details["AddrBno"] = details["AddrBno"] + "    " 		
# 				tax_payer = frappe.get_doc({
# 					'doctype':
# 					'Tax Payer Details',
# 					"gst_number":
# 					details['Gstin'],
# 					"email": " ",
# 					"phone_number": " ",
# 					"legal_name":
# 					details['LegalName'],
# 					"address_1":
# 					details['AddrBnm'],
# 					"address_2":
# 					details['AddrBno'],
# 					"location":
# 					details['AddrLoc'],
# 					"pincode":
# 					details['AddrPncd'],
# 					"gst_status":
# 					details['Status'],
# 					"tax_type":
# 					details['TxpType'],
# 					"company":
# 					data['code'],
# 					"trade_name":
# 					details['TradeName'],
# 					"state_code":
# 					details['StateCode'],
# 					"last_fetched":
# 					datetime.date.today(),
# 					"address_floor_number":
# 					details['AddrFlno'],
# 					"address_street":
# 					details['AddrSt'],
# 					"block_status":
# 					''
# 					if details['BlkStatus'] == None else details['BlkStatus'],
# 					"status":
# 					"Active"
# 				})

# 				doc = tax_payer.insert(ignore_permissions=True)
# 				return {"success":True,"data":doc}
# 			else:
# 				print("Unknown error in get taxpayer details get call  ",response)	
# 				return {"success":False,"message":"Unknown error in get taxpayer details","response":response}

# 		else:
# 			doc = frappe.get_doc('Tax Payer Details', data['gstNumber'])
# 			return {"success":True,"data":doc}
# 	except Exception as e:
# 		print(e,"get tax payers")
# 		return {"success":False,"message":e}
	   


# def check_company_exist(code):
# 	try:
# 		company = frappe.get_doc('company', code)
# 		return {"success":True,"data":company}
# 	except Exception as e:
# 		print(e,"check company exist")
# 		return {"success":False,"message":e}
		


# def check_company_exist_for_Irn(code):
# 	try:
# 		company = frappe.get_doc('company', code)
# 		return {"success":True,"data":company}
# 	except Exception as e:
# 		print(e,"check company exist")
# 		return {"success":False,"message":e}
		




# def check_token_is_valid(data):
# 	try:
# 		login_gsp(data['code'], data['mode'])
# 		gsp = frappe.db.get_value(
# 			'GSP APIS', {"company": data['code']},
# 			['gsp_test_token_expired_on', 'gsp_prod_token_expired_on'],
# 			as_dict=1)
# 		if gsp['gsp_test_token_expired_on'] != '' or gsp[
# 				'gsp_prod_token_expired_on']:
# 			expired_on = gsp[
# 				'gsp_test_token_expired_on'] if data['mode'] == 'Testing' else gsp[
# 					'gsp_prod_token_expired_on']
# 			print(expired_on)
# 			return {"success":True}
# 		else:
# 			login_gsp(data['code'], data['mode'])
# 			return {"success":True}

# 	except Exception as e:
# 		print(e,"check token is valid")
# 		return {"success":False,"message":e}
		


# def login_gsp(code, mode):
# 	try:
# 		gsp = frappe.db.get_value('GSP APIS', {"company": code}, [
# 			'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
# 			'gsp_prod_app_secret', 'gsp_test_app_secret', 'name'
# 		],
# 								  as_dict=1)
# 		if mode == 'Testing':
# 			headers = {
# 				"gspappid": gsp["gsp_test_app_id"],
# 				"gspappsecret": gsp["gsp_test_app_secret"],
# 			}
# 			login_response = request_post(gsp['auth_test'], headers)

# 			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
# 			gsp_update.gsp_test_token_expired_on = login_response['expires_in']
# 			gsp_update.gsp_test_token = login_response['access_token']
# 			gsp_update.save(ignore_permissions=True)
# 			return True
# 		elif mode == 'Production':
# 			headers = {
# 				"gspappid": gsp["gsp_prod_app_id"],
# 				"gspappsecret": gsp["gsp_prod_app_secret"]
# 			}
# 			login_response = request_post(gsp['auth_prod'], headers)
# 			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
# 			gsp_update.gsp_prod_token_expired_on= login_response['expires_in']
# 			gsp_update.gsp_prod_token = login_response['access_token']
# 			gsp_update.save(ignore_permissions=True)
# 			return True
# 	except Exception as e:
# 		print(e,"login gsp")


# def gsp_api_data(data):
# 	try:
# 		mode = data['mode']
# 		gsp_apis = frappe.db.get_value('GSP APIS', {
# 			"company": data['code'],
# 			"name": data['provider'],
# 		}, [
# 			'auth_test', 'cancel_test_irn', 'extract_prod_qr_code',
# 			'extract_test_qr_code', 'extract_test_signed_invoice',
# 			'generate_prod_irn', 'generate_test_irn',
# 			'generate_test_qr_code_image', 'get_tax_payer_prod',
# 			'get_tax_payer_test', 'get_test_irn', 'get_test_qr_image',
# 			'auth_prod', 'cancel_prod_irn', 'extract_prod_qr_code',
# 			'extract_prod_signed_invoice', 'generate_prod_irn',
# 			'generate_prod_qr_code_image', 'get_prod_irn', 'get_prod_qr_image',
# 			'get_tax_payer_prod', 'gsp_prod_app_id', 'gsp_prod_app_secret',
# 			'gsp_test_app_id', 'gsp_test_app_secret', 'gsp_test_token',
# 			'gst__prod_username', 'gst__test_username', 'gst_prod_password',
# 			'gst_test_password', 'gsp_prod_token', 'gst_test_number',
# 			'gst_prod_number',
# 		],
# 									   as_dict=1)
# 		api_details = dict()
# 		api_details['auth'] = gsp_apis[
# 			'auth_test'] if mode == 'Testing' else gsp_apis['auth_prod']
# 		api_details['generate_irn'] = gsp_apis[
# 			'generate_test_irn'] if mode == 'Testing' else gsp_apis[
# 				'generate_prod_irn']
# 		api_details['cancel_irn'] = gsp_apis[
# 			'cancel_test_irn'] if mode == 'Testing' else gsp_apis[
# 				'cancel_prod_irn']
# 		api_details['get_taxpayer_details'] = gsp_apis[
# 			'get_tax_payer_test'] if mode == 'Testing' else gsp_apis[
# 				'get_tax_payer_prod']
# 		api_details['generate_qr_code'] = gsp_apis[
# 			'generate_test_qr_code_image'] if mode == 'Testing' else gsp_apis[
# 				'generate_prod_qr_code_image']
# 		api_details['generate_signed_qr_code'] = gsp_apis[
# 			'extract_test_signed_invoice'] if mode == 'Testing' else gsp_apis[
# 				'extract_prod_signed_invoice']
# 		api_details['username'] = gsp_apis[
# 			'gst__test_username'] if mode == 'Testing' else gsp_apis[
# 				'gst__prod_username']
# 		api_details['password'] = gsp_apis[
# 			'gst_test_password'] if mode == 'Testing' else gsp_apis[
# 				'gst_prod_password']
# 		api_details['appId'] = gsp_apis[
# 			'gsp_test_app_id'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_app_id']
# 		api_details['secret'] = gsp_apis[
# 			'gsp_test_app_secret'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_app_secret']
# 		api_details['token'] = gsp_apis[
# 			'gsp_test_token'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_token']
# 		api_details['gst'] = gsp_apis[
# 			'gst_test_number'] if mode == 'Testing' else gsp_apis[
# 				'gst_prod_number']
	
# 		return {"success":True,"data":api_details}
# 	except Exception as e:
# 		print(e,"gsp api details")
# 		return {"success":False,"message":e}
		


# def gsp_api_data_for_irn(data):
# 	try:
# 		mode = data['mode']
# 		gsp_apis = frappe.db.get_value('GSP APIS', {
# 			"company": data['code'],
# 			"name": data['provider'],
# 		}, [
# 			'auth_test', 'cancel_test_irn', 'extract_prod_qr_code',
# 			'extract_test_qr_code', 'extract_test_signed_invoice',
# 			'generate_prod_irn', 'generate_test_irn',
# 			'generate_test_qr_code_image', 'get_tax_payer_prod',
# 			'get_tax_payer_test', 'get_test_irn', 'get_test_qr_image',
# 			'auth_prod', 'cancel_prod_irn', 'extract_prod_qr_code',
# 			'extract_prod_signed_invoice', 'generate_prod_irn',
# 			'generate_prod_qr_code_image', 'get_prod_irn', 'get_prod_qr_image',
# 			'get_tax_payer_prod', 'gsp_prod_app_id', 'gsp_prod_app_secret',
# 			'gsp_test_app_id', 'gsp_test_app_secret', 'gsp_test_token',
# 			'gst__prod_username', 'gst__test_username', 'gst_prod_password',
# 			'gst_test_password', 'gsp_prod_token', 'gst_test_number',
# 			'gst_prod_number',
# 		],
# 									   as_dict=1)
# 		api_details = dict()
# 		api_details['auth'] = gsp_apis[
# 			'auth_test'] if mode == 'Testing' else gsp_apis['auth_prod']
# 		api_details['generate_irn'] = gsp_apis[
# 			'generate_test_irn'] if mode == 'Testing' else gsp_apis[
# 				'generate_prod_irn']
# 		api_details['cancel_irn'] = gsp_apis[
# 			'cancel_test_irn'] if mode == 'Testing' else gsp_apis[
# 				'cancel_prod_irn']
# 		api_details['get_taxpayer_details'] = gsp_apis[
# 			'get_tax_payer_test'] if mode == 'Testing' else gsp_apis[
# 				'get_tax_payer_prod']
# 		api_details['generate_qr_code'] = gsp_apis[
# 			'generate_test_qr_code_image'] if mode == 'Testing' else gsp_apis[
# 				'generate_prod_qr_code_image']
# 		api_details['generate_signed_qr_code'] = gsp_apis[
# 			'extract_test_signed_invoice'] if mode == 'Testing' else gsp_apis[
# 				'extract_prod_signed_invoice']
# 		api_details['username'] = gsp_apis[
# 			'gst__test_username'] if mode == 'Testing' else gsp_apis[
# 				'gst__prod_username']
# 		api_details['password'] = gsp_apis[
# 			'gst_test_password'] if mode == 'Testing' else gsp_apis[
# 				'gst_prod_password']
# 		api_details['appId'] = gsp_apis[
# 			'gsp_test_app_id'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_app_id']
# 		api_details['secret'] = gsp_apis[
# 			'gsp_test_app_secret'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_app_secret']
# 		api_details['token'] = gsp_apis[
# 			'gsp_test_token'] if mode == 'Testing' else gsp_apis[
# 				'gsp_prod_token']
# 		api_details['gst'] = gsp_apis[
# 			'gst_test_number'] if mode == 'Testing' else gsp_apis[
# 				'gst_prod_number']
# 		# print(api_details)
# 		# print(api_details)
# 		return {"success":True,"data":api_details}
# 	except Exception as e:
# 		print(e,"gsp api details")
# 		return {"success":False,"message":e}
		



# def request_post(url, headers=None):
# 	try:
# 		data = requests.post(url, headers=headers)
# 		if data.status_code == 200:
# 			response_data = data.json()
# 			if 'access_token' in response_data:
# 				return response_data
# 			else:
# 				print(response_data)
# 		else:
# 			print(data)
# 	except Exception as e:
# 		print(e,"request post")


# def request_get(api, headers,invoice):
# 	try:
# 		headers = {
# 			"user_name": headers["username"],
# 			"password": headers["password"],
# 			"gstin": headers['gst'],
# 			"requestid": invoice+str(random.randrange(1, 10**4)),
# 			"Authorization": "Bearer " + headers['token']
# 		}
# 		raw_response = requests.get(api, headers=headers)
# 		# print(raw_response.json())
# 		if raw_response.status_code == 200:
# 			return raw_response.json()
# 		else:
# 			print(raw_response.text)
# 	except Exception as e:
# 		print(e,"request get")




# def check_gstNumber_Length(data):

# 	print("Error:  *******The given gst number is not a vaild one**********")
# 	return {"success":False,"Message":"The given gst number is not a vaild one"}
	




# def check_invoice_file_exists(data):
# 	try:
# 		invoiceExists = frappe.get_value('File',
# 		{"attached_to_name": data['invoice']})
# 		# invoiceExists=frappe.db.get_list('File', filters={
# 		# 	'file_name': ['like', '%'+data['invoice']+'%']})	
# 		if invoiceExists:
# 			filedata = frappe.get_doc('File',invoiceExists)
# 			# print(filedata.__dict__)
# 			return {"success":True,"data":filedata}
# 		return {"success":False}
# 	except Exception as e:
# 		print(e,"check company exist")
# 		return {"success":False,"message":e}


 


# def Error_Insert_invoice(data):
# 	try:
# 		invoice = frappe.get_doc({
# 				'doctype':
# 				'Invoices',
				
# 				'invoice_number':
# 				data['invoice_number'],
# 				'guest_name':data['guest_name'],
# 				'gst_number': data['gst_number'],
# 				'invoice_file':
# 				data['invoice_file'],
# 				'room_number': data['room_number'],
# 				'invoice_type': 
# 				data['invoice_type'],
# 				'invoice_date':
# 				datetime.datetime.strptime(data['invoice_date'],
# 											'%d-%b-%y %H:%M:%S'),
# 				'legal_name': " ",
# 				# data['taxpayer']['legal_name'],
# 				'address_1':" ",
# 				# data['taxpayer']['address_1'],
# 				'email':" ",
# 				# data['taxpayer']['email'],
# 				'trade_name':" ",
# 				# data['taxpayer']['trade_name'],
# 				'address_2': " ",
# 				# data['taxpayer']['address_2'],
# 				'phone_number': " ",
# 				# data['taxpayer']['phone_number'],
# 				'location': " ",
# 				# data['taxpayer']['location'],
# 				'pincode':
# 				data['pincode'],
# 				'state_code':
# 				data['state_code'],
# 				'amount_before_gst': 0,
# 				# round(value_before_gst, 2),
# 				"amount_after_gst": 0,
# 				# round(value_after_gst, 2),
# 				"other_charges":0,# round(other_charges,2),
# 				'irn_generated':
# 				'Pending',
# 				'irn_cancelled':
# 				'No',
# 				'qr_code_generated':
# 				'Pending',
# 				'signed_invoice_generated':
# 				'No',
# 				'company':
# 				data['company_code'],
# 				'ready_to_generate_irn':"No",
# 				'error_message':data['error_message']
# 			})
# 		v = invoice.insert(ignore_permissions=True, ignore_links=True)
# 	except Exception as e:
# 		print(e,"  Error insert Invoice")
# 		return {"success":False,"message":str(e)}










