from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn
# from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError,error_invoice_calculation
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
import pandas as pd
import json
import string
import qrcode
import os, os.path
import random, string
from random import randint
from google.cloud import storage
# from datetime import da
import datetime
import random
import math
from frappe.utils import get_site_name
from frappe.utils import logger
import time
import os




# @frappe.whitelist(allow_guest=True)
# def Convert_to_manual_tax_invoice(invoice_number):
#     try:
#         invoice = frappe.get_doc("Invoices",invoice_number)
#         invoice.invoice_from = "Web"
#         invoice.