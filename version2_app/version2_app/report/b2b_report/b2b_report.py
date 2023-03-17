
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
		columns = ['Receiver GSTIN / UIN','Receiver Name','Invoice Type (R / SEZ / DE)','Invoice Number','Invoice Date','Checkout Date','Invoice Value','Place Of Supply','Reverse Charge','E-Commerce GSTIN','Applicable % of Tax Rate','Tax Rate',"Taxable Value","Non Taxable Value",'Integrated Tax Amount','Central Tax Amount','State / UT Tax Amount','State Cess Amount','Central Cess Amount',"Irn Generated","Irn Number","Ack No","Ack Date","Other Charges"]
		fields = ['invoice_number', 'invoice_date','checkout_date','gst_number','trade_name','place_of_supply','invoice_category','total_invoice_amount','sez',"irn_generated","irn_number","ack_no","ack_date","other_charges"]
		doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['!=','Credit Invoice'],'invoice_type':'B2B'},fields=fields,as_list=True)
		# print(doc)
		if len(doc) == 0:
			data = []
			columns = []
			return columns,data
		doc_list = [list(x) for x in doc]
		invoice_names = [x[0] for x in doc_list]
		
		items_fields = ['parent','taxable','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
		items_columns = ['invoice_number',"taxable",'sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
		items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names]},fields =items_fields ,as_list=True)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		
		
		
		grouped_df = items_df.groupby(["invoice_number","taxable","gst_rate"],as_index=False).sum().round(2)
		# grouped_df = items_df.groupby(["invoice_number","taxable","sac_code", "gst_rate","igst","cgst","sgst","unit_of_measurement_description"],as_index=False).sum().round(2)
		grouped_df["tax_value"] = grouped_df.apply(lambda x:x['item_value'] if x['taxable'] == "Yes" else 0, axis=1)
		grouped_df['non_tax_value']= grouped_df.apply(lambda x:x['item_value'] if x['taxable'] == "No" is "No" else 0, axis=1)
		invoice_df = pd.DataFrame(doc,columns=fields)
		latest_invoice = frappe.get_last_doc('Invoices')

		company = frappe.get_doc('company',latest_invoice.company)

		
		
		mergedDf = pd.merge(invoice_df, grouped_df)
		# print(mergedDf.head())
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
		mergedDf.rename(columns={"other_charges":"Other Charges",'invoice_number': 'Invoice Number', 'invoice_date': 'Invoice Date','checkout_date':'Checkout Date','gst_number':'Receiver GSTIN / UIN','trade_name':'Receiver Name','total_invoice_amount':'Invoice Value','place_of_supply':'Place Of Supply','gst_rate':'Tax Rate','tax_value':'Taxable Value','non_tax_value':'Non Taxable Value','igst_amount':'Integrated Tax Amount','cgst_amount':'Central Tax Amount','sgst_amount':'State / UT Tax Amount','state_cess_amount':'State Cess Amount','cess_amount':"Central Cess Amount","irn_generated":"Irn Generated","irn_number":"Irn Number","ack_no":"Ack No","ack_date":"Ack Date"}, inplace=True)
		mergedDf = mergedDf.sort_values(by=['Invoice Number'])
		mergedDf = mergedDf[columns]
		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		
