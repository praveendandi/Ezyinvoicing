from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import random
from frappe.utils import logger
from frappe.utils import get_site_name
import time

from PyPDF2 import PdfFileWriter, PdfFileReader
# import fitz

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)


def check_company_exist_for_Irn(code):
	try:
		company = frappe.get_doc('company', code)
		return {"success":True,"data":company}
	except Exception as e:
		print(e,"check company exist")
		return {"success":False,"message":e}


def attach_qr_code(invoice_number, gsp,code):
	try:
		invoice = frappe.get_doc('Invoices', invoice_number)
		company = frappe.get_doc('company',invoice.company)
		folder_path = frappe.utils.get_bench_path()
		site_folder_path = company.site_name
		# path = folder_path + '/sites/' + get_site_name(frappe.local.request.host)
		path = folder_path + '/sites/' + site_folder_path
		src_pdf_filename = path + invoice.invoice_file
		dst_pdf_filename = path + "/private/files/" + invoice_number + 'withCreditQr.pdf'
		# attaching qr code
		img_filename = path + invoice.credit_qr_code_image
		# img_rect = fitz.Rect(250, 200, 340, 270)
		img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1, company.qr_rect_y0, company.qr_rect_y1)
		document = fitz.open(src_pdf_filename)
		page = document[0]
		im = open(img_filename,"rb").read()
		page.insertImage(img_rect, stream=im)
		document.save(dst_pdf_filename)
		document.close()
		# attacing irn an ack
		dst_pdf_text_filename = path + "/private/files/" + invoice_number + 'withCreditQrIrn.pdf'
		doc = fitz.open(dst_pdf_filename)
		# text = "IRN: " + invoice.credit_irn_number + "      " + "ACK NO: " + invoice.credit_ack_no + "\n" + "ACK DATE: " + invoice.credit_ack_date
		ackdate = invoice.credit_ack_date
		ack_date = ackdate.split(" ")
		text = "IRN: " + invoice.credit_irn_number +"          "+ "ACK NO: " + invoice.credit_ack_no + "       " + "ACK DATE: " + ack_date[0]
		if company.irn_details_page == "First":
			page = doc[0]
		else:
			page = doc[-1]
		# page = doc[0]
		where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
		page.insertText(
			where,
			text,
			fontname="Roboto-Black",  # arbitrary if fontfile given
			fontfile=folder_path+company.font_file_path,#fontpath,  # any file containing a font
			fontsize=7,  # default
			rotate=0,  # rotate text
			color=(0, 0, 0),  # some color (blue)
			overlay=True)
		doc.save(dst_pdf_text_filename)
		doc.close()

		files = {"file": open(dst_pdf_text_filename, 'rb')}
		payload = {
			"is_private": 1,
			"folder": "Home",
			"doctype": "Invoices",
			"docname": invoice_number,
			'fieldname': 'invoice_with_credit_gst_details'
		}
		site = company.host
		upload_qr_image = requests.post(site + "api/method/upload_file",
										files=files,
										data=payload)
		# print(upload_qr_image)
		response = upload_qr_image.json()
		if 'message' in response:
			invoice.invoice_with_credit_gst_details = response['message']['file_url']
			invoice.save()
		return
	except Exception as e:
		print(e, "attach qr code")


