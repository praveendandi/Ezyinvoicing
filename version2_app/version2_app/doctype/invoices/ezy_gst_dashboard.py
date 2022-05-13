from webbrowser import get
import datetime
import frappe
import json
import requests
import os
import pandas as pd
from frappe.utils import data as date_util
from frappe.utils import cstr
import xlsxwriter
import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Color,PatternFill,Font,Fill,colors,Alignment,Border,Side
from openpyxl.cell import Cell
# from xlsxwriter import add_worksheet


@frappe.whitelist(allow_guest=True)
def getGSTR1DashboardDetails(year=None, month=None):
    try:
        get_b2b_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2B' and sez=0 and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_b2b_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice') and `tabInvoices`.irn_generated = 'Success' and invoice_type='B2B' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice')  and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_hsn_summary = frappe.db.sql(
            """SELECT count(`tabSAC HSN Tax Summaries`.parent) as count, sum(`tabSAC HSN Tax Summaries`.cgst+`tabSAC HSN Tax Summaries`.sgst+`tabSAC HSN Tax Summaries`.igst) as tax_amount, sum(`tabSAC HSN Tax Summaries`.amount_before_gst) as before_gst, sum(`tabSAC HSN Tax Summaries`.amount_after_gst) as taxable_value, sum(`tabSAC HSN Tax Summaries`.igst) as igst_amount, sum(`tabSAC HSN Tax Summaries`.cgst) as cgst_amount, sum(`tabSAC HSN Tax Summaries`.sgst) as sgst_amount, 'hsn-summary' as invoice_category from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format(year, month), as_dict=1)
        nil_rated_supplies = frappe.db.sql("""SELECT count(`tabItems`.name) as count, sum(item_taxable_value) as taxable_value, sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount) as tax_amount, sum(item_value_after_gst) as before_gst, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount,'Nil Rated Supplies' as invoice_type from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where ((`tabItems`.gst_rate = 0 and `tabItems`.taxable = "Yes") or (`tabItems`.taxable = "No") or (`tabInvoices`.sez = 1 and `tabItems`.type = "Excempted")) and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}'""".format(year, month), as_dict=1)
        get_sez_SEZWP = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and sez = 1 and suptyp = 'SEZWP' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_sez_SEZWOP = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst),2) as taxable_value, round(sum(pms_invoice_summary),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and sez = 1 and suptyp = 'SEZWOP' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)

        advance_received = {"count": 0, "tax_amount": 0, "before_gst": 0,
                            "taxable_value": 0, "igst_amount": 0, "cgst_amount": 0, "sgst_amount": 0, "invoice_category": "advance-received"}
        adjustment_of_advances = {"count": 0, "tax_amount": 0, "before_gst": 0,
                                  "taxable_value": 0, "igst_amount": 0, "cgst_amount": 0, "sgst_amount": 0, "invoice_category": "adjustment-of-advances"}
        total_data = {"tax_b2b": {k: (0 if v is None else v) for k, v in get_b2b_tax_invoice_summaries[0].items()},
                      "tax_b2c": {k: (0 if v is None else v) for k, v in get_b2c_tax_invoice_summaries[0].items()},
                      "credit_b2b": {k: (0 if v is None else v) for k, v in get_b2b_credit_debit_invoice_summaries[0].items()},
                      "credit_b2c": {k: (0 if v is None else v) for k, v in get_b2c_credit_debit_invoice_summaries[0].items()},
                      "nil_rated_supplies": {k: (0 if v is None else v) for k, v in nil_rated_supplies[0].items()},
                      "sez_with_payment": {k: (0 if v is None else v) for k, v in get_sez_SEZWP[0].items()},
                      "sez_without_payment": {k: (0 if v is None else v) for k, v in get_sez_SEZWOP[0].items()},
                      "advance_received": advance_received,
                      "adjustment_of_advances": adjustment_of_advances,
                      "get_hsn_summary": {k: (0 if v is None else v) for k, v in get_hsn_summary[0].items()}}
        return {"success": True, "data": total_data}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def getInvoices(filters=[], limit_page_length=20, limit_start=0, month=None, year=None, export=False):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        filters = filters + \
            [['invoice_date', 'between', [start_date, end_date]],
                ["irn_generated", "=", "Success"]]

        invoice_summary = frappe.db.get_list("Invoices", filters=filters, fields=['COUNT(DISTINCT(gst_number)) as no_of_suppliers', 'COUNT(DISTINCT(name)) as no_of_invoices', 'SUM(pms_invoice_summary_without_gst) as total_taxable_value',
                                                                                  'SUM(total_gst_amount) as total_gst_amount', 'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst',
                                                                                  'SUM(cgst_amount) as total_cgst', 'SUM(total_central_cess_amount+total_state_cess_amount) as cess'])
        if export == False:
            invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=[
                '*'], start=int(limit_start), page_length=int(limit_page_length))
        else:
            invoice_data = frappe.db.get_list(
                "Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'DATE_FORMAT(invoice_date, "%d-%m-%Y") as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt', 'sales_amount_before_tax as TotalTaxableAmt', 'sgst_amount as SGST', 'cgst_amount as CGST', 'igst_amount as IGST', 'total_gst_amount as TotalGST', 'cess_amount as CESS'])
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
            [['invoice_date', 'Between', [start_date, end_date]],
                ["irn_generated", "=", "Success"]]
        invoice_list = frappe.db.get_list(
            "Invoices", filters=filters, as_list=1)
        invoice_list = list(sum(invoice_list, ()))
        gst_invoice_list = frappe.db.get_list(
            "GSTR One Saved Invoices", filters=[["invoice_number", "in", invoice_list]], as_list=1)
        gst_invoice_list = list(sum(gst_invoice_list, ()))
        if any("property" in sublist for sublist in filters):
            miscellaneous_gst_invoice_list = frappe.db.get_list(
                "GSTR One Saved Invoices", filters=[["invoice_number", "in", invoice_list]], as_list=1)
        matching = len(list(set(invoice_list).intersection(gst_invoice_list)))
        missing_in_einvoice = len(
            list(set(gst_invoice_list)-set(invoice_list)))
        missing_in_gst = len(list(set(invoice_list)-set(gst_invoice_list)))
        data = {"total_invoices": matching+missing_in_einvoice+missing_in_gst,
                "matching": matching,
                "missing_in_einvoice": missing_in_einvoice,
                "missing_in_gst": missing_in_gst}
        month_year = (month+year).lstrip('0')
        gstr_one_saved_filter = [["period", "=", month_year]]
        if any("company" in sublist for sublist in filters):
            company = [each[2] for each in filters if "company" in each]
            gstr_one_saved_filter += [["company", "=", company[0]]]
        last_reconciled_on = frappe.db.get_list("Gstr One Saved Details", filters=gstr_one_saved_filter, fields=[
                                                "creation"], order_by='creation desc')
        if len(last_reconciled_on) > 0:
            last_reconciled_on = last_reconciled_on[0]["creation"]
        else:
            last_reconciled_on = ""
        return {"success": True, "data": data, "last_reconciled_on": last_reconciled_on}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def getHsnSummary(filters=[], limit_page_length=20, limit_start=0, month=None, year=None, export=False):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        sql_filters = ""
        if len(filters) > 0:
            sql_filters = " and " + \
                (' and '.join("{} {} '{}'".format(
                    value[0], value[1], value[2]) for value in filters))
        if not export:
            get_hsn_summary = frappe.db.sql(
                """SELECT `tabItems`.sac_code as Sac_Code, `tabItems`.gst_rate as Gst_Rate, `tabItems`.unit_of_measurement_description as UQC, `tabItems`.quantity as total_quantity, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.state_cess_amount) as state_cess_amount,sum(`tabItems`.cess_amount) as central_cess_amount, (sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+(`tabItems`.igst_amount)) as total_gst, sum(`tabItems`.item_value) as total_tax_amount, sum(`tabItems`.item_value_after_gst) as total_amount from `tabItems` INNER JOIN `tabInvoices` ON `tabItems`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}{} GROUP BY `tabItems`.sac_code, `tabItems`.gst_rate""".format(year, month, sql_filters), as_dict=1)
        else:
            get_hsn_summary = frappe.db.sql(
                """SELECT `tabItems`.sac_code as Sac_Code, `tabItems`.gst_rate as Gst_Rate, `tabItems`.unit_of_measurement_description as UQC, `tabItems`.quantity as total_quantity, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.state_cess_amount) as state_cess_amount,sum(`tabItems`.cess_amount) as central_cess_amount, (sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+(`tabItems`.igst_amount)) as total_gst, sum(`tabItems`.item_value) as total_tax_amount, sum(`tabItems`.item_value_after_gst) as total_amount from `tabItems` INNER JOIN `tabInvoices` ON `tabItems`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={} GROUP BY `tabItems`.sac_code, `tabItems`.gst_rate""".format(year, month), as_dict=1)
        return {"success": True, "data": get_hsn_summary}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def export_invoices(filters=[], month=None, year=None):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        filters = filters + \
            [['invoice_date', 'Between', [start_date, end_date]],
                ["irn_generated", "=", "Success"]]
        invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'invoice_date as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt',
                                          "sales_amount_before_tax as TatalTaxableAmount", "cgst_amount as CGST", "sgst_amount as SGST", "igst_amount as IGST", "total_gst_amount as TotalGST", "(total_central_cess_amount+total_state_cess_amount) as CESS", "ack_date as EInvoiceGenerationDate"], order_by='invoice_number asc')
        if len(invoice_data) > 0:
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


