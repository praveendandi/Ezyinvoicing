# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SummaryPayments(Document):
	pass


def summary_payments(doc, method=None):
    try:
        if doc.summary:
            if frappe.db.exists("Summaries", {"name": doc.summary, "signature_attached":1}):
                frappe.db.set_value("Summaries", doc.summary, "signature_attached", 0)
                frappe.db.commit()
    except Exception as e:
        pass