# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Promotions(Document):
	pass


@frappe.whitelist()
def update_promotions(name=None, status=None):
    doc = frappe.db.set_value('Promotions', name,'status', status, update_modified=False)
    frappe.db.commit()
    data = {
        'name': name,
        'status': status
    }
    frappe.publish_realtime(
        "custom_socket", {'message': 'Promotions Updated', 'data': data})
    return True
