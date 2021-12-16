
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

state_code = {'1': 'Jammu and Kashmir', '2': 'Himachal Pradesh', '3': 'Punjab', '4': 'Chandigarh', '5': 'Uttarakhand', '6': 'Haryana', '7': 'Delhi', '8': 'Rajasthan', '9': 'Uttar Pradesh', '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh', '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram', '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam', '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha', '22': 'Chattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat', '26': 'Dadra & Nagar Haveli and Daman & Diu', '27': 'Maharashtra', '29': 'Karnataka', '30': 'Goa', '31': 'Lakshadweep Islands', '32': 'Kerala', '33': 'Tamil Nadu', '34': 'Pondicherry', '35': 'Andaman and Nicobar Islands', '36': 'Telangana', '37': 'Andhra Pradesh', '38': 'Ladakh'}

def execute(filters=None):
	try:
		pd.set_option("display.max_rows", None, "display.max_columns", None)
		columns = ['Check Out Date', 'Invoice Number', 'Invoice Type','Invoice Category','Guest Name', 'Legal Name','SEZ','GST No.','Place of Supply (POS)', 'Room No.', 
			 'Add CGST', 'Add SGST', 'Add IGST', 'Total Gst Amount', 'Invoice Total', "Taxable Value",'CESS Amount',
			'VAT Amount', 'Invoice Status', 'IRN Number', 'Acknowledge Number', 'Acknowledge Date', 'Includes Rebate','Credit Invoice Number',
			'Credit Taxable Value','Credit Add CGST', 'Credit Add SGST', 'Credit Add IGST', 'Credit Total Gst Amount', 'Credit Invoice Total', 'Credit CESS Amount',
			'Credit VAT Amount','Credit Invoice Status','Credit IRN Number', 'Credit Acknowledge Number', 'Credit Acknowledge Date',
			'Confirmation No.','Printed Date', 'Last Modified Date']
		
		
		fields = ['invoice_number', 'invoice_date','guest_name','gst_number','legal_name','invoice_category','invoice_type',
			'place_of_supply','confirmation_number','room_number','creation','irn_generated','sales_amount_after_tax',
			'sales_amount_before_tax','sgst_amount','cgst_amount','igst_amount','total_gst_amount','total_central_cess_amount',
			'total_state_cess_amount','total_vat_amount','irn_number','ack_no','ack_date','has_credit_items','credit_irn_generated',
			'credit_irn_number','credit_ack_no','credit_ack_date','credit_value_before_gst','credit_value_after_gst',
			'credit_cgst_amount','credit_sgst_amount','credit_igst_amount','credit_gst_amount','total_credit_central_cess_amount','total_credit_state_cess_amount',
			'total_credit_vat_amount','sez','modified']


		doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(filters['from_date'],filters['to_date'])]},fields=fields,as_list=True)
		

		invoice_df = pd.DataFrame(doc,columns=fields)
		
		for each in state_code:
			invoice_df.loc[(invoice_df.place_of_supply==each),'place_of_supply'] = state_code[each]
		invoice_df['cess_amount'] = invoice_df['total_state_cess_amount']+invoice_df['total_central_cess_amount']
		invoice_df['credit_cess_amount'] = invoice_df['total_credit_central_cess_amount']+invoice_df['total_credit_state_cess_amount']
		invoice_df['credit_invoice_number'] = invoice_df['invoice_number']+"ACN"
		invoice_df.loc[(invoice_df.sez==1),'sez'] = 'Yes'
		invoice_df.loc[(invoice_df.sez==0),'sez'] = 'No'
		invoice_df.loc[(invoice_df.invoice_type=="B2C"),'irn_number'] = 'NA'
		
		invoice_df.loc[(invoice_df.invoice_type=="B2C"),'ack_no'] = 'NA'
		invoice_df.loc[(invoice_df.invoice_type=="B2C"),'ack_date'] = 'NA'
		invoice_df.loc[(invoice_df.has_credit_items=='No')| (invoice_df.invoice_type=="B2C"),'credit_invoice_number'] = " "
		# invoice_df.loc[(invoice_df.invoice_type=="B2C"),'irn_number'] = 'NA'
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'credit_invoice_number'] = " "
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'has_credit_items'] = "No"
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'cgst_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'sgst_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'igst_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'total_gst_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'cess_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'total_vat_amount'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'sales_amount_before_tax'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'sales_amount_after_tax'] = 0
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'irn_number'] = 'NA'
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'ack_no'] = 'NA'
		invoice_df.loc[(invoice_df.invoice_category=='Credit Invoice'),'ack_date'] = 'NA'
		invoice_df.loc[(invoice_df.invoice_category!='Credit Invoice') & (invoice_df.has_credit_items == 'No'), "credit_irn_number"] = "NA"
		invoice_df.loc[(invoice_df.invoice_category!='Credit Invoice') & (invoice_df.has_credit_items == 'No'), "credit_ack_no"] = "NA"
		invoice_df.loc[(invoice_df.invoice_category!='Credit Invoice') & (invoice_df.has_credit_items == 'No'), "credit_ack_date"] = "NA"

		# mergedDf = pd.merge(invoice_df, grouped_df)
		del invoice_df['total_credit_central_cess_amount']
		del invoice_df['total_credit_state_cess_amount']
		del invoice_df['total_state_cess_amount']
		del invoice_df['total_central_cess_amount']
		
		columns_dict = {"invoice_number":"Invoice Number","invoice_date":"Check Out Date","guest_name":"Guest Name","gst_number":"GST No.","legal_name":"Legal Name",
						"invoice_category":"Invoice Category","invoice_type":"Invoice Type","place_of_supply":"Place of Supply (POS)","confirmation_number":"Confirmation No.",
						"room_number":"Room No.","creation":"Printed Date","irn_generated":"Invoice Status","sales_amount_after_tax":"Invoice Total",
						"sales_amount_before_tax":"Taxable Value","sgst_amount":"Add SGST","cgst_amount":"Add CGST","igst_amount":"Add IGST","total_gst_amount":"Total Gst Amount",
						"cess_amount":"CESS Amount","total_vat_amount":"VAT Amount","irn_number":"IRN Number","ack_no":"Acknowledge Number","ack_date":"Acknowledge Date",
						"has_credit_items":"Includes Rebate","credit_irn_generated":"Credit Invoice Status","credit_irn_number":"Credit IRN Number","credit_ack_no":"Credit Acknowledge Number",
						"credit_ack_date":"Credit Acknowledge Date","credit_value_before_gst":"Credit Taxable Value",
						"credit_cgst_amount":"Credit Add CGST","credit_sgst_amount":"Credit Add SGST","credit_igst_amount":"Credit Add IGST","credit_gst_amount":"Credit Total Gst Amount",
						"credit_cess_amount":"Credit CESS Amount","total_credit_vat_amount":"Credit VAT Amount","sez":"SEZ","modified":"Last Modified Date","credit_invoice_number":"Credit Invoice Number",
						"credit_value_after_gst":"Credit Invoice Total"}
		
		
		
		
		
		invoice_df = invoice_df.rename(columns=columns_dict)
		mergedDf = invoice_df.sort_values(by=['Invoice Number'])
		mergedDf = mergedDf[columns]
		
		data = mergedDf.values.tolist()		
		return columns, data
	except Exception as e:
		# print(str(e))
		print(traceback.print_exc())
		return {"success":False,"message":str(e)}
		
