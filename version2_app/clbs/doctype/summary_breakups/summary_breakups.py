# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from webbrowser import get

import frappe
import fitz
import base64
import pandas as pd
import pdfkit
import requests
import time
import sys
from frappe.core.doctype.communication.email import make
from frappe.model.document import Document
from frappe.utils import cstr
from weasyprint import HTML
from PyPDF2 import PdfFileMerger


from version2_app.clbs.doctype.summaries.summaries import get_summary
from version2_app.e_signature.e_signature import send_files


class SummaryBreakups(Document):
    pass


def convert_image_to_base64(image):
    try:
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        file_path1 = (
            folder_path
            + "/sites/"
            + company.site_name
            + image
        )
        with open(file_path1, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        return {"success": True, "data": encoded_str}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("convert_image_to_base64",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def summary_print_formats(name):
    try:
        doc = frappe.db.get_value(
            "Summaries", name, ["name", "tax_payer_details"], as_dict=1)
        if doc:
            company = frappe.get_last_doc("company")
            if company.company_logo:
                convimgtobase = convert_image_to_base64(company.company_logo)
                if not convimgtobase["success"]:
                    return convimgtobase
                doc["base"] = "data:image/png;base64,"+convimgtobase["data"]
            else:
                doc["base"] = ""
            get_categroies = frappe.db.get_list(
                "Summary Breakups", {"summaries": name}, pluck="category")
            if len(get_categroies) > 0:
                get_categroies.append("Summary")
                # templates = frappe.db.get_all("Print Format", filters={
                #     "name": ["in", get_categroies]}, fields=["*"])
                # if len(templates) == 0:
                # return {"success": False, ",message": "please add print formats"}
                get_categroies = list(set(get_categroies))
                total_reports = []
                for category in get_categroies:
                    if category in ["Summary", "Rooms"]:
                        # if category == "Summary":
                        #     category = "Summary With Border"
                        # if category == "Rooms":
                        #     category = "Rooms With Border"
                        templates = frappe.db.get_value(
                            "Print Format", {"name": category}, ["html"])
                        if not templates:
                            return {"success": False, ",message": "please add print formats"}
                        html_data = frappe.render_template(templates, doc)
                    else:
                        templates = frappe.db.get_value(
                            "Print Format", {"name": "Category"}, ["html"])
                        if not templates:
                            return {"success": False, ",message": "please add print formats"}
                        doc["category"] = category
                        html_data = frappe.render_template(templates, doc)
                    total_reports.append(
                        {category: html_data, "category": category})
                return {"success": True, "html": total_reports}
            return {"success": False, "message": "summary breakups not found"}
        return {"success": False, "message": "data not found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("summary_print_formats",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def get_file_size(summary, files=[], combine=False):
    try:
        documents = files
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        filesize = 0
        if len(documents) > 0:
            documents = list(set(documents))
            for each in documents:
                file_path = cwd + "/" + site_name + each
                size = os.path.getsize(file_path)
                filesize += size
        if filesize > 0:
            size_in_mb = filesize/(1024*1024)
            return {"success": True, "size": round(size_in_mb, 2)}
        else:
            return {"success": False, "size": 0}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_file_size",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def html_to_pdf(html_data, filename, name, etax=False):
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
                                      data=payload_new).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
        else:
            return {"success": False, "message": "something went wrong"}
        return {"success": True, "file_url": file_response["message"]["file_url"]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("html_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def combine_pdf(files, filename, name, add_signature=False):
    try:
        company = frappe.get_last_doc('company')
        if not frappe.db.exists("CLBS Settings", company.name):
            return {"success": False, "message": "Need to add clbs settings"}
        clbs_settings = frappe.get_doc("CLBS Settings", company.name)
        if not clbs_settings.document_sequence:
            return {"success": False, "message": "document sequence not defined"}
        document_sequence = json.loads(clbs_settings.document_sequence)
        document_sequence = dict(
            sorted(document_sequence.items(), key=lambda item: item[1]))
        summary_files = [values for each in files for key,
                         values in each.items()]
        files = []
        for each in summary_files:
            if "Summary" in each:
                files.insert(0, each)
            else:
                files.append(each)
        if add_signature == True and frappe.session.user != "Administrator":
            summaryfile = get_all_summary_files(
                name, True, frappe.session.user)
        else:
            summaryfile = get_all_summary_files(name)
        if not summaryfile["success"]:
            return summaryfile
        qr_files = [each for each in summaryfile["files"]
                    if "E Tax Invoice-" in each]
        pos = [each for each in summaryfile["files"]
                    if "ETax-Invoice-" in each]
        order_files = []
        for key, value in document_sequence.items():
            if "e_tax" == key:
                order_files.extend(qr_files)
            elif "summary" == key:
                order_files.extend(files)
            elif "POS Checks" == key:
                order_files.extend(pos)
            else:
                bills = frappe.db.get_list("Summary Documents",
                                           filters={"summary": ["=", name],
                                                    "document_type": ["=", key]}, pluck="document")
                if len(bills) > 0:
                    order_files.extend(bills)
        # ordered_files = files + qr_files + invoices + bills
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        # merger = PdfFileMerger(strict=False)
        result = fitz.open()
        for each in order_files:
            file_path = cwd + "/" + site_name + each
            with fitz.open(file_path) as mfile:
                result.insertPDF(mfile)
        file_path = cwd + "/" + site_name + "/public/files/" + name + '.pdf'
        result.save(file_path)
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home', 'doctype': 'Summaries',
                       'docname': name, 'fieldname': filename}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new).json()
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
        else:
            return {"success": False, "message": "something went wrong"}
        frappe.db.delete("File", {"file_url": ["in", qr_files]})
        frappe.db.commit()
        return {"success": True, "file_url": file_response["message"]["file_url"]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("combine_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def download_pdf(name, add_signature=False, email=False):
    try:
        if add_signature == "true":
            add_signature = True
        summary_format = summary_print_formats(name)
        if not summary_format["success"]:
            return summary_format
        file_urls = []
        if len(summary_format["html"]) > 0:
            company = frappe.get_last_doc('company')
            if not frappe.db.exists("CLBS Settings", company.name):
                return {"success": False, "message": "No data found in clbs settings"}
            clbs_settings_doc = frappe.get_doc("CLBS Settings", company.name)
            frappe.db.delete("File", {"attached_to_name": name})
            # frappe.db.sql("""DELETE FROM `tabFile` where`tabFile`.attached_to_name in {}""".format(tuple(name)))
            frappe.db.commit()
            summary_doc = frappe.get_doc("Summaries", name)
            files_for_size = []
            files = []
            for each in summary_format["html"]:
                get_pdf = html_to_pdf(
                    each[each["category"]], each["category"], name)
                if not get_pdf["success"]:
                    return get_pdf
                if ((add_signature and clbs_settings_doc.digital_signature == 1) or (clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1)) and frappe.session.user != "Administrator":
                    add_sig = send_files(
                        [get_pdf["file_url"]], frappe.session.user, name)
                    if not add_sig["success"]:
                        return add_sig
                    file_urls.append({each["category"]: add_sig["files"][0]})
                    files_for_size.append(add_sig["files"][0])
                else:
                    file_urls.append({each["category"]: get_pdf["file_url"]})
                    files_for_size.append(get_pdf["file_url"])
            if clbs_settings_doc.clbs_document_preview == "COMBINED":
                if ((add_signature and clbs_settings_doc.digital_signature == 1) or (clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1)) and frappe.session.user != "Administrator":
                    combine = combine_pdf(file_urls, "summary", name, True)
                else:
                    combine = combine_pdf(file_urls, "summary", name)
                if not combine["success"]:
                    return combine
                files_to_delete = [
                    value for each in file_urls for key, value in each.items()]
                frappe.db.delete("File", {"file_url": ["in", files_to_delete]})
                frappe.db.commit()
                file_urls = []
                file_urls.append({"Summary": combine["file_url"]})
                files_for_size = []
                files_for_size.append(combine["file_url"])
            else:
                if not email:
                    if ((add_signature and clbs_settings_doc.digital_signature == 1) or (clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1)) and frappe.session.user != "Administrator":
                        get_all_files = get_all_summary_files(
                            name, True, frappe.session.user)
                    else:
                        get_all_files = get_all_summary_files(name)
                    if not get_all_files["success"]:
                        return get_all_files
                    remaining_files = get_all_files["files"]
                    files_for_size.extend(remaining_files)
            for each in file_urls:
                if "Summary" in each.keys():
                    files.insert(0, each)
                else:
                    files.append(each)
            filesize = 0
            if len(files_for_size) > 0:
                file_size = get_file_size(name, files_for_size)
                if file_size["success"]:
                    filesize = file_size["size"]
            if add_signature:
                frappe.db.set_value("Summaries", name, "signature_attached", 1)
                frappe.db.commit()
            return {"success": True, "files": files, "size": filesize}
        return {"success": False, "message": "no data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("download_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


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
            each["qr_code_image"] = invoice_doc.qr_code_image
            each["invoice_number"] = invoice_doc.invoice_number
            sac_category = frappe.db.get_value(
                "SAC HSN CODES", each.description, "category")
            if sac_category:
                each["service_type"] = sac_category
            else:
                sac_category = frappe.db.get_value(
                    "SAC HSN CODES", {"sac_index": each.sac_index}, "category")
                if sac_category:
                    each["service_type"] = sac_category
                else:
                    return {"success": False, "message": "categories not found in sac/hsn codes"}
            start_date = min(get_item_dates).strftime("%d %B %Y")
            end_date = max(get_item_dates).strftime("%d %B %Y")
            each["Date_string"] = start_date+" to "+end_date
            each['company'] = get_company.name
            each['summaries'] = summary
            total_items.append(each)
        df = pd.DataFrame.from_records(total_items)
        data = df.groupby(['service_type', 'invoice_number'], as_index=False).agg(
            {"Date_string": 'first', "service_type": 'first', "invoice_category": 'first',
             "item_value_after_gst": 'sum', "company": 'first', "summaries": 'first',
             'invoice_number': 'first', "sac_code": list})
        data.rename(columns={'Date_string': 'date', 'service_type': 'category',
                    'invoice_category': 'invoice_type',
                             'item_value_after_gst': 'amount'}, inplace=True)
        data = data.to_dict('records')
        for each in data:
            if len(each["sac_code"]) > 0:
                each["sac_codes"] = ", ".join(set(each["sac_code"]))
                del each["sac_code"]
            else:
                each["sac_codes"] = None
        return {"success": True, "data": data, "df": df}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("extract_summary_breakups",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def extract_summary_breakup_details(df, summaries):
    try:
        summary_breakup_details = df[(df['service_type'] == summaries["category"]) &
                                     (df["invoice_number"] == summaries["invoice_number"])]
        filter_food_columns = summary_breakup_details[
            ["date", "parent", "sac_code", "item_value_after_gst",
             "item_taxable_value", "cgst_amount", "sgst_amount",
             "igst_amount", "gst_rate", "service_type",
             "description", "invoice_file", "qr_code_image"]]
        filter_food_columns.rename(columns={'parent': 'invoice_no',
                                            'item_value_after_gst': 'amount',
                                            'cgst_amount': 'cgst', "sgst_amount": "sgst",
                                            "igst_amount": "igst", "gst_rate": "tax",
                                            'item_taxable_value': 'base_amount',
                                            'service_type': 'category',
                                            'description': 'particulars'}, inplace=True)
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("extract_summary_breakup_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def create_summary_breakups(summaries, summary):
    try:
        get_existing_breakup = frappe.db.get_value("Summary Breakups", {
            "category": summaries["category"],
            "summaries": summary,
            "invoice_number": summaries["invoice_number"]},
            ["name", "amount"], as_dict=True)
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_summary_breakups",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def create_breakup_details(doc, details_data, summary):
    try:
        get_company = frappe.get_last_doc("company")
        for child_items in details_data:
            child_items["parent"] = doc.name
            invoice_file = child_items["invoice_file"]
            del child_items["invoice_file"]
            qr_code_image = child_items["qr_code_image"]
            del child_items["qr_code_image"]
            child_doc = frappe.get_doc(child_items)
            child_doc.insert()
            frappe.db.commit()
            if frappe.db.exists({"doctype": "Invoices", "clbs_summary_generated": False,
                                "invoice_number": child_items["invoice_no"],
                                 "company": get_company.name}):
                invoice_doc = frappe.get_doc(
                    "Invoices", child_items["invoice_no"])
                invoice_doc.clbs_summary_generated = 1
                invoice_doc.summary = summary
                invoice_doc.save(
                    ignore_permissions=True, ignore_version=True)
                if invoice_file.strip() != "":
                    document_doc = frappe.get_doc({"doctype": "Summary Documents",
                                                   "document_type": "Invoices",
                                                   "summary": summary,
                                                   "document": invoice_file,
                                                   "company": get_company.name,
                                                   "invoice_number": child_items["invoice_no"],
                                                   "qr_code_image": qr_code_image})
                    document_doc.insert()
                    frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_breakup_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def create_summary_breakup(filters=[], summary=None):
    try:
        if len(filters) > 0:
            summary_breakups = extract_summary_breakups(filters, summary)
            if not summary_breakups["success"]:
                return summary_breakups
            data = summary_breakups["data"]
            df = summary_breakups["df"]
            for summaries in data:
                breakup_details = extract_summary_breakup_details(
                    df, summaries)
                if not breakup_details["success"]:
                    return breakup_details
                details_data = breakup_details["data"]
                create_breakups = create_summary_breakups(summaries, summary)
                if not create_breakups["success"]:
                    return create_breakups
                doc = create_breakups["doc"]
                if doc:
                    breakup_details = create_breakup_details(
                        doc, details_data, summary)
                    if not breakup_details["success"]:
                        return breakup_details
                else:
                    return {"success": False, "message": "something went wrong"}
            return {"success": True, "message": "summary created"}
        return {"success": False}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_summary_breakup",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


def update_invoices(invoices=[], data={}):
    try:
        for each in invoices:
            frappe.db.set_value('Invoices', each, data)
            frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_invoices",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
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
            frappe.db.delete("Summary Breakups", {"summaries": summary})
            frappe.db.delete("Summary Documents", {
                             "invoice_number": ["in", deleted_invoices]})
            frappe.db.commit()
            update_invoice = update_invoices(
                deleted_invoices, {"summary": None, "clbs_summary_generated": 0})
            if not update_invoice["success"]:
                return update_invoice
            if len(remaining_invoices) > 0:
                create_breakups = create_summary_breakup(
                    [["parent", "in", remaining_invoices]], summary)
                if not create_breakups["success"]:
                    return create_breakups
            return {"success": True, "message": "Invoice is deleted from this summary"}
        else:
            return {"success": False, "message": "something went wrong"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("delete_invoice_summary_breakup",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_summary_breakup(data):
    try:
        if len(data["summary"]) == 0:
            return {"success": False, "message": "No data found"}
        for each in data["summary"]:
            name = each["name"]
            del each["name"]
            frappe.db.set_value("Summary Breakup Details", name, each)
            frappe.db.commit()
        return {"success": True, "message": "data updated successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_summary_breakup",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_summary_breakup(summary=None):
    try:
        if summary:
            get_summary_info = get_summary(summary)
            if get_summary_info["success"] == False:
                return get_summary_info
            # "`tabSummary Breakups`.date", "`tabSummary Breakups`.category", "`tabSummary Breakups`.invoice_type", "`tabSummary Breakups`.amount", "`tabSummary Breakup Details`.date as breakup_date", "`tabSummary Breakup Details`.bill_no", "`tabSummary Breakup Details`.invoice_no", "`tabSummary Breakup Details`.particulars", "`tabSummary Breakup Details`.sac_code", "`tabSummary Breakup Details`.base_amount",
            #  "`tabSummary Breakup Details`.tax", "`tabSummary Breakup Details`.cgst", "`tabSummary Breakup Details`.sgst", "`tabSummary Breakup Details`.igst", "`tabSummary Breakup Details`.amount as total_amount", "`tabSummary Breakup Details`.checkin_date", "`tabSummary Breakup Details`.checkout_date", "`tabSummary Breakup Details`.no_of_nights", "`tabSummary Breakup Details`.no_of_guests", "`tabSummary Breakup Details`.room_rate", "`tabSummary Breakup Details`.category"
            get_summary_breakups = frappe.db.get_list(
                "Summary Breakups", filters=[["summaries", "=", summary]], fields=["*"])
            if len(get_summary_breakups) > 0:
                breakup_details_data = []
                breakups_names = frappe.db.get_list("Summary Breakups", filters=[
                                                    ["summaries", "=", summary]], pluck="name")
                breakups_categories = frappe.db.get_list("Summary Breakups", filters=[
                    ["summaries", "=", summary]],
                    pluck="category")
                if len(breakups_categories) > 0:
                    breakups_categories = list(set(breakups_categories))
                    details = {}

                    for each in breakups_categories:
                        details = {}
                        breakup_details = frappe.db.get_list("Summary Breakup Details", filters=[
                            ["parent", "in", breakups_names], ["category", "=", each]],
                            fields=["*"])
                        details["category"] = each
                        details["breakup_details"] = breakup_details
                        get_breakup_details = frappe.db.get_list("Summary Breakup Details", filters=[["parent", "in", breakups_names], ["category", "=", each]], fields=[
                            "sum(cgst) as cgst", "sum(sgst) as sgst", "sum(igst) as igst", "tax", "category"], group_by="tax, category")
                        details["gst_details"] = get_breakup_details
                        get_total = frappe.db.get_value("Summary Breakup Details", {"parent": ["in", breakups_names], "category": each}, [
                            "sum(base_amount) as base_amount", "sum(cgst)+sum(sgst)+sum(igst) as gst_amount", "sum(amount) as total_amount"], as_dict=True)
                        details["get_total"] = get_total
                        breakup_details_data.append(details)
                return {"success": True, "data": get_summary_breakups,
                        "breakup_details_data": breakup_details_data,
                        "summary_info": get_summary_info["data"]}
            return {"success": True, "summary_info": get_summary_info["data"], "data": []}
        else:
            return {"success": False, "message": "summary not found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_summary_breakup",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_gst_summary(summaries):
    try:
        get_summary_breakups = frappe.db.get_list(
            "Summary Breakups", {"summaries": summaries}, pluck="name")
        if len(get_summary_breakups) > 0:
            get_breakup_details = frappe.db.get_list(
                "Summary Breakup Details",
                filters=[["parent", "in", get_summary_breakups]],
                fields=["sum(base_amount) as base_amount",
                        "sum(cgst)+sum(sgst)+sum(igst) as gst_amount",
                        "sum(amount) as total_amount",
                        "sum(cgst) as cgst", "sum(sgst) as sgst",
                        "sum(igst) as igst", "tax", "category"],
                group_by="tax, category")
            return {"success": True, "data": get_breakup_details}
        return {"success": False, "message": "no data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_gst_summary",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_summary(data, name):
    try:
        if not frappe.db.exists({'doctype': 'Summaries',
                                 "name": name,
                                 "from_date": data["from_date"],
                                 "to_date": data["to_date"]}
                                ):
            get_invoices = frappe.db.get_list(
                "Invoices", filters={"summary": name}, pluck="name")
            if len(get_invoices) > 0:
                update_invoice = update_invoices(
                    get_invoices, {"summary": None, "clbs_summary_generated": 0})
                if not update_invoice["success"]:
                    return update_invoice
            if frappe.db.exists({'doctype': 'Summary Breakups', 'summaries': name}):
                frappe.db.delete("Summary Breakups", {"summaries": name})
                frappe.db.delete("Summary Documents", {"summary": name})
        frappe.db.set_value('Summaries', name, data)
        frappe.db.commit()
        return {"success": True, "message": "updated successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_summary",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def submit_summary(summary):
    try:
        if frappe.db.exists({"doctype": "Summaries", "name": summary}):
            if frappe.db.exists({"doctype": "Summary Breakups", "summaries": summary}):
                # get_summary_breakups = frappe.db.get_list("Summary Breakups", filters={
                #                                           "summaries": summary,
                #                                           "category": ["!=", "Rooms"]},
                #                                           pluck="name")
                # check_billno = frappe.db.get_list("Summary Breakup Details", filters={
                # "parent": ["in", get_summary_breakups], "bill_no": ["=", ""]})
                # if len(check_billno) > 0:
                #     return {"success": False, "message": "	Bill No. are mandatory"}
                if frappe.db.exists({"doctype": "Invoices", "summary": summary}):
                    frappe.db.set_value("Summaries", summary, {
                                        "status": "Submitted", "docstatus": 1})
                    frappe.db.commit()
                    get_invoices = frappe.db.get_list(
                        "Invoices", filters=[["summary", "=", summary]], pluck="name")
                    invoices_update = update_invoices(
                        get_invoices, {"invoice_submitted_in_clbs": 1})
                    if not invoices_update["success"]:
                        frappe.db.set_value("Summaries", summary, {
                                            "status": "Draft"})
                        frappe.db.commit()
                        update_invoices(
                            get_invoices, {"invoice_submitted_in_clbs": 0})
                        return invoices_update
                    generate_pdf = download_pdf(summary)
                    if not generate_pdf["success"]:
                        return generate_pdf
                    return {"success": True, "message": "Summary submitted"}
                return {"success": False, "message": "something went wrong"}
            return {"success": False, "message": "no data found in summary breakups"}
        return {"success": False, "message": "no data found in summaries"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("submit_summary",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def send_summary_mail(data):
    try:
        company = frappe.get_last_doc('company')
        cc_emails = None
        if not frappe.db.exists("CLBS Settings", company.name):
            return {"success": False, "message": "No data found in clbs settings"}
        clbs_settings_doc = frappe.get_doc("CLBS Settings", company.name)
        if clbs_settings_doc.cc_mail_ids_for_clbs_reports and clbs_settings_doc.cc_mail_ids_for_clbs_reports != "":
            cc_emails = clbs_settings_doc.cc_mail_ids_for_clbs_reports
        # printformat_files = frappe.db.get_list(
        #     'File', filters={'attached_to_name': ['=', data["summary"]]}, pluck='name')
        if not frappe.db.exists("CLBS Settings", company.name):
            return {"success": False, "message": "No data found in clbs settings"}
        summary_doc = frappe.get_doc("Summaries", data["summary"])
        if clbs_settings_doc.clbs_document_preview != "COMBINED":
            if clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1 and frappe.session.user != "Administrator":
                downloadpdf = download_pdf(data["summary"], True, email=True)
            else:
                downloadpdf = download_pdf(data["summary"], False, email=True)
            if not downloadpdf["success"]:
                return downloadpdf
            summary_files = [value for each in downloadpdf["files"]
                             for key, value in each.items()]
            if clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1 and frappe.session.user != "Administrator":
                get_summary_files = get_all_summary_files(
                    data["summary"], True, frappe.session.user)
            else:
                get_summary_files = get_all_summary_files(data["summary"])
            if not get_summary_files["success"]:
                return get_summary_files
            summary_files.extend(get_summary_files["files"])
        else:
            if clbs_settings_doc.digital_signature == 1 and summary_doc.signature_attached == 1:
                combined_files = download_pdf(data["summary"], True)
            else:
                combined_files = download_pdf(data["summary"])
            if not combined_files["success"]:
                return combined_files
            if len(combined_files["files"]) > 0:
                summary_files = [combined_files["files"][0]["Summary"]]
            else:
                summary_files = []
            # summary_files = frappe.db.get_list(
            #     'File', filters={'attached_to_name': ['=', data["summary"]]}, pluck='file_url')
        if len(summary_files) == 0:
            return {"success": False, "message": "Templets Not Found"}
            generate_pdf = download_pdf(data["summary"])
            if generate_pdf["success"] == False:
                return generate_pdf
        filesize = 0
        if len(summary_files) > 0:
            file_size = get_file_size(
                data["summary"], summary_files, True if clbs_settings_doc.clbs_document_preview == "COMBINED" else False)
            if file_size["success"]:
                filesize = file_size["size"]
        if filesize > 25:
            return {"success": False, "message": "File size is more than 25MB"}
        print(summary_files, "..........................................")
        files_summary = frappe.db.get_list("File", filters={"file_url": [
                                           "in", summary_files]}, group_by="file_url", pluck='name')
        print(files_summary, ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        response = make(recipients=data["email"],
                        subject=data["subject"],
                        content=data["response"],
                        doctype=None,
                        name=None,
                        cc=cc_emails if cc_emails else "",
                        attachments=json.dumps(files_summary),
                        send_email=1
                        )
        if cc_emails:
            if "," in cc_emails:
                cc_emails_split = cc_emails.split(",")
                data["email"].extend(cc_emails_split)
            else:
                data["email"].append(cc_emails)
        emails = json.dumps(data["email"])
        frappe.db.set_value(
            'Summaries', data["summary"], 'email_sent_status', 1)
        frappe.db.commit()
        email_data = {"doctype": 'Summary Email Tracking',
                      "emails": emails, "summary": data["summary"]}
        doc = frappe.get_doc(email_data)
        doc.insert(ignore_permissions=True)
        return {"success": True, "message": "Mail Send"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("send_summary_mail",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def get_all_summary_files(summary=None, add_signature=False, user=None):
    try:
        if summary:
            etax_tax = etax_invoice_to_pdf(summary)
            if not etax_tax["success"]:
                return etax_tax
            if add_signature == True and user != "Administrator":
                print("..///........,,,,,")
                add_sig = send_files(etax_tax["file_urls"], user, summary)
                if not add_sig["success"]:
                    return add_sig
                summary_files = add_sig["files"]
            else:
                summary_files = etax_tax["file_urls"]
            remaining_bills = frappe.db.get_list("Summary Documents", filters={"summary": [
                "=", summary]}, pluck="document")
            # printformat_files = frappe.db.get_list(
            #     'File', filters={'attached_to_name': ['=', summary]}, pluck='file_url')
            # summary_files = summary_files + remaining_bills + printformat_files
            get_invoice_list = frappe.db.get_list("Invoices", filters = {"summary": summary}, pluck = "name")
            summary_files.extend(remaining_bills)
            if len(get_invoice_list) > 0:
                get_pos_checks = frappe.db.get_list("POS Checks", filters=[["attached_to","in",get_invoice_list],["POS Checks","pos_bill","is","set"]],pluck="pos_bill")
                summary_files = summary_files + get_pos_checks            
            return {"success": True, "files": summary_files}
        return {"summary": False, "message": "Summary name is mandatory"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_all_summary_files",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def add_qr_to_pdf(data):
    try:
        company = frappe.get_last_doc("company")
        qr_coordinates = frappe.db.get_value('CLBS Settings', company.name,
                                             ['qr_rect_x0', 'qr_rect_x1', 'qr_rect_y0', 'qr_rect_y1'], as_dict=1)
        if not qr_coordinates:
            return {"success": False, "message": "please add coordinates in clbs settings"}
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company.site_name
        path = folder_path + '/sites/' + site_folder_path
        files_urls = []
        for each in data:
            src_pdf_filename = path + each["document"]
            dst_pdf_filename = path + "/private/files/" + \
                each["invoice_number"] + 'withQr.pdf'
            img_filename = path + each["qr_code_image"]
            # img_rect = fitz.Rect(190, 90, 350, 220)
            add_image = add_image_to_pdf(qr_coordinates["qr_rect_x0"], qr_coordinates["qr_rect_x1"], qr_coordinates["qr_rect_y0"],
                                         qr_coordinates["qr_rect_y1"], src_pdf_filename, img_filename, dst_pdf_filename)
            if add_image["success"]:
                frappe.db.set_value(
                    'Summary Documents', each["name"],
                    'qr_attached_document', add_image["file"])
                frappe.db.commit()
            else:
                return {"success": False, "message": "something went wrong"}
        return {"success": True, "files": files_urls}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_qr_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def add_image_to_pdf(qr_rect_x0=None, qr_rect_x1=None, qr_rect_y0=None, qr_rect_y1=None, input_file=None, image=None):
    try:
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        input_file = cwd + "/" + site_name + input_file
        image = cwd + "/" + site_name + image
        file_name = os.path.basename(input_file)
        output_file = cwd + "/" + site_name + "/public/files/"+file_name
        company = frappe.get_last_doc("company")
        img_rect = fitz.Rect(
            int(qr_rect_x0),
            int(qr_rect_x1),
            int(qr_rect_y0),
            int(qr_rect_y1)
        )
        document = fitz.open(input_file)
        page = document[-1]
        im = open(image, "rb").read()
        page.insertImage(img_rect, stream=im)
        document.save(output_file)
        document.close()
        files = {"file": open(output_file, 'rb')}
        payload = {
            "is_private": 1,
            "folder": "Home"
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        # print(upload_qr_image)
        response = upload_qr_image.json()
        if 'message' in response:
            return {"success": True, "file": (response['message']['file_url'])}
        return {"success": False, "message": "some error occurred"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_image_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def add_signature_images(files, user_name):
    try:
        if user_name:
            if frappe.db.exists("User Signature", user_name):
                new_files = []
                clbs_settings = frappe.get_last_doc('CLBS Settings')
                sig_doc = frappe.get_doc("User Signature", user_name)
                for each in files:
                    signature = add_image_to_pdf(qr_rect_x0=clbs_settings.x1,
                                                 qr_rect_y0=clbs_settings.y1, qr_rect_x1=clbs_settings.x2,
                                                 qr_rect_y1=clbs_settings.y2, input_file=each, image=sig_doc.signature_image)
                    if not signature["success"]:
                        return signature
                    new_files.append(signature["file"])
                return {"success": True, "files": new_files}
            return {"success": False, "message": "User Not Found"}
        return {"success": False, "message": "User Name not given"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_signature_images",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def etax_invoice_to_pdf(summary):
    try:
        company = frappe.get_last_doc("company")
        company_logo_base = ""
        if company.company_logo:
            convimgtobase = convert_image_to_base64(company.company_logo)
            if not convimgtobase["success"]:
                return convimgtobase
            company_logo_base = "data:image/png;base64,"+convimgtobase["data"]
        checkinvoices = frappe.db.get_list("Summary Breakups", filters={"Summaries": [
            "=", summary]}, pluck="invoice_number", group_by="invoice_number")
        if len(checkinvoices) > 0:
            file_urls = []
            for each in checkinvoices:
                if frappe.db.exists("Invoices", each):
                    doc = frappe.get_doc("Invoices", each)
                    qr_image_base = ""
                    if doc.qr_code_image:
                        convimgtobase = convert_image_to_base64(
                            doc.qr_code_image)
                        if not convimgtobase["success"]:
                            return convimgtobase
                        qr_image_base = "data:image/png;base64," + \
                            convimgtobase["data"]
                    templates = frappe.db.get_value(
                        "Print Format", {"name": "E-Tax Invoice"}, ["html"])
                    if not templates:
                        return {"success": False, ",message": "please add print formats"}
                    data = doc.as_dict()
                    data["qr_code_image"] = qr_image_base
                    data["company_logo_base"] = company_logo_base
                    html_data = frappe.render_template(templates, data)
                    convert_html_to_pdf = html_to_pdf(
                        html_data, "ETax-Invoice-", summary)
                    if not convert_html_to_pdf["success"]:
                        return convert_html_to_pdf
                    frappe.db.set_value('Summary Documents',
                                        each, 'qr_attached_document',
                                        convert_html_to_pdf["file_url"])
                    frappe.db.commit()
                    file_urls.append(convert_html_to_pdf["file_url"])
            return {"success": True, "file_urls": file_urls}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("etax_invoice_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def summary_amendment(summary):
    try:
        if frappe.db.exists("Summaries", {"name": summary}):
            get_invoice_list = frappe.db.get_list(
                "Invoices", filters=[["summary", "=", summary]], pluck="name")
            invoice_list = get_invoice_list
            frappe.db.set_value("Summaries", summary, {
                                "status": "Cancelled", "docstatus": 2})
            frappe.db.sql(
                """update `tabSummary Breakups` set docstatus=2 where summaries='{}'""".format(summary))
            frappe.db.sql(
                """update `tabSummary Payments` set docstatus=2 where summary = '{}'""".format(summary))
            if len(get_invoice_list) == 1:
                get_invoice_list = get_invoice_list+["0"]
            if len(get_invoice_list) > 0:
                frappe.db.sql("""update `tabInvoices` set summary="",clbs_summary_generated=0,invoice_submitted_in_clbs=0 where name in {}""".format(
                    tuple(get_invoice_list)))
                frappe.db.commit()
            summary_data = frappe.db.get_value("Summaries", summary, ["summary_title", "from_date", "to_date", "event_type", "tax_payer_details", "between_dates",
                                               "phone_number", "land_line_number", "location", "legal_name", "header", "footer", "terms_and_conditions", "contacts", "reference", "po_number", "sequence"], as_dict=1)
            summary_data["amended_from"] = summary
            summary_data["doctype"] = "Summaries"
            summary_data["sequence"] = summary_data["sequence"] + 1
            summary_doc = frappe.get_doc(summary_data)
            summary_doc.insert()
            frappe.db.commit()
            create_summary = create_summary_breakup(
                filters=[["parent", "in", invoice_list]], summary=summary_doc.name)
            if not create_summary["success"]:
                return create_summary
            get_summary_payments = frappe.db.get_list("Summary Payments", filters=[
                                                      ["summary", "=", summary]], fields=["payment_description", "amount"])
            if len(get_summary_payments) > 0:
                summary_payment = add_summary_payment(
                    get_summary_payments, summary_doc.name)
                if not summary_payment["success"]:
                    return summary_payment
            get_summary_document = frappe.db.get_list("Summary Documents", filters=[["summary", "=", summary], [
                                                      "document_type", "not in", ["invoices", "Invoices"]]], fields=["document_type", "document", "company"])
            if len(get_summary_document) > 0:
                summary_document = add_summary_documents(get_summary_document, summary_doc.name)
                if not summary_document["success"]:
                    return summary_document
            return {"success":True, "message": "Amendment done", "summary": summary_doc.name}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("summary_amendment",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def add_summary_payment(data=None, summary=None):
    try:
        for each in data:
            each["doctype"] = "Summary Payments"
            each["summary"] = summary
            pay_doc = frappe.get_doc(each)
            pay_doc.insert()
            frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_summary_payment",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def add_summary_documents(data=None, summary=None):
    try:
        for each in data:
            each["doctype"] = "Summary Documents"
            each["summary"] = summary
            pay_doc = frappe.get_doc(each)
            pay_doc.insert()
            frappe.db.commit()
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_summary_documents",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}
