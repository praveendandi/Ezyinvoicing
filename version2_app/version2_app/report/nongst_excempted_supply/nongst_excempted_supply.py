# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
import frappe
import pandas as pd
import traceback
import calendar
import numpy as np


def execute(filters=None):
	pd.set_option("display.max_rows", None, "display.max_columns", None)
	# columns = ["Original Invoice Number","Transaction type","Debit Note No / Credit Note No.","Debit Note / Credit Note Date","Month","CustomerGSTIN/UIN","Customer Name","Type","SAC / HSN CODE","Invoice value","Base Amount","Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount"]
	
	fields = ['invoice_number', 'invoice_date','invoice_type',"place_of_supply"] 
	invoices_list = frappe.db.get_list('Invoices', filters={'invoice_date': ['>', filters['from_date']],'invoice_date':['<',filters['to_date']],'irn_generated':['like','%Success%']},fields=fields,as_list=True)
	if len(invoices_list) == 0:
		data = []
		columns = []
		return columns,data
	doc_list = [list(x) for x in invoices_list]
	invoice_names = [x[0] for x in doc_list]
	items_fields = ['parent','item_value_after_gst','igst_amount','cgst_amount',"type"]
	items_columns = ['invoice_number','item_value_after_gst','igst_amount','cgst_amount',"type"]
	items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Discount"]},fields =items_fields ,as_list=True)	

	items_df = pd.DataFrame(items_doc,columns=items_columns)
	items_df = items_df.round(2)
	
	# items_df['item_value_after_gst'] = items_df['item_value_after_gst'].abs()
	# items_df['item_value'] = items_df['item_value'].abs()

	invoice_df = pd.DataFrame(invoices_list,columns=fields)
	del invoice_df['invoice_date']

	mergedDf = pd.merge(invoice_df, items_df)
	del mergedDf['invoice_number']
	grouped_df = mergedDf.groupby(["type","invoice_type"],as_index=False).sum().round(2)
	
	grouped_df['Nature Of Supply'] = "Inter State"
	grouped_df.loc[(grouped_df.cgst_amount>0),'Nature Of Supply'] = 'Intra State'
	print(grouped_df)
	data = []
	columns = []
	return columns,data
