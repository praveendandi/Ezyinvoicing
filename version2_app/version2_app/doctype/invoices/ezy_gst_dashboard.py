import frappe
import json
import requests
import os
import pandas as pd
from frappe.utils import data as date_util
from frappe.utils import cstr


@frappe.whitelist(allow_guest=True)
def getGSTR1DashboardDetails(year=None, month=None):
    try:
        get_b2b_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2B' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2C' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_b2b_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice')  and invoice_type='B2B' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice')  and invoice_type='B2C' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_hsn_summary = frappe.db.sql(
            """SELECT count(`tabSAC HSN Tax Summaries`.parent) as count, sum(`tabSAC HSN Tax Summaries`.cgst+`tabSAC HSN Tax Summaries`.sgst+`tabSAC HSN Tax Summaries`.igst) as tax_amount, sum(`tabSAC HSN Tax Summaries`.amount_before_gst) as before_gst, sum(`tabSAC HSN Tax Summaries`.amount_after_gst) as taxable_value, 'hsn-summary' as invoice_category from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format(year, month), as_dict=1)
        nil_rated_supplies = frappe.db.sql("""SELECT count(`tabItems`.name) as count, sum(item_taxable_value) as taxable_value, sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount) as tax_amount, sum(item_value_after_gst) as before_gst, 'Nil Rated Supplies' as invoice_type from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where (`tabItems`.taxable = 'No' or (`tabInvoices`.sez = '1' and `tabItems`.type= 'Exempted')) and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}'""".format(year, month), as_dict=1)
        advance_received = {"count": 0, "tax_amount": 0, "before_gst": 0,
                            "taxable_value": 0, "invoice_category": "advance-received"}
        adjustment_of_advances = {"count": 0, "tax_amount": 0, "before_gst": 0,
                                  "taxable_value": 0, "invoice_category": "adjustment-of-advances"}
        total_data = {"tax_b2b": {k: (0 if v is None else v) for k, v in get_b2b_tax_invoice_summaries[0].items()},
                      "tax_b2c": {k: (0 if v is None else v) for k, v in get_b2c_tax_invoice_summaries[0].items()},
                      "credit_b2b": {k: (0 if v is None else v) for k, v in get_b2b_credit_debit_invoice_summaries[0].items()},
                      "credit_b2c": {k: (0 if v is None else v) for k, v in get_b2c_credit_debit_invoice_summaries[0].items()},
                      "nil_rated_supplies": {k: (0 if v is None else v) for k, v in nil_rated_supplies[0].items()},
                      "advance_received": advance_received,
                      "adjustment_of_advances": adjustment_of_advances,
                      "get_hsn_summary": {k: (0 if v is None else v) for k, v in get_hsn_summary[0].items()}}
        return {"success": True, "data": total_data}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def getInvoices(filters=[], limit_page_length=20, limit_start=0, month=None, year=None):
    try:
        filters = json.loads(filters)
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        filters = filters + [['invoice_date', 'between', [start_date, end_date]]]
        invoice_summary = frappe.db.get_list("Invoices", filters=filters, fields=['COUNT(DISTINCT(gst_number)) as no_of_suppliers', 'COUNT(DISTINCT(name)) as no_of_invoices', 'SUM(pms_invoice_summary_without_gst) as total_taxable_value',
                                                                                  'SUM(total_gst_amount) as total_gst_amount', 'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst',
                                                                                  'SUM(cgst_amount) as total_cgst', 'SUM(total_central_cess_amount+total_state_cess_amount) as cess'])
        invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=[
                                          '*'], start=int(limit_start), page_length=int(limit_page_length))
        return {"success": True, "data": invoice_data, "summary": invoice_summary[0]}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def getGSTR1ReconciliationSummaryCount(filters=[], month=None, year=None, company=None):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        filters = filters + \
            [['invoice_date', 'Between', [start_date, end_date]]]
        invoice_list = frappe.db.get_list(
            "Invoices", filters=filters, as_list=1)
        invoice_list = list(sum(invoice_list, ()))
        gst_invoice_list = frappe.db.get_list(
            "GSTR One Saved Invoices", filters=filters, as_list=1)
        gst_invoice_list = list(sum(gst_invoice_list, ()))
        if any("property" in sublist for sublist in filters):
            miscellaneous_gst_invoice_list = frappe.db.get_list(
                "GSTR One Saved Invoices", filters=filters, as_list=1)
        matching = len(list(set(invoice_list).intersection(gst_invoice_list)))
        missing_in_einvoice = len(
            list(set(gst_invoice_list)-set(invoice_list)))
        missing_in_gst = len(list(set(invoice_list)-set(gst_invoice_list)))
        data = {"total_invoices": matching+missing_in_einvoice+missing_in_gst,
                "matching": matching,
                "missing_in_einvoice": missing_in_einvoice,
                "missing_in_gst": missing_in_gst}
        month_year = (month+year).lstrip('0')
        gstr_one_saved_filter = [["period","=",month_year]]
        if any("company" in sublist for sublist in filters):
            company = [each[2] for each in filters if "company" in each]
            gstr_one_saved_filter += [["company","=",company[0]]]
        last_reconciled_on = frappe.db.get_list("Gstr One Saved Details",filters=gstr_one_saved_filter,fields=["creation"], order_by='creation desc')
        if len(last_reconciled_on) > 0:
            last_reconciled_on = last_reconciled_on[0]["creation"]
        else:
            last_reconciled_on = ""
        return {"success": True, "data": data,"last_reconciled_on":last_reconciled_on}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def getHsnSummary(filters=[], limit_page_length=20, limit_start=0, month=None, year=None):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        sql_filters = ""
        if len(filters) > 0:
            sql_filters = " and " + \
                (' and '.join("{} {} '{}'".format(
                    value[0], value[1], value[2]) for value in filters))
            if "invoice_number" in sql_filters:
                sql_filters = sql_filters.replace("invoice_number","`tabInvoices`.invoice_number")
        get_hsn_summary = frappe.db.sql(
            """SELECT `tabInvoices`.invoice_number as invoice_number, `tabInvoices`.invoice_date as invoice_date,
            `tabInvoices`.gst_number as gst_number,`tabInvoices`.legal_name as legal_name, `tabInvoices`.invoice_type as invoice_type,
            `tabInvoices`.invoice_category as invoice_category, `tabSAC HSN Tax Summaries`.sac_hsn_code as sac_hsn_code, `tabSAC HSN Tax Summaries`.cgst as cgst,
            `tabSAC HSN Tax Summaries`.sgst as sgst, `tabSAC HSN Tax Summaries`.igst as igst, `tabSAC HSN Tax Summaries`.cess as central_cess,
            `tabSAC HSN Tax Summaries`.state_cess as state_cess, (`tabSAC HSN Tax Summaries`.cgst+`tabSAC HSN Tax Summaries`.sgst+`tabSAC HSN Tax Summaries`.igst) as total_gst,`tabSAC HSN Tax Summaries`.amount_before_gst as total_tax_amount,
            `tabSAC HSN Tax Summaries`.amount_after_gst as total_amount from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}{} order by invoice_number LIMIT {},{}""".format(year, month, sql_filters, limit_start, limit_page_length), as_dict=1)
        get_hsn_summary_for_count = frappe.db.sql(
            """SELECT `tabInvoices`.invoice_number as invoice_number from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}{} order by invoice_number""".format(year, month, sql_filters))
        return {"success": True, "data": get_hsn_summary,"count":len(get_hsn_summary_for_count)}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def export_invoices(filters=[], month=None, year=None):
    try:
        invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'invoice_date as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt', "sales_amount_before_tax as TatalTaxableAmount","cgst_amount as CGST", "sgst_amount as SGST", "igst_amount as IGST", "total_gst_amount as TotalGST", "(total_central_cess_amount+total_state_cess_amount) as CESS", "ack_date as EInvoiceGenerationDate"])
        if len(invoice_data)>0:
            company = frappe.get_last_doc("company")
            cwd = os.getcwd()
            site_name = cstr(frappe.local.site)
            file_path = cwd + "/" + site_name + "/public/files/invoice_export.xlsx"
            df = pd.DataFrame.from_records(invoice_data)
            df.to_excel(file_path, index=False)
            files_new = {"file": open(file_path, 'rb')}
            payload_new = {'is_private': 1, 'folder': 'Home'}
            file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                        data=payload_new, verify=False).json()
            if "file_url" in file_response["message"].keys():
                os.remove(file_path)
                return {"success": True, "file_url": file_response["message"]["file_url"]}
            return {"success": False, "message": "something went wrong"}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}
    