def create_credit_qr_image(invoice_number, gsp):
	try:
		invoice = frappe.get_doc('Invoices', invoice_number)
		# file_path = frappe.get_site_path('private', 'files',
		#                                  invoice.invoice_file)
		company = frappe.get_doc('company',invoice.company)
		folder_path = frappe.utils.get_bench_path()
		site_folder_path = company.site_name
		# path = folder_path + '/sites/' + get_site_name(frappe.local.request.host) + "/private/files/"
		path = folder_path + '/sites/' + site_folder_path + "/private/files/"
		# print(path)
		headers = {
			"user_name": gsp['username'],
			"password": gsp['password'],
			"gstin": gsp['gst'],
			"requestid": str(random.randint(0, 1000000000000000000)),
			"Authorization": "Bearer " + gsp['token'],
			"Irn": invoice.credit_irn_number
			
		}
		if company.proxy == 0:
			qr_response = requests.get(gsp['generate_qr_code'],
										headers=headers,
										stream=True)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://","@")
			proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
			print(proxies, "     proxy console")
			qr_response = requests.get(gsp['generate_qr_code'],
										headers=headers,
										stream=True,proxies=proxies,verify=False)

		file_name = invoice_number + "creditqr.png"
		full_file_path = path + file_name
		with open(full_file_path, "wb") as f:
			for chunk in qr_response.iter_content(1024):
				f.write(chunk)
		files = {"file": open(full_file_path, 'rb')}
		payload = {
			"is_private": 1,
			"folder": "Home",
			"doctype": "Invoices",
			"docname": invoice_number,
			'fieldname': 'credit_qr_code_image'
		}
		site = company.host
		upload_qr_image = requests.post(site + "api/method/upload_file",
										files=files,
										data=payload)
		response = upload_qr_image.json()
		if 'message' in response:
			invoice.credit_qr_code_image = response['message']['file_url']
			invoice.save()
			attach_qr_code(invoice_number, gsp,invoice.company)

		return True
	except Exception as e:
		print(e, " credit qr image")

def request_get_data(api, headers,invoice,code):
	try:
		company = check_company_exist_for_Irn(code)
		
		headers = {
			"user_name": headers["username"],
			"password": headers["password"],
			"gstin": headers['gst'],
			"requestid": invoice+str(random.randrange(1, 10**4)),
			"Authorization": "Bearer " + headers['token']
		}
		if company.proxy == 0:
			raw_response = requests.get(api, headers=headers)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://","@")
			proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
			print(proxies, "     proxy console")
			raw_response = requests.get(api, headers=headers,proxies=proxies,verify=False)
	
		# print(raw_response.json())
		if raw_response.status_code == 200:
			return raw_response.json()
		else:
			print(raw_response.text)
	except Exception as e:
		print(e,"request get")



def get_tax_payer_details_data(data):
	'''
	get TaxPayerDetail from gsp   gstNumber, code, apidata
	'''
	try:
		tay_payer_details = frappe.db.get_value('TaxPayerDetail', data['gstNumber'])
		if tay_payer_details is None:
			response = request_get_data(data['apidata']['get_taxpayer_details'] + data['gstNumber'],
									data['apidata'],data['invoice'],data['code'])
			if response['success']:
				
				details = response['result']
				if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
					if (details['AddrBno'] != "") or (details['AddrBno'] != ""):
						details['AddrBnm'] = details['AddrBno']
				if (details['AddrBno'] == "") or (details['AddrBno'] == None):
					if (details['AddrBnm'] != "") or (details['AddrBnm'] != None):
						details['AddrBno'] = details['AddrBnm']
				if (details['TradeName'] == "") or (details['TradeName'] == None):
					if (details['LegalName'] != "") or (details['TradeName'] !=None):
						details['TradeName'] = details['LegalName']
				if (details['LegalName'] == "") or (details['LegalName'] == None):
					if (details['TradeName'] != "") or (details['TradeName'] != None):
						details['LegalName'] = details['TradeName']
				if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
					details['AddrLoc'] = "       "	
				if len(details["AddrBnm"]) < 3:
					details["AddrBnm"] = details["AddrBnm"]+"    "
				if len(details["AddrBno"]) < 3:
					details["AddrBno"] = details["AddrBno"] + "    " 	
				tax_payer = frappe.get_doc({
					'doctype':
					'TaxPayerDetail',
					"gst_number":
					details['Gstin'],
					"email": " ",
					"phone_number": " ",
					"legal_name":
					details['LegalName'],
					"address_1":
					details['AddrBnm'],
					"address_2":
					details['AddrBno'],
					"location":
					details['AddrLoc'],
					"pincode":
					details['AddrPncd'],
					"gst_status":
					details['Status'],
					"tax_type":
					details['TxpType'],
					"company":
					data['code'],
					"trade_name":
					details['TradeName'],
					"state_code":
					details['StateCode'],
					"last_fetched":
					datetime.date.today(),
					"address_floor_number":
					details['AddrFlno'],
					"address_street":
					details['AddrSt'],
					"block_status":
					''
					if details['BlkStatus'] == None else details['BlkStatus'],
					"status":
					"Active"
				})

				doc = tax_payer.insert(ignore_permissions=True)
				return {"success":True,"data":doc}
			else:
				print("Unknown error in get taxpayer details get call  ",response)	
				return {"success":False,"message":"Unknown error in get taxpayer details","response":response}

		else:
			doc = frappe.get_doc('TaxPayerDetail', data['gstNumber'])
			return {"success":True,"data":doc}
	except Exception as e:
		print(e,"get tax payers")
		return {"success":False,"message":e}
	   

