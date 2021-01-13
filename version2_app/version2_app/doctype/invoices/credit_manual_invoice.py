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
import os, os.path
import random, string
from random import randint
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
    # try:
    # print(data)
    company_code = {"code":data['company_code']}
    getTaxPayerDetailsResponse = {'data':data['taxpayer']}
    # calula {'guest_data':guest,'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format}
    # inv  {"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'].__dict__,"items_data":calulateItemsApiResponse['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened}
    # guest = {'name': ' Mr. Sachin Powle', 'invoice_number': '54617', 'membership': '', 'invoice_date': '10-DEC-20 06:28:00', 'items': [{'date': '08-12-20', 'item_value': 4500.0, 'sac_code': 'No Sac', 'sort_order': 1, 'name': 'Room Charges'}, {'date': '09-12-20', 'item_value': 4500.0, 'sac_code': 'No Sac', 'sort_order': 4, 'name': 'Room Charges'}], 'invoice_type': 'B2B', 'gstNumber': '27AACCI8791B1ZG', 'room_number': 303, 'company_code': 'NIK-01', 'confirmation_number': '1377005', 'start_time': '2021-01-13 07:41:03.242178', 'print_by': '9832ITRABHO23-DEC-2019', 'invoice_category': 'Tax Invoice'}, 'items': [{'date': '08-12-20', 'item_value': 4500.0, 'sac_code': 'No Sac', 'sort_order': 1, 'name': 'Room Charges'}, {'date': '09-12-20', 'item_value': 4500.0, 'sac_code': 'No Sac', 'sort_order': 4, 'name': 'Room Charges'}],'invoice_number': '54617', 'company_code': 'NIK-01', 'invoice_item_date_format': '%d-%m-%y'}
    # tax_payer = {'doctype': 'TaxPayerDetail', 'name': '27AACCI8791B1ZG', '_default_new_docs': {}, 'flags': {}, '_meta': <frappe.model.meta.Meta object at 0x7f3888feb6a0>, 'owner': 'Guest', 'creation': datetime.datetime(2020, 12, 24, 10, 20, 43, 576790), 'modified': datetime.datetime(2020, 12, 24, 10, 20, 43, 576790), 'modified_by': 'Guest', 'parent': None, 'parentfield': None, 'parenttype': None, 'idx': 0, 'docstatus': 0, 'gst_number': '27AACCI8791B1ZG', 'legal_name': 'INEGA TALENT AND PRODUCTION PRIVATE LIMITED', 'email': ' ', 'address_1': 'SAUMIL HOUSE', 'address_2': '35    ', 'location': 'BANDRA WEST', 'pincode': '400058', 'gst_status': 'ACT', 'tax_type': 'REG', 'company': 'NIK-01', 'trade_name': 'INEGA TALENT MANAGEMENT PRIVATE LIMITED', 'phone_number': ' ', 'state_code': '27', 'last_fetched': '2020-12-24', 'address_floor_number': '', 'address_street': 'PALI VILLAGE 16 TH ROAD', 'block_status': '', 'status': 'Active', '_user_tags': None, '_comments': None, '_assign': None, '_liked_by': None, 'dont_update_if_missing': []}
    # # req {'guest_data':guest,company_code:"","taxpayer":getTaxPayerDetailsResponse['data'],'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"invoice_number":guest['invoice_number'],"amened":amened}
    # data = {'guest_data':guest,company_code:"","taxpayer":getTaxPayerDetailsResponse['data'],'items':guest['items'],"invoice_number":guest['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":companyCheckResponse['data'].invoice_item_date_format,"invoice_number":guest['invoice_number'],"amened":amened}
    # print("..........",data['items'])
    # data['guest'] = guest
    calculated_data = calulate_items({'guest_data':data['guest'],'items':data['guest']['items'],"invoice_number":data['guest']['invoice_number'],"company_code":company_code['code'],"invoice_item_date_format":'%d-%m-%y'})
    # calculated_data = calulate_items({"items":data['items'],"company_code":data['company_code']})
    # print(calculated_data,"//////aaaaaaaaaaaaa")
    total_invoice_amount = data['total_invoice_amount']
    
    
    if calculated_data['success'] == True:
        # guest['invoice_file'] = filepath
        insertInvoiceApiResponse = insert_invoice({"guest_data":guest,"company_code":company_code['code'],"taxpayer":getTaxPayerDetailsResponse['data'],"items_data":calculated_data['data'],"total_invoice_amount":total_invoice_amount,"invoice_number":guest['invoice_number'],"amened":amened})
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
    # except Exception as e:
    #     print(str(e),"  CreditManualInvoice")
    #     return {"success":False,"message":str(e)}            
