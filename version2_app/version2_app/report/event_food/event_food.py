# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

import frappe
import pandas as pd

def execute(filters=None):
	if filters:
		print(filters)
		sql_filters="where `tabSAC HSN CODES`.category='Food'"
		if "invoice_number" in filters:
			for k,v in filters.items():
				if k.strip()=="form_date" or k.strip()=="to_date":
					sql_filters+=" and `tabInvoices`.invoice_date between '{}' and '{}'".format(filters["from_date"],filters["to_date"])
					sql_filters+=" and `tabInvoices`.invoice_number ='{}'".format(filters["invoice_number"])
				# else:
				# 	sql_filters+=" and `tabInvoices`.{} {} '{}'".format(k,"=",v)
			# filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],"parent":filters["invoice_number"],"`tabItems`.category":"food"}
		else:
			for k,v in filters.items():
				if k.strip()=="form_date" or k.strip()=="to_date":
					sql_filters+=" and `tabInvoices`.invoice_date between '{}' and '{}'".format(filters["from_date"],filters["to_date"])
					# sql_filters+=" and `tabInvoices`.invoice_number ='{}'".format(filters["invoice_number"])
    			# else:
				# 	sql_filters+=" and `tabInvoices`.{} {} '{}'".format(k,"=",v)
		columns = [{"fieldname": "invoice_date","fieldtype": "date","label": "Invoice Date","width": 150},
				{"fieldname": "bill_no","fieldtype": "data","label": "Bill No","width": 150},
				{"fieldname": "parent","fieldtype": "data","label": "Inovice No","width": 150},
				{"fieldname": "sac_code","fieldtype": "data","label": "Sac Code","width": 150},
				{"fieldname": "description","fieldtype": "data","label": "Particulars","width": 150},
				{"fieldname": "item_value","fieldtype": "data","label": "Base Amount","width": 150},
				{"fieldname": "gst_rate","fieldtype": "data","label": "Tax Rate","width": 150},
				{"fieldname": "cgst_amount","fieldtype": "data","label": "CGST","width": 150},
				{"fieldname": "sgst_amount","fieldtype": "data","label": "SGST","width": 150},
				{"fieldname": "item_value_after_gst","fieldtype": "data","label": "Amount","width": 150}]
		data=frappe.db.sql("""select `tabInvoices`.invoice_number,`tabInvoices`.invoice_date,`tabItems`.* from `tabInvoices` inner join `tabItems` on `tabItems`.parent=`tabInvoices`.invoice_number inner join `tabSAC HSN CODES` on `tabSAC HSN CODES`.code=`tabItems`.sac_code {}""".format(sql_filters),as_dict=1)
		
		data=list({frozenset(item.items()) : item for item in data}.values())
		# data=frappe.db.get_all(doctype="Invoices",filters=filters,fields=["`tabInvoices`.invoice_number","`tabInvoices`.invoice_date","`tabItems`.*"],group_by="description")
	else:
		columns, data=[],[]
	return columns, data
