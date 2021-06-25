
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

def execute(filters=None):
	try:
		pd.set_option("display.max_rows", None, "display.max_columns", None)
		columns = ['Invoice Number','Invoice Date','Invoice Category','Room No','Guest Name']
		fields = ['folio_type','bill_number','bill_generation_date','room','display_name']
		doc = frappe.db.get_list('Invoice Reconciliations', filters={'bill_generation_date': ['Between',(filters['from_date'],filters['to_date'])],'invoice_found':['=','No']},fields=fields,as_list=True)
		if len(doc) == 0:
			data = []
			return columns,data
		
		mergedDf = pd.DataFrame(doc,columns=fields)
		mergedDf.rename(columns={'bill_number':'Invoice Number','bill_generation_date':'Invoice Date','folio_type':'Invoice Category','room':'Room No','display_name':'Guest Name'}, inplace=True)
		mergedDf = mergedDf.sort_values(by=['Invoice Number'])
		mergedDf = mergedDf[columns]
		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		
