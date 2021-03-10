from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import random
import traceback
import string
from frappe.utils import get_site_name
import pandas as pd
import time

from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
# from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
import math



@frappe.whitelist(allow_guest=True)
def manual_upload(data):
	try:
		folder_path = frappe.utils.get_bench_path()
		items_data_file = data['invoice_file']
		company = data['company']
		companyData = frappe.get_doc('company',data['company'])
		site_folder_path = companyData.site_name
		items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
		items_dataframe = pd.read_excel(items_file_path)
		items_dataframe = items_dataframe.fillna('empty')	
				
		input_data = []
		items_dataframe.loc[(items_dataframe.FOLIO_TYPE=="CREDIT TAX INVOICE"),'FOLIO_TYPE'] = 'Credit Invoice'
		items_dataframe.loc[(items_dataframe.FOLIO_TYPE=="TAX INVOICE"),'FOLIO_TYPE'] = 'Tax Invoice'
		output = items_dataframe.to_dict('records')
		list_data={}
		# print(output)
		for each in output:
			if each['FOLIO_TYPE'] == "SUMFT_DEBITPERREPORT" or each['TRANSACTION_DESCRIPTION']== 'empty':
				break
			
			if "CGST" in each['TRANSACTION_DESCRIPTION'] or "SGST" in each['TRANSACTION_DESCRIPTION'] or "IGST" in each['TRANSACTION_DESCRIPTION']:
				continue
			paymentTypes = GetPaymentTypes()
			payment_Types  = [''.join(each) for each in paymentTypes['data']]
			if each['TRANSACTION_DESCRIPTION'] not in payment_Types:
				if 'invoice_number' not in list_data:
					list_data['invoice_category'] = each['FOLIO_TYPE']
					list_data['invoice_number'] = each['BILL_NO']
					list_data['invoice_date'] = each['BILL_GENERATION_DATE_CHAR']
					list_data['room_number'] = each['ROOM']
					list_data['guest_name'] = each['DISPLAY_NAME']
					list_data['total_invoice_amount'] = each['SUMFT_DEBITPERBILL_NO']
					item_list = {'date':each['BILL_GENERATION_DATE_CHAR'],'item_value':each['FT_DEBIT'],'name':each['TRANSACTION_DESCRIPTION'],'sort_order':1,"sac_code":'No Sac'}
					items = []
					items.append(item_list)
					list_data['items'] = items
					list_data['company_code'] = data['company']
					list_data['invoice_number'] = each['BILL_NO']
					list_data['place_of_supply'] = companyData.state_code
					list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
					list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
				else:
					if list_data['invoice_number'] == each['BILL_NO']:
						items = {'date':each['BILL_GENERATION_DATE_CHAR'],"sac_code":'No Sac','item_value':each['FT_DEBIT'],'name':each['TRANSACTION_DESCRIPTION'],'sort_order':1}
						list_data['items'].extend([items])
					else:
						input_data.append(list_data)
						list_data = {}
						list_data['invoice_category'] = each['FOLIO_TYPE']
						list_data['invoice_number'] = each['BILL_NO']
						list_data['invoice_date'] = each['BILL_GENERATION_DATE_CHAR']
						list_data['room_number'] = each['ROOM']
						list_data['guest_name'] = each['DISPLAY_NAME']
						list_data['total_invoice_amount'] = each['SUMFT_DEBITPERBILL_NO']
						item_list = {'date':each['BILL_GENERATION_DATE_CHAR'],"sac_code":'No Sac','item_value':each['FT_DEBIT'],'name':each['TRANSACTION_DESCRIPTION'],'sort_order':1}
						items = []
						items.append(item_list)
						list_data['items'] = items
						list_data['company_code'] = data['company']
						list_data['invoice_number'] = each['BILL_NO']
						list_data['place_of_supply'] = companyData.state_code
						list_data['invoice_item_date_format'] = companyData.invoice_item_date_format
						list_data['guest_data'] = {'invoice_category':list_data['invoice_category']}
		
		taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
		gstNumber = ''
		for each in input_data:
			# print(type(each['items']),each['invoice_number'],each['invoice_category'])
			# each['items'] = each['items']
			if each['invoice_category'] == "empty":
				each['invoice_category'] = "Tax Invoice"
			each['invoice_from'] = "File"
			each['company_code'] = data['company']
			each['invoice_date'] = "23-DEC-20 07:55:00"
			each['invoice_type'] = "B2C"
			each['invoice_file'] = " "
			each['gstNumber'] = ""
			each['confirmation_number'] = each['invoice_number']
			each['print_by'] = "System"
			each['start_time'] = str(datetime.datetime.utcnow())
			each['name'] = each['guest_name']
			error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":each['invoice_number'],"company_code":data['company'],"invoice_date":each['invoice_date']}
			error_data['invoice_file'] = " "
			error_data['guest_name'] = each['guest_name']
			error_data['gst_number'] = ''
			if each['invoice_type'] == "B2C":
				error_data['gst_number'] == " "
			error_data['state_code'] =  " "
			error_data['room_number'] = each['room_number']
			error_data['pincode'] = ""
			error_data['total_invoice_amount'] = each['total_invoice_amount']
			error_data['sez'] = 0
			error_data['invoice_from'] = "File"
			each['sez'] = 0
			print(each['invoice_from'])
			calulateItemsApiResponse = calulate_items(each)
			if calulateItemsApiResponse['success'] == True:
				
				insertInvoiceApiResponse = insert_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":0})
				if insertInvoiceApiResponse['success']== True:
					print("B2C Invoice Created",insertInvoiceApiResponse)
				else:
					
					error_data['error_message'] = insertInvoiceApiResponse['message']
					errorInvoice = Error_Insert_invoice(error_data)
					print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])

			else:
						
				error_data['error_message'] = calulateItemsApiResponse['message']
				errorInvoice = Error_Insert_invoice(error_data)
				print("B2C calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])

		gst_data_file = data['gst_file']
		# company = data['company']
		# companyData = frappe.get_doc('company',data['company'])
		# site_folder_path = companyData.site_name
		gst_file_path = folder_path+'/sites/'+site_folder_path+gst_data_file
		gst_dataframe = pd.read_csv(gst_file_path)
		columns = list(gst_dataframe.columns.values)
		gst_data = gst_dataframe.values.tolist()
		gst_data.insert(0,columns)
		gst_list = []
		for each in gst_data:
			if each[0][0]=="|":
				inv = each[0].split("|")
			else:
				inv = each[0].split("|")
				gst_list.append({"gst_number":inv[0],"invoice_number":inv[1]})	
		# print(gst_list)
		for each in gst_list:
			gspApiDataResponse = gsp_api_data({"code":data['company'],"mode":companyData.mode,"provider":companyData.provider})
			if gspApiDataResponse['success'] == True:
				getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":each['gst_number'],"code":data['company'],"invoice":each['invoice_number'],"apidata":gspApiDataResponse['data']})
				
				if getTaxPayerDetailsResponse['success'] == True:
					taxpayer = getTaxPayerDetailsResponse['data'].__dict__
					
					if frappe.db.exists('Invoices', each['invoice_number']):
						invoice = frappe.get_doc("Invoices",each['invoice_number'])
						print(invoice)
						irn_generated = invoice.irn_generated
						invoice.gst_number = each['gst_number']
						invoice.legal_name = taxpayer['legal_name']
						invoice.trade_name =  taxpayer['trade_name']
						invoice.address_1 = taxpayer['address_1']
						invoice.address_2 = taxpayer['address_2']
						invoice.email = taxpayer['email']
						invoice.phone_number = taxpayer['phone_number']
						invoice.location = taxpayer['location']
						invoice.pincode = taxpayer['pincode']
						invoice.state_code = taxpayer['state_code']
						if irn_generated == "Success":
							invoice.irn_generated = "Pending"
						invoice.invoice_type = "B2B"	
						invoice.save()
						if companyData.allow_auto_irn ==1:
							if irn_generated == "Success" or irn_generated=="Pending":
								irn_data = {'invoice_number': each['invoice_number'],'generation_type': "System"}
								irn_generate = generateIrn(irn_data)

		return {"success":True,"message":"Successfully Updated Gst Numbers"}		
		return input_data

	except Exception as e:
		print(str(e),"   manual_upload")
		return {"success":False,"message":str(e)}    

@frappe.whitelist(allow_guest=True)
def updateGstNumber(data):
	try:
		folder_path = frappe.utils.get_bench_path()
		items_data_file = data['invoice_file']
		gst_data_file = data['gst_file']
		company = data['company']
		companyData = frappe.get_doc('company',data['company'])
		site_folder_path = companyData.site_name
		gst_file_path = folder_path+'/sites/'+site_folder_path+gst_data_file
		gst_dataframe = pd.read_csv(gst_file_path)
		columns = list(gst_dataframe.columns.values)
		gst_data = gst_dataframe.values.tolist()
		gst_data.insert(0,columns)
		gst_list = []
		for each in gst_data:
			if each[0][0]=="|":
				inv = each[0].split("|")
			else:
				inv = each[0].split("|")
				gst_list.append({"gst_number":inv[0],"invoice_number":inv[1]})	
		# print(gst_list)
		for each in gst_list:
			gspApiDataResponse = gsp_api_data({"code":data['company'],"mode":companyData.mode,"provider":companyData.provider})
			if gspApiDataResponse['success'] == True:
				getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":each['gst_number'],"code":data['company'],"invoice":each['invoice_number'],"apidata":gspApiDataResponse['data']})
				
				if getTaxPayerDetailsResponse['success'] == True:
					taxpayer = getTaxPayerDetailsResponse['data'].__dict__
					
					if frappe.db.exists('Invoices', each['invoice_number']):
						invoice = frappe.get_doc("Invoices",each['invoice_number'])
						print(invoice)
						irn_generated = invoice.irn_generated
						invoice.gst_number = each['gst_number']
						invoice.legal_name = taxpayer['legal_name']
						invoice.trade_name =  taxpayer['trade_name']
						invoice.address_1 = taxpayer['address_1']
						invoice.address_2 = taxpayer['address_2']
						invoice.email = taxpayer['email']
						invoice.phone_number = taxpayer['phone_number']
						invoice.location = taxpayer['location']
						invoice.pincode = taxpayer['pincode']
						invoice.state_code = taxpayer['state_code']
						if irn_generated == "Success":
							invoice.irn_generated = "Pending"
						invoice.invoice_type = "B2B"	
						invoice.save()
						if companyData.allow_auto_irn ==1:
							if irn_generated == "Success" or irn_generated=="Pending":
								irn_data = {'invoice_number': each['invoice_number'],'generation_type': "System"}
								irn_generate = generateIrn(irn_data)

		return {"success":True,"message":"Successfully Updated Gst Numbers"}
	except Exception as e:
		print(str(e),"     updateGstNumber  ")
		return {"success":False,"message":str(e)}	
	 		
