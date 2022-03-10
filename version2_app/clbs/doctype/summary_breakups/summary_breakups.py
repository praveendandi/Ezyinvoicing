# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import os
from datetime import datetime, timedelta
# import weasyprint as wp
from pathlib import Path

import frappe
import pandas as pd
import pdfkit
import requests
from frappe.model.document import Document
from frappe.utils import cstr
from weasyprint import HTML

from version2_app.clbs.doctype.summaries.summaries import get_summary
# from xhtml2pdf import pisa


class SummaryBreakups(Document):
    pass


@frappe.whitelist(allow_guest=True)
def summary_print_formats(name):
    try:
        doc = frappe.db.get_value(
            "Summaries", name, ["name", "tax_payer_details"], as_dict=1)
        if doc:
            get_categroies = frappe.db.get_list(
                "Summary Breakups", {"summaries": name}, pluck="category")
            if len(get_categroies) > 0:
                get_categroies.append("Summary")
                templates = frappe.db.get_all("Print Format", filters={
                    "name": ["in", get_categroies]}, fields=["*"])
                if len(templates) == 0:
                    return {"success": False, ",message": "please add print formats"}
                total_reports = []
                for each_template in templates:
                    html = frappe.render_template(each_template["html"], doc)
                    # total_reports.append({each_template["name"]:html})
                    total_reports.append({each_template["name"]:html, "category": each_template["name"]})
                    # html += '<div style="page-break-before: always;"></div>'
                return {"success": True, "html": total_reports}
            else:
                return {"success": False, "message": "summary breakups not found"}
        else:
            return {"success": False, "message": "data not found"}
    except Exception as e:
        frappe.log_error("Error in create_html_to_pdf: ",
                         frappe.get_traceback())
        return {"success": False, "message": str(e)}


def html_to_pdf(html_data, filename, name):
    try:
        company = frappe.get_last_doc('company')
        if not company.host:
            return {'success': False, 'message': "please specify host in company"}
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        htmldoc = HTML(string=html_data, base_url="")
        file_path = cwd + "/" + site_name + "/public/files/" + filename + name + '.pdf'
        htmldoc.write_pdf(file_path)
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home', 'doctype': 'Summaries',
                       'docname': name, 'fieldname': filename}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new, verify=False).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
        return {"success": True, "file_url": file_response["message"]["file_url"]}
    except Exception as e:
        frappe.log_error("Error in html_to_pdf: ", frappe.get_traceback())
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def download_pdf(name):
    try:
        summary_format = summary_print_formats(name)
        if summary_format["success"] == False:
            return summary_format
        if len(summary_format["html"]) > 0:
            for each in summary_format["html"]:
                html_to_pdf = html_to_pdf(each[each["category"]])
                print(html_to_pdf)
            
    except Exception as e:
        pass

def extract_summary_breakups(filters, summary):
    try:
        total_items = []
        get_company = frappe.get_last_doc("company")
        get_items = frappe.db.get_list(
            "Items", filters=filters, fields=["*"])
        get_item_dates = frappe.db.get_list(
            "Items", filters=filters, pluck='date')
        for each in get_items:
            invoice_doc = frappe.get_doc("Invoices", each.parent)
            each["invoice_category"] = invoice_doc.invoice_category
            each["invoice_file"] = invoice_doc.invoice_file
            sac_category = frappe.db.get_value(
                "SAC HSN CODES", each.description, "category")
            if sac_category:
                each["service_type"] = sac_category
            else:
                sac_category = frappe.db.get_value(
                    "SAC HSN CODES", {"sac_index": each.sac_index}, "category")
                each["service_type"] = sac_category
            # start_date = datetime.datetime.strptime(str(min(get_item_dates)),'%Y-%m-%d').strftime("%d %B %Y")
            start_date = min(get_item_dates).strftime("%d %B %Y")
            end_date = max(get_item_dates).strftime("%d %B %Y")
            each["Date_string"] = start_date+" to "+end_date
            each['company'] = get_company.name
            each['summaries'] = summary
            total_items.append(each)
        df = pd.DataFrame.from_records(total_items)
        data = df.groupby('service_type', as_index=False).agg(
            {"Date_string": 'first', "service_type": 'first', "invoice_category": 'first', "item_value_after_gst": 'sum', "company": 'first', "summaries": 'first'})
        data.rename(columns={'Date_string': 'date', 'service_type': 'category',
                    'invoice_category': 'invoice_type', 'item_value_after_gst': 'amount'}, inplace=True)
        data = data.to_dict('records')
        return {"success": True, "data": data, "df": df}
    except Exception as e:
        frappe.log_error(str(e), "extract_summary_breakups")
        return {"success": False, "message": str(e)}


