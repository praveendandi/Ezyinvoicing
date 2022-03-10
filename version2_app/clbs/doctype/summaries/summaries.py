# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document


class Summaries(Document):
	pass


@frappe.whitelist(allow_guest=True)
def get_summary(name):
    try:
        get_summary = frappe.db.get_value('Summaries', name, ["summary_title", "between_dates", "tax_payer_details", "location", "header", "footer", "terms_and_conditions"], as_dict=1)
        tax_payer_details = frappe.db.get_value('TaxPayerDetail', get_summary["tax_payer_details"], ["legal_name"], as_dict=1)
        tax_payer_location = frappe.db.get_value("Taxpayer Locations", get_summary["location"],["location","address","city","state","pin_code"])
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
        if not get_summary["terms_and_conditions"]:
            get_summary["terms_and_conditions"] = company_doc.summary_terms_and_conditions
        return {"success": True, "data": total_data}
    except Exception as e:
        frappe.log_error(str(e), "get_summary")
        return {"success": False, "message": str(e)}
