from __future__ import unicode_literals
import frappe
import requests
import os
import sys
from frappe.utils import cstr
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


@frappe.whitelist()
def add_signature(invoice=None, pfx_signature=None, signature_image=None, secret=None, X1=400, Y1=10, X2=590, Y2=70, company=None, summary=None):
    try:
        if secret:
            secret = bytes(secret, 'utf-8')
        site_name = cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        invoice_file = (
            folder_path
            + "/sites/"
            + site_name
        )
        signer = signers.SimpleSigner.load_pkcs12(
            # pfx_file='/home/caratred/Desktop/projects/pyhanko/sign.pfx', passphrase=b'secret'
            pfx_file=invoice_file+pfx_signature, passphrase=secret
        )
        signature_meta = signers.PdfSignatureMetadata(
            field_name='Signature', md_algorithm='sha256',
            subfilter=SigSeedSubFilter.PADES,
            use_pades_lta=True
        )
        pdf_signer = signers.PdfSigner(
            signature_meta, signer=signer, stamp_style=stamp.TextStampStyle(
                # the 'signer' and 'ts' parameters will be interpolated by pyHanko, if present
                stamp_text='\n\n\n\nTime: %(ts)s',
                background=images.PdfImage(invoice_file+signature_image)
            ),
        )
        file_name = os.path.basename(invoice)
        output_file_path = invoice_file+"/public/files/"+file_name
        with open(invoice_file+invoice, 'rb') as inf:
            w = IncrementalPdfFileWriter(inf)
            fields.append_signature_field(
                w, sig_field_spec=fields.SigFieldSpec(
                    'Signature', box=(X1, Y1, X2, Y2), on_page=-1
                ),
                # appearance_text_params={'url': 'https://caratred.com'}
            )
            with open(output_file_path, 'wb') as outf:
                pdf_signer.sign_pdf(
                    w,
                    output=outf,
                    # appearance_text_params={'url': 'https://caratred.com'}
                )
        files = {"file": open(output_file_path, 'rb')}
        payload = {'is_private': 1, 'folder': 'Home',
                   'doctype': 'Summaries', 'docname': summary}
        if company:
            site = company.host.rstrip('/')
        else:
            site = frappe.utils.get_url()
        upload_qr_image = requests.post(site + "/api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        if 'message' in response:
            frappe.db.sql(
                """DELETE FROM `tabFile` where`tabFile`.file_url = '{}'""".format(invoice))
            frappe.db.commit()
            return {"success": True, "file": response['message']['file_url']}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("add_signature",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e)}


def send_files(files, user_name, summary):
    try:
        if user_name:
            if frappe.db.exists("User Signature", user_name):
                new_files = []
                company_doc = frappe.get_last_doc("company")
                clbs_settings = frappe.get_last_doc('CLBS Settings')
                get_doc = frappe.get_doc("User Signature", user_name)
                if not get_doc.signature_pfx and not get_doc.signature_image and not get_doc.pfx_password:
                    return {"success": False, "message": "Missing user signature details."}
                for each in files:
                    signature = add_signature(each, get_doc.signature_pfx, get_doc.signature_image,
                                              get_doc.pfx_password, X1=clbs_settings.x1,
                                              Y1=clbs_settings.y1, X2=clbs_settings.x2,
                                              Y2=clbs_settings.y2, company=company_doc, summary=summary)
                    if not signature["success"]:
                        return signature
                    new_files.append(signature["file"])
                return {"success": True, "files": new_files}
            return {"success": False, "message": "User Not Found"}
        return {"success": False, "message": "User Name not given"}
    except Exception as e:
        frappe.log_error(str(e), "send_files")
        return{"success": False, "message": str(e)}


@frappe.whitelist()
def add_esignature_to_invoice(invoice_number=None, based_on="user"):
    try:
        company = frappe.get_last_doc("company")
        get_value = frappe.db.get_value("Invoices", invoice_number, ["invoice_file"])
        if not frappe.db.exists("CLBS Settings", company.name):
            return {"success": False, "message": "Add signature coordinates in settings"}
        if company.e_signature == "User":
            user_name = frappe.session.user
            if not frappe.db.exists("User Signature", user_name):
                return {"success": False, "message": "add your signature in user settings"}
            coordinates = frappe.db.get_value("CLBS Settings", company.name, ["X1", "Y1", "X2", "Y2"], as_dict=True)
            user_signature = frappe.db.get_value("User Signature", user_name, ["signature_image","signature_pfx","pfx_password"],as_dict=True)
            print(user_signature)
            add_sig = add_signature(invoice=get_value, pfx_signature=user_signature["signature_pfx"], signature_image=user_signature["signature_image"], secret=user_signature["pfx_password"], X1=coordinates["X1"], Y1=coordinates["Y1"], X2=coordinates["X2"], Y2=coordinates["Y2"], company=company, summary=invoice_number)
            return add_sig
        if company.e_signature == "Organization":
            coordinates = frappe.db.get_value("CLBS Settings", company.name, ["X1", "Y1", "X2", "Y2"], as_dict=True)
            add_sig = add_signature(invoice=get_value, pfx_signature=company.signature_pfx, signature_image=company.signature_image, secret=company.pfx_password, X1=coordinates["X1"], Y1=coordinates["Y1"], X2=coordinates["X2"], Y2=coordinates["Y2"], company=company, summary=invoice_number)
            return add_sig
    except Exception as e:
        frappe.log_error(str(e), "add_esignature_to_invoice")
        return{"success": False, "message": str(e)}