from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from version2_app.version2_app.doctype.invoices.invoices import insert_items,insert_hsn_code_based_taxes,TaxSummariesInsert,generateIrn,send_invoicedata_to_gcb
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
import pandas as pd
import json
import string
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
from frappe.utils import logger
import time
import os




@frappe.whitelist(allow_guest=True)
def Convert_to_manual_tax_invoice(data):
	try:
		from_invoice = frappe.get_doc("Invoices",data["from_invoice_number"])
		
		company = frappe.get_doc("company",from_invoice.company)
		invoice = frappe.get_doc({
			"doctype":
			"Invoices",
			"invoice_number":data["to_invoice_number"],
			"guest_name":from_invoice.guest_name,
			"ready_to_generate_irn":"Yes",
			"invoice_from":"Web",
			"gst_number":from_invoice.gst_number,
			"invoice_round_off_amount": from_invoice.invoice_round_off_amount,
			"invoice_file":from_invoice.invoice_file,
			"room_number":from_invoice.room_number,
			"confirmation_number":from_invoice.confirmation_number,
			"invoice_type":from_invoice.invoice_type,
			"invoice_category":from_invoice.invoice_category,
			"print_by": from_invoice.print_by,
			"invoice_date":from_invoice.invoice_date,
			"legal_name":from_invoice.legal_name,
			"mode":from_invoice.mode,
			"address_1":from_invoice.address_1,
			"email":from_invoice.email,
			"trade_name":from_invoice.trade_name,
			"address_2":from_invoice.address_2,
			"phone_number":from_invoice.phone_number,
			"location":from_invoice.location,
			"pincode":from_invoice.pincode,
			"state_code":from_invoice.state_code,
			"amount_before_gst":from_invoice.amount_before_gst,
			"amount_after_gst":from_invoice.amount_after_gst,
			"other_charges":from_invoice.other_charges,
			"other_charges_before_tax": from_invoice.other_charges_before_tax,
			"credit_value_before_gst":from_invoice.credit_value_before_gst,
			"credit_value_after_gst":from_invoice.credit_value_after_gst,
			"pms_invoice_summary_without_gst":from_invoice.pms_invoice_summary_without_gst,
			"pms_invoice_summary":from_invoice.pms_invoice_summary,
			"sales_amount_after_tax":from_invoice.sales_amount_after_tax,
			"sales_amount_before_tax":from_invoice.sales_amount_before_tax,
			"irn_generated":"Pending",
			"irn_cancelled":"No",
			"qr_code_generated":"Pending",
			"signed_invoice_generated":"No",
			"company":from_invoice.company,
			"cgst_amount":from_invoice.cgst_amount,
			"sgst_amount":from_invoice.sgst_amount,
			"igst_amount":from_invoice.igst_amount,
			"total_central_cess_amount":from_invoice.total_central_cess_amount,
			"total_state_cess_amount":from_invoice.total_state_cess_amount,
			"total_vat_amount":from_invoice.total_vat_amount,
			"total_gst_amount":from_invoice.total_gst_amount,
			"has_credit_items":from_invoice.has_credit_items,
			"total_invoice_amount": from_invoice.total_invoice_amount,
			"has_discount_items":from_invoice.has_discount_items,
			"invoice_process_time":from_invoice.invoice_process_time,
			"credit_cgst_amount":from_invoice.credit_cgst_amount,
			"credit_sgst_amount":from_invoice.credit_sgst_amount,
			"credit_igst_amount":from_invoice.credit_igst_amount,
			"total_credit_state_cess_amount":from_invoice.total_credit_state_cess_amount,
			"total_credit_central_cess_amount":from_invoice.total_credit_central_cess_amount,
			"total_credit_vat_amount": from_invoice.total_credit_vat_amount,
			"credit_gst_amount": from_invoice.credit_gst_amount,
			"place_of_supply": from_invoice.place_of_supply,
			"sez": from_invoice.sez,
			"allowance_invoice":from_invoice.allowance_invoice,
			"converted_from_tax_invoices_to_manual_tax_invoices":"Yes"
		})
		v = invoice.insert()
		items = []
		for each in from_invoice.items:
			items.append(each.__dict__)
		
		itemsInsert = insert_items(items, data["to_invoice_number"])

		TaxSummariesInsert(items,data["to_invoice_number"])
		hsnbasedtaxcodes = insert_hsn_code_based_taxes(
			items,data["to_invoice_number"],"Invoice")
		invoice_data = frappe.get_doc('Invoices',data['to_invoice_number'])
		if invoice_data.invoice_type == "B2B" and invoice_data.invoice_from=="Pms":
			if invoice_data.irn_generated == "Pending" and company.allow_auto_irn == 1:
				data = {'invoice_number': invoice_data.name,'generation_type': "System"}
				irn_generate = generateIrn(data)
		# if invoice_data.invoice_type == "B2C":
		# 	send_invoicedata_to_gcb(invoice_data.invoice_number)
		return {"success": True}
	except Exception as e:
		print(e, "insert invoice")
		return {"success": False, "message": str(e)}