def extract_summary_breakup_details(df, summaries):
    try:
        summary_breakup_details = df[df['service_type']
                                     == summaries["category"]]
        filter_food_columns = summary_breakup_details[["date", "parent", "sac_code", "item_value_after_gst",
                                                       "item_taxable_value", "cgst_amount", "sgst_amount", "igst_amount", "gst_rate", "service_type", "description", "invoice_file"]]
        filter_food_columns.rename(columns={'parent': 'invoice_no', 'item_value_after_gst': 'amount', 'cgst_amount': 'cgst', "sgst_amount": "sgst", "igst_amount": "igst", "gst_rate": "tax",
                                            'item_taxable_value': 'base_amount', 'service_type': 'category', 'description': 'particulars'}, inplace=True)
        # filter_food_columns["parent"] = doc.name
        filter_food_columns["parentfield"] = "summary_breakup_details"
        filter_food_columns["parenttype"] = "Summary Breakups"
        filter_food_columns["doctype"] = "Summary Breakup Details"
        if summaries["category"] == "Rooms":
            filter_food_columns["checkin_date"] = filter_food_columns["date"]
            filter_food_columns["checkout_date"] = filter_food_columns["date"] + \
                timedelta(1)
        food_data = filter_food_columns.to_dict('records')
        return {"success": True, "data": food_data}
    except Exception as e:
        frappe.log_error(str(e), "extract_summary_breakup_details")
        return {"success": False, "message": str(e)}


def create_summary_breakups(summaries, summary):
    try:
        get_existing_breakup = frappe.db.get_value("Summary Breakups", {
            "category": summaries["category"], "summaries": summary}, ["name", "amount"], as_dict=True)
        if get_existing_breakup:
            doc = frappe.get_doc(
                "Summary Breakups", get_existing_breakup["name"])
            doc.amount = get_existing_breakup["amount"] + \
                summaries["amount"]
            doc.save(ignore_permissions=True, ignore_version=True)
        else:
            summaries["doctype"] = 'Summary Breakups'
            doc = frappe.get_doc(summaries)
            doc.insert()
            frappe.db.commit()
        return {"success": True, "doc": doc}
    except Exception as e:
        frappe.log_error(str(e), "create_summary_breakups")
        return {"success": False, "message": str(e)}


def create_breakup_details(doc, details_data, summary):
    try:
        get_company = frappe.get_last_doc("company")
        for child_items in details_data:
            child_items["parent"] = doc.name
            invoice_file = child_items["invoice_file"]
            del child_items["invoice_file"]
            child_doc = frappe.get_doc(child_items)
            child_doc.insert()
            frappe.db.commit()
            if frappe.db.exists({"doctype": "Invoices", "clbs_summary_generated": False, "invoice_number": child_items["invoice_no"], "company": get_company.name}):
                invoice_doc = frappe.get_doc(
                    "Invoices", child_items["invoice_no"])
                invoice_doc.clbs_summary_generated = 1
                invoice_doc.summary = summary
                invoice_doc.save(
                    ignore_permissions=True, ignore_version=True)
                document_doc = frappe.get_doc({"doctype": "Summary Documents", "document_type": "Invoices", "summary": summary,
                                               "document": invoice_file, "company": get_company.name, "invoice_number": child_items["invoice_no"]})
                document_doc.insert()
                frappe.db.commit()
        return {"success": True}
    except Exception as e:
        frappe.log_error(str(e), "create_breakup_details")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def create_summary_breakup(filters=[], summary=None):
    try:
        get_company = frappe.get_last_doc("company")
        if len(filters) > 0:
            summary_breakups = extract_summary_breakups(filters, summary)
            if summary_breakups["success"] == False:
                return summary_breakups
            data = summary_breakups["data"]
            df = summary_breakups["df"]
            for summaries in data:
                breakup_details = extract_summary_breakup_details(
                    df, summaries)
                if breakup_details["success"] == False:
                    return breakup_details
                details_data = breakup_details["data"]
                create_breakups = create_summary_breakups(summaries, summary)
                if create_breakups["success"] == False:
                    return create_breakups
                doc = create_breakups["doc"]
                if doc:
                    breakup_details = create_breakup_details(
                        doc, details_data, summary)
                    if breakup_details["success"] == False:
                        return breakup_details
                else:
                    return {"success": False, "message": "something went wrong"}
            return {"success": True, "message": "summary created"}
        else:
            return {"success": False}
    except Exception as e:
        frappe.log_error(str(e), "create_summary_breakup")
        return {"success": False, "message": str(e)}


