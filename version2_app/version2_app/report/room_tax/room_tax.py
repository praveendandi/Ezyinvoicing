# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

import frappe
import pandas as pd

def execute(filters=None):
	if filters:
		print(filters)
		sql_filters="where `tabSAC HSN CODES`.category='Room'"
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
		columns = [{"fieldname": "sac_code","fieldtype": "date","label": "SAC Code","width": 150},
					{"fieldname": "room_no","fieldtype": "data","label": "ROOM NO","width": 150},
					{"fieldname": "parent","fieldtype": "data","label": "Invoice No","width": 150},
					{"fieldname": "date","fieldtype": "data","label": "Check in","width": 150},
					{"fieldname": "check_out","fieldtype": "data","label": "Check out","width": 150},
					{"fieldname": "item_value","fieldtype": "data","label": "Room Rate","width": 150},
					{"fieldname": "gst_rate","fieldtype": "data","label": "Tax Rate","width": 150},
					{"fieldname": "cgst_amount","fieldtype": "data","label": "CGST","width": 150},
					{"fieldname": "sgst_amount","fieldtype": "data","label": "SGST","width": 150},
					{"fieldname": "item_value_after_gst","fieldtype": "data","label": "Amount","width": 150}]
		data=frappe.db.sql("""select DATE(DATE_ADD(`tabItems`.date, INTERVAL + 1 DAY)) as check_out,`tabInvoices`.invoice_number,`tabInvoices`.invoice_date,`tabItems`.* from `tabInvoices` inner join `tabItems` on `tabItems`.parent=`tabInvoices`.invoice_number inner join `tabSAC HSN CODES` on `tabSAC HSN CODES`.code=`tabItems`.sac_code {}""".format(sql_filters),as_dict=1)
		data=list({frozenset(item.items()) : item for item in data}.values())
		df=pd.DataFrame.from_records(data)
		group_taxrate = df.groupby(['gst_rate',"parent","sac_code"],as_index=False).sum()
		# group_taxrate=group_taxrate.iloc[1: , :]
		for d in group_taxrate.to_dict('r'):
			data.append(["", "", "", "", "", "", "", "","CGST "+str(d['gst_rate']//2),d['cgst_amount']])
			data.append(["", "", "", "", "", "", "", "","SGST "+str(d['gst_rate']//2),d['sgst_amount']])
		# updated_val={"CGST "+str(d['gst_rate']//2): d['cgst_amount'] for d in group_taxrate.to_dict(orient='records')}
		# updated_val.update({"SGST "+str(d['gst_rate']//2): d['sgst_amount'] for d in group_taxrate.to_dict(orient='records')})
		# dat=lambda x,y:x['cgst {}'.format(x['gst_rate']/2)],x["cgst_amount"] if x['gst_rate'] ==12 else 0
		# print(updated_val)
		# print(group_taxrate)
	else:
		columns, data=[],[]
	# data=[]
	return columns, data
