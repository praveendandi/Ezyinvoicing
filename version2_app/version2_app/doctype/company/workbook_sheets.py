

import frappe
import pandas as pd
import traceback



@frappe.whitelist()
def B2B_Invoices(data):
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        columns = ['GSTIN','Receiver Name','Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Reverse Charge','Applicable% of Tax Rate','Invoice Type','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
        print(len(columns),"columns,,,,",columns)
        fields = ['invoice_number','invoice_date','gst_number','invoice_type','trade_name','place_of_supply']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice'],'invoice_type':['=','B2B']},fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            
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
        mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
        
        columns_dict = {"invoice_number":"Invoice Number","trade_name":"Receiver Name","gst_rate":"Applicable% of Tax Rate","place_of_supply":"Place Of Supply","invoice_date":"Invoice Date","gst_number":"GSTIN","invoice_type":"Invoice Type","item_value":"Taxable Value","item_value_after_gst":"Invoice Value","igst_amount":"Integrated Tax Amount","cgst_amount":"Central Tax Amount","sgst_amount":"State/UT Tax Amount","gst_cess_amount":"Cess Amount","rev_charge":"Reverse Charge"}
        mergedDf.rename(columns=columns_dict,inplace=True)
        mergedDf = mergedDf.sort_values(by=['Invoice Number'])
        mergedDf = mergedDf[columns]
        mergedDf['Invoice Date'] = mergedDf['Invoice Date'].apply(str)
        data = mergedDf.values.tolist()
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}

@frappe.whitelist()
def B2CL_Invoices(data):
    latest_invoice = frappe.get_last_doc('Invoices')
    company = frappe.get_doc('company',latest_invoice.company)
    docdata = frappe.db.get_list('Invoices',filters={'place_of_supply': ""},fields=["name"])
    # print(docdata)                                
    if len(docdata) > 0:
        updatetax = frappe.db.sql(
            """update tabInvoices set place_of_supply={} where place_of_supply is null""".format(company.state_code)
        )
        frappe.db.commit()
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        
        columns = ['Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Applicable % of Tax Rate','Rate','Taxable Value','Integrated Tax Amount','Cess Amount']
        fields = ['invoice_number','invoice_date','invoice_type','place_of_supply']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice'],'invoice_type':['=','B2C'],'sales_amount_after_tax':['>=',250000],'place_of_supply':["!=",company.state_code]},fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            return columns,data
        doc_list = [list(x) for x in doc]
        invoice_names = [x[0] for x in doc_list]
        
        items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
        items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
        items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields = items_fields ,as_list=True)
        items_df = pd.DataFrame(items_doc,columns=items_columns)
        items_df = items_df.round(2)
        
        items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
        del items_df['cess_amount']
        del items_df['state_cess_amount']
        del items_df['cgst_amount']
        del items_df['sgst_amount']
        
        
        grouped_df = items_df.groupby(["invoice_number", "gst_rate"],as_index=False).sum().round(2)
        # print(grouped_df.head())
        invoice_df = pd.DataFrame(doc,columns=fields)
        invoice_df['Applicable % of Tax Rate'] = ""    
        mergedDf = pd.merge(invoice_df, grouped_df)
        mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
        
        columns_dict = {"invoice_number":"Invoice Number",'invoice_date':"Invoice Date","Applicable % of Tax Rate":"Applicable % of Tax Rate","trade_name":"Receiver Name","gst_rate":"Rate","place_of_supply":"Place Of Supply","invoice_date":"Invoice Date","gst_number":"GSTIN","invoice_type":"Invoice Type","item_value":"Taxable Value","item_value_after_gst":"Invoice Value","igst_amount":"Integrated Tax Amount","gst_cess_amount":"Cess Amount"}
        mergedDf.rename(columns=columns_dict,inplace=True)
        mergedDf = mergedDf.sort_values(by=['Invoice Number'])
        mergedDf = mergedDf[columns]
        mergedDf['Invoice Date'] = mergedDf['Invoice Date'].apply(str)
        data = mergedDf.values.tolist()
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}

