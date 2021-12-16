# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RedgCard(Document):
	pass


@frappe.whitelist(allow_guest=True)
def update_signature(name=None, signature=None, work_station=None, tab=None):
    # information_folio = frappe.get_doc('Information Folio', name)
    # information_folio.signature = signature
    # information_folio.save(ignore_permissions=True,  # ignore write permissions during insert
    #                        ignore_version=True  # do not create a version record
    #                        )
    doc = frappe.db.set_value('Redg Card', name,
                              'signature', signature, update_modified=False)

    frappe.db.commit()
    # data = {
    #     'information_invoice': name,
    #     'signature': signature,
    #     'work_station': work_station,
    #     'tab': tab
    # }
    # frappe.publish_realtime(
    #     "custom_socket", {'message': 'Signature Updated', 'data': data})

    return True