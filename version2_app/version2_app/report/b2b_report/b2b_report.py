
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
		columns = ['Receiver GSTIN / UIN','Receiver Name','Invoice Type (R / SEZ / DE)','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Reverse Charge','E-Commerce GSTIN','Applicable % of Tax Rate','Tax Rate','Taxable Value','Integrated Tax Amount','Central Tax Amount','State / UT Tax Amount','State Cess Amount','Central Cess Amount']
		fields = ['invoice_number', 'invoice_date','gst_number','trade_name','place_of_supply','invoice_category','total_invoice_amount','sez']
		doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['!=','Credit Invoice'],'invoice_type':'B2B'},fields=fields,as_list=True)
		if len(doc) == 0:
			data = []
			columns = []
			return columns,data
		doc_list = [list(x) for x in doc]
		invoice_names = [x[0] for x in doc_list]
		
		items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
		items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
		items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		
		
		
		grouped_df = items_df.groupby(["invoice_number","gst_rate"],as_index=False).sum().round(2)
		# print(grouped_df.head())
		invoice_df = pd.DataFrame(doc,columns=fields)
		# print(invoice_df.head())
		latest_invoice = frappe.get_last_doc('Invoices')

		company = frappe.get_doc('company',latest_invoice.company)

		
		
		mergedDf = pd.merge(invoice_df, grouped_df)
		print(mergedDf.head())
		mergedDf["E-Commerce GSTIN"] = " "
		# mergedDf["Invoice Type (R / SEZ / DE)"] = " "
		mergedDf['Applicable % of Tax Rate'] = " "
		mergedDf['Reverse Charge'] = "N"
		mergedDf["E-Commerce GSTIN"] = " "
		# mergedDf["Invoice Type (R / SEZ / DE)"] = 
		mergedDf.loc[(mergedDf.sez==0),'Invoice Type (R / SEZ / DE)'] = "R"
		mergedDf.loc[(mergedDf.sez==1),'Invoice Type (R / SEZ / DE)'] = "SEZ"
		mergedDf.loc[(mergedDf.invoice_category=="Debit Invoice"),'Invoice Type (R / SEZ / DE)'] = "DE"

		mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
		# mergedDf.loc[(mergedDf.invoice_type=="B2C"),'Gst Check'] = ' '
		mergedDf.rename(columns={'invoice_number': 'Invoice Number', 'invoice_date': 'Invoice Date','gst_number':'Receiver GSTIN / UIN','trade_name':'Receiver Name','total_invoice_amount':'Invoice Value','place_of_supply':'Place Of Supply','gst_rate':'Tax Rate','item_value':'Taxable Value','igst_amount':'Integrated Tax Amount','cgst_amount':'Central Tax Amount','sgst_amount':'State / UT Tax Amount','state_cess_amount':'State Cess Amount','cess_amount':"Central Cess Amount"}, inplace=True)
		mergedDf = mergedDf.sort_values(by=['Invoice Number'])
		mergedDf = mergedDf[columns]
		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		
