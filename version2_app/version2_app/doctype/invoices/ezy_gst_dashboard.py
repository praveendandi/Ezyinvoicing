from re import T
from webbrowser import get
import datetime
# from attr import fields
# from cv2 import sort
import frappe
import json
import requests
import os
import pandas as pd
import os
import os.path
import sys
import numpy as np
from frappe.utils import data as date_util
from frappe.utils import cstr
import xlsxwriter
import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Color, PatternFill, Font, Fill, colors, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.cell import Cell
# from UliPlot.XLSX import auto_adjust_xlsx_column_width
# from invoice_reconciliations import invoicereconciliationcount
# from xlsxwriter import add_worksheet


@frappe.whitelist(allow_guest=True)
def getGSTR1DashboardDetails(year=None, month=None):
    try:
        get_b2b_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2B' and sez=0 and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_b2b_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, 'credit-debit' as invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice') and `tabInvoices`.irn_generated = 'Success' and sez=0 and invoice_type='B2B' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, 'credit-debit' as invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice') and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_hsn_summary = frappe.db.sql(
            """SELECT count(`tabItems`.parent) as count, (sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount)) as tax_amount, sum(`tabItems`.item_value_after_gst) as before_gst, sum(`tabItems`.item_taxable_value) as taxable_value, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount, 'hsn-summary' as invoice_category, 0 as other_charges from `tabItems` INNER JOIN `tabInvoices` ON `tabItems`.parent = `tabInvoices`.invoice_number where `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format(year, month), as_dict=1)
        nil_rated_supplies = frappe.db.sql("""SELECT count(`tabItems`.name) as count, sum(item_taxable_value) as taxable_value, sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount) as tax_amount, sum(item_value_after_gst) as before_gst, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount,'Nil Rated Supplies' as invoice_type, 0 as other_charges from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where ((`tabItems`.gst_rate = 0 and `tabItems`.taxable = "Yes") or (`tabItems`.taxable = "No") or (`tabInvoices`.sez = 1 and `tabItems`.type = "Excempted")) and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}'""".format(year, month), as_dict=1)
        get_sez_SEZWP = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where sez = 1 and invoice_type='B2B' and suptyp = 'SEZWP' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_sez_SEZWOP = frappe.db.sql(
            """SELECT count(name) as count, round(sum(total_gst_amount),2) as tax_amount, round(sum(pms_invoice_summary_without_gst)+sum(total_central_cess_amount)+sum(total_state_cess_amount),2) as taxable_value, round(sum(sales_amount_after_tax),2) as before_gst, round(sum(igst_amount),2) as igst_amount, round(sum(cgst_amount),2) as cgst_amount, round(sum(sgst_amount),2) as sgst_amount, invoice_category, '{}' as invoice_type, sum(other_charges) as other_charges from `tabInvoices` where sez = 1 and invoice_type='B2B' and suptyp = 'SEZWOP' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)

        advance_received = {"count": 0, "tax_amount": 0, "before_gst": 0,
                            "taxable_value": 0, "igst_amount": 0, "cgst_amount": 0, "sgst_amount": 0, "invoice_category": "advance-received","other_charges":0}
        adjustment_of_advances = {"count": 0, "tax_amount": 0, "before_gst": 0,
                                  "taxable_value": 0, "igst_amount": 0, "cgst_amount": 0, "sgst_amount": 0, "invoice_category": "adjustment-of-advances","other_charges":0}
        total_data = {"tax_b2b": {k: (0 if v is None else v) for k, v in get_b2b_tax_invoice_summaries[0].items()},
                      "sez_with_payment": {k: (0 if v is None else v) for k, v in get_sez_SEZWP[0].items()},
                      "sez_without_payment": {k: (0 if v is None else v) for k, v in get_sez_SEZWOP[0].items()},
                      "tax_b2c": {k: (0 if v is None else v) for k, v in get_b2c_tax_invoice_summaries[0].items()},
                      "credit_b2b": {k: (0 if v is None else v) for k, v in get_b2b_credit_debit_invoice_summaries[0].items()},
                      "credit_b2c": {k: (0 if v is None else v) for k, v in get_b2c_credit_debit_invoice_summaries[0].items()},
                      "nil_rated_supplies": {k: (0 if v is None else v) for k, v in nil_rated_supplies[0].items()},
                      "advance_received": advance_received,
                      "adjustment_of_advances": adjustment_of_advances,
                      "get_hsn_summary": {k: (0 if v is None else v) for k, v in get_hsn_summary[0].items()}}
        return {"success": True, "data": total_data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("getGSTR1DashboardDetails",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def getInvoices(filters=[], limit_page_length=20, limit_start=0, month=None, year=None, export=False):
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        start_date = year+'-'+month+"-01"
        end_date = str(date_util.get_last_day(start_date))
        filters = filters + \
            [['invoice_date', 'between', [start_date, end_date]],
                ["irn_generated", "=", "Success"]]

        invoice_summary = frappe.db.get_list("Invoices", filters=filters, fields=['COUNT(DISTINCT(gst_number)) as no_of_suppliers', 'COUNT(DISTINCT(name)) as no_of_invoices', 'SUM(pms_invoice_summary_without_gst) as total_taxable_value',
                                                                                  'SUM(total_gst_amount) as total_gst_amount', 'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst',
                                                                                  'SUM(cgst_amount) as total_cgst', '(sum(total_central_cess_amount+total_state_cess_amount)) as cess'])
        if export == False:
            invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=[
                '*'], start=int(limit_start), page_length=int(limit_page_length))
        else:
            invoice_data = frappe.db.get_list(
                "Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'DATE_FORMAT(invoice_date, "%d-%m-%Y") as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt', 'pms_invoice_summary_without_gst as BaseAmt','other_charges as OtherCharges','sgst_amount as SGST', 'cgst_amount as CGST', 'igst_amount as IGST', 'total_gst_amount as TotalGST', '(total_central_cess_amount+total_state_cess_amount) as CESS'])
        return {"success": True, "data": invoice_data, "summary": invoice_summary[0]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("getInvoices", "line No:{}\n{}".format(
            exc_tb.tb_lineno, str(e)))
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("getGSTR1ReconciliationSummaryCount",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
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
                """SELECT `tabItems`.sac_code as Sac_Code, `tabItems`.gst_rate as Gst_Rate, `tabItems`.unit_of_measurement_description as UQC, `tabItems`.quantity as total_quantity, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.state_cess_amount) as state_cess_amount,sum(`tabItems`.cess_amount) as central_cess_amount, (sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount)) as total_gst, sum(`tabItems`.item_value) as total_tax_amount, sum(`tabItems`.item_value_after_gst) as total_amount from `tabItems` INNER JOIN `tabInvoices` ON `tabItems`.parent = `tabInvoices`.invoice_number where `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}{} GROUP BY `tabItems`.sac_code, `tabItems`.gst_rate""".format(year, month, sql_filters), as_dict=1)
        else:
            get_hsn_summary = frappe.db.sql(
                """SELECT `tabItems`.sac_code as Sac_Code, `tabItems`.gst_rate as Gst_Rate, `tabItems`.unit_of_measurement_description as UQC, `tabItems`.quantity as total_quantity, sum(`tabItems`.cgst_amount) as cgst_amount, sum(`tabItems`.sgst_amount) as sgst_amount, sum(`tabItems`.igst_amount) as igst_amount, sum(`tabItems`.state_cess_amount) as state_cess_amount,sum(`tabItems`.cess_amount) as central_cess_amount, (sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount)) as total_gst, sum(`tabItems`.item_value) as total_tax_amount, sum(`tabItems`.item_value_after_gst) as total_amount from `tabItems` INNER JOIN `tabInvoices` ON `tabItems`.parent = `tabInvoices`.invoice_number where `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={} GROUP BY `tabItems`.sac_code, `tabItems`.gst_rate""".format(year, month), as_dict=1)
        return {"success": True, "data": get_hsn_summary}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("getHsnSummary", "line No:{}\n{}".format(
            exc_tb.tb_lineno, str(e)))
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
                                          "sales_amount_before_tax as TatalTaxableAmount", "other_charges as OtherChanges","cgst_amount as CGST", "sgst_amount as SGST", "igst_amount as IGST", "total_gst_amount as TotalGST", "(total_central_cess_amount+total_state_cess_amount) as CESS", "ack_date as EInvoiceGenerationDate"], order_by='invoice_number asc')
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("export_invoices", "line No:{}\n{}".format(
            exc_tb.tb_lineno, str(e)))
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
        df = pd.DataFrame(get_summary["data"])
        print(get_summary["data"],"////////")
        df = df.T
        df1 = df.rename(index={'tax_b2b': 'B2B', 'sez_with_payment': 'B2B-SEZWP', 'sez_without_payment': 'B2B-SEZWOP', 'tax_b2c': 'B2C', 'credit_b2b': 'Credit/ Debit note (Registered)', 'credit_b2c': 'Credit/ Debit note (Unregistered)',
                               'nil_rated_supplies': 'Nil Rated Supplies', 'advance_received': 'Advance Received', 'adjustment_of_advances': 'Adjustment of Advances'})
        update_df = df1.drop('get_hsn_summary')
        total = update_df.sum()
        total.name = "Total"
        df1 = update_df.append(total.transpose())
        df2 = df1.append(pd.Series(get_summary["data"]["get_hsn_summary"], index=df1.columns, name='HSN Summary of Outward supply'))
        df3 = df2.append(pd.Series(get_summary["data"]["nil_rated_supplies"], index=df2.columns, name='Nil-Rated-Supplies'))
        df4 = df3[10:12]
        total2 = df4.sum()
        total2.name = "Total2"
        df5 = df3.append(total2.transpose())
        # df4 = df3[17:][['before_gst', 'taxable_value','igst_amount','cgst_amount','sgst_amount','tax_amount','other_charges']]
        # total = df4.sum()
        # total.name = "Total"
        # df5 = df4.append(total.transpose())
        # total = df3.iloc['get_hsn_summary','nil_rated_supplies'].sum()
        # cols = ['before_gst','taxable_value','igst_amount','cgst_amount','sgst_amount','tax_amount','other_charges']
        # df['sum'] = df.loc[0:3, cols].sum(axis=1)
        # print(total,"//////")
        summary_data = df5.to_dict('index')
        get_hsn_summary = getHsnSummary(month=month, year=year, export=True)
        if not get_hsn_summary["success"]:
            return get_hsn_summary
        get_nil_rated = nil_rated_supplies(month=month, year=year)
        if not get_nil_rated["success"]:
            return get_nil_rated
        get_count_sequence = document_sequence(month=month, year=year)
        if not get_count_sequence["success"]:
            return get_count_sequence
        filter_list = {"B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["sez", "=", 0]], "B2B-SEZWP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["sez", "=", 1], ["suptyp", "=", "SEZWP"]], "B2B-SEZWOP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["sez", "=", 1], ["suptyp", "=", "SEZWOP"]], "B2C": [["invoice_type", "=", "B2C", ]], "Credit-Debit-B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "in", ["Debit Invoice", "Credit Invoice"]], ["sez", "=", 0]], "Credit-Debit-B2C": [["invoice_type", "=", "B2C"], [
            "invoice_category", "in", ["Debit Invoice", "Credit Invoice"]]]}
        for key, value in filter_list.items():
            get_invoices_data = getInvoices(
                filters=value, month=month, year=year, export=True)
            if not get_invoices_data["success"]:
                return get_invoices_data
            total_data.update({key: get_invoices_data["data"]})
        # dataframe = pd.read_excel()
        wb = Workbook()
        ws = wb.active
        ws = wb.create_sheet("Summary")
        ws.title = "Summary"
        ws.move_range("A1:A5", rows=1, cols=0)
        fields = ['before_gst', 'taxable_value', 'igst_amount',
                  'cgst_amount', 'sgst_amount', 'tax_amount', 'other_charges']
        ws.append(["Particulars", "Invoice value", "Taxable value",
                   "IGST", "CGST", "SGST", "TOTAL TAX LIABILITY", "Other Charges"])
        for key, value in summary_data.items():
            values = (value[k] for k in fields)
            values = list(values)
            values.insert(0, key)
            ws.append(values)
        # ws.move_range("A6:A17", rows=0, cols=0)
        for i in range(ws.min_row, ws.max_row):
            ws.row_dimensions[i].height = 15
        for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            ws.column_dimensions[i].width = 30
        font = Font(name='Cambria', size=12, bold=True, color='00FFFFFF')
        blueFill = PatternFill(start_color='0B0B45',
                               end_color='0B0B45', fill_type='solid')
        number_format = "#,##0"
        alignment = Alignment(horizontal='center', vertical='top')
        border = Border(left=Side(border_style='thin', color='00000000'), right=Side(border_style='thin', color='00000000'), top=Side(border_style='thin', color='00000000'),
                        bottom=Side(border_style='thin', color='00000000'), diagonal=Side(border_style='thin', color='00000000'), diagonal_direction=0, outline=Side(border_style='thin', color='00000000'),
                        vertical=Side(border_style='thin', color='00000000'), horizontal=Side(border_style='thin', color='00000000'))
        cols = ['A', 'B', 'C']
        for col in cols:
            for i in range(2, 5):
                cols = ws[f'{col}{i}']
                cols.fill = blueFill
                cols.font = font
                cols.border = border
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for col in cols:
            cols = ws[f'{col}6']
            cols.fill = blueFill
            cols.font = font
            cols.alignment = alignment
            cols.border = border
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for col in cols:
            for i in range(7, 20):
                cols = ws[f'{col}{i}']
                cols.number_format = number_format
                cols.font = Font(name='Cambria', size=12)
                cols.border = border
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for col in cols:
            for i in [16,19]:
                cols = ws[f'{col}{i}']
                cols.font = Font(bold=True)
        ws = wb.worksheets[1]
        ws['A2'] = 'GST Number : '+company.gst_number
        ws['A3'] = 'Name of the client : '+company.legal_name
        ws['A4'] = "GSTR-1 Summary for the period {} {}".format(
            month_name, year)
        invoice_fields = ['InvoiceNo', 'InvoiceDate', 'GSTINofSupplier', 'LegalName', 'InvoiceType',
                          'InvoiceAmt', 'BaseAmt', 'OtherCharges','SGST', 'CGST', 'IGST', 'TotalGST', 'CESS']
        for key, value in total_data.items():
            ws = wb.create_sheet(key)
            ws.title = key
            for i in ['A', 'B', 'C', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
                ws.column_dimensions[i].width = 20
            ws.column_dimensions['D'].width = 60
            ws.append(['Invoice No', 'Invoice Date', 'GSTIN of Supplier', 'Legal Name', 'Invoice Type',
                      'Invoice Amt', 'Base Amt', 'OtherCharges','SGST', 'CGST', 'IGST', 'TotalGST', 'CESS'])
            if len(value) == 0:
                value = [{'InvoiceNo': None, 'InvoiceDate': None, 'GSTINofSupplier': None, 'LegalName': None, 'InvoiceType': None,
                          'InvoiceAmt': None, 'BaseAmt': None, 'OtherCharges': None,'SGST': None, 'CGST': None, 'IGST': None, 'TotalGST': None, 'CESS': None}]
            else:
                invoices_df = pd.DataFrame.from_records(value)
                total = invoices_df.sum(numeric_only=True, axis=0)
                total.name = "Total"
                invoices_df = invoices_df.append(total.transpose())
                invoices_df['InvoiceNo'] = invoices_df['InvoiceNo'].replace(
                    np.nan, "Total")
                value = invoices_df.to_dict('records')
            for product in value:
                values = (product[k] for k in invoice_fields)
                ws.append(values)
            if ws.max_row > 2:
                for cell in ws[str(ws.max_row)+":"+str(ws.max_row)]:
                    cell.font = Font(bold=True)

            # df = pd.DataFrame.from_records(value)
        nil_rated = {"Inter state Supplies to Registered person": {"Nil Rated": get_nil_rated["data"]["inter_state_nill_rated_register_person"], "Exempted": get_nil_rated["data"]["inter_state_excempted_register_person"], "Non-GST": get_nil_rated["data"]
                                                                   ["inter_state_nonregister_register_person"]}, "Inter state Supplies to Unregistered person": {"Nil Rated": get_nil_rated["data"]["inter_state_nill_rated_unregister_person"], "Exempted": get_nil_rated["data"]["inter_state_excempted_unregister_person"], "Non-GST": get_nil_rated["data"]["inter_state_nonregister_unregister_person"]},
                     "Intra state Supplies to Registered person": {"Nil Rated": get_nil_rated["data"]["intra_state_nill_rated_register_person"], "Exempted": get_nil_rated["data"]["intra_state_excempted_register_person"], "Non-GST": get_nil_rated["data"]["intra_state_nonregister_register_person"]},
                     "Intra state Supplies to Unregistered person": {"Nil Rated": get_nil_rated["data"]["intra_state_nill_rated_unregister_person"], "Exempted": get_nil_rated["data"]["intra_state_excempted_unregister_person"], "Non-GST": get_nil_rated["data"]["intra_state_nonregister_unregister_person"]}}
        ws = wb.create_sheet("Nil Rated")
        ws.title = "Nil Rated"
        ws.column_dimensions["A"].width = 40
        for i in ['B', 'C', 'D']:
            ws.column_dimensions[i].width = 20
        nilrated_fields = ["Nil Rated", "Exempted", "Non-GST"]
        ws.append(["", "Nil Rated", "Exempted", "Non-GST"])
        nil_rated_df = pd.DataFrame(nil_rated)
        nil_rated_df = nil_rated_df.T
        total = nil_rated_df.sum(numeric_only=True, axis=0)
        total.name = "Total"
        nil_rated_df = nil_rated_df.append(total.transpose())
        nil_rated_list = nil_rated_df.to_dict('index')
        for key, value in nil_rated_list.items():
            values = (value[k] for k in nilrated_fields)
            values = list(values)
            values.insert(0, key)
            ws.append(values)
        for cell in ws[str(ws.max_row)+":"+str(ws.max_row)]:
            cell.font = Font(bold=True)
        hsn_fields = ['Sac_Code', "Gst_Rate", "UQC", "total_quantity", "cgst_amount", "sgst_amount", "igst_amount",
                      "state_cess_amount", "central_cess_amount", "total_gst", "total_tax_amount", "total_amount"]
        ws = wb.create_sheet("HSN_Summary")
        ws.title = "HSN_Summary"
        for i in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
            ws.column_dimensions[i].width = 15
        ws.append(["SAC Code", "Gst Rate", "UQC", "Total Quantity", "Cgst Amount", "Sgst Amount", "Igst Amount",
                  "State Cess Amount", "Central Cess Amount", "Total Gst", "Total Tax Amount", "Total Amount"])
        hsn_summary_df = pd.DataFrame.from_records(get_hsn_summary["data"])
        total = hsn_summary_df.sum(numeric_only=True, axis=0)
        total.name = "Total"
        hsn_summary_df = hsn_summary_df.append(total.transpose())
        print(len(hsn_summary_df))
        # hsn_summary_df['Sac_Code'] = hsn_summary_df['Sac_Code'].replace(
        #     np.nan, "Total")
        # invoices_df['InvoiceNo'] = invoices_df['InvoiceNo'].replace(
        #             np.nan, "Total")
        hsn_summary = hsn_summary_df.to_dict('records')
        for product in hsn_summary:
            values = (product[k] for k in hsn_fields)
            ws.append(values)
        for cell in ws[str(ws.max_row)+":"+str(ws.max_row)]:
            cell.font = Font(bold=True)
        if len(hsn_summary_df) > 1:
            ws.cell(row=ws.max_row, column=2).value = ""
            ws.cell(row=ws.max_row, column=1).value = "Total"
        # ws = wb.create_sheet("Sequence")
        # ws.title = "Sequence"
        # for i in ['A', 'B', 'C', 'D', 'E']:
        #     ws.column_dimensions[i].width = 15
        # # print(get_count_sequence["data"])
        # ws.append(["Document","From","To","Success","Cancelled", "Error"])
        # document_fields = ["Document","From","To","Success","Cancelled", "Error"]
        # sequence_count = [{"Document":"Tax Invoice", "From":get_count_sequence["data"]["tax_invoice_from"], "To":get_count_sequence["data"]["tax_invoice_to"], "Success":get_count_sequence["data"]["tax_invoice_success_count"], "Cancelled":get_count_sequence["data"]["tax_invoice_cancelled_count"], "Error":get_count_sequence["data"]["tax_invoice_error_count"]},{"Document":"Credit Invoice", "From":get_count_sequence["data"]["credit_invoice_from"], "To":get_count_sequence["data"]["credit_invoice_to"], "Success":get_count_sequence["data"]["credit_invoice_success_count"], "Cancelled":get_count_sequence["data"]["credit_invoice_cancelled_count"], "Error":get_count_sequence["data"]["credit_invoice_error_count"]}]
        # for product in sequence_count:
        #     values = (product[k] for k in document_fields)
        #     ws.append(values)
        Sheet = wb['Sheet']
        wb.remove(Sheet)
        wb.save(file_path)
        # return True
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home'}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new, verify=False).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
            return {"success": True, "file_url": file_response["message"]["file_url"]}
        return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("export_workbook", "line No:{}\n{}".format(
            exc_tb.tb_lineno, str(e)))
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("nil_rated_supplies",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("nill_rated_items",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def document_sequence(month=None, year=None):
    try:
        data = {}
        start_date = year+'-'+month+"-01"
        end_date = date_util.get_last_day(start_date)
        invoice_filters = {"tax_invoice_success_count": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "TAX INVOICE"], ["irn_generated", "=", "Success"]], "tax_invoice_cancelled_count": [["invoice_date", 'between', [start_date, end_date]], [
            "invoice_category", "=", "TAX INVOICE"], ["irn_generated", "=", "Cancelled"]], "tax_invoice_error_count": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "TAX INVOICE"], ["irn_generated", "=", "Error"]], "credit_invoice_success_count": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "CREDIT INVOICE"], ["irn_generated", "=", "Success"]], "credit_invoice_cancelled_count": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "CREDIT INVOICE"], ["irn_generated", "=", "Cancelled"]], "credit_invoice_error_count": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "CREDIT INVOICE"], ["irn_generated", "=", "Error"]]}
        total_invoice_list = []
        if bool(invoice_filters):
            for key, value in invoice_filters.items():
                invoice_numbers = frappe.db.get_list(
                    'Invoices', filters=value, pluck='name')
                data.update({key: len(invoice_numbers)})
                total_invoice_list.extend(invoice_numbers)
        tax_invoice_recon_data = frappe.db.get_list("Invoices", filters=[["invoice_date", 'between', [
                                                    start_date, end_date]], ["invoice_category", "=", "TAX INVOICE"]], pluck='name')
        credit_invoice_recon_data = frappe.db.get_list("Invoices", filters=[["invoice_date", 'between', [
                                                       start_date, end_date]], ["invoice_category", "=", "CREDIT INVOICE"]], pluck='name')
        if len(tax_invoice_recon_data) > 0:
            data["tax_invoice_from"] = min(tax_invoice_recon_data)
            data["tax_invoice_to"] = max(tax_invoice_recon_data)
        else:
            data["tax_invoice_from"] = ""
            data["tax_invoice_to"] = ""
        if len(credit_invoice_recon_data) > 0:
            data["credit_invoice_from"] = min(credit_invoice_recon_data)
            data["credit_invoice_to"] = max(credit_invoice_recon_data)
        else:
            data["credit_invoice_from"] = ""
            data["credit_invoice_to"] = ""
        invoices_list = tax_invoice_recon_data + credit_invoice_recon_data
        d110_total_invoices = frappe.db.get_list("Invoice Reconciliations", filters=[
            ["bill_generation_date", "between", [start_date, end_date]]], pluck="name")
        if len(d110_total_invoices) > 0 and len(invoices_list) > 0:
            data["missing_in_d110"] = list(
                set(invoices_list) - set(d110_total_invoices))
            data["missing_in_ezy_invoicing"] = list(
                set(d110_total_invoices) - set(invoices_list))
        else:
            data["tax_invoice_success_count"] = 0
            data["tax_invoice_cancelled_count"] = 0
            data["tax_invoice_error_count"] = 0
            data["credit_invoice_success_count"] = 0
            data["credit_invoice_cancelled_count"] = 0
            data["credit_invoice_error_count"] = 0
        return {"success": True, "data": data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("document_sequence",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def reconciliation(start_date, end_date):
    try:
        # if isinstance(filters, str):
        #     filters = json.loads(filters)
        company = frappe.get_last_doc("company")
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        month_name = datetime.datetime.strptime(
            start_date, "%Y-%m-%d").strftime("%b")
        # month_name = datetime_object.strftime("%b")
        year_object = datetime.datetime.strptime(
            start_date, "%Y-%m-%d").strftime("%Y")
        file_path = cwd + "/" + site_name + \
            "/public/files/RECON-"+month_name+"-"+year_object+".xlsx"
        missing = get_missing_invoices(start_date, end_date)
        if not missing["success"]:
            return missing
        # return missing
        sequence_data = [{"Ezyinvoicing Count": len(missing["data"]["ezy_invoicing_invoices"]), "Opera Folios Count": len(missing["data"]["opera_folios"]), "Missing In EzyInvoicing": len(missing["data"]["missing_in_ezyinvoicing"]), "Missing In Opera": len(
            missing["data"]["missing_in_opera"]), "Type Missmatch": len(missing["data"]["type_missmatch_for_tax"])+len(missing["data"]["type_missmatch_for_credit"]) if len(missing["data"]["type_missmatch_for_credit"]) > 1 else 0}]
        # Summary of Invoices
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df_summary = pd.DataFrame(sequence_data)
        df_summary.to_excel(writer, sheet_name="Count", index=False)
        for each in ["Ezyinvoicing Count", "Opera Folios Count", "Missing In EzyInvoicing", "Missing In Opera", "Type Missmatch"]:
            col_idx = df_summary.columns.get_loc(each)
            writer.sheets['Count'].set_column(col_idx, col_idx, 20)
        # Missing Invoices In Opera
        missing_in_opera = {
            "Invoices Numbers": missing["data"]["missing_in_opera"]}
        get_missing_in_opera_data = [{"Invoice Number": "", "Invoice Date": "", "Invoice Type": "", "Invoice Category": "", "IRN Status": "", "EzyInvoice Status": "", "Invoice Amount": "", "Taxable Value": "",
                                      "IGST Amount": "", "SGST Amount": "", "CGST Amount": "", "Total Gst Amount": "", "Other Charges": "", "CESS": "", "VAT Amount": "", "IRN Number": "", "Acknowledgement No": "", "Acknowledgement Date": ""}]
        if len(missing["data"]["missing_in_opera"]) > 0:
            # get_missing_in_opera_data = frappe.db.get_list("Invoices", filters=[["name","in",missing["data"]["missing_in_opera"]]],fields=['invoice_number as InvoiceNumber', 'invoice_date as InvoiceDate','invoice_type as InvoiceType', 'invoice_category as InvoiceCategory', 'irn_generated as IRNStatus', 'invoice_from as EzyInvoiceStatus', 'pms_invoice_summary_without_gst as TaxableValue', 'total_gst_amount as TotalGstAmount', 'pms_invoice_summary as InvoicesAmount', 'other_charges as OtherCharges', 'igst_amount as IGSTAmount', 'sgst_amount as SGSTAmount', 'cgst_amount as CGSTAmount', '(total_central_cess_amount+total_state_cess_amount) as CESS','total_vat_amount as VATAmount', 'If(invoice_category!="Credit Invoice",irn_number,credit_irn_number) as IRNNumber', 'ack_no as AcknowledgementNo', 'ack_date as AcknowledgementDate'], order_by='name')
            missing_numbers = tuple(missing["data"]["missing_in_opera"])
            if len(missing_numbers) == 1:
                missing_numbers = missing_numbers + ('0',)
            get_missing_in_opera_data = frappe.db.sql("""select invoice_number as 'Invoice Number', invoice_date as 'Invoice Date',invoice_type as 'Invoice Type', invoice_category as 'Invoice Category', irn_generated as 'IRN Status', invoice_from as 'EzyInvoice Status', pms_invoice_summary as 'Invoice Amount', pms_invoice_summary_without_gst as 'Taxable Value', igst_amount as 'IGST Amount', sgst_amount as 'SGST Amount', cgst_amount as 'CGST Amount', total_gst_amount as 'Total Gst Amount', other_charges as 'Other Charges', (total_central_cess_amount+total_state_cess_amount) as CESS,total_vat_amount as 'VAT Amount', If(invoice_category!="Credit Invoice",irn_number,credit_irn_number) as 'IRN Number',If(invoice_category!="Credit Invoice",ack_no,credit_ack_no) as 'Acknowledgement No',  If(invoice_category!="Credit Invoice",ack_date,credit_ack_date) as 'Acknowledgement Date' from `tabInvoices` where name in {} ORDER BY name""".format(missing_numbers), as_dict=1)
        df_missing_opera_folios_list = pd.DataFrame.from_records(
            get_missing_in_opera_data)
        df_missing_opera_folios_list.to_excel(
            writer, sheet_name="Missing In Opera", index=False)
        for each in ["Invoice Number", "Invoice Date", "Invoice Type", "Invoice Category", "IRN Status", "EzyInvoice Status", "Invoice Amount", "Taxable Value", "IGST Amount", "SGST Amount", "CGST Amount", "Total Gst Amount", "Other Charges", "CESS", "VAT Amount", "IRN Number", "Acknowledgement No", "Acknowledgement Date"]:
            col_idx = df_missing_opera_folios_list.columns.get_loc(each)
            writer.sheets['Missing In Opera'].set_column(col_idx, col_idx, 20)
        # Missing Invoices In Ezyinvoicing
        missing_in_ezy = {
            "Invoices Numbers": missing["data"]["missing_in_ezyinvoicing"]}
        df_missing_ezy_invoicing_list = pd.DataFrame.from_dict(missing_in_ezy)
        df_missing_ezy_invoicing_list.to_excel(
            writer, sheet_name="Missing In EzyInvoicing", index=False)
        for each in ["Invoices Numbers"]:
            col_idx = df_missing_ezy_invoicing_list.columns.get_loc(each)
            writer.sheets['Missing In EzyInvoicing'].set_column(
                col_idx, col_idx, 20)
        # Type Missmatch
        type_missmatch = missing["data"]["type_missmatch_for_tax"] + \
            missing["data"]["type_missmatch_for_credit"]
        df_type_missmatch = pd.DataFrame.from_records(type_missmatch)
        # frappe.db.get_list("Invoices", filters=filters, fields=['SUM(pms_invoice_summary_without_gst) as total_taxable_value', 'SUM(total_gst_amount) as total_gst_amount', 'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst', 'SUM(cgst_amount) as total_cgst', 'SUM(total_central_cess_amount+total_state_cess_amount) as cess'])
        # gst_invoice_list = frappe.db.get_list(
        #     "Missing In Opera", filters=[["invoice_number", "in", missing_in_opera]], as_list=1)
        df_type_missmatch.to_excel(
            writer, sheet_name="Invoice Type Missmatch", index=False)
        for each in ["InvoiceNumber", "Ezyinvoicing", "Opera"]:
            col_idx = df_type_missmatch.columns.get_loc(each)
            writer.sheets['Invoice Type Missmatch'].set_column(
                col_idx, col_idx, 20)
        # auto_adjust_xlsx_column_width(
        #     df_type_missmatch, writer, sheet_name="Invoice Type Missmatch", margin=0)
        comparing = invoices_summary(start_date, end_date)
        if not comparing["success"]:
            return comparing
        df_comparing_totals = pd.DataFrame.from_records(comparing["data"])
        df_comparing_totals.to_excel(
            writer, sheet_name="Ezy Invoicing Summary", index=False)
        for each in ["BeforeTax", "CGST", "SGST", "IGST", "TotalInvoiceAmount"]:
            col_idx = df_comparing_totals.columns.get_loc(each)
            writer.sheets['Ezy Invoicing Summary'].set_column(
                col_idx, col_idx, 20)
        invoice_comparison = compare_invoice_summary(start_date, end_date)
        if not invoice_comparison["success"]:
            return invoice_comparison
        df_invoice_comparison = pd.DataFrame.from_records(
            invoice_comparison["data"])
        df_invoice_comparison = df_invoice_comparison.reindex(columns=["InvoiceNumber", "EzyinvoicingBaseAmount", "OperaBaseAmount", "BaseMissmatchAmount", "BaseAmountStatus", "EzyinvoicingInvoiceAmount",
                                                              "OperaInvoiceAmount", "InvoiceMissmatchAmount", "InvoiceAmountStatus", "MissingIn", "IRN Status", "IRN Number", "Acknowledgement No", "Acknowledgement Date"])
        df_invoice_comparison.to_excel(
            writer, sheet_name="Comparison", index=False)
        for each in ["InvoiceNumber", "EzyinvoicingBaseAmount", "OperaBaseAmount", "BaseMissmatchAmount", "BaseAmountStatus", "EzyinvoicingInvoiceAmount", "OperaInvoiceAmount", "InvoiceMissmatchAmount", "InvoiceAmountStatus", "MissingIn", "IRN Status", "IRN Number", "Acknowledgement No", "Acknowledgement Date"]:
            col_idx = df_invoice_comparison.columns.get_loc(each)
            writer.sheets['Comparison'].set_column(col_idx, col_idx, 25)
        df_b2b_to_b2c = pd.DataFrame.from_records(
            missing["data"]["converted_b2b_to_b2c"])
        df_b2b_to_b2c.to_excel(
            writer, sheet_name="Converted B2B to B2C", index=False)
        for each in ["InvoiceNumber", "InvoiceUploadType"]:
            col_idx = df_b2b_to_b2c.columns.get_loc(each)
            writer.sheets['Converted B2B to B2C'].set_column(
                col_idx, col_idx, 20)
        df_b2c_to_b2b = pd.DataFrame.from_records(
            missing["data"]["converted_b2c_to_b2b"])
        df_b2c_to_b2b.to_excel(
            writer, sheet_name="Converted B2C to B2B", index=False)
        for each in ["InvoiceNumber", "InvoiceUploadType"]:
            col_idx = df_b2c_to_b2b.columns.get_loc(each)
            writer.sheets['Converted B2C to B2B'].set_column(
                col_idx, col_idx, 20)
        writer.save()
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home'}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new, verify=False).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
            return {"success": True, "file_url": file_response["message"]["file_url"], "file_name": "RECON-"+month_name+"-"+year_object+".xlsx"}
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("document_sequence",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


# def get_missing_invoices(month=None, year=None):
#     try:
#         data = {}
#         start_date = year+'-'+month+"-01"
#         end_date = date_util.get_last_day(start_date)
#         invoice_filters = {"tax_invoices_in_ezyinvoicing": [["invoice_date", 'between', [start_date, end_date]], [
#             "invoice_category", "=", "Tax Invoice"]], "credit_invoices_in_ezyinvoicing": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "Credit Invoice"]]}
#         for key, value in invoice_filters.items():
#             ezy_invoicing_invoices = frappe.db.get_list(
#                 'Invoices', filters=value, pluck='name', order_by='name')
#             data.update({key: ezy_invoicing_invoices})
#         opera_folios_filters = {"opera_tax_folios": [["bill_generation_date", "between", [start_date, end_date]], [
#             "folio_type", "=", "TAX INVOICE"]], "opera_credit_folios": [["bill_generation_date", "between", [start_date, end_date]], ["folio_type", "=", "CREDIT INVOICE"]]}
#         for key, value in opera_folios_filters.items():
#             opera_folios = frappe.db.get_list(
#                 "Invoice Reconciliations", filters=value, pluck="name", order_by='name')
#             data.update({key: opera_folios})
#         data["type_missmatch_for_tax"] = frappe.db.get_list('Invoices', filters=[["name", "in", data["opera_tax_folios"]], [
#                                                             "invoice_category", "!=", "Tax Invoice"]], fields=['name as InvoiceNumber',"invoice_category as Ezyinvoicing"], order_by='name', as_list=False)
#         data["type_missmatch_for_credit"] = frappe.db.get_list('Invoices', filters=[["name", "in", data["opera_credit_folios"]], [
#                                                                "invoice_category", "!=", "Credit Invoice"]], fields=['name as InvoiceNumber',"invoice_category as Ezyinvoicing"], order_by='name', as_list=False)
#         if len(data["type_missmatch_for_credit"])>0:
#             data["type_missmatch_for_credit"] = [dict(item, **{'Opera':'Credit Invoice'}) for item in data["type_missmatch_for_credit"]]
#         else:
#             data["type_missmatch_for_credit"] = [{"InvoiceNumber":"","Ezyinvoicing":"","Opera":""}]
#         if len(data["type_missmatch_for_tax"])>0:
#             data["type_missmatch_for_tax"] = [dict(item, **{'Opera':'Tax Invoice'}) for item in data["type_missmatch_for_tax"]]
#         data["missing_count_tax_invoices"] = list(
#             set(data["tax_invoices_in_ezyinvoicing"]) ^ set(data["opera_tax_folios"]))
#         data["missing_count_credit_invoices"] = list(
#             set(data["credit_invoices_in_ezyinvoicing"]) ^ set(data["opera_credit_folios"]))
#         data["missing_tax_opera"] = list(
#             set(data["tax_invoices_in_ezyinvoicing"]) - set(data["opera_tax_folios"]))
#         data["missing_credit_opera"] = list(
#             set(data["credit_invoices_in_ezyinvoicing"]) - set(data["opera_credit_folios"]))
#         data["missing_tax_ezyinvoicing"] = list(
#             set(data["opera_tax_folios"]) - set(data["tax_invoices_in_ezyinvoicing"]))
#         data["missing_credit_ezyinvoicing"] = list(
#             set(data["opera_credit_folios"]) - set(data["credit_invoices_in_ezyinvoicing"]))
#         data["converted_b2b_to_b2c"] = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]],["converted_from_b2b","=","Yes"]], fields=['name as InvoiceNumber',"invoice_from as InvoiceUploadType"], order_by='name')
#         if len(data["converted_b2b_to_b2c"])==0:
#             data["converted_b2b_to_b2c"] = [{"InvoiceNumber":"", "InvoiceUploadType":""}]
#         data["converted_b2c_to_b2b"] = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]],["converted_from_b2c","=","Yes"]], fields=['name as InvoiceNumber',"invoice_from as InvoiceUploadType"], order_by='name')
#         if len(data["converted_b2c_to_b2b"])==0:
#             data["converted_b2c_to_b2b"] = [{"InvoiceNumber":"", "InvoiceUploadType":""}]
#         return {"success": True, "data": data}
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         frappe.log_error("get_missing_invoices",
#                          "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
#         return {"success": False, "message": str(e)}

def get_missing_invoices(start_date, end_date):
    try:
        data = {}
        invoice_filters = {"tax_invoices_in_ezyinvoicing": [["invoice_date", 'between', [start_date, end_date]], [
            "invoice_category", "=", "Tax Invoice"]], "credit_invoices_in_ezyinvoicing": [["invoice_date", 'between', [start_date, end_date]], ["invoice_category", "=", "Credit Invoice"]]}
        for key, value in invoice_filters.items():
            ezy_invoicing_invoices = frappe.db.get_list(
                'Invoices', filters=value, pluck='name', order_by='name')
            data.update({key: ezy_invoicing_invoices})
        opera_folios_filters = {"opera_tax_folios": [["bill_generation_date", "between", [start_date, end_date]], [
            "folio_type", "=", "TAX INVOICE"]], "opera_credit_folios": [["bill_generation_date", "between", [start_date, end_date]], ["folio_type", "=", "CREDIT INVOICE"]]}
        for key, value in opera_folios_filters.items():
            opera_folios = frappe.db.get_list(
                "Invoice Reconciliations", filters=value, pluck="name", order_by='name')
            data.update({key: opera_folios})
        data["ezy_invoicing_invoices"] = frappe.db.get_list('Invoices', filters=[
                                                            ["invoice_date", 'between', [start_date, end_date]]], pluck='name', order_by='name')
        data["opera_folios"] = frappe.db.get_list("Invoice Reconciliations", filters=[
                                                  ["bill_generation_date", "between", [start_date, end_date]]], pluck="name", order_by='name')
        data["type_missmatch_for_tax"] = frappe.db.get_list('Invoices', filters=[["name", "in", data["opera_tax_folios"]], [
                                                            "invoice_category", "!=", "Tax Invoice"]], fields=['name as InvoiceNumber', "invoice_category as Ezyinvoicing"], order_by='name', as_list=False)
        data["type_missmatch_for_credit"] = frappe.db.get_list('Invoices', filters=[["name", "in", data["opera_credit_folios"]], [
                                                               "invoice_category", "!=", "Credit Invoice"]], fields=['name as InvoiceNumber', "invoice_category as Ezyinvoicing"], order_by='name', as_list=False)
        if len(data["type_missmatch_for_credit"]) > 0:
            data["type_missmatch_for_credit"] = [dict(
                item, **{'Opera': 'Credit Invoice'}) for item in data["type_missmatch_for_credit"]]
        else:
            data["type_missmatch_for_credit"] = [
                {"InvoiceNumber": "", "Ezyinvoicing": "", "Opera": ""}]
        if len(data["type_missmatch_for_tax"]) > 0:
            data["type_missmatch_for_tax"] = [dict(
                item, **{'Opera': 'Tax Invoice'}) for item in data["type_missmatch_for_tax"]]
        data["missing_in_opera"] = list(
            set(data["ezy_invoicing_invoices"]) - set(data["opera_folios"]))
        data["missing_in_ezyinvoicing"] = list(
            set(data["opera_folios"]) - set(data["ezy_invoicing_invoices"]))
        data["converted_b2b_to_b2c"] = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]], [
                                                          "converted_from_b2b", "=", "Yes"]], fields=['name as InvoiceNumber', "invoice_from as InvoiceUploadType"], order_by='name')
        if len(data["converted_b2b_to_b2c"]) == 0:
            data["converted_b2b_to_b2c"] = [
                {"InvoiceNumber": "", "InvoiceUploadType": ""}]
        data["converted_b2c_to_b2b"] = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]], [
                                                          "converted_from_b2c", "=", "Yes"]], fields=['name as InvoiceNumber', "invoice_from as InvoiceUploadType"], order_by='name')
        if len(data["converted_b2c_to_b2b"]) == 0:
            data["converted_b2c_to_b2b"] = [
                {"InvoiceNumber": "", "InvoiceUploadType": ""}]
        return {"success": True, "data": data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_missing_invoices",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def invoices_summary(start_date, end_date):
    try:
        ezy_invoicing_invoices = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]]], fields=[
                                                    "sum(sales_amount_before_tax) as BeforeTax", "sum(cgst_amount) as CGST", "sum(sgst_amount) as SGST", "sum(igst_amount) as IGST", "sum(sales_amount_after_tax) as TotalInvoiceAmount"], order_by='name')
        return {"success": True, "data": ezy_invoicing_invoices}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("invoices_summary",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def compare_invoice_summary(start_date, end_date):
    try:
        get_invoices = frappe.db.get_list('Invoices', filters=[["invoice_date", 'between', [start_date, end_date]]], fields=[
                                          "name as InvoiceNumber", "(sales_amount_before_tax+total_central_cess_amount+total_state_cess_amount+total_credit_vat_amount) as EzyinvoicingBaseAmount", "sales_amount_after_tax as EzyinvoicingInvoiceAmount"], order_by='name')
        get_payments = frappe.db.get_list("Payment Types", pluck="name")
        if len(get_invoices) > 0:
            for each in get_invoices:
                get_folios = frappe.db.get_value("Invoice Reconciliations", {"name": each["InvoiceNumber"]}, [
                                                 "name as InvoiceNumber", "total_invoice_amount"], order_by='name', as_dict=True)
                if get_folios:
                    each["OperaInvoiceAmount"] = get_folios["total_invoice_amount"]
                    each["InvoiceMissmatchAmount"] = round(
                        each["EzyinvoicingInvoiceAmount"]-get_folios["total_invoice_amount"], 2)
                    if each["InvoiceMissmatchAmount"] > -1 and each["InvoiceMissmatchAmount"] < 1:
                        each["InvoiceAmountStatus"] = "Match"
                    else:
                        each["InvoiceAmountStatus"] = "MisMatch"
                    get_items = frappe.db.get_list("Opera Invoice Items", filters=[["invoice_reconciliations", "=", each["InvoiceNumber"]], [
                                                   "transaction_description", "not in", get_payments]], fields=["sum(debit_amount) as BaseAmount"])
                    if len(get_items) > 0:
                        each["OperaBaseAmount"] = get_items[0]["BaseAmount"] if get_items[0]["BaseAmount"] else 0
                        each["BaseMissmatchAmount"] = round(
                            each["EzyinvoicingBaseAmount"]-each["OperaBaseAmount"], 2)
                        if each["BaseMissmatchAmount"] > -1 and each["BaseMissmatchAmount"] < 1:
                            each["BaseAmountStatus"] = "Match"
                        else:
                            each["BaseAmountStatus"] = "MisMatch"
                    else:
                        each["OperaBaseAmount"] = 0
                    each["MissingIn"] = ""
                else:
                    each.update({"OperaInvoiceAmount": 0, "InvoiceMissmatchAmount": 0, "InvoiceAmountStatus": "",
                                "OperaBaseAmount": 0, "BaseMissmatchAmount": 0, "BaseAmountStatus": "", "MissingIn": "Opera"})
                invoice_columns = frappe.db.sql(
                    """select irn_generated as 'IRN Status',If(invoice_category!="Credit Invoice",irn_number,credit_irn_number) as 'IRN Number',If(invoice_category!="Credit Invoice",ack_no,credit_ack_no) as 'Acknowledgement No',  If(invoice_category!="Credit Invoice",ack_date,credit_ack_date) as 'Acknowledgement Date' from `tabInvoices` where name='{}' ORDER BY name""".format(each["InvoiceNumber"]), as_dict=1)
                if len(invoice_columns) > 0:
                    each.update(invoice_columns[0])
                else:
                    each.update({"IRN Status": "", "IRN Number": "",
                                "Acknowledgement No": "", "Acknowledgement Date": ""})
            return {"success": True, "data": get_invoices}
        else:
            data = [{"InvoiceNumber": "", "EzyinvoicingBaseAmount": "", "EzyinvoicingInvoiceAmount": "", "OperaInvoiceAmount": "", "InvoiceMissmatchAmount": "",
                     "InvoiceAmountStatus": "", "OperaBaseAmount": "", "BaseMissmatchAmount": "", "BaseAmountStatus": "", "MissingIn": ""}]
            return {"success": True, "data": data}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("compare_invoice_summary",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}
