
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

def execute(filters=None):
	try:
		pd.set_option("display.max_rows", None, "display.max_columns", None)
		columns = ['Check Out Date', 'Invoice Number', 'Guest Name', 'Confirmation No.', 'GST No.','Place of Supply (POS)', 'Room No.', 'Invoice Type', 'Sales Amount', 'Add CGST', 'Add SGST', 'Add IGST', 'Total Gst Amount', 'Invoice Total', 'CESS Amount', 'VAT Amount', 'IRN Generated', 'IRN Number', 'Acknowledge Number', 'Acknowledge Date', 'Credit Invoice', 'Credit IRN Generated', 'Credit IRN Number', 'Credit Acknowledge Number', 'Credit Acknowledge Date', 'Printed Date', 'Last Modified Date']
		fields = ['invoice_number', 'invoice_date','guest_name','gst_number','invoice_type','place_of_supply','confirmation_number','room_number','creation','irn_generated','irn_number','ack_no','ack_date','has_credit_items','credit_irn_generated','credit_irn_number','credit_ack_no','credit_ack_date','modified']
		doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice']},fields=fields,as_list=True)
		if len(doc) == 0:
			data = []
			columns = []
			return columns,data
		doc_list = [list(x) for x in doc]
		invoice_names = [x[0] for x in doc_list]
		
		items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement','quantity','vat_amount']
		items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement','quantity','vat_amount']
		items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
		items_df = pd.DataFrame(items_doc,columns=items_columns)
		items_df = items_df.round(2)
		# items_df["gst_cess_rate"] = items_df['cess'] + items_df['state_cess']
		items_df["cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
		items_df['total_gst_amount'] = items_df['igst_amount']+items_df['sgst_amount']+items_df['cgst_amount']
		del items_df['cess']
		del items_df['state_cess']
		# del items_df['cess_amount']
		del items_df['state_cess_amount']
		del items_df['cgst']
		del items_df['sgst']
		del items_df['igst']

		
		grouped_df = items_df.groupby(["invoice_number"],as_index=False).sum().round(2)

		invoice_df = pd.DataFrame(doc,columns=fields)
		
		# latest_invoice = frappe.get_last_doc('Invoices')

		# company = frappe.get_doc('company',latest_invoice.company)

		
		
		mergedDf = pd.merge(invoice_df, grouped_df)
		
		print(columns)
		
		# mergedDf["Original Invoice Number"] = mergedDf['invoice_number'].tolist()
		# mergedDf["Original Invoice Date"] = mergedDf['invoice_date'].tolist()
		# mergedDf["Original Customer GSTIN / UIN"] = mergedDf['gst_number'].tolist()
		# mergedDf["UQC"] = " "
		# mergedDf["Quantity"] = " "

		# mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
		# mergedDf.loc[(mergedDf.invoice_type=="B2C"),'Gst Check'] = ' '
		# columns = ['Check Out Date', 'Invoice Number', 'Guest Name', 'Confirmation No.', 'GST No.''Place of Supply (POS)', 'Room No.', 'Invoice Type', 'Sales Amount', 'Add CGST', 'Add SGST', 'Add IGST', 'Total Gst Amount', 'Invoice Total', 'CESS Amount', 'VAT Amount', 'IRN Generated', 'IRN Number', 'Acknowledge Number', 'Acknowledge Date', 'Credit Invoice', 'Credit IRN Generated', 'Credit IRN Number', 'Credit Acknowledge Number', 'Credit Acknowledge Date', 'Printed Date', 'Last Modified Date']
		# fields = ['invoice_number', 'invoice_date','guest_name','gst_number','invoice_type','place_of_supply','confirmation_number','room_number','creation','irn_generated','irn_number','ack_no','ack_date','has_credit_items','credit_irn_generated','credit_irn_number','credit_ack_no','credit_ack_date','modified']
		mergedDf.rename(columns={'invoice_number': 'Invoice Number','guest_name':'Guest Name','confirmation_number':'Confirmation No.', 'invoice_date': 'Check Out Date','gst_number':'GST No.','invoice_type':'Invoice Type','place_of_supply':'Place of Supply (POS)','room_number':'Room No.','item_value':'Sales Amount','cgst_amount':'Add CGST','sgst_amount':'Add SGST','igst_amount':'Add IGST','total_gst_amount':'Total Gst Amount','item_value_after_gst':'Invoice Total','cess_amount':'CESS Amount','vat_amount':'VAT Amount','irn_generated':'IRN Generated','irn_number':'IRN Number','ack_no':'Acknowledge Number','ack_date':'Acknowledge Date','has_credit_items':'Credit Invoice','credit_irn_number':'Credit IRN Number','credit_irn_generated':'Credit IRN Generated','credit_ack_no':'Credit Acknowledge Number','credit_ack_date':'Credit Acknowledge Date','creation':'Printed Date','modified':'Last Modified Date'}, inplace=True)
		print(mergedDf.head())
		mergedDf = mergedDf.sort_values(by=['Invoice Number'])
		mergedDf = mergedDf[columns]
		data = mergedDf.values.tolist()
		
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		