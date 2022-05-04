from webbrowser import get
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
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2B' and sez=0 and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_tax_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_b2b_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice') and `tabInvoices`.irn_generated = 'Success' and invoice_type='B2B' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_b2c_credit_debit_invoice_summaries = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, 'credit-debit' as invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category in ('Credit Invoice','Debit Invoice')  and invoice_type='B2C' and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2C', year, month), as_dict=1)
        get_hsn_summary = frappe.db.sql(
            """SELECT count(`tabSAC HSN Tax Summaries`.parent) as count, sum(`tabSAC HSN Tax Summaries`.cgst+`tabSAC HSN Tax Summaries`.sgst+`tabSAC HSN Tax Summaries`.igst) as tax_amount, sum(`tabSAC HSN Tax Summaries`.amount_before_gst) as before_gst, sum(`tabSAC HSN Tax Summaries`.amount_after_gst) as taxable_value, 'hsn-summary' as invoice_category from `tabSAC HSN Tax Summaries` INNER JOIN `tabInvoices` ON `tabSAC HSN Tax Summaries`.parent = `tabInvoices`.invoice_number where YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format(year, month), as_dict=1)
        nil_rated_supplies = frappe.db.sql("""SELECT count(`tabItems`.name) as count, sum(item_taxable_value) as taxable_value, sum(`tabItems`.cgst_amount)+sum(`tabItems`.sgst_amount)+sum(`tabItems`.igst_amount) as tax_amount, sum(item_value_after_gst) as before_gst, 'Nil Rated Supplies' as invoice_type from `tabInvoices` INNER JOIN `tabItems` ON `tabItems`.parent = `tabInvoices`.name where ((`tabItems`.gst_rate = 0 and `tabItems`.taxable = "Yes") or (`tabItems`.taxable = "No") or (`tabInvoices`.sez = 1 and `tabItems`.type = "Excempted")) and `tabInvoices`.irn_generated = 'Success' and YEAR(invoice_date)='{}' and MONTH(invoice_date)='{}'""".format(year, month), as_dict=1)
        get_sez_SEZWP = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and sez = 1 and suptyp = 'SEZWP' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)
        get_sez_SEZWOP = frappe.db.sql(
            """SELECT count(name) as count, sum(total_gst_amount) as tax_amount, sum(pms_invoice_summary_without_gst) as taxable_value, sum(pms_invoice_summary) as before_gst, invoice_category, '{}' as invoice_type from `tabInvoices` where invoice_category='Tax Invoice' and sez = 1 and suptyp = 'SEZWOP' and YEAR(invoice_date)={} and MONTH(invoice_date)={}""".format('B2B', year, month), as_dict=1)

        advance_received = {"count": 0, "tax_amount": 0, "before_gst": 0,
                            "taxable_value": 0, "invoice_category": "advance-received"}
        adjustment_of_advances = {"count": 0, "tax_amount": 0, "before_gst": 0,
                                  "taxable_value": 0, "invoice_category": "adjustment-of-advances"}
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
            [['invoice_date', 'between', [start_date, end_date]]]
        invoice_summary = frappe.db.get_list("Invoices", filters=filters, fields=['COUNT(DISTINCT(gst_number)) as no_of_suppliers', 'COUNT(DISTINCT(name)) as no_of_invoices', 'SUM(pms_invoice_summary_without_gst) as total_taxable_value',
                                                                                  'SUM(total_gst_amount) as total_gst_amount', 'SUM(pms_invoice_summary) as total_invoices_amount', 'SUM(other_charges) as other_charges', 'SUM(igst_amount) as total_igst', 'SUM(sgst_amount) as total_sgst',
                                                                                  'SUM(cgst_amount) as total_cgst', 'SUM(total_central_cess_amount+total_state_cess_amount) as cess'])
        if export == False:
            invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=[
                '*'], start=int(limit_start), page_length=int(limit_page_length))
        else:
            invoice_data = frappe.db.get_list(
                "Invoices", filters=filters, fields=['invoice_number as InvoiceNo','invoice_date as InvoiceDate','gst_number as GSTINofSupplier','legal_name as LegalName','invoice_type as InvoiceType','amount_after_gst as InvoiceAmt','amount_before_gst as TotalTaxableAmt','sgst_amount as SGST','cgst_amount as CGST','igst_amount as IGST','total_gst_amount as TotalGST','cess_amount as CESS'])
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
            "GSTR One Saved Invoices", filters=[["invoice_number","in",invoice_list]], as_list=1)
        gst_invoice_list = list(sum(gst_invoice_list, ()))
        if any("property" in sublist for sublist in filters):
            miscellaneous_gst_invoice_list = frappe.db.get_list(
                "GSTR One Saved Invoices", filters=[["invoice_number","in",invoice_list]], as_list=1)
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
            [['invoice_date', 'Between', [start_date, end_date]]]
        invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'invoice_date as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt',
                                          "sales_amount_before_tax as TatalTaxableAmount", "cgst_amount as CGST", "sgst_amount as SGST", "igst_amount as IGST", "total_gst_amount as TotalGST", "(total_central_cess_amount+total_state_cess_amount) as CESS", "ack_date as EInvoiceGenerationDate","irn_generated" "=" "Success"], order_by='invoice_number asc')
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
    # try:
        total_data = {}
        get_summary = getGSTR1DashboardDetails(month, year)
        if not get_summary["success"]:
            return get_summary
        total_data["Summary"] = get_summary["data"]
        get_hsn_summary = getHsnSummary(month=month, year=year, export=True)
        if not get_hsn_summary["success"]:
            return get_hsn_summary
        total_data["HSN Summary"] = get_hsn_summary["data"]
        get_nil_rated = nil_rated_supplies(month=month, year=year)
        if not get_nil_rated["success"]:
            return get_nil_rated
        filter_list = {"B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 0]], "B2C": [["invoice_type", "=", "B2C", ], ["irn_generated", "=", "Success"]], "Credit-Debit-B2B": [["invoice_type", "=", "B2B"], ["invoice_category", "in", ["Debit Invoice", "Credit Invoice"]], ["irn_generated", "=", "Success"], ["sez", "=", 0]], "Credit-Debit-B2C": [["invoice_type", "=", "B2C"], [
            "invoice_category", "in", ["Debit Invoice", "Credit Invoice"]], ["irn_generated", "=", "Success"]], "B2B-SEZWP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 1], ["suptyp", "=", "SEZWP"]], "B2B-SEZWOP": [["invoice_type", "=", "B2B"], ["invoice_category", "=", "Tax Invoice"], ["irn_generated", "=", "Success"], ["sez", "=", 1], ["suptyp", "=", "SEZWOP"]]}
        for key,value in filter_list.items():
            get_invoices_data = getInvoices(filters=value, month=month, year=year, export=True)
            if not get_invoices_data["success"]:
                return get_invoices_data
            total_data.update({key: get_invoices_data["data"]})
        writer = pd.ExcelWriter('multiple.xlsx', engine='xlsxwriter')
        for key,value in total_data.items():
            if len(value) == 0:
                value = [{'InvoiceNo': None, 'InvoiceDate': None, 'GSTINofSupplier': None, 'LegalName': None, 'InvoiceType': None, 'InvoiceAmt': None, 'TotalTaxableAmt': None, 'SGST': None, 'CGST': None, 'IGST': None, 'TotalGST': None, 'CESS': None}]
            df = pd.DataFrame.from_records(value)
            df.to_excel(writer, sheet_name=key, index=False)
        df1 = pd.DataFrame(get_nil_rated["data"].items(), columns=[None, 'Values'])
        print(df1)
        df1.to_excel(writer, sheet_name="Nil Rated", index=False)
        writer.save()

        # invoice_data = frappe.db.get_list("Invoices", filters=filters, fields=['invoice_number as InvoiceNo', 'invoice_date as InvoiceDate', 'gst_number as GSTINofSupplier', 'legal_name as LegalName', 'invoice_type as InvoiceType', 'sales_amount_after_tax as InvoiceAmt', "sales_amount_before_tax as TatalTaxableAmount","cgst_amount as CGST", "sgst_amount as SGST", "igst_amount as IGST", "total_gst_amount as TotalGST", "(total_central_cess_amount+total_state_cess_amount) as CESS", "ack_date as EInvoiceGenerationDate"])
        # if len(invoice_data)>0:
        #     company = frappe.get_last_doc("company")
        #     cwd = os.getcwd()
        #     site_name = cstr(frappe.local.site)
        #     file_path = cwd + "/" + site_name + "/public/files/workbook_export.xlsx"
        #     df = pd.DataFrame.from_records(invoice_data)
        #     df.to_excel(file_path, index=False)
        #     files_new = {"file": open(file_path, 'rb')}
        #     payload_new = {'is_private': 1, 'folder': 'Home'}
        #     file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
        #                                 data=payload_new, verify=False).json()
        #     outputxlsx = pd.DataFrame()
        #     for file in file_response:
        #         df = pd.concat(pd.read_excel( file, sheet_name=None), ignore_index=True, sort=False)
        #         outputxlsx = outputxlsx.append( df, ignore_index=True)
        #         outputxlsx.to_excel(cwd + "/" + site_name + "/public/files/workbook_export.xlsx", index=False)
        #     if "file_url" in file["message"].keys():
        #         os.remove(file_path)
        #         return {"success": True, "file_url": file["message"]["file_url"]}
        #     return {"success": False, "message": "something went wrong"}
        # else:
        #     return {"success": False, "message": "no data found"}
    # except Exception as e:
    #     print(str(e))
    #     return {"success": False, "message": str(e)}


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
