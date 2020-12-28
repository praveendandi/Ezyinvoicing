# # -*- coding: utf-8 -*-
# # Copyright (c) 2020, caratred and contributors
# # For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError
import pandas as pd
import json
import qrcode
import os, os.path
import random, string
from random import randint
from google.cloud import storage
# from datetime import da
import datetime
import random
import math
from frappe.utils import get_site_name
import time
import os

from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz


class Invoices(Document):


	def generateIrn(self, invoice_number):
		# try:
		# get invoice details
		start_time = datetime.datetime.utcnow()
		invoice = frappe.get_doc('Invoices', invoice_number)
		# get seller details
		company_details = check_company_exist_for_Irn(invoice.company)
		# get gsp_details
		credit_note_items = []
		companyData = {
			"code": company_details['data'].name,
			"mode": company_details['data'].mode,
			"provider": company_details['data'].provider
		}
		GSP_details = gsp_api_data(companyData)
		# get taxpayer details
		GspData = {
			"gstNumber": invoice.gst_number,
			"code": invoice.company,
			"apidata": GSP_details['data']
		}
		taxpayer_details = get_tax_payer_details(GspData)
		#gst data
		gst_data = {
			"Version": "1.1",
			"TranDtls": {
				"TaxSch": "GST",
				"SupTyp": "B2B",
				"RegRev": "Y",
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
				"INV",
				"No":
				invoice.invoice_number + str(random.randint(0, 100)) +
				'T' if company_details['data'].mode == 'Testing' else
				invoice.invoice_number,
				"Dt":
				datetime.datetime.strftime(invoice.invoice_date,
											'%d/%m/%Y')
			},
			"ItemList": [],
		}
		total_igst_value = 0
		total_sgst_value = 0
		total_cgst_value = 0
		total_cess_value = 0
		total_state_cess_value = 0
		discount_after_value = 0
		discount_before_value = 0
		ass_value = 0
		for index, item in enumerate(invoice.items):
			# print(item.sac_code,"HsnCD")
			if item.is_credit_item == "No" and item.taxable == "Yes" and item.type == "Included":
				total_igst_value += item.igst_amount
				total_sgst_value += item.sgst_amount
				total_cgst_value += item.cgst_amount
				total_cess_value += item.cess_amount
				total_state_cess_value += item.state_cess_amount
				ass_value += item.item_value
				i = {
					"SlNo":
					str(index + 1),
					"PrdDesc":
					item.item_name,
					"IsServc":
					"Y" if item.item_type == "SAC" else
					"N",
					"HsnCd":
					item.sac_code if item.sac_code != 'No Sac' else '',
					"Qty":
					1,
					"FreeQty":
					0,
					"UnitPrice":
					round(item.item_value, 1),
					"TotAmt":
					round(item.item_value, 1),
					"Discount":
					0,
					"AssAmt":
					0 if item.sac_code == 'No Sac' else round(
						item.item_value, 1),
					"GstRt":
					item.gst_rate,
					"IgstAmt":
					round(item.igst_amount, 1),
					"CgstAmt":
					round(item.cgst_amount, 1),
					"SgstAmt":
					round(item.sgst_amount, 1),
					"CesRt":
					item.cess,
					"CesAmt":
					round(item.cess_amount, 2),
					"CesNonAdvlAmt":
					0,
					"StateCesRt": item.state_cess,
					"StateCesAmt": round(item.state_cess_amount,2),
					"StateCesNonAdvlAmt":
					0,
					"OthChrg":
					00,
					"TotItemVal":
					round(item.item_value_after_gst, 2),
				}
				gst_data['ItemList'].append(i)
			else:
				if item.taxable=="Yes" and item.type=="Included" and item.is_credit_item=="Yes" and company_details['data'].allowance_type=="Credit":
					
					credit_note_items.append(item)
				else:
					if item.type == "Included":
						discount_before_value +=item.item_value	
						discount_after_value += item.item_value_after_gst
						credit_note_items.append(item)
		discount_before_value = abs(discount_before_value)	
		discount_after_value = abs(discount_after_value)
		gst_data["ValDtls"] = {
			"AssVal": round(ass_value, 2), 
			"CgstVal": round(total_cgst_value, 2),
			"SgstVal": round(total_sgst_value, 2),
			"IgstVal": round(total_igst_value, 2),
			"CesVal": round(total_cess_value, 2),
			"StCesVal": round(total_state_cess_value,2),
			"Discount": round(discount_after_value,2),
			"OthChrg": 0,
			"RndOffAmt": 0,
			"TotInvVal": round(invoice.amount_after_gst, 2) - round(discount_after_value,2),
			"TotInvValFc": round(invoice.amount_after_gst, 2) - round(discount_after_value,2)
		}
		# return{"success":True}
		if ass_value > 0:

			response = postIrn(gst_data, GSP_details['data'],
								company_details['data'])
			if response['success']:
				invoice = frappe.get_doc('Invoices', invoice_number)
				invoice.ack_no = response['result']['AckNo']
				invoice.irn_number = response['result']['Irn']
				invoice.ack_date = response['result']['AckDt']
				invoice.signed_invoice = response['result'][
					'SignedInvoice']
				invoice.signed_invoice_generated = 'Yes'
				invoice.irn_generated = 'Success'
				invoice.qr_code = response['result']['SignedQRCode']
				invoice.qr_code_generated = 'Success'
				invoice.irn_cancelled = 'No'
				invoice.irn_generated_time = datetime.datetime.utcnow()
				invoice.irn_process_time = datetime.datetime.utcnow(
				) - start_time
				invoice.save(ignore_permissions=True, ignore_version=True)
				create_qr = create_qr_image(invoice_number,
											GSP_details['data'])
				if create_qr['success'] == True and company_details['data'].allowance_type=="Credit":
					if credit_note_items != []:
						cgetIrn = CreditgenerateIrn(invoice_number)
						invoice = frappe.get_doc('Invoices',
													invoice_number)
						invoice.irn_process_time = datetime.datetime.utcnow(
						) - start_time
						invoice.save(ignore_permissions=True,
										ignore_version=True)
						# insert_hsn_code_based_taxes(credit_note_items,invoice_number,"Credit")				
				
				return response
			else:
				return response
		# else:
		# 	if credit_note_items != [] and company_details['data'].allowance_type=="Discount":
		# 		CreditgenerateIrn(invoice_number)
		# 		invoice = frappe.get_doc('Invoices', invoice_number)
		# 		invoice.irn_process_time = datetime.datetime.utcnow(
		# 		) - start_time
		# 		invoice.save(ignore_permissions=True, ignore_version=True)
		# 		return {"success": True}
		# 	return {"success": False}

		# except Exception as e:
		# 	print(str(e), "generate Irn")

	def cancelIrn(self, invoice_number, reason='wrong Entry'):
		try:
			# get invoice details
			invoice = frappe.get_doc('Invoices', invoice_number)
			# get seller details

			company_details = check_company_exist_for_Irn(invoice.company)
			# get gsp_details
			gsp_data = {"mode":company_details['data'].mode,"code":company_details['data'].name,"provider":company_details['data'].provider}
			GSP_details = gsp_api_data_for_irn(gsp_data)
			# GSP_details = gsp_api_data(company_details.name,
			# 						   company_details.mode,
			# 						   company_details.provider)
			cancel_response = cancel_irn(invoice.irn_number, GSP_details, reason,company_details['data'])
			if cancel_response['success']:
				invoice.cancelled_on = cancel_response['result']['CancelDate']
				invoice.cancel_message = reason
				invoice.irn_cancelled = 'Yes'
				invoice.irn_generated = 'Cancelled'
				invoice.save()
				if invoice.has_credit_items=="Yes" and company_details['data'].allowance_type == "Credit":
					credit_cancel_response = cancel_irn(invoice.credit_irn_number, GSP_details, reason,company_details['data'])
					if credit_cancel_response['success']:
						# invoice.cancelled_on = cancel_response['result']['CancelDate']
						# invoice.cancel_message = reason
						invoice.credit_irn_cancelled = 'Yes'
						invoice.credit_irn_generated = 'Cancelled'
						invoice.save()
						return {
							"success": True,
							"message": "E-Invoice is cancelled successfully"
						}
					return {"success":True,"message":"E-Invoice is cancelled successfully and credit notes failed"}	
				return {
					"success": True,
					"message": "E-Invoice is cancelled successfully"
					}		
			else:
				return {"success": False, "message": "Invoice is not active"}
		except Exception as e:
			print(e,"cancel irn")


	def getTaxPayerDetails(self, gstNumber):
		try:
			gstDetails = frappe.get_doc('TaxPayerDetail', gstNumber)
			return {"success": True, "data": gstDetails}
		except Exception as e:
			print(e, "get TaxPayerDetail")

	def updateTaxPayerDetails(self, taxPayerDetails):
		taxPayerDeatilsData = frappe.get_doc('TaxPayerDetail',
											 taxPayerDetails['gst'])
		# print(taxPayerDeatils.name)
		taxPayerDeatilsData.address_1 = taxPayerDetails['address_1']
		taxPayerDeatilsData.address_2 = taxPayerDetails['address_2']
		taxPayerDeatilsData.email = taxPayerDetails['email']
		taxPayerDeatilsData.phone_number = taxPayerDetails['phone_number']
		taxPayerDeatilsData.legal_name = taxPayerDetails['legal_name']
		taxPayerDeatilsData.trade_name = taxPayerDetails['trade_name']
		taxPayerDeatilsData.location = taxPayerDetails['location']
		taxPayerDeatilsData.save()
		return True

	def send_invoicedata_to_gcb(self, invoice_number):
		try:
			folder_path = frappe.utils.get_bench_path()

			doc = frappe.get_doc('Invoices', invoice_number)
			company = frappe.get_doc('company', doc.company)
			path = folder_path + '/sites/' + company.site_name
			file_name = invoice_number + 'b2cqr.png'
			dst_pdf_filename = path + "/private/files/" + file_name

			if doc.b2c_qrimage:
				attach_qr = attach_b2c_qrcode({
					"invoice_number": invoice_number,
					"company": doc.company
				})
				if attach_qr["success"] == False:
					return {"success": False, "message": attach_qr["message"]}
				else:
					return {
						"success": True,
						"message": "QR-Code generated successfully"
					}

			filename = invoice_number + doc.company + ".json"
			b2c_file = path + "/private/files/" + filename
			items_count = 0
			hsn_code = ""
			items = doc.items
			items_count = 0
			hsn_code = ""
			headers = {'Content-Type': 'application/json'}
			if company.b2c_qr_type == "Invoice Details":
				if company.proxy == 1:
					proxyhost = company.proxy_url
					proxyhost = proxyhost.replace("http://","@")
					proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
							'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
								}
				
				for xyz in items:
					if xyz.sac_code not in hsn_code:
						hsn_code += xyz.sac_code + ", "
					items_count += 1
				b2c_data = {
					"invoice_number": doc.invoice_number,
					"invoice_type": doc.invoice_type,
					"invoice_date": str(doc.invoice_date),
					"pms_invoice_summary": doc.pms_invoice_summary,
					"irn": "N/A",
					"company_name": company.company_name,
					"guest_name": doc.guest_name,
					"issued_by": "ezyinvoicing",
					"items_count": items_count,
					"hsn_code": hsn_code.rstrip(', '),
					"company": company.name
				}
				if company.proxy == 0:
					json_response = requests.post(
						"https://gst.caratred.in/ezy/api/addJsonToGcb",
						headers=headers,
						json=b2c_data)
					response = json_response.json()
					if response["success"] == False:
						return {
							"success": False,
							"message": response["message"]
						}
				else:
					json_response = requests.post(
						"https://gst.caratred.in/ezy/api/addJsonToGcb",
						headers=headers,
						json=b2c_data,
						proxies=proxies)
					response = json_response.json()
					if response["success"] == False:
						return {
							"success": False,
							"message": response["message"]
						}

				# storage_client = storage.Client.from_service_account_json(
				# 	folder_path +"/apps/version2_app/version2_app/version2_app/doctype/invoices/jaypee-group-a9b672ada582.json"
				# )
				# bucket = storage_client.get_bucket("ezyinvoices-b2c")
				# with open(b2c_file, "w") as outfile:
				# 	json.dump(b2c_data, outfile)
				# blob = bucket.blob(filename)
				# with open(b2c_file, 'rb') as img_data:
				# 	blob.upload_from_file(img_data)

				qr = qrcode.QRCode(
					version=1,
					error_correction=qrcode.constants.ERROR_CORRECT_L,
					box_size=3,
					border=4
				)
				qrurl = company.b2c_qr_url + response['data']
				qr.add_data(qrurl)
				qr.make(fit=True)
				img = qr.make_image(fill_color="black", back_color="white")
				img.save(dst_pdf_filename)
			elif company.b2c_qr_type == "Virtual Payment":

				if company.proxy == 0:
					generate_qr = requests.post(
						"https://upiqr.in/api/qr?format=png",
						headers=headers,
						json={
							"vpa": company.merchant_virtual_payment_address,
							"name": company.merchant_name,
							"txnReference": invoice_number,
							"amount": '%.2f' % doc.pms_invoice_summary
						})
				else:
					proxyhost = company.proxy_url
					proxyhost = proxyhost.replace("http://", "@")
					proxies = {
						'http':
						'http://' + company.proxy_username + ":" +
						company.proxy_password + proxyhost,
						'https':
						'https://' + company.proxy_username + ":" +
						company.proxy_password + proxyhost
					}
					generate_qr = requests.post(
						"https://upiqr.in/api/qr?format=png",
						headers=headers,
						json={
							"vpa": company.merchant_virtual_payment_address,
							"name": company.merchant_name,
							"txnReference": invoice_number,
							"amount": '%.2f' % doc.pms_invoice_summary
						},
						proxies=proxies)
				if generate_qr.status_code == 200:
					with open(dst_pdf_filename, "wb") as f:
						f.write(generate_qr.content)
			else:
				return {
					"success":
					False,
					"message":
					"Please select any in 'B2C QR Code Type' in Company Details"
				}
			files = {"file": open(dst_pdf_filename, 'rb')}
			payload = {
				"is_private": 1,
				"folder": "Home",
				"doctype": "Invoices",
				"docname": invoice_number,
				'fieldname': 'b2c_qrimage'
			}
			site = company.host
			upload_qr_image = requests.post(site + "api/method/upload_file",
											files=files,
											data=payload)
			response = upload_qr_image.json()
			if 'message' in response:
				doc.b2c_qrimage = response['message']['file_url']
				doc.name = invoice_number
				doc.save(ignore_permissions=True, ignore_version=True)
				attach_qr = attach_b2c_qrcode({
					"invoice_number": invoice_number,
					"company": doc.company
				})
				if attach_qr["success"] == False:
					if os.path.exists(b2c_file):
						os.remove(b2c_file)
					if os.path.exists(dst_pdf_filename):
						os.remove(dst_pdf_filename)
					return {"success": False, "message": attach_qr["message"]}
				if os.path.exists(b2c_file):
					os.remove(b2c_file)
				if os.path.exists(dst_pdf_filename):
					os.remove(dst_pdf_filename)
				return {
					"success": True,
					"message": "QR-Code generated successfully"
				}
		except Exception as e:
			print(e, "send invoicedata to gcb")
			return {"success": False, "message": str(e)}


