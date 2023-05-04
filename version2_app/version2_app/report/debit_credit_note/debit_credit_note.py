
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback
import calendar
import sys
import numpy as np


def execute(filters=None):
	try:
		pd.set_option("display.max_rows", None, "display.max_columns", None)
		columns = ["Original Invoice Number","Transaction type","Debit Note No / Credit Note No.","Guest Name","Debit Note / Credit Note Date","Month","CustomerGSTIN/UIN","Customer Name","Type","SAC / HSN CODE","Invoice value","Base Amount","Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount",'IRN Number', 'Acknowledge Number', 'Acknowledge Date']
		fields = ['invoice_number','guest_name', 'invoice_date','gst_number','invoice_type','trade_name','tax_invoice_referrence_number','invoice_category','irn_number','ack_no','ack_date']
		debit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date':  ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['like','%Success%'],'invoice_category':['=','Debit Invoice'], 'un_billed_invoice': 0},fields=['invoice_number','guest_name', 'invoice_date','gst_number','invoice_type','trade_name','tax_invoice_referrence_number','invoice_category','irn_number','ack_no','ack_date'],as_list=True)
		credit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date':  ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['like','%Success%'],'invoice_category':['=','Credit Invoice'], 'un_billed_invoice': 0},fields=['invoice_number','guest_name','invoice_date','gst_number','invoice_type','trade_name','tax_invoice_referrence_number','invoice_category','credit_irn_number as irn_number','credit_ack_no as ack_no','credit_ack_date as ack_date'],as_list=True)
		# sysCredit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date':  ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['like','%Success%'],'invoice_category':['=','Tax Invoice'],'has_credit_items':['=','Yes']},fields=fields,as_list=True)

		doc = debit_invoices+credit_invoices
		if len(doc) == 0:
			data = []
			columns = []
			return columns,data
		doc_list = [list(x) for x in doc]
		invoice_names = [x[0] for x in doc_list]
		debit_names_list = [list(x) for x in debit_invoices]
		debit_names = [x[0] for x in debit_names_list]
		credit_names_list = [list(x) for x in credit_invoices]
		credit_names = [x[0] for x in credit_names_list]
		# sys_names_list = [list(x) for x in sysCredit_invoices]
		# sys_names = [x[0] for x in sys_names_list]
		items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount']
		items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount']
		if len(debit_invoices)>0:
			items_debit_doc = frappe.db.get_list('Items',filters={'parent':['in',debit_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
		else:
			items_debit_doc=()
		if len(credit_invoices)>0:

			items_credit_doc = frappe.db.get_list('Items',filters={'parent':['in',credit_names],'item_mode':['=',"Credit"]},fields =items_fields ,as_list=True)
		else:
			items_credit_doc = ()
		# if len(sysCredit_invoices)>0:
			
		# 	items_sysCredit_doc = frappe.db.get_list('Items',filters={'parent':['in',sys_names],'item_mode':['=',"Credit"]},fields =items_fields ,as_list=True)
		# else:
			# items_sysCredit_doc = () 
		items_doc = items_debit_doc+items_credit_doc#+items_sysCredit_doc	
		# print(items_doc)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		# print(items_df)
		items_df["gst_cess_rate"] = items_df['cess'] + items_df['state_cess']
		items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
		del items_df['cess']
		del items_df['state_cess']
		del items_df['cess_amount']
		del items_df['state_cess_amount']
		
		
		grouped_df = items_df.groupby(["invoice_number","sac_code", "gst_rate","igst","cgst","sgst"],as_index=False).sum().round(2)
		invoice_df = pd.DataFrame(doc,columns=fields)
	
		latest_invoice = frappe.get_last_doc('Invoices')

		company = frappe.get_doc('company',latest_invoice.company)

		
		
		mergedDf = pd.merge(invoice_df, grouped_df)
		# print(mergedDf,"======")
		if mergedDf.empty:
			data = []
			columns = []
			return columns,data
		mergedDf["Taxable Value"] = mergedDf['item_value']

		mergedDf.loc[(mergedDf.invoice_category=="Tax Invoice"),'invoice_category'] = 'Credit Note For Sales'
		mergedDf.loc[(mergedDf.invoice_category=="Debit Invoice"),'invoice_category'] = 'Debit Note'
		mergedDf.loc[(mergedDf.invoice_category=="Credit Invoice"),'invoice_category'] = 'Credit Note For Sales'

		mergedDf.rename(columns={'invoice_category':'Transaction type','tax_invoice_referrence_number':'Original Invoice Number','invoice_number': 'Debit Note No / Credit Note No.','guest_name':'Guest Name', 'invoice_date': 'Debit Note / Credit Note Date','gst_number':'CustomerGSTIN/UIN','invoice_type':'Type','trade_name':'Customer Name','sac_code':'SAC / HSN CODE','gst_rate':'Total GST RATE %','item_value':'Base Amount','item_value_after_gst':'Invoice value','igst':'IGST Rate','igst_amount':'IGST Amount','cgst':'CGST Rate','cgst_amount':'CGST Amount','sgst':'SGST / UT Rate','sgst_amount':'SGST / UT GST Amount','gst_cess_rate':'GST Compensation Cess Rate','gst_cess_amount':'GST Compensation Cess Amount','irn_number':'IRN Number','ack_no':'Acknowledge Number','ack_date': 'Acknowledge Date'}, inplace=True)
		mergedDf['Month'] = pd.DatetimeIndex(mergedDf['Debit Note / Credit Note Date']).month
		mergedDf['Month'] = mergedDf['Month'].apply(lambda x: calendar.month_abbr[x])

		mergedDf = mergedDf[columns]
		
		# mergedDf.update(mergedDf.select_dtypes(include=[np.number]).abs())
		mergedDf = mergedDf.sort_values(by=['Debit Note No / Credit Note No.'])
		# mergedDf = mergedDf.abs()
		mergedDf['Invoice value'] = mergedDf['Invoice value'].abs()
		mergedDf['Base Amount'] = mergedDf['Base Amount'].abs()
		mergedDf['Taxable Value'] = mergedDf['Taxable Value'].abs()
		mergedDf['IGST Amount'] = mergedDf['IGST Amount'].abs()
		mergedDf['CGST Amount'] = mergedDf['CGST Amount'].abs()
		mergedDf['SGST / UT GST Amount'] = mergedDf['SGST / UT GST Amount'].abs()
		mergedDf['GST Compensation Cess Amount'] = mergedDf['GST Compensation Cess Amount'].abs()
		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		# print(str(e))
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-invoicing invoice_created Event","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