@frappe.whitelist()
def B2CS_Invoices(data):
    latest_invoice = frappe.get_last_doc('Invoices')
    company = frappe.get_doc('company',latest_invoice.company)
    
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        
        columns = ['Invoice Number','Invoice Date','Invoice Value','Place Of Supply','Applicable % of Tax Rate','Rate','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
        fields = ['invoice_number','invoice_date','invoice_type','place_of_supply']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice'],'invoice_type':['=','B2C'],'sales_amount_after_tax':['<=',250000],'place_of_supply':["=",company.state_code]},fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            
            return columns,data
        doc_list = [list(x) for x in doc]
        invoice_names = [x[0] for x in doc_list]
        
        items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
        items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount']
        items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields = items_fields ,as_list=True)
        items_df = pd.DataFrame(items_doc,columns=items_columns)
        items_df = items_df.round(2)
        
        items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
        del items_df['cess_amount']
        del items_df['state_cess_amount']
        
        
        grouped_df = items_df.groupby(["invoice_number", "gst_rate"],as_index=False).sum().round(2)
        # print(grouped_df.head())
        invoice_df = pd.DataFrame(doc,columns=fields)
        invoice_df['Applicable % of Tax Rate'] = ""    
        mergedDf = pd.merge(invoice_df, grouped_df)
        mergedDf['place_of_supply'] = mergedDf['place_of_supply'].fillna(company.state_code)
       
        columns_dict = {"invoice_number":"Invoice Number","Applicable % of Tax Rate":"Applicable % of Tax Rate","trade_name":"Receiver Name","gst_rate":"Rate","place_of_supply":"Place Of Supply","invoice_date":"Invoice Date","gst_number":"GSTIN","invoice_type":"Invoice Type","item_value":"Taxable Value","item_value_after_gst":"Invoice Value","igst_amount":"Integrated Tax Amount","cgst_amount":"Central Tax Amount","sgst_amount":"State/UT Tax Amount","gst_cess_amount":"Cess Amount"}
        mergedDf.rename(columns=columns_dict,inplace=True)
        mergedDf = mergedDf.sort_values(by=['Invoice Number'])
        mergedDf = mergedDf[columns]
        mergedDf['Invoice Date'] = mergedDf['Invoice Date'].apply(str)
        data = mergedDf.values.tolist()
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}


@frappe.whitelist()
def HSN_SAC_SUMMARY_REPORT(data):
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        
        columns = ['HSN','Description','UQC','Total Quantity','Total Value','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','State Cess Amount','Central Cess Amount']
        fields = ['invoice_number']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['!=','Credit Invoice']},fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            
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
        grouped_df['Description'] = " "
        latest_invoice = frappe.get_last_doc('Invoices')

        company = frappe.get_doc('company',latest_invoice.company)

        
        
        mergedDf = grouped_df
        
        mergedDf['Total Quantity'] =1.0
        
        mergedDf.rename(columns={'unit_of_measurement_description':'UQC',"Description":"Description",'sac_code':'HSN','total_value':'Total Value','item_value':'Taxable Value','igst_amount':'Integrated Tax Amount','cgst_amount':'Central Tax Amount','sgst_amount':'State/UT Tax Amount','cess_amount':'Central Cess Amount','state_cess_amount':'State Cess Amount'}, inplace=True)
        # print(mergedDf.head())
        mergedDf = mergedDf[columns]
        data = mergedDf.values.tolist()
        
        # data.append(['Total',' ',round(mergedDf['Total Quantity'].sum(),2),round(mergedDf['Total Value'].sum(),2),round(mergedDf['Taxable Value'].sum(),2),round(mergedDf['Integrated Tax Amount'].sum(),2),round(mergedDf['Central Tax Amount'].sum(),2),round(mergedDf['State/UT Tax Amount'].sum(),2),round(mergedDf['State Cess Amount'].sum(),2),round(mergedDf['Central Cess Amount'].sum(),2)])
        # print(columns,data,mergedDf['Total Value'].sum())
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)} 


