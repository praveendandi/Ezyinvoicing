# -*- coding: utf-8 -*-
# Copyright (c) 2020, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import random
import traceback 
from frappe.utils import get_site_name
import time

from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz

site = 'http://0.0.0.0:8000/'
site_folder_path = 'version2_app.com/'
fontpath = '/home/caratred/frappe_projects/Einvoice_Bench/apps/version2_app/version2_app/version2_app/doctype/invoices/Roboto-Black.ttf'
# site = 'http://jps.ezyinvoicing.com/'
# site_folder_path = 'jps.ezyinvoicing.com/'
# fontpath = '/home/frappe/invoices/apps/einvoices/einvoices/einvoices/doctype/invoices/Roboto-Black.ttf'


@frappe.whitelist(allow_guest=True)
def Reinitiate_invoice(data):
	'''
	insert invoice data     data, company_code, taxpayer,items_data
	'''
	try:
		print(data['taxpayer'])
		total_invoice_amount = data['total_invoice_amount']
		del data['total_invoice_amount']
		value_before_gst = 0
		value_after_gst = 0
		other_charges = 0
		credit_value_before_gst = 0
		credit_value_after_gst = 0
		
		if "legal_name" not in data['taxpayer']:
			data['taxpayer']['legal_name'] = " "
				
		#calculat items
		# items_data = calulate_items(data['items'], data['invoice_number'],company_code)
		for item in data['items_data']:
			if item['taxable'] == 'No':
				other_charges += item['item_value']

			elif item['sac_code'].isdigit():  
				if "-" not in str(item['item_value']):
					# has_cedit_items = Y
					value_before_gst += item['item_value']
					value_after_gst += item['item_value_after_gst']
				else:
					credit_value_before_gst += abs(item['item_value'])
					credit_value_after_gst  += abs(item['item_value_after_gst'])
			else:
				pass
		if (round(value_after_gst,2) - round(credit_value_after_gst,2)) >0:
			ready_to_generate_irn = "Yes"
		else:
			ready_to_generate_irn = "No"		
		pms1 = round(value_before_gst,2) - round(credit_value_before_gst,2)	
		pms2 = round(value_after_gst,2) - round(credit_value_after_gst,2)
		# print(pms1,pms2,credit_value_after_gst,credit_value_before_gst)
		# print(type(value_after_gst),type(value_before_gst),type(other_charges),type(credit_value_after_gst),type(credit_value_before_gst),type(total_invoice_amount))	
		if credit_value_after_gst>0:
			has_cedit_items = "Yes"
		else:
			has_cedit_items = "No"	
		if "address_1" not in data['taxpayer']:
			data['taxpayer']['address_1'] = data['taxpayer']['address_2']	
		doc = frappe.get_doc('Invoices',data['guest_data']['invoice_number'])
			
		doc.invoice_number=data['guest_data']['invoice_number']
		doc.guest_name=data['guest_data']['name']
		doc.gst_number=data['guest_data']['gstNumber']
		doc.invoice_file=data['guest_data']['invoice_file']
		doc.room_number=data['guest_data']['room_number']
		doc.invoice_type=data['guest_data']['invoice_type']
		doc.invoice_date=datetime.datetime.strptime(data['guest_data']['invoice_date'],'%d-%b-%y %H:%M:%S')
		doc.legal_name=data['taxpayer']['legal_name']
		doc.address_1=data['taxpayer']['address_1']
		doc.email=data['taxpayer']['email']
		doc.conformation_number = data['guest_data']['conformation_number']
		doc.trade_name=data['taxpayer']['trade_name']
		doc.address_2=data['taxpayer']['address_2']
		phone_number=data['taxpayer']['phone_number']
		location=data['taxpayer']['location']
		pincode=data['taxpayer']['pincode']
		state_code=data['taxpayer']['state_code']
		doc.amount_before_gst=round(value_before_gst, 2)
		doc.amount_after_gst=round(value_after_gst, 2)
		doc.credit_value_before_gst=round(credit_value_before_gst,2)
		doc.credit_value_after_gst=round(credit_value_after_gst,2)
		doc.pms_invoice_summary_without_gst=pms1
		doc.pms_invoice_summary= pms2
		doc.other_charges= other_charges
		doc.ready_to_generate_irn = ready_to_generate_irn
		doc.has_cedit_items = has_cedit_items
		doc.irn_generated='Pending'
		doc.irn_cancelled='No'
		doc.qr_code_generated='Pending'
		doc.signed_invoice_generated='No'
		doc.company=data['company_code']
		doc.save()

		# v = invoice.insert(ignore_permissions=True, ignore_links=True)
		# print(invoice)
		# if total_invoice_amount == value_after_gst - credit_value_after_gst: 
			# v = invoice.insert(ignore_permissions=True, ignore_links=True)
		items = data['items_data']
		# items = [x for x in items if x['sac_code']!="Liquor"]
	
		itemsInsert = insert_items(items)
		# insert tax summaries
		# insert_tax_summaries(items_data, data['invoice_number'])
		taxSummariesInsert = insert_tax_summariesd(items, data['guest_data']['invoice_number'])
		# insert sac code based taxes
		hsnbasedtaxcodes = insert_hsn_code_based_taxes(items, data['guest_data']['invoice_number'])
		return {"success":True}
		# return {"success":False,"message":"calculation doesnot match"}	
	except Exception as e:
		print(e,"reinitaite invoice", traceback.print_exc())
		return {"success":False,"message":e}
		