def creditgsp_api_data(data):
	try:
		mode = data['mode']
		gsp_apis = frappe.db.get_value('GSP APIS', {
			"company": data['code'],
			"name": data['provider'],
		}, [
			'auth_test', 'cancel_test_irn', 'extract_prod_qr_code',
			'extract_test_qr_code', 'extract_test_signed_invoice',
			'generate_prod_irn', 'generate_test_irn',
			'generate_test_qr_code_image', 'get_tax_payer_prod',
			'get_tax_payer_test', 'get_test_irn', 'get_test_qr_image',
			'auth_prod', 'cancel_prod_irn', 'extract_prod_qr_code',
			'extract_prod_signed_invoice', 'generate_prod_irn',
			'generate_prod_qr_code_image', 'get_prod_irn', 'get_prod_qr_image',
			'get_tax_payer_prod', 'gsp_prod_app_id', 'gsp_prod_app_secret',
			'gsp_test_app_id', 'gsp_test_app_secret', 'gsp_test_token',
			'gst__prod_username', 'gst__test_username', 'gst_prod_password',
			'gst_test_password', 'gsp_prod_token', 'gst_test_number',
			'gst_prod_number',
		],
									   as_dict=1)
		api_details = dict()
		api_details['auth'] = gsp_apis[
			'auth_test'] if mode == 'Testing' else gsp_apis['auth_prod']
		api_details['generate_irn'] = gsp_apis[
			'generate_test_irn'] if mode == 'Testing' else gsp_apis[
				'generate_prod_irn']
		api_details['cancel_irn'] = gsp_apis[
			'cancel_test_irn'] if mode == 'Testing' else gsp_apis[
				'cancel_prod_irn']
		api_details['get_taxpayer_details'] = gsp_apis[
			'get_tax_payer_test'] if mode == 'Testing' else gsp_apis[
				'get_tax_payer_prod']
		api_details['generate_qr_code'] = gsp_apis[
			'generate_test_qr_code_image'] if mode == 'Testing' else gsp_apis[
				'generate_prod_qr_code_image']
		api_details['generate_signed_qr_code'] = gsp_apis[
			'extract_test_signed_invoice'] if mode == 'Testing' else gsp_apis[
				'extract_prod_signed_invoice']
		api_details['username'] = gsp_apis[
			'gst__test_username'] if mode == 'Testing' else gsp_apis[
				'gst__prod_username']
		api_details['password'] = gsp_apis[
			'gst_test_password'] if mode == 'Testing' else gsp_apis[
				'gst_prod_password']
		api_details['appId'] = gsp_apis[
			'gsp_test_app_id'] if mode == 'Testing' else gsp_apis[
				'gsp_prod_app_id']
		api_details['secret'] = gsp_apis[
			'gsp_test_app_secret'] if mode == 'Testing' else gsp_apis[
				'gsp_prod_app_secret']
		api_details['token'] = gsp_apis[
			'gsp_test_token'] if mode == 'Testing' else gsp_apis[
				'gsp_prod_token']
		api_details['gst'] = gsp_apis[
			'gst_test_number'] if mode == 'Testing' else gsp_apis[
				'gst_prod_number']
	
		return {"success":True,"data":api_details}
	except Exception as e:
		print(e,"gsp api details")
		return {"success":False,"message":str(e)}

