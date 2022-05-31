from __future__ import unicode_literals
import frappe
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


@frappe.whitelist(allow_guest=True)
def add_signature(invoice=None, pfx_signature=None, secret=b'123', X1=400, Y1=10, X2=590, Y2=70):
    try:
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
                stamp_text='This is custom text!\nSigned by: %(signer)s\nTime: %(ts)s',
                # background=images.PdfImage('')
            ),
        )
        with open(invoice_file+invoice, 'rb') as inf:
            w = IncrementalPdfFileWriter(inf)
            fields.append_signature_field(
                w, sig_field_spec=fields.SigFieldSpec(
                    'Signature', box=(X1, Y1, X2, Y2)
                ),
                # appearance_text_params={'url': 'https://caratred.com'}
            )
            with open('/home/caratred/output.pdf', 'wb') as outf:
                pdf_signer.sign_pdf(
                    w,
                    output=outf,
                    # appearance_text_params={'url': 'https://caratred.com'}
                )
    except Exception as e:
        frappe.log_error(str(e), "add_signature")
        return{"success": False, "message": str(e)}