def update_invoices(invoices=[], data={}):
    try:
        for each in invoices:
            frappe.db.set_value('Invoices', each, data)
            frappe.db.commit()
        return {"success": True}
    except Exception as e:
        frappe.log_error(str(e), "update_invoices")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def delete_invoice_summary_breakup(deleted_invoices=[], summary=None):
    try:
        deleted_invoices = json.loads(deleted_invoices)
        if len(deleted_invoices) == 0:
            return {"success": False, "message": "please select invoices for delete"}
        get_invoices_under_summary = frappe.db.get_list(
            "Invoices", {"summary": summary}, pluck="name")
        if len(get_invoices_under_summary) > 0:
            remaining_invoices = list(
                set(get_invoices_under_summary)-set(deleted_invoices))
            if len(remaining_invoices) > 0:
                frappe.db.delete("Summary Breakups", {"summaries": summary})
                frappe.db.delete("Summary Documents", {"summary": summary})
                frappe.db.commit()
                update_invoice = update_invoices(
                    deleted_invoices, {"summary": None, "clbs_summary_generated": 0})
                if update_invoice["success"] == False:
                    return update_invoice
                create_breakups = create_summary_breakup(
                    [["parent", "in", remaining_invoices]], summary)
                if create_breakups["success"] == False:
                    return create_breakups
                return {"success": True, "message": "Invoice is deleted from this summary"}
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        frappe.log_error(str(e), "delete_invoice_summary_breakup")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_summary_breakup(data):
    try:
        if len(data["summary"]) == 0:
            return {"success": False, "message": "No data found"}
        for each in data["summary"]:
            name = each["name"]
            del each["name"]
            update_breakup_summary = frappe.db.set_value(
                "Summary Breakup Details", name, each)
            frappe.db.commit()
        return {"success": True, "message": "data updated successfully"}
    except Exception as e:
        frappe.log_error(str(e), "update_summary_breakup")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_summary_breakup(summary=None):
    try:
        if summary:
            # "`tabSummary Breakups`.date", "`tabSummary Breakups`.category", "`tabSummary Breakups`.invoice_type", "`tabSummary Breakups`.amount", "`tabSummary Breakup Details`.date as breakup_date", "`tabSummary Breakup Details`.bill_no", "`tabSummary Breakup Details`.invoice_no", "`tabSummary Breakup Details`.particulars", "`tabSummary Breakup Details`.sac_code", "`tabSummary Breakup Details`.base_amount",
            #  "`tabSummary Breakup Details`.tax", "`tabSummary Breakup Details`.cgst", "`tabSummary Breakup Details`.sgst", "`tabSummary Breakup Details`.igst", "`tabSummary Breakup Details`.amount as total_amount", "`tabSummary Breakup Details`.checkin_date", "`tabSummary Breakup Details`.checkout_date", "`tabSummary Breakup Details`.no_of_nights", "`tabSummary Breakup Details`.no_of_guests", "`tabSummary Breakup Details`.room_rate", "`tabSummary Breakup Details`.category"
            get_summary_breakups = frappe.db.get_list(
                "Summary Breakups", filters=[["summaries", "=", summary]], fields=["*"])
            if len(get_summary_breakups) > 0:
                for each in get_summary_breakups:
                    breakup_details = frappe.db.get_list("Summary Breakup Details", filters=[
                                                         ["parent", "=", each["name"]]], fields=["*"])
                    each["summary_breakup_details"] = breakup_details
                get_summary_info = get_summary(summary)
                if get_summary_info["success"] == False:
                    return get_summary_info
                gst_summary = get_gst_summary(summary)
                if gst_summary["success"] == False:
                    return gst_summary
                return {"success": True, "data": get_summary_breakups, "summary_info": get_summary_info["data"],"gst_summary": gst_summary["data"], "get_totals": gst_summary["get_totals"]}
            else:
                return {"success": False, "message": "summary breakups not found"}
        else:
            return {"success": False, "message": "summary not found"}
    except Exception as e:
        frappe.log_error(str(e), "get_summary_breakup")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_gst_summary(summaries):
    try:
        get_summary_breakups = frappe.db.get_list(
            "Summary Breakups", {"summaries": summaries}, pluck="name")
        if len(get_summary_breakups) > 0:
            get_breakup_details = frappe.db.get_list("Summary Breakup Details", filters=[["parent", "in", get_summary_breakups]], fields=[
                                                    "sum(base_amount) as base_amount", "sum(amount) as total_amount","sum(cgst) as cgst", "sum(sgst) as sgst", "sum(igst) as igst", "tax"], group_by="tax")
            get_total = frappe.db.get_value("Summary Breakup Details", {"parent":["in", get_summary_breakups]}, [
                                                    "sum(base_amount) as base_amount","sum(cgst)+sum(sgst)+sum(igst) as gst_amount", "sum(amount) as total_amount"], as_dict=1)
            return {"success": True, "data": get_breakup_details, "get_totals": get_total}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        frappe.log_error(str(e), "get_gst_summary")
        return {"success": False, "message": str(e)}