def insert_credit_items(items,invoice_number):
	try:
		for item in items:
			# print(item.sac_code,item['sac_code'])
			# item = {'doctype': 'Credit Note Items', 'sac_code': item['sac_code'], 'item_name': item['item_name'], 'date': item['date'], 'cgst': item['cgst'], 'cgst_amount': item['cgst_amount'], 'sgst': item['sgst'], 'sgst_amount': item['sgst_amount'], 'igst': item['igst'], 'igst_amount': item['igst_amount'], 'item_value': item['item_value'],
			# 		'description': item['description'], 'item_taxable_value': item['item_taxable_value'], 'gst_rate': item['gst_rate'], 'item_value_after_gst': item['item_value_after_gst'], 'parent': invoice_number, 'parentfield': 'credit_note_items', 'parenttype': 'invoices', 'sac_code_found': 'Yes'}
			item = {'doctype': 'Credit Note Items', 'sac_code': item.sac_code, 'item_name': item.item_name, 'date': item.date, 'cgst': item.cgst, 'cgst_amount': item.cgst_amount, 'sgst': item.sgst, 'sgst_amount': item.sgst_amount, 'igst': item.igst, 'igst_amount': item.igst_amount, 'item_value': item.item_value,
					'description': item.description, 'item_taxable_value': item.item_taxable_value, 'gst_rate': item.gst_rate, 'item_value_after_gst': item.item_value_after_gst, 'parent': invoice_number, 'parentfield': 'credit_note_items', 'parenttype': 'invoices', 'sac_code_found': 'Yes'}
			if item['sac_code'].isdigit():
				
				doc = frappe.get_doc(item)
				doc.insert(ignore_permissions=True, ignore_links=True)
		return {"sucess":True,"data":doc}
				# print(doc)
	except Exception as e:
		print(e,"insert itemns api")
		return {"success":False,"message":e}

def insert_discount_items(items,invoice_number):
	try:
		for item in items:
			# print(item.sac_code,item['sac_code'])
			# item = {'doctype': 'Credit Note Items', 'sac_code': item['sac_code'], 'item_name': item['item_name'], 'date': item['date'], 'cgst': item['cgst'], 'cgst_amount': item['cgst_amount'], 'sgst': item['sgst'], 'sgst_amount': item['sgst_amount'], 'igst': item['igst'], 'igst_amount': item['igst_amount'], 'item_value': item['item_value'],
			# 		'description': item['description'], 'item_taxable_value': item['item_taxable_value'], 'gst_rate': item['gst_rate'], 'item_value_after_gst': item['item_value_after_gst'], 'parent': invoice_number, 'parentfield': 'credit_note_items', 'parenttype': 'invoices', 'sac_code_found': 'Yes'}
			item = {'doctype': 'Discount Items', 'sac_code': item.sac_code, 'item_name': item.item_name, 'date': item.date, 'cgst': item.cgst, 'cgst_amount': item.cgst_amount, 'sgst': item.sgst, 'sgst_amount': item.sgst_amount, 'igst': item.igst, 'igst_amount': item.igst_amount, 'item_value': item.item_value,
					'description': item.description, 'item_taxable_value': item.item_taxable_value, 'gst_rate': item.gst_rate, 'item_value_after_gst': item.item_value_after_gst, 'parent': invoice_number, 'parentfield': 'discount_items', 'parenttype': 'invoices', 'sac_code_found': 'Yes'}
			if item['sac_code'].isdigit():
				
				doc = frappe.get_doc(item)
				doc.insert(ignore_permissions=True, ignore_links=True)
		return {"sucess":True,"data":doc}
				# print(doc)
	except Exception as e:
		print(e,"insert itemns api")
		return {"success":False,"message":e}

