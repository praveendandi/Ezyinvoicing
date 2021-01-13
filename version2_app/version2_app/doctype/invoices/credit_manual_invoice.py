from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
from version2_app.version2_app.doctype.invoices.invoices import *
import pandas as pd
import json
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






@frappe.whitelist(allow_guest=True)
def CreditManualInvoice(data):
    try:
        calculated_data = calulate_items(data['items'])
        print(calculated_data)
        guest = data['guest']
        # company_code
        if calculated_data['success'] == True:
           # guest['invoice_file'] = filepath
            insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
            if insertInvoiceApiResponse['success']== True:
                print("Invoice Created",insertInvoiceApiResponse)
                return {"success":True,"message":"Invoice Created"}

            else:
                error_data['error_message'] = insertInvoiceApiResponse['message']
                error_data['amened'] = amened
                error_data["items_data"]=calulateItemsApiResponse['data']
                errorInvoice = Error_Insert_invoice(error_data)
                print("insertInvoiceApi fialed:  ",insertInvoiceApiResponse['message'])
                return {"success":False,"message":insertInvoiceApiResponse['message']}
