from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import time
import traceback
import os
import datetime
import json
from version2_app.version2_app.doctype.invoices.invoices import calulate_items
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.payment_types.payment_types import *

# {'items': [{'date': '11-12-19', 'item_value': 222000.0, 'sac_code': 'No Sac', 'sort_order': 1, 'name': 'BQT (OC) Lunch'}], 'invoice_number': '303698', 'company_code': 'ICSJWMA-01', 'invoice_item_date_format': '%d-%m-%y', 'sez': 0}
# insertInvoiceApiResponse = Reinitiate_invoice({"guest_data":each,"company_code":data['company'],"items_data":calulateItemsApiResponse['data'],
# "total_invoice_amount":each['total_invoice_amount'],"invoice_number":str(each['invoice_number']),"amened":'No',"taxpayer":taxpayer,"sez":sez,
# "invoice_object_from_file":invoice_referrence_objects[each['invoice_number']]})
 

@frappe.whitelist(allow_guest=True)
def BulkUploadReprocess(data):
	try:
		invoice_number = data['invoice_number']
		invoice_data = frappe.get_doc('Invoices',invoice_number)

		company = frappe.get_doc('company',invoice_data.company)
		if company.bulk_excel_upload_type == "HolidayIn":
			line_items = json.loads(invoice_data.invoice_object_from_file)
			print(line_items,type(line_items),type(invoice_data.invoice_object_from_file))
			# invoice_date = invoice_data.invoice_date
			invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
			items = []
			sort_order = 1
			paymentTypes = GetPaymentTypes()
			payment_Types  = [''.join(each) for each in paymentTypes['data']]
			for each in line_items['data']:
				if each['goods_desc'] not in payment_Types:
					item_dict = {}
					date_time_obj = datetime.datetime.strptime(each['invoicedate'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
					item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
					item_dict['item_value'] = each['invoiceamount']
					item_dict['sac_code'] = str(each["taxcode_dsc"])
					item_dict['name'] = each['goods_desc']
					item_dict['sort_order'] = sort_order
					sort_order+=1
					items.append(item_dict)
			calculate_data = {}
			calculate_data['items'] = items
			calculate_data['invoice_number'] = invoice_number
			calculate_data['company_code'] = invoice_data.company 
			calculate_data['invoice_item_date_format'] = company.invoice_item_date_format
			calculate_data['sez'] = invoice_data.sez	
			calculate_items_data = calulate_items(calculate_data)
			print(calculate_items_data)
			if calculate_items_data['success']==True:

				guest_data = {'items':calculate_items_data['data'],'name':invoice_data.guest_name,"invoice_number":invoice_data.name,"membership":"","invoice_date":invdate,"invoice_type":invoice_data.invoice_type,
								"gstNumber":invoice_data.gst_number,"room_number":invoice_data.room_number,"company_code":company.name,"confirmation_number":invoice_data.confirmation_number,"start_time":str(datetime.datetime.now()),"print_by":invoice_data.print_by,"invoice_category":invoice_data.invoice_category,"invoice_file":invoice_data.invoice_file}
				reinitiate_data = {"company_code":company.name,"items_data":calculate_items_data['data'],"total_invoice_amount":invoice_data.total_invoice_amount,"invoice_number":invoice_data.name,"amened":"No","sez":invoice_data.sez}
				taxpayer_details = {"gst_number":invoice_data.gst_number,"legal_name":invoice_data.legal_name,"email":invoice_data.email,"address_1":invoice_data.address_1,"address_2":invoice_data.address_1,"trade_name":invoice_data.trade_name,"location":invoice_data.location,"pincode":invoice_data.pincode,"phone_number":invoice_data.phone_number,"state_code":invoice_data.state_code}
				reinitiate_data['taxpayer']= taxpayer_details
				reinitiate_data['guest_data'] = guest_data
				reinitiate_data['invoice_object_from_file'] = json.loads(invoice_data.invoice_object_from_file)
				invoicereinitiate = Reinitiate_invoice(reinitiate_data)
				return invoicereinitiate

			return {"success":True,"data":line_items}
		elif company.bulk_excel_upload_type == "Marriot":
			line_items = json.loads(invoice_data.invoice_object_from_file)
			print(line_items,type(line_items),type(invoice_data.invoice_object_from_file))
			# invoice_date = invoice_data.invoice_date
			invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
			items = []
			sort_order = 1
			paymentTypes = GetPaymentTypes()
			payment_Types  = [''.join(each) for each in paymentTypes['data']]
			for each in line_items['data']:
				if each['TRANSACTION_DESCRIPTION'] not in payment_Types:
					item_dict = {}
					date_time_obj = datetime.datetime.strptime(each['BILL_GENERATION_DATE'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
					item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
					item_dict['item_value'] = each['FT_DEBIT']
					item_dict['sac_code'] = "No Sac"
					item_dict['name'] = each['TRANSACTION_DESCRIPTION']
					item_dict['sort_order'] = sort_order
					sort_order+=1
					items.append(item_dict)
			calculate_data = {}
			calculate_data['items'] = items
			calculate_data['invoice_number'] = invoice_number
			calculate_data['company_code'] = invoice_data.company 
			calculate_data['invoice_item_date_format'] = company.invoice_item_date_format
			calculate_data['sez'] = invoice_data.sez	
			calculate_items_data = calulate_items(calculate_data)
			print(calculate_items_data)
			if calculate_items_data['success']==True:

				guest_data = {'items':calculate_items_data['data'],'name':invoice_data.guest_name,"invoice_number":invoice_data.name,"membership":"","invoice_date":invdate,"invoice_type":invoice_data.invoice_type,
								"gstNumber":invoice_data.gst_number,"room_number":invoice_data.room_number,"company_code":company.name,"confirmation_number":invoice_data.confirmation_number,"start_time":str(datetime.datetime.now()),"print_by":invoice_data.print_by,"invoice_category":invoice_data.invoice_category,"invoice_file":invoice_data.invoice_file}
				reinitiate_data = {"company_code":company.name,"items_data":calculate_items_data['data'],"total_invoice_amount":invoice_data.total_invoice_amount,"invoice_number":invoice_data.name,"amened":"No","sez":invoice_data.sez}
				taxpayer_details = {"gst_number":invoice_data.gst_number,"legal_name":invoice_data.legal_name,"email":invoice_data.email,"address_1":invoice_data.address_1,"address_2":invoice_data.address_1,"trade_name":invoice_data.trade_name,"location":invoice_data.location,"pincode":invoice_data.pincode,"phone_number":invoice_data.phone_number,"state_code":invoice_data.state_code}
				reinitiate_data['taxpayer']= taxpayer_details
				reinitiate_data['guest_data'] = guest_data
				reinitiate_data['invoice_object_from_file'] = json.loads(invoice_data.invoice_object_from_file)
				invoicereinitiate = Reinitiate_invoice(reinitiate_data)
				return invoicereinitiate

			return {"success":True,"data":line_items}
		else:
			return {"success":False}	
	except Exception as e:
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}    

# @frappe.whitelist(allow_guest=True)
# def BulkUploadReprocess(data):
# 	try:
# 		invoice_number = data['invoice_number']
# 		invoice_data = frappe.get_doc('Invoices',invoice_number)

# 		company = frappe.get_doc('company',invoice_data.company)
# 		line_items = json.loads(invoice_data.invoice_object_from_file)
# 		print(line_items,type(line_items),type(invoice_data.invoice_object_from_file))
# 		# invoice_date = invoice_data.invoice_date
# 		invdate =datetime.datetime.strptime(str(invoice_data.invoice_date),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
# 		items = []
# 		sort_order = 1
# 		paymentTypes = GetPaymentTypes()
# 		payment_Types  = [''.join(each) for each in paymentTypes['data']]
# 		for each in line_items['data']:
# 			if each['TRANSACTION_DESCRIPTION'] not in payment_Types:
# 				item_dict = {}
# 				date_time_obj = datetime.datetime.strptime(each['BILL_GENERATION_DATE'],'%Y-%m-%d %H:%M:%S').strftime(company.invoice_item_date_format)
# 				item_dict['date'] = date_time_obj#each['BILL_GENERATION_DATE_CHAR']
# 				item_dict['item_value'] = each['FT_DEBIT']
# 				item_dict['sac_code'] = "No Sac"
# 				item_dict['name'] = each['TRANSACTION_DESCRIPTION']
# 				item_dict['sort_order'] = sort_order
# 				sort_order+=1
# 				items.append(item_dict)
# 		calculate_data = {}
# 		calculate_data['items'] = items
# 		calculate_data['invoice_number'] = invoice_number
# 		calculate_data['company_code'] = invoice_data.company 
# 		calculate_data['invoice_item_date_format'] = company.invoice_item_date_format
# 		calculate_data['sez'] = invoice_data.sez	
# 		calculate_items_data = calulate_items(calculate_data)
# 		print(calculate_items_data)
# 		if calculate_items_data['success']==True:

# 			guest_data = {'items':calculate_items_data['data'],'name':invoice_data.guest_name,"invoice_number":invoice_data.name,"membership":"","invoice_date":invdate,"invoice_type":invoice_data.invoice_type,
# 							"gstNumber":invoice_data.gst_number,"room_number":invoice_data.room_number,"company_code":company.name,"confirmation_number":invoice_data.confirmation_number,"start_time":str(datetime.datetime.now()),"print_by":invoice_data.print_by,"invoice_category":invoice_data.invoice_category,"invoice_file":invoice_data.invoice_file}
# 			reinitiate_data = {"company_code":company.name,"items_data":calculate_items_data['data'],"total_invoice_amount":invoice_data.total_invoice_amount,"invoice_number":invoice_data.name,"amened":"No","sez":invoice_data.sez}
# 			taxpayer_details = {"gst_number":invoice_data.gst_number,"legal_name":invoice_data.legal_name,"email":invoice_data.email,"address_1":invoice_data.address_1,"address_2":invoice_data.address_1,"trade_name":invoice_data.trade_name,"location":invoice_data.location,"pincode":invoice_data.pincode,"phone_number":invoice_data.phone_number,"state_code":invoice_data.state_code}
# 			reinitiate_data['taxpayer']= taxpayer_details
# 			reinitiate_data['guest_data'] = guest_data
# 			reinitiate_data['invoice_object_from_file'] = json.loads(invoice_data.invoice_object_from_file)
# 			invoicereinitiate = Reinitiate_invoice(reinitiate_data)
# 			return invoicereinitiate

# 		return {"success":True,"data":line_items}
# 	except Exception as e:
# 		print(traceback.print_exc())
# 		return {"success":False,"message":str(e)}    
