from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers, timestamps, fields
from pyhanko.sign.fields import SigSeedSubFilter
from pyhanko_certvalidator import ValidationContext
from pyhanko.sign import signers, fields, timestamps
from pyhanko import stamp
from pyhanko.pdf_utils.font import opentype
from pyhanko.pdf_utils import text, images


# Load signer key material from PKCS#12 file
# This assumes that any relevant intermediate certs are also included
# in the PKCS#12 file.
signer = signers.SimpleSigner.load_pkcs12(
    # pfx_file='/home/caratred/Desktop/projects/pyhanko/sign.pfx', passphrase=b'secret'
    pfx_file='/home/caratred/Desktop/projects/pyhanko/sign.pfx', passphrase=b'123'
)

# Set up a timestamping client to fetch timestamps tokens
# timestamper = timestamps.HTTPTimeStamper(
#     url='http://tsa.example.com/timestampService'
# )

# Settings for PAdES-LTA
signature_meta = signers.PdfSignatureMetadata(
    field_name='Signature', md_algorithm='sha256',
    # Mark the signature as a PAdES signature
    subfilter=SigSeedSubFilter.PADES,
    # We'll also need a validation context
    # to fetch & embed revocation info.
    # validation_context=ValidationContext(allow_fetching=True),
    # Embed relevant OCSP responses / CRLs (PAdES-LT)
    # embed_validation_info=True,
    # Tell pyHanko to put in an extra DocumentTimeStamp
    # to kick off the PAdES-LTA timestamp chain.
    use_pades_lta=True
)

pdf_signer = signers.PdfSigner(
    signature_meta, signer=signer, stamp_style=stamp.TextStampStyle(
        # the 'signer' and 'ts' parameters will be interpolated by pyHanko, if present
        stamp_text='This is custom text!\nSigned by: %(signer)s\nTime: %(ts)s',
        background=images.PdfImage(
            '/home/caratred/Desktop/projects/pyhanko/stamp.png')
    ),
)


with open('/home/caratred/Desktop/projects/pyhanko/input.pdf', 'rb') as inf:
    w = IncrementalPdfFileWriter(inf)
    fields.append_signature_field(
        w, sig_field_spec=fields.SigFieldSpec(
            'Signature', box=(200, -100, 400, 300)
        ),
        # appearance_text_params={'url': 'https://caratred.com'}
    )
    with open('/home/caratred/Desktop/projects/pyhanko/output.pdf', 'wb') as outf:
        pdf_signer.sign_pdf(
            w,
            # timestamper=timestamper,
            output=outf,
            appearance_text_params={'url': 'https://caratred.com'}

        )
