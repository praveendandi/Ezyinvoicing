import frappe
import json
from frappe.utils import data as date_util


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
            """SELECT count(`tabSAC HSN Tax Summaries`.parent) as count, sum(`tabSAC HSN Tax Summaries`.cgst+`tabSAC HSN Tax Summaries`.sgst+`tabSAC HSN Tax Summaries`.igst) as tax_amount, sum(`tabSAC HSN Tax Summaries`.amount_before_gst) as taxable_value, sum(`tabSAC HSN Tax Summaries`.amount_after_gst) as before_gst, 'hsn-summary' as invoice_category from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format(year, month), as_dict=1)
        nil_rated_supplies = {"count": 0, "tax_amount": 0, "before_gst": 0,
                              "taxable_value": 0, "invoice_category": "nill-rated-supplies"}
        advance_received = {"count": 0, "tax_amount": 0, "before_gst": 0,
                            "taxable_value": 0, "invoice_category": "advance-received"}
        adjustment_of_advances = {"count": 0, "tax_amount": 0, "before_gst": 0,
                                  "taxable_value": 0, "invoice_category": "adjustment-of-advances"}
        total_data = {"tax_b2b": {k: (0 if v is None else v) for k, v in get_b2b_tax_invoice_summaries[0].items()},
                      "tax_b2c": {k: (0 if v is None else v) for k, v in get_b2c_tax_invoice_summaries[0].items()},
                      "credit_b2b": {k: (0 if v is None else v) for k, v in get_b2b_credit_debit_invoice_summaries[0].items()},
                      "credit_b2c": {k: (0 if v is None else v) for k, v in get_b2c_credit_debit_invoice_summaries[0].items()},
                      "nil_rated_supplies": nil_rated_supplies,
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
        invoice_summary = frappe.db.get_list("Invoices", filters=filters, fields=['COUNT(DISTINCT(gst_number)) as no_of_suppliers', 'COUNT(DISTINCT(name)) as no_of_invoices', 'SUM(pms_invoice_summary_without_gst) as total_invoices_amount_before_tax',
                                                                                  'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(total_gst_amount) as total_taxable_value', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst',
                                                                                  'SUM(cgst_amount) as total_cgst', 'SUM(total_central_cess_amount+total_state_cess_amount) as cess'])
        invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=[
                                          '*'], start=int(limit_start), page_length=int(limit_page_length))
        return {"success": True, "data": invoice_data, "summary": invoice_summary[0]}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}
