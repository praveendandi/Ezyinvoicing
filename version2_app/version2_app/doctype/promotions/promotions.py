# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class Promotions(Document):
	pass


@frappe.whitelist(allow_guest=True)
def update_promotions(name=None, status=None):
    doc = frappe.db.set_value('Promotions', name,'status', status, update_modified=False)
    frappe.db.commit()
    return True