def cancel_irn(irn_number, gsp, reason, company):
	try:

		headers = {
			"user_name": gsp['data']['username'],
			"password": gsp['data']['password'],
			"gstin": gsp['data']['gst'],
			"requestid": str(random.randint(0, 1000000000000000000)),
			"Authorization": "Bearer " + gsp['data']['token'],
		}
		payload = {"irn": irn_number, "cnlrem": reason, "cnlrsn": "1"}
		if company.proxy == 0:

			cancel_response = requests.post(gsp['data']['cancel_irn'],
											headers=headers,
											json=payload)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://", "@")
			proxies = {
				'http':
				'http://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost,
				'https':
				'https://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost
			}
			cancel_response = requests.post(gsp['data']['cancel_irn'],
											headers=headers,
											json=payload,
											proxies=proxies)
		repsone = cancel_response.json()
		return repsone
	except Exception as e:
		print("cancel irn", e)


def attach_qr_code(invoice_number, gsp, code):
	try:
		invoice = frappe.get_doc('Invoices', invoice_number)
		company = frappe.get_doc('company', invoice.company)
		folder_path = frappe.utils.get_bench_path()
		site_folder_path = company.site_name
		# path = folder_path + '/sites/' + get_site_name(frappe.local.request.host)
		path = folder_path + '/sites/' + site_folder_path
		src_pdf_filename = path + invoice.invoice_file
		dst_pdf_filename = path + "/private/files/" + invoice_number + 'withQr.pdf'
		# attaching qr code
		img_filename = path + invoice.qr_code_image
		# img_rect = fitz.Rect(250, 200, 340, 270)
		img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
							 company.qr_rect_y0, company.qr_rect_y1)
		document = fitz.open(src_pdf_filename)

		page = document[0]

		page.insertImage(img_rect, filename=img_filename)
		document.save(dst_pdf_filename)
		document.close()
		# attacing irn an ack
		dst_pdf_text_filename = path + "/private/files/" + invoice_number + 'withQrIrn.pdf'
		doc = fitz.open(dst_pdf_filename)
		
		if company.irn_details_page == "First":
			page = doc[0]
		else:
			page = doc[-1]
		# page = doc[0]
		# where = fitz.Point(15, 55)
		where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
		text = "IRN: " + invoice.irn_number +"          "+ "ACK NO: " + invoice.ack_no + "       " + "ACK DATE: " + invoice.ack_date
		
		page.insertText(
			where,
			text,
			fontname="Roboto-Black",  # arbitrary if fontfile given
			fontfile=folder_path +
			company.font_file_path,  #fontpath,  # any file containing a font
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
			'fieldname': 'invoice_with_gst_details'
		}
		site = company.host
		upload_qr_image = requests.post(site + "api/method/upload_file",
										files=files,
										data=payload)
		response = upload_qr_image.json()
		if 'message' in response:
			invoice.invoice_with_gst_details = response['message']['file_url']
			invoice.save()
		return
	except Exception as e:
		print(e, "attach qr code")


