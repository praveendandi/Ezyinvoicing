# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from version2_app.version2_app.doctype.invoices.invoices import check_company_exist_for_Irn,gsp_api_data,get_tax_payer_details

class IRNObjects(Document):
    pass


import pandas as pd
import json
import os, os.path,traceback,sys
import random, string
from random import randint
import datetime
from frappe.utils import get_site_name
from frappe.utils import logger

@frappe.whitelist(allow_guest=True)
def IrnObject(invoice_number):
    try:
        invoice = frappe.get_doc('Invoices', invoice_number)
        # if invoice.irn_generated == "Success":
        # 	return {"success":True,"message":"Already IRN Generated"}
        if invoice.invoice_type=="B2C":
            return {"success":False,"message":"B2C Invoice"}	
        # get seller details
        if invoice.invoice_category == "Tax Invoice":
            category = "INV"
        elif invoice.invoice_category == "Debit Invoice":	
            category = "DBN"
        else:
            category = "CRN"	
        # IRNObjectdoc = frappe.get_doc({'doctype':'IRN Objects','invoice_number':invoice_number,"invoice_category":invoice.invoice_category})
        company_details = frappe.get_doc('company',invoice.company)
        # get gsp_details
        credit_note_items = []
        companyData = {
            "code": company_details.name,
            "mode": company_details.mode,
            "provider": company_details.provider
        }
        GSP_details = gsp_api_data(companyData)
        # get taxpayer details
        GspData = {
            "gstNumber": invoice.gst_number,
            "code": invoice.company,
            "apidata": GSP_details['data']
        }
        taxpayer_details = get_tax_payer_details(GspData)
        #gst data
        gst_data = {
            "Version": "1.1",
            "TranDtls": {
                "TaxSch": "GST",
                "SupTyp": "B2B",
                "RegRev": "N",
                "IgstOnIntra": "Y" if invoice.place_of_supply == company_details.state_code and invoice.sez == 1 else "N"
            },
            "SellerDtls": {
                "Gstin":
                GSP_details['data']['gst'],
                "LglNm":
                company_details.legal_name,
                "TrdNm":
                company_details.trade_name,
                "Addr1":
                company_details.address_1,
                "Addr2":
                company_details.address_2,
                "Loc":
                company_details.location,
                "Pin":
                193502 if company_details.mode == "Testing" else
                company_details.pincode,
                "Stcd":
                "01" if company_details.mode == "Testing" else
                company_details.state_code,
                "Ph":
                company_details.phone_number,
                "Em":
                company_details.email
            },
            "BuyerDtls": {
                "Gstin":
                taxpayer_details['data'].gst_number,
                "LglNm":
                taxpayer_details['data'].legal_name,
                "TrdNm":
                taxpayer_details['data'].trade_name,
                "Pos":
                "01" if company_details.mode == "Testing" else
                # company_details.state_code,
                invoice.place_of_supply,
                "Addr1":
                taxpayer_details['data'].address_1,
                "Addr2":
                taxpayer_details['data'].address_2,
                "Loc":
                taxpayer_details['data'].location,
                "Pin":
                int(taxpayer_details['data'].pincode),
                "Stcd":
                taxpayer_details['data'].state_code,
                # "Ph": taxpayer_details.phone_number,
                # "Em": taxpayer_details.
            },
            "DocDtls": {
                "Typ":
                category,
                "No":
                invoice.invoice_number + str(random.randint(0, 100)) +
                    'T' if company_details.mode == 'Testing' else
                    invoice.invoice_number,
                "Dt":
                datetime.datetime.strftime(invoice.invoice_date,
                                            '%d/%m/%Y')
            },
            "ItemList": [],
            "CreditItemList":[],
        }
        total_igst_value = 0
        total_sgst_value = 0
        total_cgst_value = 0
        total_cess_value = 0
        total_state_cess_value = 0
        discount_after_value = 0
        discount_before_value = 0
        ass_value = 0
        credit_total_igst_value = 0
        credit_total_sgst_value = 0
        credit_total_cgst_value = 0
        credit_total_cess_value = 0
        credit_total_state_cess_value = 0
        credit_discount_after_value = 0
        credit_discount_before_value = 0
        credit_ass_value = 0
        for index, item in enumerate(invoice.items):
            # print(item.sac_code,"HsnCD")
            if item.is_credit_item == "No" and item.taxable == "Yes" and item.type != "Non-Gst":
                total_igst_value += item.igst_amount
                total_sgst_value += item.sgst_amount
                total_cgst_value += item.cgst_amount
                total_cess_value += item.cess_amount
                total_state_cess_value += item.state_cess_amount
                ass_value += item.item_value
                i = {
                    "SlNo":
                    str(index + 1),
                    "PrdDesc":
                    item.item_name,
                    "IsServc":
                    "Y" if item.item_type == "SAC" else
                    "N",
                    "HsnCd":
                    item.sac_code if item.sac_code != 'No Sac' else '',
                    "Qty":int(item.quantity),
                    "Unit":item.unit_of_measurement,
                    "FreeQty":
                    0,
                    "UnitPrice":
                    round(item.item_value, 2),
                    "TotAmt":
                    round(item.item_value, 2),
                    "Discount":
                    0,
                    "AssAmt":
                    0 if item.sac_code == 'No Sac' else round(
                        item.item_value, 2),
                    "GstRt":
                    item.gst_rate,
                    "IgstAmt":
                    round(item.igst_amount, 2),
                    "CgstAmt":
                    round(item.cgst_amount, 2),
                    "SgstAmt":
                    round(item.sgst_amount, 2),
                    "CesRt":
                    item.cess,
                    "CesAmt":
                    round(item.cess_amount, 2),
                    "CesNonAdvlAmt":
                    0,
                    "StateCesRt": item.state_cess,
                    "StateCesAmt": round(item.state_cess_amount,2),
                    "StateCesNonAdvlAmt":
                    0,
                    "OthChrg":
                    00,
                    "TotItemVal":
                    round(item.item_value_after_gst, 2),
                }
                gst_data['ItemList'].append(i)
            else:
                if item.item_mode == "Credit" and item.type!="Non-Gst":
                    credit_total_igst_value += abs(item.igst_amount)
                    credit_total_sgst_value += abs(item.sgst_amount)
                    credit_total_cgst_value += abs(item.cgst_amount)
                    credit_total_cess_value += abs(item.cess_amount)
                    credit_total_state_cess_value += abs(item.state_cess_amount)
                    credit_ass_value += abs(item.item_value)
                    i = {
                        "SlNo":
                        str(index + 1),
                        "PrdDesc":
                        item.item_name,
                        "IsServc":
                        "Y",
                        "HsnCd":
                        item.sac_code if item.sac_code != 'No SAC' else '',
                        "Qty":
                        1,
                        "FreeQty":
                        0,
                        "UnitPrice":
                        abs(round(item.item_value, 2)),
                        "TotAmt":
                        abs(round(item.item_value, 2)),
                        "Discount":
                        0,
                        "AssAmt":
                        0 if item.sac_code == 'No SAC' else abs(round(
                            item.item_value, 2)),
                        "GstRt":
                        item.gst_rate,
                        "IgstAmt":
                        abs(round(item.igst_amount, 2)),
                        "CgstAmt":
                        abs(round(item.cgst_amount, 2)),
                        "SgstAmt":
                        abs(round(item.sgst_amount, 2)),
                        "CesRt":
                        item.cess,
                        "CesAmt":
                        abs(item.cess_amount),
                        "CesNonAdvlAmt":
                        0,
                        "StateCesRt":
                        item.state_cess,
                        "StateCesAmt":
                        abs(item.state_cess_amount),
                        "StateCesNonAdvlAmt":
                        0,
                        "OthChrg":
                        00,
                        "TotItemVal":
                        abs(round(item.item_value_after_gst, 2)),
                    }
                    gst_data['CreditItemList'].append(i)
                
        discount_before_value = abs(discount_before_value)	
        discount_after_value = abs(discount_after_value)
        TotInnVal = round(invoice.amount_after_gst, 2) - round(discount_after_value,2)
        TotInvValFc = round(invoice.amount_after_gst, 2) - round(discount_after_value,2)
        
        # print(TotInnVal,TotInvValFc)
        gst_data["ValDtls"] = {
            "AssVal": round(ass_value, 2), 
            "CgstVal": round(total_cgst_value, 2),
            "SgstVal": round(total_sgst_value, 2),
            "IgstVal": round(total_igst_value, 2),
            "CesVal": round(total_cess_value, 2),
            "StCesVal": round(total_state_cess_value,2),
            "Discount": round(discount_after_value,2),
            "OthChrg": 0,
            "RndOffAmt": 0,
            "TotInvVal": round(TotInnVal,2),
            "TotInvValFc": round(TotInvValFc, 2)
        }
        
        gst_data['CreditValDtls']= {"AssVal": round(credit_ass_value, 2), 
            "CgstVal": round(credit_total_cgst_value, 2),
            "SgstVal": round(credit_total_sgst_value, 2),
            "IgstVal": round(credit_total_igst_value, 2),
            "CesVal": round(credit_total_cess_value, 2),
            "StCesVal": round(credit_total_state_cess_value,2),
            "Discount": round(credit_discount_after_value,2),
            "OthChrg": 0,
            "RndOffAmt": 0,
            "TotInvVal": round(invoice.credit_value_before_gst, 2),
            "TotInvValFc": round(invoice.credit_value_after_gst, 2)}
        # print(gst_data['ValDtls'])
        if gst_data['CreditValDtls']['AssVal']==0:
            del gst_data['CreditValDtls']
            del gst_data['CreditItemList']
        if gst_data['ValDtls']['AssVal']==0:
            del gst_data['ValDtls']
            del gst_data['ItemList']	
        return {"success":True,"data":gst_data}
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing IrnObject Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}



# @frappe.whitelist(allow_guest=True)
# def getsuccessirnobject(invoiceNumber):
# 	get_data = frappe.db.get_list('IRN Objects',filters={'invoice_number': invoiceNumber,'irn_status':'Success'})
# 	if len(get_data)>0:
# 		getobj = frappe.get_doc('IRN Objects',get_data[0])
# 		print(getobj)
# 		return {"success":True,"data":getobj}