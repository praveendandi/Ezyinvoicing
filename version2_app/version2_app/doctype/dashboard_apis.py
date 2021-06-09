import frappe
import traceback,os,sys
import pandas as pd

@frappe.whitelist(allow_guest=True)
def invoicecategorycount():
    try:
        # data = {"fromdate":"2020-12-31","todate":"2021-04-04"}
        deletedocuments = frappe.db.get_list('Deleted Document',filters={"deleted_doctype":"Invoices"},fields=['count(name) as count'])
        # print(deletedocuments)
        outputdata = frappe.db.get_list('Invoices',fields=['count(name) as count', 'invoice_category'],group_by='invoice_category')
        outputdata.append({'invoice_category':"Deleted Documents","count":deletedocuments[0]['count']})
        return {"success":True,"data":outputdata}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoicecategorycount","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"status":False,"message":str(e)}   

@frappe.whitelist(allow_guest=True)
def invoicedetailscount(data):
    try:
        # data = {"fromdate":"2020-12-31","todate":"2021-04-04"}
        taxdata = frappe.db.get_list('Invoices',filters={'invoice_date':["between", [data['fromdate'], data['todate']]],'invoice_category':'Tax Invoice'},fields=['count(name) as count', 'irn_generated'],group_by='irn_generated')
        creditdata = frappe.db.get_list('Invoices',filters={'invoice_date':["between", [data['fromdate'], data['todate']]],'invoice_category':'Credit Invoice'},fields=['count(name) as count', 'irn_generated'],group_by='irn_generated')
        debitdata = frappe.db.get_list('Invoices',filters={'invoice_date':["between", [data['fromdate'], data['todate']]],'invoice_category':'Debit Invoice'},fields=['count(name) as count', 'irn_generated'],group_by='irn_generated')
        outputdata = {"invoices":taxdata,"creditinvoices":creditdata,"debitinvoices":debitdata}
        return {"success":True,"data":outputdata}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoicedetailscount","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"status":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def GSTR1Statistics(data):
    try:
        
        taxb2b=frappe.db.get_all('Invoices',filters={"invoice_date":['between', (data['fromdate'],data['todate'])],'invoice_category':"Tax Invoice",'irn_generated':'Success','invoice_type':'B2B'},fields=['count(name) as count','sum(total_invoice_amount) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(cgst_amount) as Cgstamount', 'sum(sgst_amount) as Sgstamount','sum(igst_amount) as Igstamount'])
        # fields=['count(name) as count','sum(total_invoice_amount) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(cgst_amount) as Cgstamount', 'sum(sgst_amount) as Sgstamount','sum(igst_amount) as Igstamount']
        taxb2c=frappe.db.get_all('Invoices',filters={'invoice_category':"Tax Invoice",'irn_generated':'Success','invoice_type':'B2C','invoice_date': ['between', (data['fromdate'],data['todate'])]},fields=['count(name) as count','sum(total_invoice_amount) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(cgst_amount) as Cgstamount', 'sum(sgst_amount) as Sgstamount','sum(igst_amount) as Igstamount'])
        debitb2b=frappe.db.get_all('Invoices',filters={'invoice_category':"Debit Invoice",'irn_generated':'Success','invoice_type':'B2B','invoice_date': ['between', (data['fromdate'],data['todate'])]},fields=['count(name) as count','sum(total_invoice_amount) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(cgst_amount) as Cgstamount', 'sum(sgst_amount) as Sgstamount','sum(igst_amount) as Igstamount'])
        debitb2c=frappe.db.get_all('Invoices',filters={'invoice_category':"Debit Invoice",'irn_generated':'Success','invoice_type':'B2C','invoice_date': ['between', (data['fromdate'],data['todate'])]},fields=['count(name) as count','sum(total_invoice_amount) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(cgst_amount) as Cgstamount', 'sum(sgst_amount) as Sgstamount','sum(igst_amount) as Igstamount'])
        creditb2b=frappe.db.get_all('Invoices',filters={'has_credit_items':"Yes",'irn_generated':'Success','invoice_type':'B2B','invoice_date': ['between', (data['fromdate'],data['todate'])]},fields=['count(name) as count','sum(credit_value_before_gst) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(credit_cgst_amount) as Cgstamount', 'sum(credit_sgst_amount) as Sgstamount','sum(credit_igst_amount) as Igstamount'])
        creditb2c=frappe.db.get_all('Invoices',filters={'has_credit_items':"Yes",'irn_generated':'Success','invoice_type':'B2C','invoice_date': ['between', (data['fromdate'],data['todate'])]},fields=['count(name) as count','sum(credit_value_before_gst) as Totalinvoicevalue','sum(amount_before_gst) as Totaltaxablevalue','sum(credit_cgst_amount) as Cgstamount', 'sum(credit_sgst_amount) as Sgstamount','sum(credit_igst_amount) as Igstamount'])
        doc = frappe.db.get_list('Invoices', filters={'invoice_date': ['Between',(data['fromdate'],data['todate'])],'irn_generated':['=','Success'],'invoice_category':['=','Tax Invoice']},fields=['invoice_number'],as_list=True)
        outputdata = {'taxb2b':taxb2b,'taxb2c':taxb2c,'debitb2b':debitb2b,"debitb2c":debitb2c,"creditb2b":creditb2b,"creditb2c":creditb2c}
        if len(doc)>0:
            doc_list = [list(x) for x in doc]
            invoice_names = [x[0] for x in doc_list]
            items_fields = ['parent','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount']
            items_columns = ['invoice_number','sac_code','item_value','item_value_after_gst','gst_rate','igst','igst_amount','cgst','cgst_amount','sgst','sgst_amount']
            items_doc = frappe.db.get_list('Items',filters={'parent':['in',invoice_names],'item_mode':['!=',"Credit"],'taxable':"Yes"},fields =items_fields ,as_list=True)
            items_df = pd.DataFrame(items_doc,columns=items_columns)
            grouped_df = items_df.groupby(["sac_code", "gst_rate"],as_index=False).sum().round(2)
            # print(grouped_df['item_value'].sum(),len(grouped_df))
            sacHsnSummary = {"count":len(grouped_df),"Totalinvoicevalue":round(grouped_df['item_value_after_gst'].sum(),2),"Totaltaxablevalue":round(grouped_df['item_value'].sum(),2),"Cgstamount":round(grouped_df['cgst_amount'].sum(),2),"Sgstamount":round(grouped_df['sgst_amount'].sum(),2),"Igstamount":round(grouped_df['igst_amount'].sum(),2)}
            outputdata['sacSummary'] = [sacHsnSummary]
        else:
            sacHsnSummary = {"count":0,"Totalinvoicevalue":0,"Totaltaxablevalue":0,"Cgstamount":0,"Sgstamount":0,"Igstamount":0}
            outputdata['sacSummary'] = [sacHsnSummary]
        
        return {"success":True,"data":outputdata}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing GSTR1Statistics","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"status":False,"message":str(e)}


@frappe.whitelist(allow_guest=True)
def invoicereconsiliationcount(data):
    try:
        # data = {"fromdate":"2020-12-31","todate":"2021-04-04"}
        ezydata = frappe.db.get_list('Invoice Reconciliations',filters={'bill_generation_date':["between", [data['fromdate'], data['todate']]]},fields=['count(name) as count','invoice_found'],group_by='invoice_found')
        operadata = frappe.db.get_list('Invoice Reconciliations',filters={'bill_generation_date':["between", [data['fromdate'], data['todate']]]},fields=['count(name) as count'])
        outputdata = {"ezydata":ezydata,"operadata":operadata}
        return {"success":True,"data":outputdata}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing invoicereconsiliationcount","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"status":False,"message":str(e)}


