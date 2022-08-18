# -*- coding: utf-8 -*-
# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document

class DocumentTypes(Document):
	pass


def add_document_sequence(doc, method=None):
    try:
        get_count = frappe.db.count('Document Types')
        get_count = get_count+1
        doc.sequence = get_count
    except Exception as e:
        frappe.log_error(str(e), "add_document_sequence")
        return {"Success":False,"message":str(e)}
    
@frappe.whitelist(allow_guest=True)
def update_document_sequence(data):
    try:
        # print(data,"................")
        # if isinstance(data, str):
        #     print("......................")
        #     data = json.loads(data)
        if len(data["data"]) > 0:
            for each in data["data"]:
                print(each,"..................")
                frappe.db.set_value("Document Types", each["name"], "sequence", each["sequence"])
                frappe.db.commit()
            return {"success": True, "message": "Sequence updated"}
        return {"success": False, "message": "No data found"}
    except Exception as e:
        frappe.log_error(str(e), "add_document_sequence")
        return {"Success":False,"message":str(e)}