def DebitCreditNote(data):
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        # columns = ["Original Invoice Number","Transaction type","Debit Note No / Credit Note No.","Debit Note / Credit Note Date","Month","CustomerGSTIN/UIN","Customer Name","Type","SAC / HSN CODE","Invoice value","Base Amount","Taxable Value","Total GST RATE %","IGST Rate","IGST Amount","CGST Rate","CGST Amount","SGST / UT Rate","SGST / UT GST Amount","GST Compensation Cess Rate","GST Compensation Cess Amount"]
        columns = ['GSTIN/UIN of Recipient','Receiver Name','Note Number','Note Date','Note Type','Place Of Supply','Reverse Charge','Note Supply Type','Note Value','Applicable % of Tax Rate','Rate','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']
        
        fields = ['invoice_number', 'invoice_date','guest_name','gst_number','invoice_type','trade_name','tax_invoice_referrence_number','invoice_category','place_of_supply','suptyp']
        debit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Debit Invoice']},fields=fields,as_list=True)
        credit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Credit Invoice']},fields=fields,as_list=True)
        sysCredit_invoices = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice'],'has_credit_items':['=','Yes']},fields=fields,as_list=True)

        doc = debit_invoices+credit_invoices+sysCredit_invoices
        if len(doc) == 0:
            data = []
            
            return columns,data
        doc_list = [list(x) for x in doc]
        invoice_names = [x[0] for x in doc_list]
        debit_names_list = [list(x) for x in debit_invoices]
        debit_names = [x[0] for x in debit_names_list]
        credit_names_list = [list(x) for x in credit_invoices]
        credit_names = [x[0] for x in credit_names_list]
        sys_names_list = [list(x) for x in sysCredit_invoices]
        sys_names = [x[0]+"ACN" for x in sys_names_list]
        # print(invoice_names)
        items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount','cgst','sgst','igst']
        items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst_amount','cgst_amount','sgst_amount','state_cess_amount','cess_amount','cgst','sgst','igst']
        if len(debit_invoices)>0:
            items_debit_doc = frappe.db.get_list('Items',filters={'parent':['in',debit_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
        else:
            items_debit_doc=()
        if len(credit_invoices)>0:

            items_credit_doc = frappe.db.get_list('Items',filters={'parent':['in',credit_names],'item_mode':['=',"Credit"]},fields =items_fields ,as_list=True)
        else:
            items_credit_doc = ()
        if len(sysCredit_invoices)>0:	
            items_sysCredit_doc = frappe.db.get_list('Items',filters={'parent':['in',sys_names],'item_mode':['=',"Credit"]},fields =items_fields ,as_list=True)
        else:
            items_sysCredit_doc = ()
        items_doc = items_debit_doc+items_credit_doc+items_sysCredit_doc	
        items_df = pd.DataFrame(items_doc,columns=items_columns)
        items_df = items_df.round(2)
        
        items_df["gst_cess_amount"] = items_df['cess_amount'] + items_df['state_cess_amount']
     
        del items_df['cess_amount']
        del items_df['state_cess_amount']
        
        
        grouped_df = items_df.groupby(["invoice_number","sac_code", "gst_rate","igst","cgst","sgst"],as_index=False).sum().round(2)
        invoice_df = pd.DataFrame(doc,columns=fields)
    
        latest_invoice = frappe.get_last_doc('Invoices')

        company = frappe.get_doc('company',latest_invoice.company)

        
        
        mergedDf = pd.merge(invoice_df, grouped_df)		
        mergedDf["Taxable Value"] = mergedDf['item_value']
        mergedDf['Reverse Charge'] = "No"
        mergedDf['rate'] = mergedDf['gst_rate']
        
        columns_dict ={'gst_number':'GSTIN/UIN of Recipient','guest_name':'Receiver Name','invoice_number':'Note Number','invoice_date':'Note Date','invoice_category':'Note Type','place_of_supply':'Place Of Supply','Reverse Charge':'Reverse Charge','suptyp':'Note Supply Type','item_value_after_gst':'Note Value','gst_rate':'Applicable % of Tax Rate','rate':'Rate','item_value':'Taxable Value','igst_amount':'Integrated Tax Amount','cgst_amount':'Central Tax Amount','sgst_amount':'State/UT Tax Amount','gst_cess_amount':'Cess Amount'}
        mergedDf.rename(columns=columns_dict, inplace=True)
        
        

        mergedDf = mergedDf[columns]
        
        mergedDf['Note Value'] = mergedDf['Note Value'].abs()
        mergedDf['Taxable Value'] = mergedDf['Taxable Value'].abs()
        mergedDf['Integrated Tax Amount'] = mergedDf['Integrated Tax Amount'].abs()
        mergedDf['Central Tax Amount'] = mergedDf['Central Tax Amount'].abs()
        mergedDf['State/UT Tax Amount'] = mergedDf['State/UT Tax Amount'].abs()
        mergedDf['Cess Amount'] = mergedDf['Cess Amount'].abs()
        mergedDf['Note Date'] = mergedDf['Note Date'].apply(str)
        data = mergedDf.values.tolist()
        
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)}   

@frappe.whitelist()
def Excempted(data):
    try:
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        
        # columns = ['HSN','Description','UQC','Total Quantity','Total Value','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','State Cess Amount','Central Cess Amount']
        columns = ['Description','Nil Rated Supplies','Exempted(other than nil rated/non GST supply)','Non-GST Supplies']
        fields = ['invoice_number','place_of_supply','invoice_type']
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice']},fields=fields,as_list=True)
        if len(doc) == 0:
            data = []
            return columns,data
        doc_list = [list(x) for x in doc]
        invoice_names = [x[0] for x in doc_list]
        
        items_fields = ['parent','sac_code','item_value','item_value_after_gst','taxable','type']
        items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','taxable','type']
        items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"]},fields =items_fields ,as_list=True)
        items_df = pd.DataFrame(items_doc,columns=items_columns)
        items_df = items_df.round(2)
        # print(items_df.head())
        invoice_df = pd.DataFrame(doc,columns=fields)
        mergedDf = pd.merge(invoice_df, items_df)
        latest_invoice = frappe.get_last_doc('Invoices')

        company = frappe.get_doc('company',latest_invoice.company)
        mergedDf.loc[(mergedDf.place_of_supply!=company.state_code),'place_of_supply'] = "inter"
    
        mergedDf = mergedDf.groupby(["taxable","type",'place_of_supply','invoice_type'],as_index=False).sum().round(2)
        output_data = mergedDf.to_dict('records')

        interstate_b2b = ['Inter-State supplies to registered persons','','','']
        intrastate_b2b = ['Intra-State supplies to registered persons','','','']
        interstate_b2c = ['Inter-State supplies to unregistered persons','','','']
        intrastate_b2c = ['Intra-State supplies to unregistered persons','','','']
        for each in output_data:
            if each['taxable'] == 'No' and each['invoice_type'] == 'B2B' and each['place_of_supply']!=company.state_code:
                interstate_b2b[3] = each['item_value_after_gst']
            if each['taxable'] == 'No' and each['invoice_type'] == 'B2B' and each['place_of_supply']==company.state_code:     
                intrastate_b2b[3] = each['item_value_after_gst']
            if each['taxable'] == 'No' and each['invoice_type'] == 'B2C' and each['place_of_supply']!=company.state_code:
                interstate_b2c[3] = each['item_value_after_gst']
            if each['taxable'] == 'No' and each['invoice_type'] == 'B2C' and each['place_of_supply']==company.state_code:     
                intrastate_b2c[3] = each['item_value_after_gst']  
            
            if each['taxable'] == 'Yes' and each['invoice_type'] == 'B2B' and each['place_of_supply']!=company.state_code and each['type'] == "Excempted":
                interstate_b2b[2] = each['item_value_after_gst']
            if each['taxable'] == 'Yes' and each['invoice_type'] == 'B2B' and each['place_of_supply']==company.state_code and each['type'] == "Excempted":     
                intrastate_b2b[2] = each['item_value_after_gst']
            if each['taxable'] == 'Yes' and each['invoice_type'] == 'B2C' and each['place_of_supply']!=company.state_code and each['type'] == "Excempted":
                interstate_b2c[2] = each['item_value_after_gst']
            if each['taxable'] == 'Yes' and each['invoice_type'] == 'B2C' and each['place_of_supply']==company.state_code and each['type'] == "Excempted":     
                intrastate_b2c[2] = each['item_value_after_gst']         

        data = [interstate_b2b,intrastate_b2b,interstate_b2c,intrastate_b2c]
        return columns, data
    except Exception as e:
        # print(str(e))
        print(traceback.print_exc())
        return {"success":False,"message":str(e)} 
