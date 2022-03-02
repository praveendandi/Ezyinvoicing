# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from datetime import timedelta

import frappe,pdfkit,os
import pandas as pd
from frappe.model.document import Document
from weasyprint import HTML
# import weasyprint as wp
from pathlib import Path
# from xhtml2pdf import pisa 



class SummaryBreakups(Document):
    pass


@frappe.whitelist(allow_guest=True)
def create_html_to_pdf(name):
    try:
        doc=frappe.db.get_value("Summaries",name,["name","tax_payer_details"],as_dict=1)
        print(doc,"==========")
        if doc:
            templates=frappe.db.get_all("Print Format",filters={"name":["in",["Summary","Rooms","Food","Misc"]]},fields=["*"])
            html=""
            for each_template in templates:
                html+=frappe.render_template(each_template["html"],doc)
                html+='<div style="page-break-before: always;"></div>'
            responce=html_to_pdf(html, "sample")
            return responce
    except Exception as e:
        frappe.log_error("Error in create_html_to_pdf: ",frappe.get_traceback())
        return {"Success":False,"message":str(e)}
    

def html_to_pdf(html_data,filename):
    try:
        cwd = os.getcwd() 
        options = {
                "enable-local-file-access": None
                }

        # with open(html_path,'r') as f:
        # mycss = wp.CSS(string=(
        #         "@page longpage {\n"
        #         "    size: 210mm 10000mm;\n"
        #         "}"
        #         "body {\n"
        #         "   page: longpage;\n"
        #         "}\n"
        #     ))
        htmldoc = HTML(string=html_data, base_url="")#.render(stylesheets=[mycss])
        file_path = cwd + "/" + filename + '.pdf'
        # pisaStatus = pisa.CreatePDF(
        #     src=html_data,            # the HTML to convert
        #     dest=file_path)  
        Path(file_path).write_bytes(htmldoc.write_pdf())
        print(htmldoc.write_pdf(),"===========")
        return {"Success":True,"message":"pdf created successfully"}
    except Exception as e:
        frappe.log_error("Error in html_to_pdf: ",frappe.get_traceback())
        return {"Success":False,"message":str(e)}

@frappe.whitelist(allow_guest=True)
def create_summary_breakup(filters=[], summary=None):
    try:
        total_items = []
        get_company = frappe.get_last_doc("company")
        if len(filters) > 0:
            get_items = frappe.db.get_list(
                "Items", filters=filters, fields=["*"])
            get_item_dates = frappe.db.get_list(
                "Items", filters=filters, pluck='date')
            for each in get_items:
                invoice_doc = frappe.get_doc("Invoices", each.parent)
                each["invoice_category"] = invoice_doc.invoice_category
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
            for summaries in data:
                summaries["doctype"] = 'Summary Breakups'
                doc = frappe.get_doc(summaries)
                doc.insert()
                frappe.db.commit()
                summary_breakup_details = df[df['service_type']
                                             == summaries["category"]]
                filter_food_columns = summary_breakup_details[["date", "parent", "sac_code", "item_value_after_gst",
                                                               "item_taxable_value", "cgst_amount", "sgst_amount", "igst_amount", "gst_rate", "service_type", "description"]]
                filter_food_columns.rename(columns={'parent': 'invoice_no', 'item_value_after_gst': 'amount', 'cgst_amount': 'cgst', "sgst_amount": "sgst", "igst_amount": "igst", "gst_rate": "tax",
                                                    'item_taxable_value': 'base_amount', 'service_type': 'category', 'description': 'particulars'}, inplace=True)
                filter_food_columns["parent"] = doc.name
                filter_food_columns["parentfield"] = "summary_breakup_details"
                filter_food_columns["parenttype"] = "Summary Breakups"
                filter_food_columns["doctype"] = "Summary Breakup Details"
                if summaries["category"] == "Room":
                    filter_food_columns["checkin_date"] = filter_food_columns["date"]
                    filter_food_columns["checkout_date"] = filter_food_columns["date"]+timedelta(1)
                food_data = filter_food_columns.to_dict('records')
                for each in food_data:
                    child_doc = frappe.get_doc(each)
                    child_doc.insert()
                    frappe.db.commit()
            return {"success": True, "message": "data updated successfully"}
        else:
            return {"success": False}
    except Exception as e:
        frappe.log_error(str(e), "create_summary_breakup")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def update_summary_breakup():
    try:
        pass
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
                return {"success": True, "data": get_summary_breakups}
            else:
                return {"success": False, "message": "summary breakups not found"}
        else:
            return {"success": False, "message": "summary not found"}
    except Exception as e:
        frappe.log_error(str(e), "get_summary_breakup")
        return {"success": False, "message": str(e)}
