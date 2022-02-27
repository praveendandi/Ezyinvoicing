# Copyright (c) 2013, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import itertools

import frappe
import pandas as pd


def execute(filters=None):
    if "gst_number" in filters.keys():
        data = get_summary(filters)
        if data["success"] == False:
            return data
        columns, data = data["columns"], data["data"]
        return columns, data
    return [], []


def get_summary(filters):
    try:
        get_invoices = frappe.db.get_list("Invoices", filters=[['invoice_date', 'between', [
                                        filters["from_date"], filters["to_date"]]], ["gst_number", "=", filters["gst_number"]]], pluck='name')
        total_items = []
        if len(get_invoices) > 0:
            get_items = frappe.db.get_list(
                "Items", filters=[['parent', 'in', get_invoices]], fields=["*"])
            get_item_dates = frappe.db.get_list(
                "Items", filters=[['parent', 'in', get_invoices]], pluck='date')
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
                each["Date_string"] = str(
                    min(get_item_dates))+" to "+str(max(get_item_dates))
                total_items.append(each)
        df = pd.DataFrame.from_records(total_items)
        data = df.groupby('service_type',as_index=False).agg({"Date_string":'first', "service_type": 'first', "invoice_category": 'first', "item_value_after_gst": 'sum'})
        data.rename(columns={'Date_string': 'Date', 'service_type': 'Service Type','invoice_category':'Invoice Type','item_value_after_gst':'Amount'}, inplace=True)
        data = data.values.tolist()
        print(data)
        columns = ["Date", "Service Type", "Invoice Type", "Amount"]
        return {"success":True, "data":data, "columns":columns}
    except Exception as e:
        return {"success":False, "message": str(e)}
