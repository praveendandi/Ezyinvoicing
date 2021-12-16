# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ActiveWorkStations(Document):
	pass

@frappe.whitelist(allow_guest=True)
def removeWorkstation(name=None):
    # delete tablet config
    print("remove workstation", name)
    frappe.db.delete('Tablet Config', {
        'work_station': name})
    # delete active tablet
    frappe.delete_doc('Active Work Stations', name)
    return True