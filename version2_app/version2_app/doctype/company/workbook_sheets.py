

import frappe
import pandas as pd
import traceback



@frappe.whitelist(allow_guest=True)
def B2B_Invoices(data):
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        columns = ['GSTIN','Receiver Name','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Reverse Charge','Applicable% of Tax Rate','Invoice Type','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
        print(len(columns),"columns,,,,",columns)
        fields = ['invoice_number','invoice_date','gst_number','invoice_type','trade_name','place_of_supply']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['from_date'],data['to_date'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice'],'invoice_type':['=','B2B']},fields=fields,as_list=True)
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
        
        items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
        del items_df['cess_amount']
        del items_df['state_cess_amount']
        
        
        grouped_df = items_df.groupby(["invoice_number", "gst_rate"],as_index=False).sum().round(2)
        # print(grouped_df.head())
        invoice_df = pd.DataFrame(doc,columns=fields)    
        mergedDf = pd.merge(invoice_df, grouped_df)
        latest_invoice = frappe.get_last_doc('Invoices')

        company = frappe.get_doc('company',latest_invoice.company)
        mergedDf['rev_charge'] = "No"
        print(mergedDf.columns.values.tolist(),len(mergedDf.columns.values.tolist()))
        mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
        # columns = ['GSTIN','Receiver Name','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Reverse Charge','Applicable of Tax Rate','Invoice Type','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
        # ['invoice_number', 'invoice_date', 'gst_number', 'invoice_type', 'trade_name', 'place_of_supply', 'gst_rate', 'item_value', 'item_value_after_gst', 'igst_amount', 'cgst_amount', 'sgst_amount', 'gst_cess_amount', 'rev_charge']
        columns_dict = {"invoice_number":"Invoice Number","trade_name":"Receiver Name","gst_rate":"Applicable% of Tax Rate","place_of_supply":"Place Of Supply","invoice_date":"Invoice Date","gst_number":"GSTIN","invoice_type":"Invoice Type","item_value":"Taxable Value","item_value_after_gst":"Invoice Value","igst_amount":"Integrated Tax Amount","cgst_amount":"Central Tax Amount","sgst_amount":"State/UT Tax Amount","gst_cess_amount":"Cess Amount","rev_charge":"Reverse Charge"}
        mergedDf.rename(columns=columns_dict,inplace=True)
        # 20213432
        mergedDf = mergedDf.sort_values(by=['Invoice Number'])
        mergedDf = mergedDf[columns]
        data = mergedDf.values.tolist()
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}