def CreditgenerateIrn(invoice_number):
	try:
		# get invoice details
		credit_items = []
		invoice = frappe.get_doc('Invoices', invoice_number)

		# get seller details
		company_details = check_company_exist_for_Irn(invoice.company)
		# get gsp_details
		companyData = {"code":company_details['data'].name,"mode":company_details['data'].mode,"provider":company_details['data'].provider}
		GSP_details = creditgsp_api_data(companyData)
		# get taxpayer details
		GspData = {"gstNumber":invoice.gst_number,"code":invoice.company,"apidata":GSP_details['data'],"invoice":invoice_number}
		taxpayer_details = get_tax_payer_details_data(GspData)
		#gst data
		# print(taxpayer_details,"taxxxxxx")
		if invoice.invoice_category == "Credit Invoice":
			invoice_numberIrn = invoice.invoice_number + str(random.randint(0, 100)) +'T' if company_details['data'].mode == 'Testing' else invoice.invoice_number+"ACN"
		else:
			invoice_numberIrn = invoice.invoice_number + str(random.randint(0, 100)) +'T' if company_details['data'].mode == 'Testing' else invoice.invoice_number
		# irnInvoiceNumber = 
		gst_data = {
			"Version": "1.1",
			"TranDtls": {
				"TaxSch": "GST",
				"SupTyp": "B2B",
				"RegRev": "N",
				"IgstOnIntra": "N"
			},
			"SellerDtls": {
				"Gstin":
				GSP_details['data']['gst'],
				"LglNm":
				company_details['data'].legal_name,
				"TrdNm":
				company_details['data'].trade_name,
				"Addr1":
				company_details['data'].address_1,
				"Addr2":
				company_details['data'].address_2,
				"Loc":
				company_details['data'].location,
				"Pin":
				193502 if company_details['data'].mode == "Testing" else
				company_details['data'].pincode,
				"Stcd":
				"01" if company_details['data'].mode == "Testing" else
				company_details['data'].state_code,
				"Ph":
				company_details['data'].phone_number,
				"Em":
				company_details['data'].email
			},
			"BuyerDtls": {
				"Gstin":
				taxpayer_details['data'].gst_number,
				"LglNm":
				taxpayer_details['data'].legal_name,
				"TrdNm":
				taxpayer_details['data'].trade_name,
				"Pos":
				"01" if company_details['data'].mode == "Testing" else
				company_details['data'].state_code,
				"Addr1":
				taxpayer_details['data'].address_1,
				"Addr2":
				taxpayer_details['data'].address_2,
				"Loc":
				taxpayer_details['data'].location,
				"Pin":
				int(taxpayer_details['data'].pincode),
				"Stcd":
				taxpayer_details['data'].state_code,
				# "Ph": taxpayer_details.phone_number,
				# "Em": taxpayer_details.
			},
			"DocDtls": {
				"Typ":
				"CRN",
				"No":
				invoice_numberIrn,
				"Dt":
				datetime.datetime.strftime(invoice.invoice_date,
											'%d/%m/%Y')
			},
			"ItemList": [],
		}
		total_igst_value = 0
		total_sgst_value = 0
		total_cgst_value = 0
		total_cess_calue = 0
		ass_value = 0
		for index, item in enumerate(invoice.items):
			# print(item.sac_code,"HsnCD")
			if item.item_mode == "Credit":
				credit_items.append(item.__dict__)
				total_igst_value += abs(item.igst_amount)
				total_sgst_value += abs(item.sgst_amount)
				total_cgst_value += abs(item.cgst_amount)
				total_cess_calue += abs(item.cess_amount)
				ass_value += abs(item.item_value)
				i = {
					"SlNo":
					str(index + 1),
					"PrdDesc":
					item.item_name,
					"IsServc":
					"Y",
					"HsnCd":
					item.sac_code if item.sac_code != 'No SAC' else '',
					"Qty":
					1,
					"FreeQty":
					0,
					"UnitPrice":
					abs(round(item.item_value, 2)),
					"TotAmt":
					abs(round(item.item_value, 2)),
					"Discount":
					0,
					"AssAmt":
					0 if item.sac_code == 'No SAC' else abs(round(
						item.item_value, 2)),
					"GstRt":
					item.gst_rate,
					"IgstAmt":
					abs(round(item.igst_amount, 2)),
					"CgstAmt":
					abs(round(item.cgst_amount, 2)),
					"SgstAmt":
					abs(round(item.sgst_amount, 2)),
					"CesRt":
					item.cess,
					"CesAmt":
					item.cess_amount,
					"CesNonAdvlAmt":
					0,
					"StateCesRt":
					0,
					"StateCesAmt":
					0,
					"StateCesNonAdvlAmt":
					0,
					"OthChrg":
					00,
					"TotItemVal":
					abs(round(item.item_value_after_gst, 2)),
				}
				gst_data['ItemList'].append(i)
		gst_data["ValDtls"] = {
			"AssVal": round(ass_value,2),
			"CgstVal": round(total_cgst_value, 2),
			"SgstVal": round(total_sgst_value, 2),
			"IgstVal": round(total_igst_value, 2),
			"CesVal": round(total_cess_calue,2),
			"StCesVal": 0,
			"Discount": 0,
			"OthChrg": 0,
			"RndOffAmt": 0,
			"TotInvVal": abs(round(invoice.credit_value_after_gst, 2)),
			"TotInvValFc": abs(round(invoice.credit_value_after_gst, 2))
		}
		print(gst_data)
		response = postIrn(gst_data, GSP_details['data'],company_details, invoice_number)
		if response['success']==True:
			invoice = frappe.get_doc('Invoices', invoice_number)
			invoice.credit_ack_no = response['result']['AckNo']
			invoice.credit_irn_number = response['result']['Irn']
			invoice.credit_ack_date = response['result']['AckDt']
			invoice.credit_signed_invoice = response['result']['SignedInvoice']
			invoice.credit_signed_invoice_generated = 'Yes'
			invoice.credit_irn_generated = 'Success'
			invoice.irn_generated = "Success"
			invoice.irn_number = " "
			invoice.credit_qr_code = response['result']['SignedQRCode']
			invoice.credit_qr_code_generated = 'Success'
			invoice.credit_irn_cancelled = 'No'
			invoice.credit_irn_generated_time = datetime.datetime.utcnow()
			invoice.save(ignore_permissions=True,ignore_version=True)
			create_credit_qr_image(invoice_number, GSP_details['data'])
			# print(credit_items)
			# insert_credit_items = insert_credit_items(credit_items,invoice_number)
		else:
			if "result" in list(response.keys()):
				if response['result'][0]['InfCd'] == "DUPIRN":
					invoice = frappe.get_doc('Invoices', invoice_number)
					invoice.credit_duplicate_ack_date = response['result'][0]['Desc']['AckDt']
					invoice.credit_duplicate_ack_no = response['result'][0]['Desc']['AckNo']
					invoice.credit_duplicate_irn_number = response['result'][0]['Desc']['Irn']
					invoice.credit_ack_no = response['result'][0]['Desc']['AckNo']
					invoice.credit_irn_number = response['result'][0]['Desc']['Irn']
					invoice.credit_ack_date = response['result'][0]['Desc']['AckDt']
					invoice.credit_irn_generated = "Success"
					invoice.credit_qr_code_generated = "Success"
					invoice.credit_qr_code_image = ""
					invoice.save(ignore_permissions=True, ignore_version=True)
			invoice = frappe.get_doc('Invoices', invoice_number)
			invoice.credit_irn_generated = 'Failed'
			invoice.credit_irn_error_message = response['message'][6:]
			response_error_message = response['message']
			invoice.save(ignore_permissions=True,ignore_version=True)
			return {"success": False, "message": response_error_message}
		return response
	except Exception as e:
		print(str(e), "Credit generate Irn")
		frappe.log_error(frappe.get_traceback(),invoice_number)
		logger.error(f"{invoice_number},     Credit Generate Irn,   {str(e)}")
		return {"success": False, "message": str(e)}