def create_qr_image(invoice_number, gsp):
	try:
		invoice = frappe.get_doc('Invoices', invoice_number)

		folder_path = frappe.utils.get_bench_path()
		company = frappe.get_doc('company', invoice.company)
		site_folder_path = company.site_name
		path = folder_path + '/sites/' + site_folder_path + "/private/files/"
		# print(path)
		headers = {
			"user_name": gsp['username'],
			"password": gsp['password'],
			"gstin": gsp['gst'],
			"requestid": str(random.randint(0, 1000000000000000000)),
			"Authorization": "Bearer " + gsp['token'],
			"Irn": invoice.irn_number,
			"height":"100",
			"width":"100"
		}
		if company.proxy == 0:
			qr_response = requests.get(gsp['generate_qr_code'],
									   headers=headers,
									   stream=True)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://", "@")
			proxies = {
				'http':
				'http://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost,
				'https':
				'https://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost
			}
			qr_response = requests.get(gsp['generate_qr_code'],
									   headers=headers,
									   stream=True,
									   proxies=proxies)
		file_name = invoice_number + "qr.png"
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
			'fieldname': 'qr_code_image'
		}
		site = company.host
		upload_qr_image = requests.post(site + "api/method/upload_file",
										files=files,
										data=payload)
		response = upload_qr_image.json()
		if 'message' in response:
			invoice.qr_code_image = response['message']['file_url']
			invoice.save()
			attach_qr_code(invoice_number, gsp, invoice.company)
			return {"success": True}
		return {"success": True}
	except Exception as e:
		print(e, "qr image")
		return {"success": False}


def postIrn(gst_data, gsp, company):
	try:
		# print(gst_data)
		headers = {
			"user_name": gsp['username'],
			"password": gsp['password'],
			"gstin": gsp['gst'],
			"requestid": str(random.randint(0, 1000000000000000000)),
			"Authorization": "Bearer " + gsp['token']
		}
		if company.proxy == 0:

			irn_response = requests.post(gsp['generate_irn'],
										 headers=headers,
										 json=gst_data)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://", "@")
			proxies = {
				'http':
				'http://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost,
				'https':
				'https://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost
			}
			irn_response = requests.post(gsp['generate_irn'],
										 headers=headers,
										 json=gst_data,
										 proxies=proxies)

		# print(irn_response.text)
		if irn_response.status_code == 200:
			return irn_response.json()
		else:
			return {"success": False, 'message': irn_response.text}
		# print(irn_response.text)
	except Exception as e:
		print(e, "post irn")


@frappe.whitelist(allow_guest=True)
def create_invoice(data):
	try:

		if data['invoice_type'] == 'B2B':
			# check token is valid or not
			isValid = check_token_is_valid(company.name, company.mode)
			if isValid == True:
				# get taxpayer details
				tax_payer = get_tax_payer_details(data['gstNumber'],
												  company_code, api_details)
				# insert invoices
				a = insert_invoice(data, company_code, tax_payer)
			else:
				pass
		else:
			print("b2c")

		return True
	except Exception as e:
		print(e)


