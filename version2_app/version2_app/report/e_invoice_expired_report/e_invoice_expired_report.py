# Copyright (c) 2013, caratred and contributors
# License: MIT. See LICENSE

import frappe
from frappe.utils import add_days, getdate,date_diff


def execute(filters=None):
	'''
	params:
	company:str
	'''
	# Todo add date condition 31-04-2023
	fields = ['invoice_number', 
	   'invoice_date',
	   'gst_number',
	   'trade_name','place_of_supply',
	   'invoice_category',
	   'total_invoice_amount','sez']
	company = frappe.get_last_doc('company')
	print(company.einvoice_missing_date_feature)
	print(company.einvoice_missing_start_date)

	query = '''SELECT '''
	for field in fields:
		query =  f'{query} {field},'
	


	if company.einvoice_missing_date_feature == 1:
		query = '''{query} other_charges  FROM `tabInvoices` WHERE DATE(invoice_date) >= DATE('{company_date}') AND invoice_date < DATE_SUB(NOW(), INTERVAL 7 DAY) AND irn_number is NULL and invoice_type='B2B' ORDER BY invoice_date '''.format(query=query,company_date=company.einvoice_missing_start_date)
	else:
		query = '''{query} other_charges  FROM `tabInvoices` WHERE invoice_date < DATE_SUB(NOW(), INTERVAL 7 DAY) AND irn_number is NULL and invoice_type='B2B' ORDER BY invoice_date '''.format(query=query)
	print(query)
	data = frappe.db.sql(query,as_list=1)
	# today = getdate()
	# new_data = []
	# for row in data:
	# 	eight_days_ago = date_diff(today,row[1])
	# 	# print(row)
	# 	# print(eight_days_ago)
	# 	row.append(eight_days_ago)
	# 	# new_data.append(row)
	# 	# print(row)
	# print(data[0])
	fields.append('other_charges')
	# fields.append('days')
	# print(fields)
	# columns, data = [], []
	return fields, data