def postIrn(gst_data, gsp,company,invoice_number):
	try:
		# print(gst_data)
		headers = {
			"user_name": gsp['username'],
			"password": gsp['password'],
			"gstin": gsp['gst'],
			"requestid": str(random.randint(0, 1000000000000000000)),
			"Authorization": "Bearer " + gsp['token']
		}
		if company['data'].proxy == 0:
			irn_response = requests.post(gsp['generate_irn'],
											headers=headers,
											json=gst_data)
		else:
			
			proxyhost = company['data'].proxy_url
			proxyhost = proxyhost.replace("http://","@")
			proxies = {'https':'https://'+company['data'].proxy_username+":"+company['data'].proxy_password+proxyhost}
			print(proxies, "     proxy console")
			irn_response = requests.post(gsp['generate_irn'],
											headers=headers,
											json=gst_data,proxies=proxies,verify=False)									
		if irn_response.status_code == 200:
			return irn_response.json()
		else:
			response_error_message = str(irn_response.text)
			logger.error(f"{invoice_number},     Credit Post Irn,   {response_error_message}")
			frappe.log_error(frappe.get_traceback(),invoice_number)
			return {"success": False, 'message': irn_response.text}
		# print(irn_response.text)
	except Exception as e:
		print(e, "post irn credit")
		frappe.log_error(frappe.get_traceback(),invoice_number)
		logger.error(f"{invoice_number},     Credit Generate Irn,   {str(e)}")
		return {"success": False, 'message':str(e)}

