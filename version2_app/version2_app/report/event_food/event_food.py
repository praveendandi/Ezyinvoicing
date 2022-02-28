# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	if filters:
		print(filters)
		if "invoice_number" in filters:
			filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],"parent":filters["invoice_number"],"`tabItems`.category":"food"}
		else:
			filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])]}
		columns = [{"fieldname": "invoice_date","fieldtype": "date","label": "Invoice Date","width": 150},
				{"fieldname": "parent","fieldtype": "data","label": "Bill No","width": 150},
				{"fieldname": "sac_code","fieldtype": "data","label": "Sac Code","width": 150},
				{"fieldname": "description","fieldtype": "data","label": "Particulars","width": 150},
				{"fieldname": "item_value","fieldtype": "data","label": "Base Amount","width": 150},
				{"fieldname": "cgst_amount","fieldtype": "data","label": "CGST 9%","width": 150},
				{"fieldname": "sgst_amount","fieldtype": "data","label": "SGST 9%","width": 150},
				{"fieldname": "item_value_after_gst","fieldtype": "data","label": "Amount","width": 150}]
		data=frappe.db.get_all(doctype="Invoices",filters=filters,fields=["`tabInvoices`.invoice_number","`tabInvoices`.invoice_date","`tabItems`.*"],group_by="description")
	else:
		columns, data=[],[]
	return columns, data
