# Copyright (c) 2013, caratred and contributors
# License: MIT. See LICENSE

import frappe
from frappe.utils import add_days, getdate


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

	query = '''SELECT '''
	for field in fields:
		query =  f'{query} {field},'

	query = '''{query} other_charges  FROM `tabInvoices` WHERE invoice_date > DATE_SUB(NOW(), INTERVAL 7 DAY) AND irn_number is NULL and invoice_type='B2B' and DATE(invoice_date) > 2023-04-01'''.format(query=query)
	print(query)
	data = frappe.db.sql(query,as_list=1)
	print(data)
	today = getdate()
	for row in data:
		eight_days_ago = add_days(row[1], -8)
		row.append(eight_days_ago)
	
	fields.append('days')
	# columns, data = [], []
	return fields, data
