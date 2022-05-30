from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, timestamps, fields
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko_certvalidator import ValidationContext
from pyhanko.sign import signers, fields, timestamps
from pyhanko import stamp
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils import text, images


class UserSignature(Document):
    pass


@frappe.whitelist(allow_guest=True)
def add_signature(user=None, summary=None):
    try:
        if user and summary:
            get_signature = frappe.db.get_value("User Signature", {"users":user}, ["signature_image","signature_pfx"],as_dict=1)
            print(get_signature)
    except Exception as e:
        frappe.log_error(str(e), "add_signature")
        return{"success": False, "message": str(e)}