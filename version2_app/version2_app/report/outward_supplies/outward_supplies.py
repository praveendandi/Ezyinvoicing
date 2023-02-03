
# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import pandas as pd
import traceback

@frappe.whitelist()
def execute(filters=None):
    try:
        # print(filters,"======")           
        company_data=frappe.db.get_all("company",fields=["*"])
        if company_data[0]["show_pending_invoices_in_reports"]==1 or company_data[0]["mode"]=="Testing":
            if "export" in filters:
                if filters["export"]:
                    filter = {'invoice_date': ['Between',[filters['from_date'],filters['to_date']]],'irn_generated':["in",["Pending","Success"]]}
                else:
                    filter = {'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':["in",["Pending","Success"]],'invoice_category':['=','Tax Invoice']}
            else:
                filter = {'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':["in",["Pending","Success"]],'invoice_category':['=','Tax Invoice']}
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            columns = ["Invoice Number","Document Type","Invoice Date","Transaction type","Transaction Subtype","Gst Number","Gst Check","Invoice Type","Registered Name","SAC / HSN CODE","HSN UOM","HSN Quantity","Place of Supply (POS)","Taxable Value","Non Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount","Port Code","Shipping Bill / Bill of Export No.","Shipping Bill / Bill of Export Date","Invoice Cancellation","Pre GST Regime Credit / Debit Note","Original Invoice Number","Original Invoice Date","Original Customer GSTIN / UIN","Original Transaction Type","Reason for issuing Credit / Debit Note","Return Month And Year (MM-YYYY)","Original Invoice Value","Other Charges", "IRN Number", "Acknowledge Number", "Acknowledge Date"]
            
            fields = ['invoice_number','invoice_date','gst_number','invoice_type','trade_name','place_of_supply','sez','sales_amount_after_tax',"other_charges", "irn_number", "ack_no", "ack_date"]
            doc = frappe.db.get_list('Invoices', filters=filter, fields=fields,as_list=True)
        else:
            if "export" in filters:
                if filters["export"]:
                    filter = {'invoice_date': ['Between',[filters['from_date'],filters['to_date']]],'irn_generated':['=','Success']}
                else:
                    filter = {'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice']}
            else:
                filter = {'invoice_date': ['Between',(filters['from_date'],filters['to_date'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice']}
            pd.set_option("display.max_rows", None, "display.max_columns", None)
            columns = ["Invoice Number","Document Type","Invoice Date","Transaction type","Transaction Subtype","Gst Number","Gst Check","Invoice Type","Registered Name","SAC / HSN CODE","HSN UOM","HSN Quantity","Place of Supply (POS)","Taxable Value","Non Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount","Port Code","Shipping Bill / Bill of Export No.","Shipping Bill / Bill of Export Date","Invoice Cancellation","Pre GST Regime Credit / Debit Note","Original Invoice Number","Original Invoice Date","Original Customer GSTIN / UIN","Original Transaction Type","Reason for issuing Credit / Debit Note","Return Month And Year (MM-YYYY)","Original Invoice Value","Other Charges", "IRN Number", "Acknowledge Number", "Acknowledge Date"]
            
            fields = ['invoice_number','invoice_date','gst_number','invoice_type','trade_name','place_of_supply','sez','sales_amount_after_tax',"other_charges", "irn_number", "ack_no", "ack_date"]
            doc = frappe.db.get_list('Invoices', filters=filter, fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            columns = []
            return columns,data
        doc_list = [list(x) for x in doc]
        invoice_names = [x[0] for x in doc_list]
        items_fields = ['parent',"taxable",'sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement_description','quantity']
        items_columns = ['invoice_number',"taxable",'sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount','state_cess','state_cess_amount','cess','cess_amount','unit_of_measurement_description','quantity']
        item_filter = {'parent':['in',invoice_names]}
        get_sac_hsn_desc = frappe.db.get_list("SAC HSN CODES", filters=[["ignore_non_taxable_items","=",1]],pluck="sac_index")
        if "export" in filters:
            if filters["export"]:
                item_filter = {'parent':['in',invoice_names],"sac_index":["not in",get_sac_hsn_desc]}
        items_doc = frappe.db.get_list('Items',filters=item_filter,fields =items_fields ,as_list=True)
        items_df = pd.DataFrame(items_doc,columns=items_columns)
        items_df = items_df.round(2)
        items_df['quantity'] = (items_df['quantity'].replace(r'^\s*$', '1', regex=True)).astype(int)
        items_df["gst_cess_rate"] = items_df['cess'] + items_df['state_cess']
        items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
        del items_df['cess']
        del items_df['state_cess']
        del items_df['cess_amount']
        del items_df['state_cess_amount']
        
        
        grouped_df = items_df.groupby(["invoice_number","taxable","sac_code", "gst_rate","igst","cgst","sgst","unit_of_measurement_description"],as_index=False).sum().round(2)
        grouped_df["tax_value"] = grouped_df.apply(lambda x:x['item_value'] if x['taxable'] == "Yes" else 0, axis=1)
        grouped_df['non_tax_value']= grouped_df.apply(lambda x:x['item_value'] if x['taxable'] == "No" is "No" else 0, axis=1)
        invoice_df = pd.DataFrame(doc,columns=fields)
        
        latest_invoice = frappe.get_last_doc('Invoices')

        company = frappe.get_doc('company',latest_invoice.company) 
        mergedDf = pd.merge(invoice_df, grouped_df)
        mergedDf["Transaction type"] = "Sales"
        mergedDf['Transaction Subtype'] = "Domestic Sales"
        mergedDf["Port Code"] = " "
        mergedDf["Gst Check"] = 15
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
        # mergedDf["UQC"] = " "
        # mergedDf["Quantity"] = " "

        mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
        mergedDf['sales_amount_after_tax'] = mergedDf['sales_amount_after_tax'].tolist() 
        mergedDf.loc[(mergedDf.invoice_type=="B2C"),'Gst Check'] = ' '
        mergedDf.loc[(mergedDf.sez==0),'sez'] = 'REG'
        mergedDf.loc[(mergedDf.sez==1),'sez'] = 'SEZ'
        if company.name != "RBHND-01":
            mergedDf.rename(columns={'invoice_number': 'Invoice Number',"other_charges":"Other Charges", "irn_number":"IRN Number", "ack_no":"Acknowledge Number", "ack_date":"Acknowledge Date", "unit_of_measurement_description":"HSN UOM","sez":"Document Type",'invoice_date': 'Invoice Date','gst_number':'Gst Number','invoice_type':'Invoice Type','trade_name':'Registered Name','place_of_supply':'Place of Supply (POS)','sac_code':'SAC / HSN CODE','gst_rate':'Gst Number','gst_rate':'Total GST RATE %','tax_value':'Taxable Value','non_tax_value':'Non Taxable Value','item_value_after_gst':'Original Invoice Value','igst':'IGST Rate','igst_amount':'IGST Amount','cgst':'CGST Rate','cgst_amount':'CGST Amount','sgst':'SGST / UT Rate','sgst_amount':'SGST / UT GST Amount','gst_cess_rate':'GST Compensation Cess Rate','gst_cess_amount':'GST Compensation Cess Amount','quantity':"HSN Quantity"}, inplace=True)
        else:
            mergedDf.rename(columns={'invoice_number': 'Invoice Number',"other_charges":"Other Charges","irn_number":"IRN Number", "ack_no":"Acknowledge Number", "ack_date":"Acknowledge Date", "unit_of_measurement_description":"HSN UOM","sez":"Document Type",'invoice_date': 'Invoice Date','gst_number':'Gst Number','invoice_type':'Invoice Type','trade_name':'Registered Name','place_of_supply':'Place of Supply (POS)','sac_code':'SAC / HSN CODE','gst_rate':'Gst Number','gst_rate':'Total GST RATE %','tax_value':'Taxable Value','non_tax_value':'Non Taxable Value','sales_amount_after_tax':'Original Invoice Value','igst':'IGST Rate','igst_amount':'IGST Amount','cgst':'CGST Rate','cgst_amount':'CGST Amount','sgst':'SGST / UT Rate','sgst_amount':'SGST / UT GST Amount','gst_cess_rate':'GST Compensation Cess Rate','gst_cess_amount':'GST Compensation Cess Amount','quantity':"HSN Quantity"}, inplace=True)
        mergedDf = mergedDf.sort_values(by=['Invoice Number'])
        # print(mergedDf,"===========")
        mergedDf = mergedDf[columns]
        if "export" in filters:
            if filters["export"]:
                data = mergedDf.to_dict('records')
            else:
                data = mergedDf.values.tolist()
        else:
            data = mergedDf.values.tolist()
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}
        
