import frappe
from datetime import datetime
import datetime
import pandas as pd
import sys


@frappe.whitelist(allow_guest=True)
def after_lut_Number():
    try:
        company = frappe.get_last_doc('company')
        application_reference_number = company.application_reference_number
        data_filing = company.data_filing
        gst_number = company.gst_number
        inv = frappe.db.get_list('Invoices',fields =['invoice_number','invoice_date'])
        invoice_date = frappe.db.sql('''select invoice_number,invoice_date from `tabInvoices` where invoice_date >='2023-04-01' ''',as_dict=1)
        # date_format = invoice_date[0]['invoice_date']
        # print(date_format)
        inv_df = pd.DataFrame.from_records(inv)
        filter_df_inv = pd.DataFrame.from_records(invoice_date)
        merged_inner = pd.merge(left=inv_df, right=filter_df_inv, left_on='invoice_number', right_on='invoice_number')
        renamimg_data = merged_inner.rename(columns={'invoice_number': 'invoice_number', 'invoice_date_x':'invoice_date'})
        convert_data = renamimg_data.to_dict('records')
        for i in convert_data:
            print(i['invoice_number'],i['invoice_date'],"......................")
            frappe.db.set_value('Invoices',i['invoice_number'],{'company_application_reference_number':application_reference_number,'company_data_filing':data_filing,'company_gst':gst_number},update_modified=False)
            frappe.db.commit()
        return {"success":True, "message": "updated successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("after_lut_Number",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}
    
    



@frappe.whitelist(allow_guest=True)
def before_lut_Number():
    try:
        company = frappe.get_last_doc('company')
        application_reference_number = company.application_reference_number
        data_filing = company.data_filing
        gst_number = company.gst_number
        inv = frappe.db.get_list('Invoices',fields =['invoice_number','invoice_date'])
        invoice_date = frappe.db.sql('''select invoice_number,invoice_date from `tabInvoices` where invoice_date < '2023-04-01' ''',as_dict=1)
        # date_format = invoice_date[0]['invoice_date']
        # print(date_format)
        inv_df = pd.DataFrame.from_records(inv)
        filter_df_inv = pd.DataFrame.from_records(invoice_date)
        merged_inner = pd.merge(left=inv_df, right=filter_df_inv, left_on='invoice_number', right_on='invoice_number')
        renamimg_data = merged_inner.rename(columns={'invoice_number': 'invoice_number', 'invoice_date_x':'invoice_date'})
        convert_data = renamimg_data.to_dict('records')
        for i in convert_data:
            print(i['invoice_number'],i['invoice_date'],"......................")
            frappe.db.set_value('Invoices',i['invoice_number'],{'company_application_reference_number':application_reference_number,'company_data_filing':data_filing,'company_gst':gst_number},update_modified=False)
            frappe.db.commit()
        return {"success":True, "message": "updated successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("before_lut_Number",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}