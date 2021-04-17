# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ActiveTablets(Document):
    pass


@frappe.whitelist(allow_guest=True)
def validateConnection(property_code=None, ip_address=None, type=None):
    # return True
    company = frappe.get_doc('company', property_code)
    if company is not None:
        return True
    else:
        return False


@frappe.whitelist(allow_guest=True)
def removeTab(name=None):
    # delete tablet config
    frappe.db.delete('Tablet Config', {
        'Tablet': name})
    # delete active tablet
    frappe.delete_doc('Active Tablets', name)
    return True

@frappe.whitelist(allow_guest=True)
def updateTab(name=None,status=None):
    #update Tab status
    doc = frappe.get_doc('Active Tablets',name)
    doc.status = status
    doc.save()
    return True
