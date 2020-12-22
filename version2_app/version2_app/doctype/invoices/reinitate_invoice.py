
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import random
import traceback 
from frappe.utils import get_site_name
import time
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError
from version2_app.version2_app.doctype.invoices.invoices import insert_items,insert_tax_summaries2,insert_hsn_code_based_taxes
from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz



@frappe.whitelist(allow_guest=True)
def Reinitiate_invoice(data):
	'''
	insert invoice data     data, company_code, taxpayer,items_data
	'''
	try:
		total_invoice_amount = data['total_invoice_amount']
		# del data['total_invoice_amount']
		company = frappe.get_doc('company',data['company_code'])
		print(data)
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
				other_charges += item['item_value']
			elif item['taxable']=="No" and item['item_type']=="Discount":
				discountAmount += item['item_value'] 
			elif item['sac_code'].isdigit():
				if "-" not in str(item['item_value']):
					cgst_amount+=item['cgst_amount']
					sgst_amount+=item['sgst_amount']
					igst_amount+=item['igst_amount']
					cess_amount+=item['cess_amount']
					value_before_gst += item['item_value']
					value_after_gst += item['item_value_after_gst']
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
		# if int(data['total_invoice_amount']) != int(pms_invoice_summary):
		# 	calculated_data = {"value_before_gst":value_before_gst,"value_after_gst":value_after_gst,"other_charges":other_charges,"credit_value_after_gst":credit_value_after_gst,"credit_value_before_gst":credit_value_before_gst,"irn_generated":"Error","cgst_amount":cgst_amount,"sgst_amount":sgst_amount,"igst_amount":igst_amount,"cess_amount":cess_amount,"credit_cess_amount":credit_cess_amount,"credit_cgst_amount":credit_cgst_amount,"credit_igst_amount":credit_igst_amount,"credit_sgst_amount":credit_sgst_amount,"pms_invoice_summary":pms_invoice_summary,"pms_invoice_summary_without_gst":pms_invoice_summary_without_gst}
		# 	TotalMismatchErrorAPI = TotalMismatchError(data,calculated_data)
		# 	if TotalMismatchErrorAPI['success']==True:
		# 		items = data['items_data']
				
		# 		itemsInsert = insert_items(items, TotalMismatchErrorAPI['invoice_number'])
				
		# 		insert_tax_summaries2(items, TotalMismatchErrorAPI['invoice_number'])
		# 		hsnbasedtaxcodes = insert_hsn_code_based_taxes(
		# 			items, TotalMismatchErrorAPI['invoice_number'])
		# 		return {"success": True}

		# 	return{"success":False,"message":TotalMismatchErrorAPI['message']}
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
		doc.confirmation_number = data['guest_data']['confirmation_number']
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
		doc.pms_invoice_summary_without_gst=pms_invoice_summary_without_gst
		doc.pms_invoice_summary= pms_invoice_summary
		doc.other_charges= other_charges
		doc.ready_to_generate_irn = ready_to_generate_irn
		doc.cgst_amount=round(cgst_amount,2)
		doc.sgst_amount=round(sgst_amount,2)
		doc.igst_amount=round(igst_amount,2)
		doc.total_gst_amount = round(cgst_amount,2) + round(sgst_amount,2) + round(igst_amount,2)
		doc.irn_generated=irn_generated
		doc.irn_cancelled='No'
		doc.qr_code_generated='Pending'
		doc.signed_invoice_generated='No'
		doc.company=data['company_code']
		doc.print_by = data['guest_data']['print_by']
		doc.credit_cess_amount = round(credit_cess_amount,2)
		doc.credit_cgst_amount = round(credit_cgst_amount,2)
		doc.credit_sgst_amount = round(credit_sgst_amount,2)
		doc.credit_igst_amount = round(credit_igst_amount,2)
		doc.credit_gst_amount = round(credit_cgst_amount,2) + round(credit_sgst_amount,2) + round(credit_igst_amount,2)	
		doc.has_credit_items = has_credit_items
		if int(data['total_invoice_amount']) != int(pms_invoice_summary) + int(other_charges):
			doc.error_message = " Invoice Total Mismatch"
			doc.irn_generated = "Error"
			doc.ready_to_generate_irn = "No"
		doc.save()

		
		items = data['items_data']
		# items = [x for x in items if x['sac_code']!="Liquor"]
	
		itemsInsert = insert_items(items,data['guest_data']['invoice_number'])
		# insert tax summaries
		# insert_tax_summaries(items_data, data['invoice_number'])
		taxSummariesInsert = insert_tax_summaries2(items, data['guest_data']['invoice_number'])
		# insert sac code based taxes
		hsnbasedtaxcodes = insert_hsn_code_based_taxes(items, data['guest_data']['invoice_number'])
		return {"success":True}
		# return {"success":False,"message":"calculation doesnot match"}	
	except Exception as e:
		print(e,"reinitaite invoice", traceback.print_exc())
		return {"success":False,"message":e}
		


