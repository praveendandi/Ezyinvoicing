# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class IdTextDocumentDetails(Document):
    pass


@frappe.whitelist()
def insert_doc_details(data):
    try:
        doc = frappe.get_doc(
            {
                "doctype": "Id Text Document Details",
                "text": data["text"],
                "label": data["label"],
                "filepath": data["filepath"],
                "ocr_type": data["ocr_type"],
                "clean_text": data["clean_text"],
            }
        )
        doc.insert()
        return True
    except Exception as e:
        print(e)
