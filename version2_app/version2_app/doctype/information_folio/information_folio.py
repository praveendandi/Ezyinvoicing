# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe
import datetime

class InformationFolio(Document):
	pass
@frappe.whitelist(allow_guest=True)
def insert_information_folio(data):
	company = frappe.get_doc('company',data['company_code'])
	check_inf_folio = frappe.get_list('Information Folio',filters={'name': data['guest_data']['confirmation_number']})
	if len(check_inf_folio) == 0:
		inf_folio = frappe.get_doc({
			'doctype':
			'Information Folio',
			'guest_name':
			data['guest_data']['name'],
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
			'invoice_category':data['guest_data']['invoice_category'],
			'print_by': data['guest_data']['print_by'],
			'invoice_date':
			datetime.datetime.strptime(data['guest_data']['invoice_date'],
										'%d-%b-%y %H:%M:%S'),
			'legal_name':
			data['taxpayer']['legal_name'],
			'mode':company.mode,
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
			'company':
			data['company_code'],
			'total_invoice_amount': data['guest_data']['total_invoice_amount'],
			'invoice_process_time':
			datetime.datetime.utcnow() - datetime.datetime.strptime(
				data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
			"mode": company.mode,
			"place_of_supply": company.state_code,
			})	
		inf_folio.save()
		return {"success":True}
	else:
		updateinf_folio = frappe.get_doc('Information Folio',check_inf_folio[0])
		updateinf_folio.guest_name = data['guest_data']['name']
		updateinf_folio.invoice_from = "Pms"
		updateinf_folio.gst_number=data['guest_data']['gstNumber']
		updateinf_folio.invoice_file = data['guest_data']['invoice_file']
		updateinf_folio.room_number = data['guest_data']['room_number']
		updateinf_folio.confirmation_number=data['guest_data']['confirmation_number']
		updateinf_folio.invoice_type = data['guest_data']['invoice_type']
		updateinf_folio.invoice_category=data['guest_data']['invoice_category']
		updateinf_folio.print_by = data['guest_data']['print_by']
		updateinf_folio.invoice_date=datetime.datetime.strptime(data['guest_data']['invoice_date'],'%d-%b-%y %H:%M:%S')
		updateinf_folio.legal_name=data['taxpayer']['legal_name']
		updateinf_folio.mode=company.mode
		updateinf_folio.address_1=data['taxpayer']['address_1']
		updateinf_folio.email=data['taxpayer']['email']
		updateinf_folio.trade_name=data['taxpayer']['trade_name']
		updateinf_folio.address_2=data['taxpayer']['address_2']
		updateinf_folio.phone_number=data['taxpayer']['phone_number']
		updateinf_folio.location=data['taxpayer']['location']
		updateinf_folio.pincode=data['taxpayer']['pincode']
		updateinf_folio.state_code=data['taxpayer']['state_code']
		updateinf_folio.company=data['company_code']
		updateinf_folio.total_invoice_amount=data['guest_data']['total_invoice_amount']
		updateinf_folio.invoice_process_time=datetime.datetime.utcnow() - datetime.datetime.strptime(data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f")
		updateinf_folio.mode=company.mode
		updateinf_folio.place_of_supply=company.state_code
		updateinf_folio.save()
		return {"success":True}
