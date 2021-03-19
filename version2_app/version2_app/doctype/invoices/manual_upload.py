from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import date
import requests
import datetime
import random
import traceback
import string
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
import time
import json
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.excel_upload_stats.excel_upload_stats import InsertExcelUploadStats
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
import math



@frappe.whitelist(allow_guest=True)
def manual_upload(data):
	try:
		start_time = datetime.datetime.now()
		folder_path = frappe.utils.get_bench_path()
		items_data_file = data['invoice_file']
		company = data['company']
		companyData = frappe.get_doc('company',data['company'])
		site_folder_path = companyData.site_name
		items_file_path = folder_path+'/sites/'+site_folder_path+items_data_file
		items_dataframe = pd.read_excel(items_file_path)
		items_dataframe = items_dataframe.fillna('empty')	
		items_dataframe['Gst Number'] = "NoGst"
		invoice_columns = list(items_dataframe.columns.values)
		invoice_num = list(set(items_dataframe['BILL_NO']))
		company_check_columns = companyData.bulk_import_invoice_headers
		company_check_columns = company_check_columns.split(",")

		if company_check_columns != invoice_columns:
			frappe.db.delete('File', {'file_url': data['invoice_file']})
			frappe.db.delete('File',{'file_url': data['gst_file']})
			frappe.db.commit()
			return {"success":False,"message":"Invoice data mismatch"}

		gst_data_file = data['gst_file']
		gst_file_path = folder_path+'/sites/'+site_folder_path+gst_data_file
		gst_dataframe = pd.read_csv(gst_file_path)
		columns = list(gst_dataframe.columns.values)
		gst_data = gst_dataframe.values.tolist()
		gst_data.insert(0,columns)
		gst_list = []
		count = gst_data[0][0].split("|")
		if companyData.bulk_import_gst_count != len(count):
			frappe.db.delete('File', {'file_url': data['invoice_file']})
			frappe.db.delete('File',{'file_url': data['gst_file']})
			frappe.db.commit()
			return {"success":False,"message":"Gst data mismatch"}
		for each in gst_data:
			if each[0][0]=="|":
				inv = each[0].split("|")
			else:
				inv = each[0].split("|")
				
				items_dataframe.loc[items_dataframe.BILL_NO==int(inv[1]),'Gst Number'] = inv[0]
				

				gst_list.append({"gst_number":inv[0],"invoice_number":inv[1]})

		input_data = []
		items_dataframe.loc[(items_dataframe.FOLIO_TYPE=="CREDIT TAX INVOICE"),'FOLIO_TYPE'] = 'Credit Invoice'
		items_dataframe.loc[(items_dataframe.FOLIO_TYPE=="TAX INVOICE"),'FOLIO_TYPE'] = 'Tax Invoice'
		output = items_dataframe.to_dict('records')
		list_data={}

		invoice_referrence_objects = {}
		
		for each in output:
			del each['BILL_GENERATION_DATE']
			del each['TRX_DATE']
			if each['FOLIO_TYPE'] == "SUMFT_DEBITPERREPORT" or each['TRANSACTION_DESCRIPTION']== 'empty':
				break
			
			if each['BILL_NO'] not in invoice_referrence_objects:
				
				invoice_referrence_objects[each['BILL_NO']] = []
				invoice_referrence_objects[each['BILL_NO']].append(each)
			else:
				invoice_referrence_objects[each['BILL_NO']].append(each)
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
					list_data['gstNumber'] = each['Gst Number']
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
						list_data['gstNumber'] = each['Gst Number']
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
		output_date = []


		for each in input_data:
			# each['invoice_number'] = str(each['invoice_number'])
			check_invoice = check_invoice_exists(str(each['invoice_number']))
			if check_invoice['success']==True:
				inv_data = check_invoice['data']
				if inv_data.docstatus!=2 and inv_data.irn_generated!="Success" and inv_data.invoice_type=="B2B":
					reupload = True
				elif inv_data.invoice_type == "B2C":
					reupload = True
				else:
					reupload = False	
			else:
				reupload = False	
			if each['invoice_category'] == "empty":
				each['invoice_category'] = "Tax Invoice"
			each['invoice_from'] = "File"
			each['company_code'] = data['company']
			
			each['invoice_date'] = each['invoice_date'].replace("/","-")
			date_time_obj = (each['invoice_date'].split(":")[-1]).strip()
			date_time_obj = datetime.datetime.strptime(date_time_obj,'%d-%m-%y').strftime('%d-%b-%y %H:%M:%S')
			each['invoice_date'] = date_time_obj
			each['mode'] = companyData.mode
			each['invoice_file'] = ""
			each['gstNumber'] = each['gstNumber']
			if each['gstNumber'] == "NoGst":
				each['invoice_type'] = "B2C"
				each['gstNumber']=""
			else:
				each['invoice_type'] = "B2B"
				invoice_referrence_objects[each['invoice_number']][0]['gstNumber'] = each['gstNumber']

			each['confirmation_number'] = each['invoice_number']
			each['print_by'] = "System"
			each['start_time'] = str(datetime.datetime.utcnow())
			each['name'] = each['guest_name']
			error_data = {"invoice_type":'B2B' if gstNumber != '' else 'B2C',"invoice_number":each['invoice_number'],"company_code":data['company'],"invoice_date":each['invoice_date']}
			error_data['invoice_file'] = ""
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
			sez = 0
			
			if each['invoice_type']=="B2B":
				gspApiDataResponse = gsp_api_data({"code":data['company'],"mode":companyData.mode,"provider":companyData.provider})
				checkTokenIsValidResponse = check_token_is_valid({"code":data['company'],"mode":companyData.mode})
				if checkTokenIsValidResponse['success'] == True:
					getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":each['gstNumber'],"code":data['company'],"invoice":each['invoice_number'],"apidata":gspApiDataResponse['data']})
					if getTaxPayerDetailsResponse['success'] == True:
						sez = 1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
						each['sez']=1 if getTaxPayerDetailsResponse["data"].tax_type == "SEZ" else 0
						taxpayer=getTaxPayerDetailsResponse['data'].__dict__
			calulateItemsApiResponse = calulate_items(each)

			if calulateItemsApiResponse['success'] == True:
				if reupload==False:
					insertInvoiceApiResponse = insert_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":each['invoice_number'],"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":invoice_referrence_objects[each['invoice_number']]})
					print(insertInvoiceApiResponse)
					if insertInvoiceApiResponse['success']== True:
						
						if insertInvoiceApiResponse['data'].invoice_type == "B2B":
							B2B = "B2B"
							B2C = np.nan
						else:
							B2B=np.nan
							B2C = "B2C"	 
						if insertInvoiceApiResponse['data'].irn_generated == "Success":
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						else:
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
					else:
						error_data['error_message'] = insertInvoiceApiResponse['message']
						error_data['invoice_object_from_file'] = invoice_referrence_objects[each['invoice_number']]
						errorInvoice = Error_Insert_invoice(error_data)
						if errorInvoice['data'].invoice_type == "B2B":
							B2B = "B2B"
							B2C = np.nan
						else:
							B2B=np.nan
							B2C = "B2C"
						output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
				else:
					insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,"invoice_object_from_file":invoice_referrence_objects[each['invoice_number']]})
					if insertInvoiceApiResponse['success']== True:
						
						if insertInvoiceApiResponse['data'].invoice_type == "B2B":
							B2B = "B2B"
							B2C = np.nan
						else:
							B2B=np.nan
							B2C = "B2C"	 
						if insertInvoiceApiResponse['data'].irn_generated == "Success":
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Success":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						elif insertInvoiceApiResponse['data'].irn_generated == "Pending":
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Pending":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						else:
							output_date.append({'invoice_number':insertInvoiceApiResponse['data'].name,"Error":insertInvoiceApiResponse['data'].irn_generated,"date":str(insertInvoiceApiResponse['data'].invoice_date),"B2B":B2B,"B2C":B2C})
					else:
						error_data['error_message'] = insertInvoiceApiResponse['message']
						error_data['invoice_object_from_file'] = invoice_referrence_objects[each['invoice_number']]
						errorInvoice = Error_Insert_invoice(error_data)
						if errorInvoice['data'].invoice_type == "B2B":
							B2B = "B2B"
							B2C = np.nan
						else:
							B2B=np.nan
							B2C = "B2C"
						output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
						print("B2C insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])

			else:
						
				error_data['error_message'] = calulateItemsApiResponse['message']
				error_data['invoice_object_from_file'] = invoice_referrence_objects[each['invoice_number']]
				errorInvoice = Error_Insert_invoice(error_data)
				if errorInvoice['data'].invoice_type == "B2B":
					B2B = "B2B"
					B2C = np.nan
				else:
					B2B=np.nan
					B2C = "B2C"
				output_date.append({'invoice_number':errorInvoice['data'].name,"Error":errorInvoice['data'].irn_generated,"date":str(errorInvoice['data'].invoice_date),"B2B":B2B,"B2C":B2C})
				print("calulateItemsApi fialed:  ",calulateItemsApiResponse['message'])
		df = pd.DataFrame(output_date)
		df = df.groupby('date').count().reset_index()
		output_data = df.to_dict('records')
		# data['UserName'] = "Ganesh"
		InsertExcelUploadStats({"data":output_data,"uploaded_by":data['username'],"start_time":str(start_time),"referrence_file":data['invoice_file'],"gst_file":data['gst_file']})

		return {"success":True,"message":"Successfully Uploaded Invoices","data":output_data}		

	except Exception as e:
		frappe.db.delete('File', {'file_url': data['invoice_file']})
		frappe.db.delete('File',{'file_url': data['gst_file']})
		frappe.db.commit()
		print(str(e),"   manual_upload")
		return {"success":False,"message":str(e)}    
