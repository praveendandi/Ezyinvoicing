
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

def execute(filters=None):
	try:
		pd.set_option("display.max_rows", None, "display.max_columns", None)
		# columns = ["Invoice Number","Invoice Date","Transaction type","Transaction Subtype","Gst Number","Gst Check","Invoice Type","Registered Name","SAC / HSN CODE","Place of Supply (POS)","Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount","Port Code","Shipping Bill / Bill of Export No.","Shipping Bill / Bill of Export Date","UQC","Quantity","Invoice Cancellation","Pre GST Regime Credit / Debit Note","Original Invoice Number","Original Invoice Date","Original Customer GSTIN / UIN","Original Transaction Type","Reason for issuing Credit / Debit Note","Return Month And Year (MM-YYYY)","Original Invoice Value"]
		# columns = ['GSTIN','Legal Entity','Invoice Number','Taxable Value','Tax Rate','CGST','SGST','GST','Invoice Value']
		columns = ['HSN','UQC','Total Quantity','Total Value','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','State Cess Amount','Central Cess Amount']
		fields = ['invoice_number']
		doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['!=','Credit Invoice']},fields=fields,as_list=True)
		if len(doc) == 0:
			data = []
			columns = []
			return columns,data
		doc_list = [list(x) for x in doc]
		invoice_names = [x[0] for x in doc_list]
		
		items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount','quantity','unit_of_measurement_description']
		items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount','quantity','unit_of_measurement_description']
		items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		items_df['total_value'] = items_df['item_value_after_gst']+items_df['cess_amount']+items_df['state_cess_amount']
		# print(items_df.head())
		# items_df['total_gst_amount'] = items_df['sgst_amount']+items_df['cgst_amount']
		
		
		grouped_df = items_df.groupby(["sac_code","unit_of_measurement_description"],as_index=False).sum().round(2)
		# print(grouped_df.head())
		invoice_df = pd.DataFrame(doc,columns=fields)
		latest_invoice = frappe.get_last_doc('Invoices')

		company = frappe.get_doc('company',latest_invoice.company)

		
		
		mergedDf = grouped_df
		
		mergedDf['Total Quantity'] =1.0
		
		mergedDf.rename(columns={'unit_of_measurement_description':'UQC','sac_code':'HSN','total_value':'Total Value','item_value':'Taxable Value','igst_amount':'Integrated Tax Amount','cgst_amount':'Central Tax Amount','sgst_amount':'State/UT Tax Amount','cess_amount':'Central Cess Amount','state_cess_amount':'State Cess Amount'}, inplace=True)

		mergedDf = mergedDf[columns]
		data = mergedDf.values.tolist()
		
		data.append(['Total',' ',round(mergedDf['Total Quantity'].sum(),2),round(mergedDf['Total Value'].sum(),2),round(mergedDf['Taxable Value'].sum(),2),round(mergedDf['Integrated Tax Amount'].sum(),2),round(mergedDf['Central Tax Amount'].sum(),2),round(mergedDf['State/UT Tax Amount'].sum(),2),round(mergedDf['State Cess Amount'].sum(),2),round(mergedDf['Central Cess Amount'].sum(),2)])
		# print(columns,data,mergedDf['Total Value'].sum())
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		
