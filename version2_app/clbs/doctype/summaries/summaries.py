# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import frappe
import html2text
from frappe.model.document import Document


class Summaries(Document):
    pass


@frappe.whitelist(allow_guest=True)
def get_summary(name):
    try:
        if frappe.db.exists("Summaries", name):
            get_summary = frappe.db.get_value('Summaries', name, [
                                            "summary_title", "between_dates", "tax_payer_details", "location", "header", "footer", "terms_and_conditions"], as_dict=1)
            tax_payer_details = frappe.db.get_value(
                'TaxPayerDetail', get_summary["tax_payer_details"], ["legal_name"], as_dict=1)
            tax_payer_location = frappe.db.get_value("Taxpayer Locations", get_summary["location"], [
                                                    "address", "location", "city", "state", "pin_code"])
            total_data = get_summary.update(tax_payer_details)
            if tax_payer_location:
                total_data["location"] = ", ".join(tax_payer_location)
            else:
                total_data["location"] = None
            company_doc = frappe.get_last_doc('company')
            clbs_settings = frappe.get_doc("CLBS Settings",company_doc.name)
            if not get_summary["header"]:
                get_summary["header"] = clbs_settings.summary_header
            if not get_summary["footer"]:
                get_summary["footer"] = clbs_settings.summary_footer
            ht = html2text.HTML2Text()
            if get_summary["terms_and_conditions"] == "" or get_summary["terms_and_conditions"] == None:
                if clbs_settings.summary_terms_and_conditions:
                    get_summary["terms_and_conditions"] = ht.handle(clbs_settings.summary_terms_and_conditions)
                else:
                    get_summary["terms_and_conditions"] = ""
            else:
                get_summary["terms_and_conditions"] = ht.handle(get_summary["terms_and_conditions"])
            return {"success": True, "data": total_data}
        else:
            return {"success": False, "message": "no data found"}
    except Exception as e:
        frappe.log_error(str(e), "get_summary")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_all_summary(filters=[], limit_start=0, limit_page_length=20):
    try:
        sql_filters = ""
        if len(filters) > 0:
            sql_filters = " where "+(' and '.join("{} {} {}".format(each[0], each[1], each[2]) if (isinstance(each[2], list) or isinstance(each[2], int)) else "{} {} '{}'".format(each[0], each[1], each[2]) for each in filters))
            print(sql_filters)
        data = frappe.db.sql("""SELECT acc.account_number gl.debit gl.credit FROM `tabGL Entry` gl LEFT JOIN `tabAccount` acc ON gl.account = acc.name{} LIMIT 10 OFFSET 15""".format(filters), as_dict=0)
    except Exception as e:
        frappe.log_error(str(e), "get_summary")
        return {"success": False, "message": str(e)}
    
@frappe.whitelist(allow_guest=True)
def delete_summaries(name=None, status=None):
    try:
        if not status:
            return {"success": False, "message": "status is required"}
        if frappe.db.exists("Summaries", name):
            frappe.db.set_value('Summaries', name, "status", status)
            # frappe.db.sql("""UPDATE `tabSummary Breakups` SET deleted_breakups=1 where summaries='{}'""".format(name))
            frappe.db.sql("""UPDATE `tabInvoices` SET summary=null, clbs_summary_generated=0, invoice_submitted_in_clbs=0 where summary='{}'""".format(name))
            frappe.db.commit()
            delete_files = frappe.db.delete("File", {"attached_to_name": name})
            frappe.db.commit()
            return {'success': True, 'message': "summary "+status}
        else:
            return {"success": False, 'message': "summary not found"}
    except Exception as e:
        frappe.log_error(str(e), "get_summary")
        return {"success": False, "message": str(e)}
    
@frappe.whitelist(allow_guest=True)
def summary_activity_log(summary=None):
    try:
        if summary:
            get_summary_log = frappe.db.get_list("Version",filters=[["docname","=",summary]], fields=['*'])
            for each in get_summary_log:
                if "terms_and_conditions" in each["data"]:
                    log = json.loads(each["data"])
                    terms_list = log["changed"][0]
                    each["data"] = json.dumps({"changed":[["terms and conditions has been changed"]]})
                if "contacts" in each["data"]:
                    # each = each.as_dict()
                    log = json.loads(each["data"])
                    contact_list = log["changed"][0]
                    for index, con in enumerate(contact_list):
                        if con not in ["contacts","[]"]:
                            con = json.loads(con)
                            if isinstance(con, list):
                                if len(con)>0:
                                    contacts = frappe.db.get_list("Contacts",filters=[["name","in",con]], pluck="contact_name")
                                    contact_list[index] =  json.dumps(contacts)
                    log["changed"][0] = contact_list
                    each["data"] = json.dumps(log)
            get_payments_names = frappe.db.get_list("Summary Payments", filters=[["summary","=",summary]], pluck="name")
            if get_payments_names or len(get_payments_names) > 0:
                get_payment_log = frappe.db.get_list("Version", filters=[["docname","in",get_payments_names]], fields=['*'])
                get_summary_log.extend(get_payment_log)
            return {"success":True, "data":get_summary_log}
    except Exception as e:
        frappe.log_error(str(e), "summary_activity_log")
        return {"success": False, "message": str(e)}
    