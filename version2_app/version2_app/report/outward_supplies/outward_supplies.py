
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

def execute(filters=None):
	try:
		columns = ["Invoice Number","Invoice Date","Transaction type","Transaction Subtype","Gst Number","Gst Check","Invoice Type","Registered Name","SAC / HSN CODE","Place of Supply (POS)","Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount","Port Code","Shipping Bill / Bill of Export No.","Shipping Bill / Bill of Export Date","UQC","Quantity","Invoice Cancellation","Pre GST Regime Credit / Debit Note","Original Invoice Number","Original Invoice Date","Original Customer GSTIN / UIN","Original Transaction Type","Reason for issuing Credit / Debit Note","Return Month And Year (MM-YYYY)","Original Invoice Value"]
		
		fields = ['invoice_number', 'invoice_date','gst_number','invoice_type','trade_name','place_of_supply']
		doc = frappe.db.get_list('Invoices', filters={'Creation': ['>', filters['from_date']],'Creation':['<',filters['to_date']],'irn_generated':['like','%Success%'],'invoice_category':['=','Tax Invoice']},fields=fields,as_list=True)
		if len(doc) == 0:
			return {"success":False,"Message":"No data found"}
		doc_list = [list(x) for x in doc]
		# print(doc_list)
		invoice_names = [x[0] for x in doc_list]
		# print(invoice_names)
		items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement','quantity']
		items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement','quantity']
		items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
		# print(items_doc)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		items_df["gst_cess_rate"] = items_df['cess'] + items_df['state_cess']
		items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
		del items_df['cess']
		del items_df['state_cess']
		del items_df['cess_amount']
		del items_df['state_cess_amount']
		
		
		grouped_df = items_df.groupby(["invoice_number","sac_code", "gst_rate"],as_index=False).sum().round(2)

		invoice_df = pd.DataFrame(doc,columns=fields)
		items_df = grouped_df.astype(str)
		
		latest_invoice = frappe.get_last_doc('Invoices')

		company = frappe.get_doc('company',latest_invoice.company)

		invoice_df = invoice_df.astype(str)
		# print(invoice_df)
		
		mergedDf = pd.merge(invoice_df, items_df)
		mergedDf["Transaction type"] = "Sales"
		mergedDf['Transaction Subtype'] = "Domestic Sales"
		mergedDf["Port Code"] = " "
		mergedDf["Gst Check"] = "15"
		mergedDf["Shipping Bill / Bill of Export No."] = " "
		mergedDf["Shipping Bill / Bill of Export Date"] = " "
		mergedDf["Invoice Cancellation"] = " "
		mergedDf["Pre GST Regime Credit / Debit Note"] = " "
		mergedDf["Original Transaction Type"] = " "
		mergedDf["Reason for issuing Credit / Debit Note"] = " "
		mergedDf["Return Month And Year (MM-YYYY)"] = " "
		mergedDf["Original Invoice Number"] = mergedDf['invoice_number'].tolist()
		mergedDf["Original Invoice Date"] = mergedDf['invoice_date'].tolist()
		mergedDf["Original Customer GSTIN / UIN"] = mergedDf['gst_number'].tolist()
		mergedDf["UQC"] = " "
		mergedDf["Quantity"] = " "
		
		

		mergedDf.loc[(mergedDf.place_of_supply == 'None'),'place_of_supply']=company.state_code
		mergedDf.loc[(mergedDf.invoice_type=="B2C"),'Gst Check'] = ' '
		mergedDf.rename(columns={'invoice_number': 'Invoice Number', 'invoice_date': 'Invoice Date','gst_number':'Gst Number','invoice_type':'Invoice Type','trade_name':'Registered Name','place_of_supply':'Place of Supply (POS)','sac_code':'SAC / HSN CODE','gst_rate':'Gst Number','gst_rate':'Total GST RATE %','item_value':'Taxable Value','item_value_after_gst':'Original Invoice Value','igst':'IGST Rate','igst_amount':'IGST Amount','cgst':'CGST Rate','cgst_amount':'CGST Amount','sgst':'SGST / UT Rate','sgst_amount':'SGST / UT GST Amount','gst_cess_rate':'GST Compensation Cess Rate','gst_cess_amount':'GST Compensation Cess Amount'}, inplace=True)
		mergedDf = mergedDf[columns]

		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