@frappe.whitelist(allow_guest=True)
def insert_invoice(data):
	'''
	insert invoice data     data, company_code, taxpayer,items_data
	'''
	# try:
	company = frappe.get_doc('company',data['company_code'])

	value_before_gst = 0
	value_after_gst = 0
	other_charges = 0
	credit_value_before_gst = 0
	credit_value_after_gst = 0
	cgst_amount = 0
	sgst_amount = 0
	igst_amount = 0
	cess_amount = 0
	discountAmount = 0
	credit_cgst_amount = 0
	credit_sgst_amount = 0
	credit_igst_amount = 0
	credit_cess_amount = 0
	has_discount_items = "No"
	has_credit_items = "No"
	# print(data['items_data'])
	if data['guest_data']['invoice_type'] == "B2B":
		irn_generated = "Pending"
	else:
		irn_generated = "NA"
	if "legal_name" not in data['taxpayer']:
		data['taxpayer']['legal_name'] = " "
	#calculat items
	for item in data['items_data']:
		if item['taxable'] == 'No' and item['item_type'] != "Discount":
			other_charges += item['item_value_after_gst']
		elif item['taxable']=="No" and item['item_type']=="Discount":
			discountAmount += item['item_value_after_gst'] 
		elif item['sac_code'].isdigit():
			if "-" not in str(item['item_value']):
				cgst_amount+=item['cgst_amount']
				sgst_amount+=item['sgst_amount']
				igst_amount+=item['igst_amount']
				cess_amount+=item['cess_amount']
				value_before_gst += item['item_value']
				value_after_gst += item['item_value_after_gst']
				print(value_before_gst,value_after_gst," ******")
			else:
				cgst_amount+=item['cgst_amount']
				sgst_amount+=item['sgst_amount']
				igst_amount+=item['igst_amount']
				cess_amount+=item['cess_amount']
				credit_cgst_amount+=abs(item['cgst_amount'])
				credit_sgst_amount+=abs(item['sgst_amount'])
				credit_igst_amount+=abs(item['igst_amount'])
				credit_cess_amount+=abs(item['cess_amount'])
				credit_value_before_gst += abs(item['item_value'])
				credit_value_after_gst += abs(item['item_value_after_gst'])
		else:
			pass
	# pms_invoice_summary = value_after_gst
	# pms_invoice_summary_without_gst = value_before_gst
	if company.allowance_type=="Discount":
		discountAfterAmount = abs(discountAmount)+abs(credit_value_after_gst)
		discountBeforeAmount = abs(discountAmount)+abs(credit_value_before_gst)
		pms_invoice_summary = value_after_gst-discountAfterAmount
		pms_invoice_summary_without_gst = value_before_gst-discountBeforeAmount
		if pms_invoice_summary == 0:
			
			credit_value_after_gst = 0
		if credit_value_before_gst > 0:

			has_discount_items = "Yes"
		else:
			has_discount_items = "No"
	else:
		pms_invoice_summary = value_after_gst - credit_value_after_gst
		pms_invoice_summary_without_gst = value_before_gst - credit_value_before_gst
		if credit_value_before_gst > 0:

			has_credit_items = "Yes"
		else:
			has_credit_items = "No"			

	if (pms_invoice_summary > 0) or (credit_value_after_gst > 0):
		ready_to_generate_irn = "Yes"
	else:
		ready_to_generate_irn = "No"

		
	#check invoice total
	if data['total_invoice_amount'] == 0:
		ready_to_generate_irn = "No"
		
	else:
		if int(data['total_invoice_amount']) != int(pms_invoice_summary+other_charges) and int(math.ceil(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.floor(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.ceil(data['total_invoice_amount'])) != int(math.floor(pms_invoice_summary+other_charges)):
			calculated_data = {"value_before_gst":value_before_gst,"value_after_gst":value_after_gst,"other_charges":other_charges,"credit_value_after_gst":credit_value_after_gst,"credit_value_before_gst":credit_value_before_gst,"irn_generated":"Error","cgst_amount":cgst_amount,"sgst_amount":sgst_amount,"igst_amount":igst_amount,"cess_amount":cess_amount,"credit_cess_amount":credit_cess_amount,"credit_cgst_amount":credit_cgst_amount,"credit_igst_amount":credit_igst_amount,"credit_sgst_amount":credit_sgst_amount,"pms_invoice_summary":pms_invoice_summary,"pms_invoice_summary_without_gst":pms_invoice_summary_without_gst}
			TotalMismatchErrorAPI = TotalMismatchError(data,calculated_data)
			if TotalMismatchErrorAPI['success']==True:
				items = data['items_data']
				itemsInsert = insert_items(items, TotalMismatchErrorAPI['invoice_number'])
				insert_tax_summaries2(items, TotalMismatchErrorAPI['invoice_number'])
				hsnbasedtaxcodes = insert_hsn_code_based_taxes(
					items, TotalMismatchErrorAPI['invoice_number'],"Invoice")
				return {"success": True}

			return{"success":False,"message":TotalMismatchErrorAPI['message']}


	invoice = frappe.get_doc({
		'doctype':
		'Invoices',
		'invoice_number':
		data['guest_data']['invoice_number'],
		'guest_name':
		data['guest_data']['name'],
		'ready_to_generate_irn':ready_to_generate_irn,
		'invoice_from':"Pms",
		'gst_number':
		data['guest_data']['gstNumber'],
		'invoice_file':
		data['guest_data']['invoice_file'],
		'room_number':
		data['guest_data']['room_number'],
		'confirmation_number':
		data['guest_data']['confirmation_number'],
		'invoice_type':
		data['guest_data']['invoice_type'],
		'print_by': data['guest_data']['print_by'],
		'invoice_date':
		datetime.datetime.strptime(data['guest_data']['invoice_date'],
									'%d-%b-%y %H:%M:%S'),
		'legal_name':
		data['taxpayer']['legal_name'],
		'address_1':
		data['taxpayer']['address_1'],
		'email':
		data['taxpayer']['email'],
		'trade_name':
		data['taxpayer']['trade_name'],
		'address_2':
		data['taxpayer']['address_2'],
		'phone_number':
		data['taxpayer']['phone_number'],
		'location':
		data['taxpayer']['location'],
		'pincode':
		data['taxpayer']['pincode'],
		'state_code':
		data['taxpayer']['state_code'],
		'amount_before_gst':
		round(value_before_gst, 2),
		"amount_after_gst":
		round(value_after_gst, 2),
		"other_charges":
		round(other_charges, 2),
		"credit_value_before_gst":
		round(credit_value_before_gst, 2),
		"credit_value_after_gst":
		round(credit_value_after_gst, 2),
		"pms_invoice_summary_without_gst":
		round(pms_invoice_summary_without_gst, 2) ,
		"pms_invoice_summary":
		round(pms_invoice_summary, 2) ,
		'irn_generated':
		irn_generated,
		'irn_cancelled':
		'No',
		'qr_code_generated':
		'Pending',
		'signed_invoice_generated':
		'No',
		'company':
		data['company_code'],
		'cgst_amount':
		round(cgst_amount, 2),
		'sgst_amount':
		round(sgst_amount, 2),
		'igst_amount':
		round(igst_amount, 2),
		'cess_amount':
		round(cess_amount, 2),
		'total_gst_amount':
		round(cgst_amount, 2) + round(sgst_amount, 2) +
		round(igst_amount, 2),
		'has_credit_items':
		has_credit_items,
		'total_inovice_amount': data['total_invoice_amount'],
		'has_discount_items':has_discount_items,
		'invoice_process_time':
		datetime.datetime.utcnow() - datetime.datetime.strptime(
			data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
		'credit_cgst_amount':round(credit_cgst_amount,2),
		'credit_sgst_amount':round(credit_sgst_amount,2),
		'credit_igst_amount':round(credit_igst_amount,2),
		'credit_cess_amount':round(credit_cess_amount,2),
		'credit_gst_amount': round(credit_cgst_amount,2) + round(credit_sgst_amount,2) + round(credit_igst_amount,2)	
	})
	if data['amened'] == 'Yes':
		invCount = frappe.db.get_list(
			'Invoices',
			filters={
				'invoice_number':
				['like', '%' + data['guest_data']['invoice_number'] + '%']
			})
		invoice.amended_from = invCount[0]['name']
		if "-" in invCount[0]['name'][-4:]:
			amenedindex = invCount[0]['name'].rfind("-")
			ameneddigit = int(invCount[0]['name'][amenedindex+1:])
			ameneddigit = ameneddigit+1 
			invoice.invoice_number = data['guest_data']['invoice_number'] + "-"+str(ameneddigit)
			# pass
		else:
			invoice.invoice_number = data['guest_data']['invoice_number'] + "-1"

				
	v = invoice.insert(ignore_permissions=True, ignore_links=True)
	data['invoice_number'] = v.name
	data['guest_data']['invoice_number'] = v.name
	# # insert items

	itemsInsert = insert_items(data['items_data'], data['invoice_number'])

	
	# items = [
	# 	x for x in data['items_data'] if '-' not in str(x['item_value'])
	# ]
	items = data['items_data']
	insert_tax_summaries2(items, data['invoice_number'])
	hsnbasedtaxcodes = insert_hsn_code_based_taxes(
		items, data['guest_data']['invoice_number'],"Invoice")
	
	return {"success": True}
	# except Exception as e:
	# 	print(e, "insert invoice")
	# 	return {"success": False, "message": str(e)}


def insert_hsn_code_based_taxes(items, invoice_number,sacType):
	# try:
	
	sac_codes = []
	for item in items:
		# if sacType == "Credit":
		# 	item = item.__dict__
		if item['sac_code'] not in sac_codes and item['sac_code'].isdigit(
		):
			sac_codes.append(item['sac_code'])

	tax_data = []
	for sac in sac_codes:
		sac_tax = {
			'cess':0,
			'cgst': 0,
			'sgst': 0,
			'igst': 0,
			'amount_before_gst':0,
			'amount_after_gst':0,
			'sac_hsn_code': sac,
			'invoice_number': invoice_number,
			'doctype': "SAC HSN Tax Summaries",
			'parent': invoice_number,
			'parentfield': 'sac_hsn_based_taxes',
			'parenttype': "invoices",
			"state_cess":0,
			"vat":0,
			"type":sacType
		}
		for item in items:
			# print(item)
			if item['sac_code'] == sac:
				sac_tax['cgst'] += item['cgst_amount']
				sac_tax['sgst'] += item['sgst_amount']
				sac_tax['igst'] += item['igst_amount']
				sac_tax['cess'] += item['cess_amount']
				sac_tax["state_cess"] += item["state_cess_amount"]
				sac_tax["vat"] += item["vat_amount"]
				sac_tax['amount_before_gst'] += item['item_taxable_value']
				sac_tax['amount_after_gst'] += item['item_value_after_gst']

		tax_data.append(sac_tax)
	for sac in tax_data:
		# sac['total_amount'] = sac['cgst'] + sac['sgst'] + sac['igst'] + sac['cess']
		doc = frappe.get_doc(sac)
		doc.insert(ignore_permissions=True, ignore_links=True)
	return {"sucess": True, "data": 'doc'}
	# except Exception as e:
	# 	print(e, "insert hsn")
	# 	return {"success": False, "message": str(e)}


def insert_items(items, invoice_number):
	try:
		for item in items:
			item['parent'] = invoice_number
			# if item['sac_code'].isdigit():
			if "-" in str(item['item_value']):
				item['is_credit_item'] = "Yes"
			else:
				item['is_credit_item'] = "No"

			doc = frappe.get_doc(item)
			doc.insert(ignore_permissions=True, ignore_links=True)
		return {"sucess": True, "data": doc}
		# print(doc)
	except Exception as e:
		print(e,"**********  insert itemns api")
		return {"success":False,"message":str(e)}
		

@frappe.whitelist(allow_guest=True)
def calulate_items(data):
	#items, invoice_number,company_code
	try:
		total_items = []
		second_list = []
		for item in data['items']:
			final_item = {}
			companyDetails = frappe.get_doc('company', data['company_code'])
			if companyDetails.allowance_type == "Credit":
				ItemMode = "Credit"
			else:
				ItemMode = "Discount"
					
			if companyDetails.calculation_by == "Description":
				sac_code_based_gst = frappe.db.get_list(
					'SAC HSN CODES',
					filters={'name': ['=',item['name']]})
				if not sac_code_based_gst:
					sac_code_based_gst = frappe.db.get_list(
						'SAC HSN CODES',
						filters={'name': ['like', '%' + item['name'] + '%']})
				if len(sac_code_based_gst)>0:
					sac_code_based_gst_rates = frappe.get_doc(
					'SAC HSN CODES',sac_code_based_gst[0]['name'])	
					SAC_CODE = sac_code_based_gst_rates.code 
					item['item_type'] = sac_code_based_gst_rates.type
				else:
					
					return{"success":False,"message":"SAC Code "+ item['name']+" not found"}	
				if sac_code_based_gst_rates.service_charge == "Yes":
					service_dict = {}

					if sac_code_based_gst_rates.net == "Yes":
						scharge = companyDetails.service_charge_percentage
						gstpercentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
						total_gst_amount = (gstpercentage * item['item_value']) / 100.0
						scharge_value = item['item_value'] - total_gst_amount
						scharge_value = (scharge * item['item_value']) / 100.0
						base_value = round(item['item_value'] * (100 / (scharge + 100)),3)
						scharge_value = item['item_value'] - base_value
						gst_percentage = 18
					else:
						scharge = companyDetails.service_charge_percentage
						base_value = item['item_value']
						scharge_value = (scharge * item['item_value']) / 100.0
						gst_percentage = 18
						gst_value = (gst_percentage* scharge_value)/100.0
						service_dict['item_name'] = item['name']+"-SC "
						service_dict['description'] = item['name']+"-SC "
						service_dict['date'] = datetime.datetime.strptime(item['date'],data['invoice_item_date_format'])
						service_dict['sac_code'] = item['sac_code']
						service_dict['sac_code_found'] = 'Yes'
						service_dict['cgst'] = 9
						service_dict['other_charges'] = 0
						service_dict['cgst_amount'] = gst_value/2
						service_dict['sgst'] = 0
						service_dict['sgst_amount'] = gst_value/2
						service_dict['igst'] = 0
						service_dict['igst_amount'] = 0
						service_dict['gst_rate'] = 18
						service_dict['item_value_after_gst'] = scharge_value+gst_value
						service_dict['item_taxable_value'] = scharge_value
						service_dict['item_value'] = scharge_value
						service_dict['taxable'] = sac_code_based_gst_rates.taxble
						service_dict['cess'] = 0
						service_dict['cess_amount'] = 0
						service_dict['state_cess'] = 0
						service_dict['state_cess_amount'] = 0
						service_dict['type'] = "Included"
						service_dict['item_mode'] = "Debit"
						service_dict['vat_amount'] = 0
						service_dict['vat'] = 0
						service_dict['sort_order'] = item['sort_order']
						service_dict['doctype'] = 'Items'
						service_dict['parentfield'] = 'items'
						service_dict['parenttype'] = 'invoices'

						second_list.append(service_dict)
					# second_list	
				if item['sac_code'] == "No Sac" and SAC_CODE.isdigit():
					item['sac_code'] = sac_code_based_gst_rates.code
				if sac_code_based_gst_rates.type == "Discount":
					
						final_item['sac_code'] = 'No Sac'
						final_item['sac_code_found'] = 'No'
						final_item['cgst'] = 0
						final_item['other_charges'] = 0
						final_item['cgst_amount'] = 0
						final_item['sgst'] = 0
						final_item['sgst_amount'] = 0
						final_item['igst'] = 0
						final_item['igst_amount'] = 0
						final_item['gst_rate'] = 0
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = item['item_value']
						final_item['taxable'] = sac_code_based_gst_rates.taxble
						final_item['cess'] = 0
						final_item['cess_amount'] = 0
						final_item['type'] = "Excempted"
						final_item['item_type'] = "Discount"
						final_item['item_mode'] = ItemMode
				if sac_code_based_gst_rates.taxble == "Yes" and sac_code_based_gst_rates.type != "Discount":
					if "-" in str(item['item_value']):
						final_item['item_mode'] = ItemMode
					else:
						final_item['item_mode'] = "Debit"
					# if sac_code_based_gst_rates.net == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])):
					if sac_code_based_gst_rates.net == "No":
						if item['sac_code'] == '996311':
							if item['item_value']>1000 and item['item_value']<=7500:
								gst_percentage = 12
							elif item['item_value'] > 7500:
								gst_percentage = 18
							elif item['item_value'] == 1000:
								gst_percentage = 0
							else:
								gst_percentage = 0
							if gst_percentage == 0:
								final_item['cgst'] = 0
								final_item['sgst'] = 0
								final_item['igst'] = 0
								final_item['type'] = "Excempted"
							else:
								final_item['cgst'] = gst_percentage/2
								final_item['sgst'] = gst_percentage/2
								final_item['igst'] = 0
								final_item['type'] = "Included"
						else:
							final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
							final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
							final_item['igst'] = float(sac_code_based_gst_rates.igst)
						final_item['cgst_amount'] = round((item["item_value"]*(final_item['cgst']/100)),3)
						final_item['sgst_amount'] = round((item["item_value"]*(final_item['sgst']/100)),3)
						final_item['igst_amount'] = round((item["item_value"]*(final_item['igst']/100)),3)
						final_item['gst_rate'] = final_item['cgst']+final_item['sgst']+final_item['igst']
						final_item['item_value_after_gst'] = final_item['cgst_amount']+final_item['sgst_amount']+final_item['igst_amount']+item['item_value']
						final_item['item_value'] = item['item_value']
					elif sac_code_based_gst_rates.net == "Yes" and item['sac_code'] != "996311":
						gst_percentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
						base_value = round(item['item_value'] * (100 / (gst_percentage + 100)),3)
						gst_value = item['item_value'] - base_value
						final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
						final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
						final_item['cgst_amount'] = round(gst_value / 2,3)
						final_item['sgst_amount'] = round(gst_value / 2,3)
						final_item['igst'] = float(sac_code_based_gst_rates.igst)
						if float(sac_code_based_gst_rates.igst) <= 0:
							final_item['igst_amount'] = 0
						else:
							gst_percentage = (float(sac_code_based_gst_rates.cgst) +
											float(sac_code_based_gst_rates.sgst))
							base_value = item['item_value'] * (100 / (gst_percentage + 100))
							final_item['igst_amount'] = item['item_value'] - base_value
						final_item['gst_rate'] = float(sac_code_based_gst_rates.cgst)+float(sac_code_based_gst_rates.sgst)+float(sac_code_based_gst_rates.igst)
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = base_value
					final_item['other_charges'] = 0
					final_item['sac_code_found'] = 'Yes'
					final_item['taxable'] = sac_code_based_gst_rates.taxble
					final_item['type'] = "Included"
					final_item['sort_order'] = item['sort_order']
				else:
					# if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])) and sac_code_based_gst_rates.type != "Discount":
					if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No":
						final_item['sort_order'] = item['sort_order']
						if item['sac_code'].isdigit():
							final_item['sac_code'] = item['sac_code']
							final_item['sac_code_found'] = 'Yes'
						else:
							final_item['sac_code'] = 'No Sac'
							final_item['sac_code_found'] = 'No'
						final_item['cgst'] = 0
						final_item['other_charges'] = 0
						final_item['cgst_amount'] = 0
						final_item['sgst'] = 0
						final_item['sgst_amount'] = 0
						final_item['igst'] = 0
						final_item['igst_amount'] = 0
						final_item['gst_rate'] = 0
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = item['item_value']
						final_item['taxable'] = sac_code_based_gst_rates.taxble
						final_item['type'] = "Non-Gst"
						# final_item['item_mode'] = "Debit"
						if "-" in str(item['item_value']):
							final_item['item_mode'] = ItemMode
						else:
							final_item['item_mode'] = "Debit"
				final_item['state_cess'] = sac_code_based_gst_rates.state_cess_rate
				if sac_code_based_gst_rates.state_cess_rate > 0:
					final_item["state_cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.state_cess_rate/100))
				else:
					final_item["state_cess_amount"] = 0

				final_item['cess'] = sac_code_based_gst_rates.central_cess_rate
				if sac_code_based_gst_rates.central_cess_rate > 0:
					final_item["cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.central_cess_rate/100))
				else:
					final_item["cess_amount"] = 0
				final_item['vat'] = sac_code_based_gst_rates.vat_rate
				if sac_code_based_gst_rates.vat_rate > 0:
					final_item["vat_amount"] = (item["item_value"]*(sac_code_based_gst_rates.vat_rate/100))
				else:
					final_item["vat_amount"] = 0
				final_item['item_value_after_gst'] = final_item['item_value_after_gst']+final_item['cess_amount']+final_item['vat_amount']+final_item["state_cess_amount"]
			else:
				sac_code_based_gst_rates = frappe.get_doc(
					'SAC HSN CODES',item["sac_code"])
				item['item_type'] = sac_code_based_gst_rates.type
				if sac_code_based_gst_rates.type == "Discount":
						final_item['sac_code'] = 'No Sac'
						final_item['sac_code_found'] = 'No'
						final_item['cgst'] = 0
						final_item['other_charges'] = 0
						final_item['cgst_amount'] = 0
						final_item['sgst'] = 0
						final_item['sgst_amount'] = 0
						final_item['igst'] = 0
						final_item['igst_amount'] = 0
						final_item['gst_rate'] = 0
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = item['item_value']
						final_item['taxable'] = sac_code_based_gst_rates.taxble
						final_item['cess'] = 0
						final_item['cess_amount'] = 0
						final_item['type'] = "Excempted"
						final_item['item_type'] = "Discount"
						final_item['item_mode'] = ItemMode
						final['']
				if sac_code_based_gst_rates.taxble == "Yes" and sac_code_based_gst_rates.type != "Discount":
					if "-" in str(item['item_value']):
						final_item['item_mode'] = ItemMode
					else:
						final_item['item_mode'] = "Debit"
					# if sac_code_based_gst_rates.net == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])):
					if sac_code_based_gst_rates.net == "No":
						if item['sac_code'] == '996311':
							if item['item_value']>1000 and item['item_value']<=7500:
								gst_percentage = 12
							elif item['item_value'] > 7500:
								gst_percentage = 18
							elif item['item_value'] == 1000:
								gst_percentage = 0
							else:
								gst_percentage = 0
							if gst_percentage == 0:
								final_item['cgst'] = 0
								final_item['sgst'] = 0
								final_item['igst'] = 0
								final_item['type'] = "Excempted"
							else:
								final_item['cgst'] = gst_percentage/2
								final_item['sgst'] = gst_percentage/2
								final_item['igst'] = 0
								final_item['type'] = "Included"
						else:
							final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
							final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
							final_item['igst'] = float(sac_code_based_gst_rates.igst)
						final_item['cgst_amount'] = round((item["item_value"]*(final_item['cgst']/100)),3)
						final_item['sgst_amount'] = round((item["item_value"]*(final_item['sgst']/100)),3)
						final_item['igst_amount'] = round((item["item_value"]*(final_item['igst']/100)),3)
						final_item['gst_rate'] = final_item['cgst']+final_item['sgst']+final_item['igst']
						final_item['item_value_after_gst'] = final_item['cgst_amount']+final_item['sgst_amount']+final_item['igst_amount']+item['item_value']
						final_item['item_value'] = item['item_value']
					elif sac_code_based_gst_rates.net == "Yes" and item['sac_code'] != "996311":
						gst_percentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
						base_value = round(item['item_value'] * (100 / (gst_percentage + 100)),3)
						gst_value = item['item_value'] - base_value
						final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
						final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
						final_item['cgst_amount'] = round(gst_value / 2,3)
						final_item['sgst_amount'] = round(gst_value / 2,3)
						final_item['igst'] = float(sac_code_based_gst_rates.igst)
						if float(sac_code_based_gst_rates.igst) <= 0:
							final_item['igst_amount'] = 0
						else:
							gst_percentage = (float(sac_code_based_gst_rates.cgst) +
											float(sac_code_based_gst_rates.sgst))
							base_value = item['item_value'] * (100 / (gst_percentage + 100))
							final_item['igst_amount'] = item['item_value'] - base_value
						final_item['gst_rate'] = float(sac_code_based_gst_rates.cgst)+float(sac_code_based_gst_rates.sgst)+float(sac_code_based_gst_rates.igst)
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = base_value
					final_item['other_charges'] = 0
					final_item['sac_code_found'] = 'Yes'
					final_item['taxable'] = sac_code_based_gst_rates.taxble
					final_item['type'] = "Included"
					final_item['sort_order'] = item['sort_order']
				else:
					# if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])) and sac_code_based_gst_rates.type != "Discount":
					if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No":
						final_item['sort_order'] = item['sort_order']
						if item['sac_code'].isdigit():
							final_item['sac_code'] = item['sac_code']
							final_item['sac_code_found'] = 'Yes'
						else:
							final_item['sac_code'] = 'No Sac'
							final_item['sac_code_found'] = 'No'
						final_item['cgst'] = 0
						final_item['other_charges'] = 0
						final_item['cgst_amount'] = 0
						final_item['sgst'] = 0
						final_item['sgst_amount'] = 0
						final_item['igst'] = 0
						final_item['igst_amount'] = 0
						final_item['gst_rate'] = 0
						final_item['item_value_after_gst'] = item['item_value']
						final_item['item_value'] = item['item_value']
						final_item['taxable'] = sac_code_based_gst_rates.taxble
						final_item['type'] = "Non-Gst"
						final_item['item_mode'] = "Debit"
				final_item['state_cess'] = sac_code_based_gst_rates.state_cess_rate
				if sac_code_based_gst_rates.state_cess_rate > 0:
					final_item["state_cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.state_cess_rate/100))
				else:
					final_item["state_cess_amount"] = 0
				final_item['cess'] = sac_code_based_gst_rates.central_cess_rate
				if sac_code_based_gst_rates.central_cess_rate > 0:
					final_item["cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.central_cess_rate/100))
				else:
					final_item["cess_amount"] = 0
				final_item['vat'] = sac_code_based_gst_rates.vat_rate
				if sac_code_based_gst_rates.vat_rate > 0:
					final_item["vat_amount"] = (item["item_value"]*(sac_code_based_gst_rates.vat_rate/100))
				else:
					final_item["vat_amount"] = 0
				final_item['item_value_after_gst'] = final_item['item_value_after_gst']+final_item['cess_amount']+final_item['vat_amount']+final_item["state_cess_amount"]
			total_items.append({
				'doctype':
				'Items',
				'sac_code':
				item['sac_code'],
				'item_name':
				item['name'],
				'sort_order':final_item['sort_order'],
				"item_type":item['item_type'],
				'date':
				datetime.datetime.strptime(item['date'],
										   data['invoice_item_date_format']),
				'cgst':
				final_item['cgst'],
				'cgst_amount':
				round(final_item['cgst_amount'], 2),
				'sgst':
				final_item['sgst'],
				'sgst_amount':
				round(final_item['sgst_amount'], 2),
				'igst':
				final_item['igst'],
				'igst_amount':
				round(final_item['igst_amount'], 2),
				'item_value':
				final_item['item_value'],
				'description':
				item['name'],
				'item_taxable_value':
				final_item['item_value'],
				'gst_rate':
				final_item['gst_rate'],
				'item_value_after_gst':
				round(final_item['item_value_after_gst'], 2),
				'cess':
				final_item['cess'],
				'cess_amount':
				final_item['cess_amount'],
				'state_cess':final_item["state_cess"],
				"state_cess_amount":final_item["state_cess_amount"],
				'parent':
				data['invoice_number'],
				'parentfield':
				'items',
				'parenttype':
				"invoices",
				'sac_code_found':
				final_item['sac_code_found'],
				'type':
				final_item['type'],
				'other_charges':
				final_item['other_charges'],
				'taxable':
				final_item['taxable'],
				'item_mode':final_item['item_mode'],
				"vat_amount":final_item["vat_amount"],
				"vat":final_item['vat']
			})
		total_items.extend(second_list)	
		return {"success": True, "data": total_items}
	except Exception as e:
		print(e, "calculation api")
		return {"success": False, "message": str(e)}


def insert_tax_summariesd(items, invoice_number):
	try:
		tax_list = []
		for item in items:
			if item['sgst'] > 0:
				dup_dict = {
					'tax_type': 'SGST',
					'tax_percentage': item['sgst'],
					'amount': 0
				}
				if dup_dict not in tax_list:
					tax_list.append(dup_dict)
			if item['cgst'] > 0:
				dup_dict = {
					'tax_type': 'CGST',
					'tax_percentage': item['cgst'],
					'amount': 0
				}
				if dup_dict not in tax_list:
					tax_list.append(dup_dict)
			if item['igst'] > 0:
				dup_dict = {
					'tax_type': 'IGST',
					'tax_percentage': item['igst'],
					'amount': 0
				}
				if dup_dict not in tax_list:
					tax_list.append(dup_dict)

		for tax in tax_list:
			for item in items:
				# print(item)
				if item['sgst'] > 0 and tax['tax_type'] == 'SGST' and item[
						'sgst'] == tax['tax_percentage']:
					tax['amount'] += item['sgst_amount']
				if item['cgst'] > 0 and tax['tax_type'] == 'CGST' and item[
						'cgst'] == tax['tax_percentage']:
					tax['amount'] += item['cgst_amount']
				if item['igst'] > 0 and tax['tax_type'] == 'IGST' and item[
						'igst'] == tax['tax_percentage']:
					tax['amount'] += item['igst_amount']

		for tax in tax_list:
			doc = frappe.get_doc({
				'doctype': 'Tax Summaries',
				'invoce_number': invoice_number,
				'tax_percentage': tax['tax_percentage'],
				'amount': tax['amount'],
				'tax_type': tax['tax_type'],
				'parent': invoice_number,
				'parentfield': 'gst_summary',
				'parenttype': "Invoices"
			})
			doc.insert(ignore_permissions=True)
		return {"success": True}
	except Exception as e:
		print('tax', e)
		return {'succes': False, "message": str(e)}


def insert_tax_summaries2(items,invoice_number):
	df = pd.DataFrame(items)

	df = df.set_index('sgst')
	df['cess_duplicate'] = df['cess']
	df['state_cess_duplicate'] = df['state_cess']
	df['vat_duplication'] = df['vat']
	df1 = df.groupby(['cgst','cess_duplicate','state_cess_duplicate','vat_duplication'])[["cgst_amount", "sgst_amount","igst_amount","cess_amount","cess",'state_cess','vat',"state_cess_amount","vat_amount"]].apply(lambda x : x.astype(float).sum())
	df1.reset_index(level=0, inplace=True) 
	
	df1.reset_index(level=0, inplace=True)
	df1.reset_index(level=0, inplace=True)
	df1.reset_index(level=0, inplace=True)
	df1['cess'] = df1['cess_duplicate']
	df1['state_cess'] = df1['state_cess_duplicate']
	df1['vat'] = df1['vat_duplication']
	data = df1.to_dict('records')
	for each in data:
		if each['cgst']>0:
			
			doc = frappe.get_doc({
				'doctype': 'Tax Summaries',
				'invoce_number': invoice_number,
				'tax_percentage': each['cgst'],
				'amount': each['cgst_amount'],
				'tax_type': "CGST",
				'parent': invoice_number,
				'parentfield': 'gst_summary',
				'parenttype': "Invoices"
			})
			doc.insert(ignore_permissions=True)
			doc = frappe.get_doc({
				'doctype': 'Tax Summaries',
				'invoce_number': invoice_number,
				'tax_percentage': each['cgst'],
				'amount': each['sgst_amount'],
				'tax_type': "SGST",
				'parent': invoice_number,
				'parentfield': 'gst_summary',
				'parenttype': "Invoices"
			})
			doc.insert(ignore_permissions=True)
			if each['igst_amount'] > 0:
				doc = frappe.get_doc({
					'doctype': 'Tax Summaries',
					'invoce_number': invoice_number,
					'tax_percentage': each['cgst'],
					'amount': each['igst_amount'],
					'tax_type': "IGST",
					'parent': invoice_number,
					'parentfield': 'gst_summary',
					'parenttype': "Invoices"
				})
				doc.insert(ignore_permissions=True)
		if each['cess']>0:
			# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
			tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'Central CESS','tax_percentage':each['cess']})
			tax_summary_cess = [element for tupl in tax_summary_cess for element in tupl]
			if len(tax_summary_cess)==0:
				if each['cess_amount']>0:
					doc = frappe.get_doc({
					'doctype': 'Tax Summaries',
					'invoce_number': invoice_number,
					'tax_percentage': each['cess'],
					'amount': each['cess_amount'],
					'tax_type': "Central CESS",
					'parent': invoice_number,
					'parentfield': 'gst_summary',
					'parenttype': "Invoices"
						})
					doc.insert(ignore_permissions=True)	
			else:
				tax_summary_cess_update = frappe.get_doc('Tax Summaries',tax_summary_cess[0])
				tax_summary_cess_update.tax_percentage = each['cess_amount']+float(tax_summary_cess_update.tax_percentage)			
				tax_summary_cess_update.save()
		if each['state_cess']>0:
			# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
			tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'State CESS','tax_percentage':each['state_cess']})
			if tax_summary_cess is ():
				if each['state_cess_amount']>0:
					doc = frappe.get_doc({
					'doctype': 'Tax Summaries',
					'invoce_number': invoice_number,
					'tax_percentage': each['state_cess'],
					'amount': each['state_cess_amount'],
					'tax_type': "State CESS",
					'parent': invoice_number,
					'parentfield': 'gst_summary',
					'parenttype': "Invoices"
						})
					doc.insert(ignore_permissions=True)	
			else:
				tax_summary_state = [element for tupl in tax_summary_cess for element in tupl]
				tax_summary_cess_update = frappe.get_doc('Tax Summaries',tax_summary_state[0])
				tax_summary_cess_update.tax_percentage = each['state_cess_amount']+float(tax_summary_cess_update.tax_percentage)		
				tax_summary_cess_update.save()
		if each['vat']>0:
			# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
			tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'VAT','tax_percentage':each['state_cess']})
			if tax_summary_cess is ():
				if each['vat_amount']>0:
					doc = frappe.get_doc({
					'doctype': 'Tax Summaries',
					'invoce_number': invoice_number,
					'tax_percentage': each['vat'],
					'amount': each['vat_amount'],
					'tax_type': "VAT",
					'parent': invoice_number,
					'parentfield': 'gst_summary',
					'parenttype': "Invoices"
						})
					doc.insert(ignore_permissions=True)	
			else:
				tax_summary_cess_update = frappe.db.get_doc('Tax Summaries',tax_summary_cess[0])
				tax_summary_cess_update.tax_percentage = each['vat_amount']+tax_summary_cess_update.tax_percentage			
				tax_summary_cess_update.save()				

def insert_tax_summaries(items, invoice_number):
	'''
	insert tax_summaries into tax_summaries table
	'''
	try:
		tax_summaries = []
		for item in items:
			if len(tax_summaries) > 0:
				found = False
				for tax in tax_summaries:
					found = False
					if item['sgst'] > 0:
						if tax['tax_type'] == 'SGST' and tax[
								'tax_percentage'] == item['sgst']:
							tax['amount'] += item['sgst_amount']
							found = True
					if item['cgst'] > 0:
						if tax['tax_type'] == 'CGST' and tax[
								'tax_percentage'] == item['cgst']:

							tax['amount'] += item['cgst_amount']
							found = True
					if item['igst'] > 0:
						if tax['tax_type'] == 'IGST' and tax[
								'tax_percentage'] == item['igst']:
							tax['amount'] += item['igst_amount']
							found = True
				if found == False:
					if item['sgst'] > 0:
						summary = {}
						summary['tax_type'] = 'SGST'
						summary['tax_percentage'] = item['sgst']
						summary['amount'] = item['sgst_amount']
						summary['invoice_number'] = invoice_number
						tax_summaries.append(summary)
					if item['cgst'] > 0:
						summary = {}
						summary['tax_type'] = 'CGST'
						summary['tax_percentage'] = item['cgst']
						summary['amount'] = item['cgst_amount']
						summary['invoice_number'] = invoice_number
						tax_summaries.append(summary)
					if item['igst'] > 0:
						summary = {}
						summary['tax_type'] = 'IGST'
						summary['tax_percentage'] = item['igst']
						summary['amount'] = item['igst_amount']
						summary['invoice_number'] = invoice_number
						tax_summaries.append(summary)
			else:
				if item['sgst'] > 0:
					summary = {}
					summary['tax_type'] = 'SGST'
					summary['tax_percentage'] = item['sgst']
					summary['amount'] = item['sgst_amount']
					summary['invoice_number'] = invoice_number
					tax_summaries.append(summary)
				if item['cgst'] > 0:
					summary = {}
					summary['tax_type'] = 'CGST'
					summary['tax_percentage'] = item['cgst']
					summary['amount'] = item['cgst_amount']
					summary['invoice_number'] = invoice_number
					tax_summaries.append(summary)
				if item['igst'] > 0:
					summary = {}
					summary['tax_type'] = 'IGST'
					summary['tax_percentage'] = item['igst']
					summary['amount'] = item['igst_amount']
					summary['invoice_number'] = invoice_number
					tax_summaries.append(summary)
		actual_summaries = [
			tax_summaries[0],
		]
		for tax in tax_summaries:
			found = False
			for actual in actual_summaries:
				found = False
				if tax['tax_type'] == actual['tax_type'] and tax[
						'tax_percentage'] == actual['tax_percentage']:
					actual['amount'] += tax['amount']
					found = True
			if found == False:
				actual_summaries.append(tax)

		for i in actual_summaries:
			print(i)

		for tax in tax_summaries:

			doc = frappe.get_doc({
				'doctype': 'Tax Summaries',
				'invoce_number': tax['invoice_number'],
				'tax_percentage': tax['tax_percentage'],
				'amount': tax['amount'],
				'tax_type': tax['tax_type'],
				'parent': invoice_number,
				'parentfield': 'gst_summary',
				'parenttype': "Invoices"
			})
			doc.insert(ignore_permissions=True)

	except Exception as e:
		print(e, 'insert tax summerie')


@frappe.whitelist(allow_guest=True)
def get_tax_payer_details(data):
	'''
	get TaxPayerDetail from gsp   gstNumber, code, apidata
	'''
	try:

		tay_payer_details = frappe.db.get_value('TaxPayerDetail',
												data['gstNumber'])
		if tay_payer_details is None:
			response = request_get(
				data['apidata']['get_taxpayer_details'] + data['gstNumber'],
				data['apidata'], data['invoice'], data['code'])
			if response['success']:

				details = response['result']
				if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
					if (details['AddrBno'] != "") or (details['AddrBno'] !=
													  ""):
						details['AddrBnm'] = details['AddrBno']
				if (details['AddrBno'] == "") or (details['AddrBno'] == None):
					if (details['AddrBnm'] != "") or (details['AddrBnm'] !=
													  None):
						details['AddrBno'] = details['AddrBnm']
				if (details['TradeName'] == "") or (details['TradeName']
													== None):
					if (details['LegalName'] != "") or (details['TradeName'] !=
														None):
						details['TradeName'] = details['LegalName']
				if (details['LegalName'] == "") or (details['LegalName']
													== None):
					if (details['TradeName'] != "") or (details['TradeName'] !=
														None):
						details['LegalName'] = details['TradeName']
				if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
					details['AddrLoc'] = "New Delhi"

				if len(details["AddrBnm"]) < 3:
					details["AddrBnm"] = details["AddrBnm"] + "    "
				if len(details["AddrBno"]) < 3:
					details["AddrBno"] = details["AddrBno"] + "    "
				tax_payer = frappe.new_doc('TaxPayerDetail')
				tax_payer.gst_number = details['Gstin']
				tax_payer.email = " "
				tax_payer.phone_number = " "
				tax_payer.legal_name = details['LegalName']
				tax_payer.address_1 = details['AddrBnm']
				tax_payer.address_2 = details['AddrBno']
				tax_payer.location = details['AddrLoc']
				tax_payer.pincode = details['AddrPncd']
				tax_payer.gst_status = details['Status']
				tax_payer.tax_type = details['TxpType']
				tax_payer.company = data['code']
				tax_payer.trade_name = details['TradeName']
				tax_payer.state_code = details['StateCode']
				tax_payer.last_fetched = datetime.date.today()
				tax_payer.address_floor_number = details['AddrFlno']
				tax_payer.address_street = details['AddrSt']
				tax_payer.block_status = ''
				tax_payer.status = details['Status']
				if details['Status'] == "ACT":
					tax_payer.status = 'Active'
					doc = tax_payer.insert(ignore_permissions=True)
					return {"success": True, "data": doc}
				else:
					tax_payer.status = 'In-Active'
					doc = tax_payer.insert(ignore_permissions=True)
					return {
						"success": False,
						"message": "Gst Number is Inactive"
					}
			else:
				print("Unknown error in get taxpayer details get call  ",
					  response)
				return {
					"success": False,
					"message": response['message'],
					"response": response
				}

		else:
			doc = frappe.get_doc('TaxPayerDetail', data['gstNumber'])
			return {"success": True, "data": doc}
	except Exception as e:
		print(e, "get tax payers")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def check_company_exist(code):
	try:
		company = frappe.get_doc('company', code)
		return {"success": True, "data": company}
	except Exception as e:
		print(e, "check company exist")
		return {"success": False, "message": str(e)}


def check_company_exist_for_Irn(code):
	try:
		company = frappe.get_doc('company', code)
		return {"success": True, "data": company}
	except Exception as e:
		print(e, "check company exist")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def check_token_is_valid(data):
	try:
		login_gsp(data['code'], data['mode'])
		gsp = frappe.db.get_value(
			'GSP APIS', {"company": data['code']},
			['gsp_test_token_expired_on', 'gsp_prod_token_expired_on'],
			as_dict=1)
		if gsp['gsp_test_token_expired_on'] != '' or gsp[
				'gsp_prod_token_expired_on']:
			expired_on = gsp['gsp_test_token_expired_on'] if data[
				'mode'] == 'Testing' else gsp['gsp_prod_token_expired_on']
			print(expired_on)
			return {"success": True}
		else:
			login_gsp(data['code'], data['mode'])
			return {"success": True}

	except Exception as e:
		print(e, "check token is valid")
		return {"success": False, "message": str(e)}


def login_gsp(code,mode):
	try:
		# code = "MHKCP-01"
		# mode = "Testing"
		# print("********** scheduler")
		gsp = frappe.db.get_value('GSP APIS', {"company": code}, [
			'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
			'gsp_prod_app_secret', 'gsp_test_app_secret', 'name'
		],
								  as_dict=1)
		if mode == 'Testing':
			headers = {
				"gspappid": gsp["gsp_test_app_id"],
				"gspappsecret": gsp["gsp_test_app_secret"],
			}
			login_response = request_post(gsp['auth_test'], code, headers)

			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
			gsp_update.gsp_test_token_expired_on = login_response['expires_in']
			gsp_update.gsp_test_token = login_response['access_token']
			gsp_update.save(ignore_permissions=True)
			return True
		elif mode == 'Production':
			headers = {
				"gspappid": gsp["gsp_prod_app_id"],
				"gspappsecret": gsp["gsp_prod_app_secret"]
			}
			login_response = request_post(gsp['auth_prod'], code, headers)
			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
			gsp_update.gsp_prod_token_expired_on = login_response['expires_in']
			gsp_update.gsp_prod_token = login_response['access_token']
			gsp_update.save(ignore_permissions=True)
			return True
	except Exception as e:
		print(e, "login gsp")


def login_gsp2():
	try:
		code = "MHKCP-01"
		mode = "Testing"
		print("********** scheduler")
		gsp = frappe.db.get_value('GSP APIS', {"company": code}, [
			'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
			'gsp_prod_app_secret', 'gsp_test_app_secret', 'name'
		],
								  as_dict=1)
		if mode == 'Testing':
			headers = {
				"gspappid": gsp["gsp_test_app_id"],
				"gspappsecret": gsp["gsp_test_app_secret"],
			}
			login_response = request_post(gsp['auth_test'], code, headers)

			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
			gsp_update.gsp_test_token_expired_on = login_response['expires_in']
			gsp_update.gsp_test_token = login_response['access_token']
			gsp_update.save(ignore_permissions=True)
			return True
		elif mode == 'Production':
			headers = {
				"gspappid": gsp["gsp_prod_app_id"],
				"gspappsecret": gsp["gsp_prod_app_secret"]
			}
			login_response = request_post(gsp['auth_prod'], code, headers)
			gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
			gsp_update.gsp_prod_token_expired_on = login_response['expires_in']
			gsp_update.gsp_prod_token = login_response['access_token']
			gsp_update.save(ignore_permissions=True)
			return True
	except Exception as e:
		print(e, "login gsp")

@frappe.whitelist(allow_guest=True)
def gsp_api_data(data):
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
		# print(api_details,"//////")
		return {"success":True,"data":api_details}
	except Exception as e:
		print(e,"gsp api details")
		return {"success":False,"message":str(e)}
		


def gsp_api_data_for_irn(data):
	try:
		mode = data['mode']
		gsp_apis = frappe.db.get_value('GSP APIS', {
			"company": data['code'],
			"name": data['provider'],
		}, [
			'auth_test',
			'cancel_test_irn',
			'extract_prod_qr_code',
			'extract_test_qr_code',
			'extract_test_signed_invoice',
			'generate_prod_irn',
			'generate_test_irn',
			'generate_test_qr_code_image',
			'get_tax_payer_prod',
			'get_tax_payer_test',
			'get_test_irn',
			'get_test_qr_image',
			'auth_prod',
			'cancel_prod_irn',
			'extract_prod_qr_code',
			'extract_prod_signed_invoice',
			'generate_prod_irn',
			'generate_prod_qr_code_image',
			'get_prod_irn',
			'get_prod_qr_image',
			'get_tax_payer_prod',
			'gsp_prod_app_id',
			'gsp_prod_app_secret',
			'gsp_test_app_id',
			'gsp_test_app_secret',
			'gsp_test_token',
			'gst__prod_username',
			'gst__test_username',
			'gst_prod_password',
			'gst_test_password',
			'gsp_prod_token',
			'gst_test_number',
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
		# print(api_details)
		# print(api_details)
		return {"success": True, "data": api_details}
	except Exception as e:
		print(e, "gsp api details for irn")
		return {"success": False, "message": str(e)}


def request_post(url, code, headers=None):
	try:
		company = frappe.get_doc('company', code)
		if company.proxy == 0:
			data = requests.post(url, headers=headers)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://", "@")
			proxies = {
				'http':
				'http://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost,
				'https':
				'https://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost
			}
			data = requests.post(url, headers=headers, proxies=proxies)
		if data.status_code == 200:
			response_data = data.json()
			if 'access_token' in response_data:
				return response_data
			else:
				print(response_data)
		else:
			print(data)
	except Exception as e:
		print(e, "request post")


def request_get(api, headers, invoice, code):
	try:
		headers = {
			"user_name": headers["username"],
			"password": headers["password"],
			"gstin": headers['gst'],
			"requestid": invoice + str(random.randrange(1, 10**4)),
			"Authorization": "Bearer " + headers['token']
		}
		company = frappe.get_doc('company', code)
		if company.proxy == 0:
			raw_response = requests.get(api, headers=headers)
		else:
			proxyhost = company.proxy_url
			proxyhost = proxyhost.replace("http://", "@")
			proxies = {
				'http':
				'http://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost,
				'https':
				'https://' + company.proxy_username + ":" +
				company.proxy_password + proxyhost
			}
			raw_response = requests.get(api, headers=headers, proxies=proxies)
		# print(raw_response.json())
		if raw_response.status_code == 200:
			return raw_response.json()
		else:
			print(raw_response.text)
	except Exception as e:
		print(e, "request get")


@frappe.whitelist(allow_guest=True)
def check_gstNumber_Length(data):

	print("Error:  *******The given gst number is not a vaild one**********")
	return {
		"success": False,
		"Message": "The given gst number is not a vaild one"
	}


@frappe.whitelist(allow_guest=True)
def check_invoice_file_exists(data):
	try:
		invoiceExists = frappe.get_value(
			'File', {"file_name": data['invoice'] + ".pdf"})

		if invoiceExists:
			# frappe.delete_doc('File', invoiceExists)

			filedata = frappe.get_doc('File', invoiceExists)

			return {"success": True, "data": filedata}
		return {"success": False, "message": "sample"}
	except Exception as e:
		print(e, "check file exist")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def check_invoice_exists(invoice_number):
	try:
		invoiceExists = frappe.get_doc('Invoices', invoice_number)
		if invoiceExists:

			return {"success": True, "data": invoiceExists}
		return {"success": False}
	except Exception as e:
		print(e, "check invoice exist")
		return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def Error_Insert_invoice(data):
	try:
		# print(data,"8888")
		invoice = frappe.get_doc({
			'doctype':
			'Invoices',
			'invoice_number':
			data['invoice_number'],
			'guest_name':
			data['guest_name'],
			'gst_number':
			data['gst_number'],
			'invoice_file':
			data['invoice_file'],
			'room_number':
			data['room_number'],
			'invoice_type':
			data['invoice_type'],
			'irn_generated':
			"Error",
			'invoice_date':
			datetime.datetime.strptime(data['invoice_date'],
									   '%d-%b-%y %H:%M:%S'),
			'legal_name':
			" ",
			# data['taxpayer']['legal_name'],
			'address_1':
			" ",
			# data['taxpayer']['address_1'],
			'email':
			" ",
			# data['taxpayer']['email'],
			'trade_name':
			" ",
			# data['taxpayer']['trade_name'],
			'address_2':
			" ",
			# data['taxpayer']['address_2'],
			'phone_number':
			" ",
			# data['taxpayer']['phone_number'],
			'location':
			" ",
			# data['taxpayer']['location'],
			'pincode':
			data['pincode'],
			'state_code':
			data['state_code'],
			'amount_before_gst':
			0,
			# round(value_before_gst, 2),
			"amount_after_gst":
			0,
			# round(value_after_gst, 2),
			"other_charges":
			0,  # round(other_charges,2),
			'irn_cancelled':
			'No',
			'qr_code_generated':
			'Pending',
			'signed_invoice_generated':
			'No',
			'company':
			data['company_code'],
			'ready_to_generate_irn':
			"No",
			'error_message':
			data['error_message']
		})
		v = invoice.insert(ignore_permissions=True, ignore_links=True)
	except Exception as e:
		print(e, "  Error insert Invoice")
		return {"success": False, "message": str(e)}


def attach_b2c_qrcode(data):
	try:
		invoice = frappe.get_doc('Invoices', data["invoice_number"])
		company = frappe.get_doc('company', invoice.company)
		folder_path = frappe.utils.get_bench_path()
		path = folder_path + '/sites/' + company.site_name
		attach_qrpath = path + "/private/files/" + data[
			"invoice_number"] + "attachb2cqr.pdf"
		src_pdf_filename = path + invoice.invoice_file
		img_filename = path + invoice.b2c_qrimage
		img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
							 company.qr_rect_y0, company.qr_rect_y1)
		document = fitz.open(src_pdf_filename)
		page = document[0]
		page.insertImage(img_rect, filename=img_filename)
		document.save(attach_qrpath)
		document.close()
		dst_pdf_text_filename = path + "/private/files/" + data[
			"invoice_number"] + 'withattachqr.pdf'
		doc = fitz.open(attach_qrpath)
		irn_number = ''.join(
			random.choice(string.ascii_uppercase + string.ascii_lowercase +
						  string.digits) for _ in range(50))
		ack_no = str(randint(100000000000, 9999999999999))
		ack_date = str(datetime.datetime.now())
		text = "IRN: " + irn_number + "      " + "ACK NO: " + ack_no + "    " + "ACK DATE: " + ack_date
		if company.irn_details_page == "First":
			page = doc[0]
		else:
			page = doc[-1]
		where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
		page.insertText(
			where,
			text,
			fontname="Roboto-Black",  # arbitrary if fontfile given
			fontfile=folder_path +
			company.font_file_path,  #fontpath,  # any file containing a font
			fontsize=6,  # default
			rotate=0,  # rotate text
			color=(0, 0, 0),  # some color (blue)
			overlay=True)
		doc.save(dst_pdf_text_filename)
		doc.close()
		files_new = {"file": open(dst_pdf_text_filename, 'rb')}
		payload_new = {
			"is_private": 1,
			"folder": "Home",
			"doctype": "Invoices",
			"docname": data["invoice_number"],
			'fieldname': 'b2c_qrinvoice'
		}
		site = company.host
		upload_qrinvoice_image = requests.post(site + "api/method/upload_file",
											   files=files_new,
											   data=payload_new)
		attach_response = upload_qrinvoice_image.json()
		if 'message' in attach_response:
			invoice.b2c_qrinvoice = attach_response['message']['file_url']
			invoice.name = data["invoice_number"]
			invoice.qr_generated = "Success"
			invoice.qr_code_generated = "Success"
			invoice.save(ignore_permissions=True, ignore_version=True)
			if os.path.exists(attach_qrpath):
				os.remove(attach_qrpath)
			return {"success": True, "message": "Qr Attached successfully"}
	except Exception as e:
		print(e, "attach b2c qrcode")
		return {"success": False, "message": e}