def insert_hsn_code_based_taxes(items, invoice_number):
	try:
		sac_codes = []
		for item in items:
			if item['sac_code'] not in sac_codes:
				sac_codes.append(item['sac_code'])

		tax_data = []
		for sac in sac_codes:
			sac_tax = {
				'cgst': 0,
				'sgst': 0,
				'igst': 0,
				'sac_hsn_code': sac,
				'invoice_number': invoice_number,
				'doctype': "SAC HSN Tax Summaries",
				'parent': invoice_number,
				'parentfield': 'sac_hsn_based_taxes',
				'parenttype': "invoices"
			}
			for item in items:
				if item['sac_code'] == sac:
					sac_tax['cgst'] += item['cgst_amount']
					sac_tax['sgst'] += item['sgst_amount']
					sac_tax['igst'] += item['igst_amount']
			tax_data.append(sac_tax)

		for sac in tax_data:
			sac['total_amount'] = sac['cgst'] + sac['sgst'] + sac['igst']
			doc = frappe.get_doc(sac)
			doc.insert(ignore_permissions=True, ignore_links=True)
			return {"sucess":True,"data":doc}
	except Exception as e:
		print(e,"insert hsn")
		return {"success":False,"message":e}
		


def insert_items(items):
	try:
		itemsDelete = frappe.db.delete('Items', {
    		'parent': items[0]['parent']})
		frappe.db.commit()
		for item in items:
			
			if "-" in str(item['item_value']):
				item['is_credit_item'] = "Yes"
			else:
				item['is_credit_item'] = "No"
			doc = frappe.get_doc(item)
			doc.insert(ignore_permissions=True, ignore_links=True)
		return {"sucess":True,"data":doc}
			# print(doc)
	except Exception as e:
		print(e,"insert itemns api")
		return {"success":False,"message":e}
		



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
			# print('*************************************8')

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
		return {"success":True}
	except Exception as e:
		print('tax', e)
		return {'succes':False,"message":e}
		

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
		print(e,'insert tax summerie')



import os
import subprocess
# site = 'http://0.0.0.0:8000/'
# site_folder_path = 'version2_app.com'

@frappe.whitelist(allow_guest=True)
def CallReinitiateParser(data):
	
	folder_path = frappe.utils.get_bench_path()
	path = folder_path + '/sites/' + site_folder_path
	filepath = path+data['filepath']
	path = path + "public/files/jp_siddharth_reinitiate.py"
	print(path,"************","python "+path+" "+filepath+" "+"yes")
	# v=os.system("python "+path+" "+filepath+" "+"yes")
	# print(v,type(v),"*))))))))))))))")
	v = os.popen("python "+path+" "+filepath+" "+"yes")
	print(v.read(),"///////////////////")
	# out = subprocess.Popen(["python "+path+" "+filepath+" "+"yes"], 
    #        stdout=subprocess.PIPE, 
    #        stderr=subprocess.STDOUT)
	# out =subprocess.call("python "+path+" "+filepath+" "+"yes")
	# print(out,"*********")
	return {"success":True,"data":'out'}