@frappe.whitelist()
def export_workbook(month=None, year=None):
    try:
        total_data = {}
        company = frappe.get_last_doc("company")
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        datetime_object = datetime.datetime.strptime(month, "%m")
        month_name = datetime_object.strftime("%b")
        file_path = cwd + "/" + site_name + \
            "/public/files/GSTR-"+month_name+"-"+year+".xlsx"
        get_summary = getGSTR1DashboardDetails(year, month)
        if not get_summary["success"]:
            return get_summary
        get_hsn_summary = getHsnSummary(month=month, year=year, export=True)
        if not get_hsn_summary["success"]:
            return get_hsn_summary
        get_nil_rated = nil_rated_supplies(month=month, year=year)
        if not get_nil_rated["success"]:
            return get_nil_rated
        filter_list = {"B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 0]], "B2B-SEZWP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 1], ["suptyp", "=", "SEZWP"]], "B2B-SEZWOP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 1], ["suptyp", "=", "SEZWOP"]], "B2C": [["invoice_type", "=", "B2C", ], ["irn_generated", "=", "Success"]], "Credit-Debit-B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "in", ["Debit Invoice", "Credit Invoice"]], ["irn_generated", "=", "Success"], ["sez", "=", 0]], "Credit-Debit-B2C": [["invoice_type", "=", "B2C"], [
            "invoice_category", "in", ["Debit Invoice", "Credit Invoice"]], ["irn_generated", "=", "Success"]]}
        for key, value in filter_list.items():
            get_invoices_data = getInvoices(
                filters=value, month=month, year=year, export=True)
            if not get_invoices_data["success"]:
                return get_invoices_data
            total_data.update({key: get_invoices_data["data"]})



        # wb = Workbook()
        # ws = wb.active
        # ws = wb.create_sheet("Summary")
        # ws.title = "Summary"
        # ws.move_range("A1:A3", rows=1, cols=0)
        # for i in range(ws.min_row,ws.max_row):
        #     ws.row_dimensions[i].height = 15
        # # sheet = wb['Sheet1']
        # font = Font(name = 'Cambria',size=12,bold=True,color = '00FFFFFF')
        # blueFill = PatternFill(start_color = '0B0B45',end_color = '0B0B45',fill_type = 'solid')
        # number_format = "#,##0"
        # alignment = Alignment(horizontal='center',vertical='top')
        # border = Border(left=Side(border_style='thin',color='00000000'),right=Side(border_style='thin',color='00000000'),top=Side(border_style='thin',color='00000000'),
        # bottom=Side(border_style='thin',color='00000000'),diagonal=Side(border_style='thin',color='00000000'),diagonal_direction=0,outline=Side(border_style='thin',color='00000000'),
        # vertical=Side(border_style='thin', color='00000000'),horizontal=Side(border_style='thin',color='00000000'))
        # cols = ['A','B','C']
        # for col in cols:
        #     for i in range(2,5):
        #         cols = ws[f'{col}{i}']
        #         cols.fill = blueFill
        #         cols.font = font
        #         cols.border = border
        # cols = ['B','C','D','E','F','G','H']
        # for col in cols :
        #     cols = ws[f'{col}6']
        #     cols.fill = blueFill
        #     cols.font = font
        #     cols.alignment = alignment
        #     cols.border = border
        # cols = ['B','C','D','E','F','G','H']
        # for col in cols:
        #     for i in range(7,27):
        #         cols = ws[f'{col}{i}']
        #         cols.number_format = number_format
        #         cols.font = Font(name = 'Cambria',size=12)
        #         cols.border = border
        # for col in range(7,10):
        #     cols = ws[f'B{col}']
        #     cols.fill = blueFill
        #     cols.font = font
        # cols = ['C','D','E','F','G','H']
        # for col in cols:
        #     cols = ws[f'{col}9']
        #     cols.font = Font(bold = True)
        #     cols = ws[f'{col}23']
        #     cols.font = Font(bold = True)
        # cols = ['C','D','E','F','G','H']
        # for col in cols:
        #     cols = ws[f'{col}24']
        #     cols.font = Font(bold = True)
        #     number_format = "(#,##0)"
        #     cols.number_format = number_format
        # for ws1 in ws:
        #     for row in ws.rows:
        #         x1=ucr(row[0].value)
        #         row[1].value=x1
        # ws = wb.worksheets[1]
        # ws['A2'] = 'Hiregange associates'
        # ws['A3'] = 'Name of the client: '
        # ws['A4'] = "GSTR-1 Summary for the period"
        # ws['B6'] = [('')]
        # Invoice_value = [('Invoice value',)]
        # # ws['B6'] = {get_summary["data"], index=["count", "taxable_value", "igst_amount", "cgst_amount", "sgst_amount", "tax_amount", "before_gst"]}

        # # ws.cell(row=2, column=2).value = 2
        # # ws.cell(coordinate="C3").value = 3

        # wb.save(file_path)


        # return True
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        # wb = pd.DataFrame(get_summary["data"], index=[
        #                           "count", "taxable_value", "igst_amount", "cgst_amount", "sgst_amount", "tax_amount", "before_gst"])
        # wb = wb.rename(index={'count': 'Count', "taxable_value": "Taxable Value", "igst_amount": "IGST",
        #                                "cgst_amount": "CGST", "sgst_amount": "SGST", "tax_amount": "Tax amount", "before_gst": "Invoice value"})
        # wb = wb.T
        # wb = wb.reindex({'tax_b2b': 'B2B', 'sez_with_payment': 'B2B-SEZWP', 'sez_without_payment': 'B2B-SEZWOP', 'tax_b2c': 'B2C', 'credit_b2b': 'Credit/ Debit note (Registered)', 'credit_b2c': 'Credit/ Debit note (Unregistered)',
        #                                 'nil_rated_supplies': 'Nil Rated Supplies', 'advance_received': 'Advance Received', 'adjustment_of_advances': 'Adjustment of Advances', 'get_hsn_summary': 'HSN Summary of Outward supply'})
        # wb = wb.rename(index={'tax_b2b': 'B2B', 'sez_with_payment': 'B2B-SEZWP', 'sez_without_payment': 'B2B-SEZWOP', 'tax_b2c': 'B2C', 'credit_b2b': 'Credit/ Debit note (Registered)', 'credit_b2c': 'Credit/ Debit note (Unregistered)',
        #                                'nil_rated_supplies': 'Nil Rated Supplies', 'advance_received': 'Advance Received', 'adjustment_of_advances': 'Adjustment of Advances', 'get_hsn_summary': 'HSN Summary of Outward supply'})
        # wb.loc['Total'] = wb.sum(numeric_only=True, axis=0)


        df_summary = pd.DataFrame(get_summary["data"], index=[
                                  "count", "taxable_value", "igst_amount", "cgst_amount", "sgst_amount", "tax_amount", "before_gst"])
        df_summary = df_summary.rename(index={'count': 'Count', "taxable_value": "Taxable Value", "igst_amount": "IGST",
                                       "cgst_amount": "CGST", "sgst_amount": "SGST", "tax_amount": "Tax amount", "before_gst": "Invoice value"})
        df_summary = df_summary.T
        df_summary = df_summary.reindex({'tax_b2b': 'B2B', 'sez_with_payment': 'B2B-SEZWP', 'sez_without_payment': 'B2B-SEZWOP', 'tax_b2c': 'B2C', 'credit_b2b': 'Credit/ Debit note (Registered)', 'credit_b2c': 'Credit/ Debit note (Unregistered)',
                                        'nil_rated_supplies': 'Nil Rated Supplies', 'advance_received': 'Advance Received', 'adjustment_of_advances': 'Adjustment of Advances', 'get_hsn_summary': 'HSN Summary of Outward supply'})
        df_summary = df_summary.rename(index={'tax_b2b': 'B2B', 'sez_with_payment': 'B2B-SEZWP', 'sez_without_payment': 'B2B-SEZWOP', 'tax_b2c': 'B2C', 'credit_b2b': 'Credit/ Debit note (Registered)', 'credit_b2c': 'Credit/ Debit note (Unregistered)',
                                       'nil_rated_supplies': 'Nil Rated Supplies', 'advance_received': 'Advance Received', 'adjustment_of_advances': 'Adjustment of Advances', 'get_hsn_summary': 'HSN Summary of Outward supply'})
        df_summary.loc['Total'] = df_summary.sum(numeric_only=True, axis=0)
        df_summary.to_excel(writer, sheet_name="Summary")

        # Summary = df_summary.add_worksheet()
        # worksheet2 = df_summary.add_worksheet()
        # Summary.write('A1', 123)
        # df_summary.close()
        # df_summary.move_range("A1:A3", rows=1, cols=0)
        # df_summary.insert_rows(7)
        for key, value in total_data.items():
            if len(value) == 0:
                value = [{'InvoiceNo': None, 'InvoiceDate': None, 'GSTINofSupplier': None, 'LegalName': None, 'InvoiceType': None,
                          'InvoiceAmt': None, 'TotalTaxableAmt': None, 'SGST': None, 'CGST': None, 'IGST': None, 'TotalGST': None, 'CESS': None}]
            df = pd.DataFrame.from_records(value)
            df.to_excel(writer, sheet_name=key, index=False)
        nil_rated = {"Inter state Supplies to Registered person": {"Nil Rated": get_nil_rated["data"]["inter_state_nill_rated_register_person"], "Exempted": get_nil_rated["data"]["inter_state_excempted_register_person"], "Non-GST": get_nil_rated["data"]
                                                                   ["inter_state_nonregister_register_person"]}, "Inter state Supplies to Unregistered person": {"Nil Rated":get_nil_rated["data"]["inter_state_nill_rated_unregister_person"], "Exempted": get_nil_rated["data"]["inter_state_excempted_unregister_person"], "Non-GST": get_nil_rated["data"]["inter_state_nonregister_unregister_person"]}, 
                                                                   "Intra state Supplies to Registered person": {"Nil Rated": get_nil_rated["data"]["intra_state_nill_rated_register_person"], "Exempted": get_nil_rated["data"]["intra_state_excempted_register_person"], "Non-GST": get_nil_rated["data"]["intra_state_nonregister_register_person"]}, 
                                                                   "Intra state Supplies to Unregistered person": {"Nil Rated": get_nil_rated["data"]["intra_state_nill_rated_unregister_person"], "Exempted": get_nil_rated["data"]["intra_state_excempted_unregister_person"], "Non-GST": get_nil_rated["data"]["intra_state_nonregister_unregister_person"]}}
        df1 = pd.DataFrame(nil_rated)
        df1 = df1.T
        df1.loc['Total'] = df1.sum(numeric_only=True)
        df1.to_excel(writer, sheet_name="Nil Rated")
        df2 = pd.DataFrame.from_records(get_hsn_summary["data"])
        df2.loc['Total'] = df2.sum(numeric_only=True)
        df2.to_excel(writer, sheet_name="HSN Summary", index=False)
        writer.save()
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home'}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new, verify=False).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
            return {"success": True, "file_url": file_response["message"]["file_url"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def nil_rated_supplies(month=None, year=None):
    try:
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        company = frappe.get_last_doc("company")
        inter_state_nill_rated_register_person = frappe.db.get_list("Invoices", filters=[["Items", "gst_rate", "=", 0], ["Items", "taxable", "=", "Yes"], ["Invoices", "place_of_supply", "=", company.state_code], [
                                                                    "Invoices", "invoice_type", "=", "B2B"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        inter_state_excempted_register_person = frappe.db.get_list("Invoices", filters=[["Items", "type", "=", "Excempted"], ["Invoices", "sez", "=", 1], ["Invoices", "place_of_supply", "=", company.state_code], [
                                                                   "Invoices", "invoice_type", "=", "B2B"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        inter_state_nonregister_register_person = frappe.db.get_list("Invoices", filters=[["Items", "taxable", "=", "No"], ["Invoices", "place_of_supply", "=", company.state_code], ["Invoices", "invoice_type", "=", "B2B"], [
                                                                     "Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        inter_state_nill_rated_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "gst_rate", "=", 0], ["Items", "taxable", "=", "Yes"], ["Invoices", "place_of_supply", "=", company.state_code], [
                                                                      "Invoices", "invoice_type", "=", "B2C"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        inter_state_excempted_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "type", "=", "Excempted"], ["Invoices", "sez", "=", 1], ["Invoices", "place_of_supply", "=", company.state_code], [
                                                                     "Invoices", "invoice_type", "=", "B2C"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        inter_state_nonregister_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "taxable", "=", "No"], ["Invoices", "place_of_supply", "=", company.state_code], ["Invoices", "invoice_type", "=", "B2C"], [
                                                                       "Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_nill_rated_register_person = frappe.db.get_list("Invoices", filters=[["Items", "gst_rate", "=", 0], ["Items", "taxable", "=", "Yes"], ["Invoices", "place_of_supply", "!=", company.state_code], [
                                                                    "Invoices", "invoice_type", "=", "B2B"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_excempted_register_person = frappe.db.get_list("Invoices", filters=[["Items", "type", "=", "Excempted"], ["Invoices", "sez", "=", 1], ["Invoices", "place_of_supply", "!=", company.state_code], [
                                                                   "Invoices", "invoice_type", "=", "B2B"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_nonregister_register_person = frappe.db.get_list("Invoices", filters=[["Items", "taxable", "=", "No"], ["Invoices", "place_of_supply", "!=", company.state_code], ["Invoices", "invoice_type", "=", "B2B"], [
                                                                     "Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_nill_rated_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "gst_rate", "=", 0], ["Items", "taxable", "=", "Yes"], ["Invoices", "place_of_supply", "!=", company.state_code], [
                                                                      "Invoices", "invoice_type", "=", "B2C"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_excempted_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "type", "=", "Excempted"], ["Invoices", "sez", "=", 1], ["Invoices", "place_of_supply", "!=", company.state_code], [
                                                                     "Invoices", "invoice_type", "=", "B2C"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        intra_state_nonregister_unregister_person = frappe.db.get_list("Invoices", filters=[["Items", "taxable", "=", "No"], ["Invoices", "place_of_supply", "!=", company.state_code], [
                                                                       "Invoices", "invoice_type", "=", "B2C"], ["Invoices", "irn_generated", "=", "Success"], ['invoice_date', 'Between', [start_date, end_date]]], fields=["sum(`tabItems`.item_value_after_gst) as item"])
        data = {"inter_state_nill_rated_register_person": inter_state_nill_rated_register_person[0]["item"] if inter_state_nill_rated_register_person[0]["item"] else 0,
                "inter_state_excempted_register_person": inter_state_excempted_register_person[0]["item"] if inter_state_excempted_register_person[0]["item"] else 0,
                "inter_state_nonregister_register_person": inter_state_nonregister_register_person[0]["item"] if inter_state_nonregister_register_person[0]["item"] else 0,
                "inter_state_nill_rated_unregister_person": inter_state_nill_rated_unregister_person[0]["item"] if inter_state_nill_rated_unregister_person[0]["item"] else 0,
                "inter_state_excempted_unregister_person": inter_state_excempted_unregister_person[0]["item"] if inter_state_excempted_unregister_person[0]["item"] else 0,
                "inter_state_nonregister_unregister_person": inter_state_nonregister_unregister_person[0]["item"] if inter_state_nonregister_unregister_person[0]["item"] else 0,
                "intra_state_nill_rated_register_person": intra_state_nill_rated_register_person[0]["item"] if intra_state_nill_rated_register_person[0]["item"] else 0,
                "intra_state_excempted_register_person": intra_state_excempted_register_person[0]["item"] if intra_state_excempted_register_person[0]["item"] else 0,
                "intra_state_nonregister_register_person": intra_state_nonregister_register_person[0]["item"] if intra_state_nonregister_register_person[0]["item"] else 0,
                "intra_state_nill_rated_unregister_person": intra_state_nill_rated_unregister_person[0]["item"] if intra_state_nill_rated_unregister_person[0]["item"] else 0,
                "intra_state_excempted_unregister_person": intra_state_excempted_unregister_person[0]["item"] if intra_state_excempted_unregister_person[0]["item"] else 0,
                "intra_state_nonregister_unregister_person": intra_state_nonregister_unregister_person[0]["item"] if intra_state_nonregister_unregister_person[0]["item"] else 0
                }
        return {"success": True, "data": data}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def nill_rated_items(month=None, year=None, limit_page_length=20, limit_start=0, Type="All"):
    try:
        count = 0
        if Type == "Non GST":
            filter = "`tabItems`.taxable = 'No'"
        elif Type == "Nil Rated":
            filter = "`tabItems`.gst_rate = 0 and `tabItems`.taxable = 'Yes'"
        elif Type == "Excempted":
            filter = "`tabInvoices`.sez = 1 and `tabItems`.type = 'Excempted'"
        else:
            filter = "((`tabItems`.gst_rate = 0 and `tabItems`.taxable = 'Yes') or (`tabItems`.taxable = 'No') or (`tabInvoices`.sez = 1 and `tabItems`.type = 'Excempted'))"
        nil_rated_supplies = frappe.db.sql("""SELECT invoice_number as 'Invoice_Number', item_name as 'Description', sac_code as 'SAC_Code',`tabItems`.item_value as 'Item_Value', `tabItems`.cgst_amount as CGST, `tabItems`.sgst_amount as SGST, `tabItems`.igst_amount as IGST, item_value_after_gst as 'Total_Value', if(`tabItems`.gst_rate = 0 and `tabItems`.taxable = "Yes", "Nil Rated", if(`tabItems`.taxable = 'No', 'Non GST', if(`tabInvoices`.sez = 1 and `tabItems`.type = "Excempted", "Excempted", ""))) as Type from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where {} and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}' limit {}, {}""".format(filter, year, month, limit_start, limit_page_length), as_dict=1)
        supplies_count = frappe.db.sql(
            """SELECT count(`tabItems`.name) as count from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where {} and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}'""".format(filter, year, month), as_dict=1)
        if len(supplies_count) > 0:
            count = supplies_count[0]["count"]
        return {"success": True, "data": nil_rated_supplies, "count": count}
    except Exception as e:
        print(str(e))
        return {"success": False, "message": str(e)}
