# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

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
            print(get_summary,"//////")
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
            if not get_summary["header"]:
                get_summary["header"] = company_doc.summary_header
            if not get_summary["footer"]:
                get_summary["footer"] = company_doc.summary_footer
            if get_summary["terms_and_conditions"] == "" or get_summary["terms_and_conditions"] == None:
                get_summary["terms_and_conditions"] = company_doc.summary_terms_and_conditions
            else:
                ht = html2text.HTML2Text()
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
        pass
