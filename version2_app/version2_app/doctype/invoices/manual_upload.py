from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import random
import traceback
import string
from frappe.utils import get_site_name
import time
# from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError, CheckRatePercentages
# from version2_app.version2_app.doctype.invoices.invoices import insert_items,insert_hsn_code_based_taxes,send_invoicedata_to_gcb,TaxSummariesInsert,generateIrn
# from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
# from PyPDF2 import PdfFileWriter, PdfFileReader
# import fitz
import math