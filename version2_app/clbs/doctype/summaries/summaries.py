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
        get_summary = frappe.db.get_value('Summaries', name, ["summary_title"])
    except Exception as e:
        frappe.log_error(str(e), "get_summary_breakup")
        return {"success": False, "message": str(e)}
