# # -*- coding: utf-8 -*-
# # Copyright (c) 2020, caratred and contributors
# # For license information, please see license.txt

from __future__ import unicode_literals
from logging import exception
# from typing_extensions import Self
from unittest import expectedFailure
import frappe
from frappe import database
from frappe.model.document import Document
import requests
from frappe.utils import data as date_util
from version2_app.version2_app.doctype.invoices.credit_generate_irn import CreditgenerateIrn
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError,error_invoice_calculation
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages, SCCheckRatePercentages
from version2_app.version2_app.doctype.invoices.referrence_payments_parser import paymentsAndReferences
import pandas as pd
import traceback
import json
import string
import qrcode
import os, os.path,sys
import importlib.util
import random, string
from random import randint
from google.cloud import storage
# from datetime import da
import datetime
import random
import math
from frappe.utils import get_site_name
from frappe.utils import logger
from version2_app.events import invoiceCreated
import time
import os
import json

from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz
from frappe.utils import cstr


frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api")

class Invoices(Document):



    @frappe.whitelist()
    def cancelIrn(self, invoice_number, reason='wrong Entry'):
        try:
            # get invoice details
            invoice = frappe.get_doc('Invoices', invoice_number)
            # get seller details

            company_details = check_company_exist_for_Irn(invoice.company)
            # get gsp_details
            gsp_data = {"mode":company_details['data'].mode,"code":company_details['data'].name,"provider":company_details['data'].provider}
            GSP_details = gsp_api_data_for_irn(gsp_data)
            # GSP_details = gsp_api_data(company_details.name,
            # 						   company_details.mode,
            # 						   company_details.provider)

            # if invoice.has_credit_items=="Yes" and company_details['data'].allowance_type == "Credit" and len(invoice.irn_number)<3:
            if invoice.invoice_category == "Credit Invoice":
                credit_cancel_response = cancel_irn(invoice.credit_irn_number, GSP_details, reason,company_details['data'],invoice_number)
                if credit_cancel_response['success']:
                    # invoice.cancelled_on = cancel_response['result']['CancelDate']
                    # invoice.cancel_message = reason
                    invoice.credit_irn_cancelled = 'Yes'
                    invoice.credit_irn_generated = 'Cancelled'
                    invoice.irn_cancelled = 'Yes'
                    invoice.irn_generated = 'Cancelled'
                    invoice.save()
                    return {
                        "success": True,
                        "message": "E-Invoice is cancelled successfully"
                    }
                    return {"success":True,"message":"E-Invoice is cancelled successfully and credit notes failed"}	
                else:
                    credit_error_message = credit_cancel_response["message"]
                    logger.error(f"{invoice_number},     cancel_irn,   {credit_error_message}")
                    return {"success": False, "message": credit_error_message}
            cancel_response = cancel_irn(invoice.irn_number, GSP_details, reason,company_details['data'],invoice_number)
            if cancel_response['success']:
                invoice.cancelled_on = cancel_response['result']['CancelDate']
                invoice.cancel_message = reason
                invoice.irn_cancelled = 'Yes'
                invoice.irn_generated = 'Cancelled'
                invoice.save()
                if invoice.has_credit_items=="Yes" and company_details['data'].allowance_type == "Credit":
                    credit_cancel_response = cancel_irn(invoice.credit_irn_number, GSP_details, reason,company_details['data'],invoice_number)
                    if credit_cancel_response['success']:
                        # invoice.cancelled_on = cancel_response['result']['CancelDate']
                        # invoice.cancel_message = reason
                        invoice.credit_irn_cancelled = 'Yes'
                        invoice.credit_irn_generated = 'Cancelled'
                        invoice.save()
                        return {
                            "success": True,
                            "message": "E-Invoice is cancelled successfully"
                        }
                        return {"success":True,"message":"E-Invoice is cancelled successfully and credit notes failed"}	
                    else:
                        credit_error_message = credit_cancel_response["message"]
                        logger.error(f"{invoice_number},     cancel_irn,   {credit_error_message}")
                        return {"success": False, "message": credit_error_message}
                return {
                    "success": True,
                    "message": "E-Invoice is cancelled successfully"
                    }		
            else:
                error_message = cancel_response["message"]
                frappe.log_error(frappe.get_traceback(), invoice_number)
                logger.error(f"{invoice_number},     cancel_irn,   {error_message}")
                return {"success": False, "message": cancel_response["message"]}
        except Exception as e:
            print(e,"cancel irn")
            # frappe.log_error(frappe.get_traceback(), invoice_number)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            frappe.log_error("Ezy-invoicing cancelIrn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
            logger.error(f"{invoice_number},     cancelIrn,   {str(e)}")
            return {"success": False, "message": str(e)}


    def getTaxPayerDetails(self, gstNumber):
        try:
            gstDetails = frappe.get_doc('TaxPayerDetail', gstNumber)
            return {"success": True, "data": gstDetails}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            frappe.log_error("Ezy-invoicing getTaxPayerDetails","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
            print(e, "get TaxPayerDetail")

    def updateTaxPayerDetails(self, taxPayerDetails):
        taxPayerDeatilsData = frappe.get_doc('TaxPayerDetail',
                                             taxPayerDetails['gst'])
        # print(taxPayerDeatils.name)
        taxPayerDeatilsData.address_1 = taxPayerDetails['address_1']
        taxPayerDeatilsData.address_2 = taxPayerDetails['address_2']
        taxPayerDeatilsData.email = taxPayerDetails['email']
        taxPayerDeatilsData.phone_number = taxPayerDetails['phone_number']
        taxPayerDeatilsData.legal_name = taxPayerDetails['legal_name']
        taxPayerDeatilsData.trade_name = taxPayerDetails['trade_name']
        taxPayerDeatilsData.location = taxPayerDetails['location']
        taxPayerDeatilsData.save()
        return True

@frappe.whitelist()
def generateIrn(data):
    try:
        company = frappe.get_last_doc("company")
        invoice_number = data['invoice_number']
        generation_type = data['generation_type']
        # get invoice detail
        start_time = datetime.datetime.utcnow()
        invoice = frappe.get_doc('Invoices', invoice_number)
        if company.block_irn == "True":
            return {"success":False,"message":"IRN/QR Services has been Blocked"}
        if invoice.irn_generated == "Success":
            return {"success":True,"message":"Already IRN Generated"}
        if invoice.invoice_type=="B2C":
            return {"success":False,"message":"B2C Invoice"}	
        # get seller details
        if invoice.invoice_category == "Tax Invoice":
            category = "INV"
        elif invoice.invoice_category == "Debit Invoice":	
            category = "DBN"
        else:
            category = "CRN"
        # if "bulk_irn" in data:
        #     if data["bulk_irn"]:
        if invoice.invoice_category == "Tax Invoice" and invoice.has_credit_items == "Yes" and invoice.invoice_from == "Pms":
            get_is_credit_items = frappe.db.get_list("Items", filters=[["parent","=",data['invoice_number']]], pluck="is_credit_item")
            if "Yes" in get_is_credit_items:
                abs_path = os.path.dirname(os.getcwd())
                file_path = abs_path + '/apps/version2_app/version2_app/version2_app/doctype/invoices/reinitate_invoice.py'
                module_name = 'auto_adjustment'
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                auto_adj = module.auto_adjustment({"invoice_number": data["invoice_number"]})
                if not auto_adj["success"]:
                    return auto_adj
                get_is_credit_items = frappe.db.get_list("Items", filters=[["parent","=",data['invoice_number']]], pluck="is_credit_item") 
                if "Yes" in get_is_credit_items:
                    return {"success": False, "message": "please do adjust manually"}
        # IRNObjectdoc = frappe.get_doc({'doctype':'IRN Objects','invoice_number':invoice_number,"invoice_category":invoice.invoice_category})
        company_details = check_company_exist_for_Irn(invoice.company)
        invoice = frappe.get_doc('Invoices', invoice_number)
        # get gsp_details
        credit_note_items = []
        companyData = {
            "code": company_details['data'].name,
            "mode": company_details['data'].mode,
            "provider": company_details['data'].provider
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
        if company_details['data'].mode == 'Testing':
            if len(invoice.invoice_number) > 13:
                testing_invoice_number = invoice.invoice_number
            else :
                testing_invoice_number = invoice.invoice_number + str(random.randint(0, 100)) + 'T'
        gst_data = {
            "Version": "1.1",
            "TranDtls": {
                "TaxSch": "GST",
                "SupTyp": invoice.suptyp,
                "RegRev": "Y" if invoice.state_code == company_details['data'].state_code and invoice.sez == 1 else "N",
                "IgstOnIntra": "Y" if invoice.state_code == company_details['data'].state_code==1 and invoice.sez == 1 else "N"
            },
            "SellerDtls": {
                "Gstin":
                GSP_details['data']['gst'],
                "LglNm":
                company_details['data'].legal_name,
                "TrdNm":
                company_details['data'].trade_name,
                "Addr1":
                company_details['data'].address_1,
                "Addr2":
                company_details['data'].address_2,
                "Loc":
                company_details['data'].location,
                "Pin":
                193502 if company_details['data'].mode == "Testing" else
                company_details['data'].pincode,
                "Stcd":
                "01" if company_details['data'].mode == "Testing" else
                company_details['data'].state_code,
                "Ph":
                company_details['data'].phone_number,
                "Em":
                company_details['data'].email
            },
            "BuyerDtls": {
                "Gstin":
                taxpayer_details['data'].gst_number,
                "LglNm":
                taxpayer_details['data'].legal_name,
                "TrdNm":
                taxpayer_details['data'].trade_name,
                "Pos":
                "01" if company_details['data'].mode == "Testing" else
                # company_details['data'].state_code,
                invoice.state_code,
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
                "No": testing_invoice_number if company_details['data'].mode == 'Testing' else invoice.invoice_number,
                "Dt":
                datetime.datetime.strftime(invoice.invoice_date,
                                            '%d/%m/%Y')
            },
            "ItemList": [],
        }
        print(gst_data,"????")
        total_igst_value = 0
        total_sgst_value = 0
        total_cgst_value = 0
        total_cess_value = 0
        total_state_cess_value = 0
        discount_after_value = 0
        discount_before_value = 0
        ass_value = 0
        items_data = sorted(invoice.items, key = lambda i: i.sort_order)
        for index, item in enumerate(items_data):
        # print(item.sac_code,"HsnCD")
            if item.sac_code == "996339" and item.taxable == "Yes" :
                return{"success": False, "message": "for liquor item given taxable yes"}
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
                if invoice.invoice_category == "Credit Invoice":
                    if item.type != "Non-Gst":
                        credit_note_items.append(item.__dict__)
                elif invoice.invoice_category == "Tax Invoice":
                    if item.taxable=="Yes" and item.type!="Non-Gst" and item.is_credit_item=="Yes" and company_details['data'].allowance_type=="Credit":
                        
                        credit_note_items.append(item.__dict__)
                    else:
                        if item.type != "Non-Gst" and company_details['data'].allowance_type=="Discount" and item.table=="yes" and item.is_credit_item=="Yes":
                            discount_before_value +=item.item_value	
                            discount_after_value += item.item_value_after_gst
                            # credit_note_items.append(item.__dict__)
        if (len(gst_data['ItemList']) == 0 and invoice.invoice_category == "Tax Invoice") or (invoice.has_credit_items=="Yes" and invoice.invoice_category == "Tax Invoice"):
            return {"success":False,"message":"Please convert Tax invoice to Credit invoice"}
        if invoice.invoice_category == "Credit Invoice":
            creditIrn = CreditgenerateIrn(invoice_number,generation_type,None)
            return creditIrn
        discount_before_value = abs(discount_before_value)	
        discount_after_value = abs(discount_after_value)
        TotInnVal = round(invoice.amount_after_gst, 2)+round(invoice.other_charges,2) - round(discount_after_value,2)
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
            "OthChrg": abs(round(invoice.other_charges,2)) if company_details['data'].vat_reporting==1 else abs(round(invoice.other_charges_before_tax,2)),
            "RndOffAmt": 0,
            "TotInvVal": round(TotInnVal,2) if company_details['data'].vat_reporting==1 else round(TotInnVal-invoice.total_vat_amount, 2),
            "TotInvValFc": round(TotInvValFc, 2)
        }        
        if len(gst_data['ItemList']) == 0:
            return {"success":False,"message":"Items cannot be Empty"}
        if ass_value > 0:
            try:
                response = postIrn(gst_data, GSP_details['data'],
                                    company_details['data'], invoice_number)
                # IRNObjects = {"invoice_number":invoice_number,"irn_request_object":gst_data,"irn_response_object":response}				
                # IRNObjectdoc = frappe.get_doc({'doctype':'IRN Objects','invoice_number':invoice_number,'irn_request_object':str(gst_data),'irn_response_object':str(response)})
                # IRNObjectdoc.insert(ignore_permissions=True, ignore_links=True)
                # print(response,"Kudos its working")
                if response['success']:
                    # json.dumps(data['invoice_object_from_file']
                    IRNObjectdoc = frappe.get_doc({'doctype':'IRN Objects','invoice_number':invoice_number,"invoice_category":invoice.invoice_category,"irn_request_object":json.dumps({"data":gst_data}),"irn_response_object":json.dumps({"data":response})})
                    
                    IRNObjectdoc.save()
                    frappe.db.commit()
                    # print(IRNObjectdoc.name,"/a/a/a/")
                    invoice = frappe.get_doc('Invoices', invoice_number)
                    invoice.ack_no = response['result']['AckNo']
                    invoice.irn_number = response['result']['Irn']
                    invoice.ack_date = response['result']['AckDt']
                    invoice.signed_invoice = response['result'][
                        'SignedInvoice']
                    invoice.signed_invoice_generated = 'Yes'
                    invoice.irn_generated = 'Success'
                    invoice.qr_code = response['result']['SignedQRCode']
                    invoice.qr_code_generated = 'Success'
                    invoice.irn_cancelled = 'No'
                    invoice.irn_generated_time = datetime.datetime.now()
                    invoice.irn_generated_type = generation_type
                    invoice.irn_process_time = datetime.datetime.utcnow(
                    ) - start_time
                    invoice.save(ignore_permissions=True, ignore_version=True)
                    frappe.db.commit()
                    create_qr = create_qr_image(invoice_number,
                                                GSP_details['data'])
                    if create_qr['success'] == True and company_details['data'].allowance_type=="Credit":
                        if credit_note_items != []:
                            CreditgenerateIrn(invoice_number,generation_type,IRNObjectdoc.name)
                            invoice = frappe.get_doc('Invoices',
                                                        invoice_number)
                            invoice.irn_process_time = datetime.datetime.utcnow(
                            ) - start_time
                            invoice.save(ignore_permissions=True,
                                            ignore_version=True)
                            frappe.db.commit()              
                    return response
                else:
                    if "result" in list(response.keys()):
                        if response['result'][0]['InfCd'] == "DUPIRN":
                            IRNObjectdoc = frappe.get_doc({'doctype':'IRN Objects','invoice_number':invoice_number,"invoice_category":invoice.invoice_category,"irn_request_object":json.dumps({"data":gst_data}),"irn_response_object":json.dumps({"data":response}),"error_message":"Duplicate Irn"})
                            IRNObjectdoc.save()
                            invoice = frappe.get_doc('Invoices', invoice_number)
                            invoice.duplicate_ack_date = response['result'][0]['Desc']['AckDt']
                            invoice.duplicate_ack_no = response['result'][0]['Desc']['AckNo']
                            invoice.duplicate_irn_number = response['result'][0]['Desc']['Irn']
                            invoice.ack_no = response['result'][0]['Desc']['AckNo']
                            invoice.irn_number = response['result'][0]['Desc']['Irn']
                            invoice.ack_date = response['result'][0]['Desc']['AckDt']
                            invoice.irn_generated = "Success"
                            invoice.irn_generated_type = generation_type
                            # invoice.qr_code_image = ""
                            # invoice.qr_code_generated = "Success"
                            invoice.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
                        
                        irn_error_message = response["message"]
                        frappe.log_error(frappe.get_traceback(),invoice_number)
                        logger.error(f"{invoice_number},     postIrn,   {irn_error_message}")
                        return response
                    irn_error_message = response["message"]
                    frappe.log_error(frappe.get_traceback(),invoice_number)
                    logger.error(f"{invoice_number},     postIrn,   {irn_error_message}")
                    return response
            
            except Exception as e:
                print(str(e), "generate Irn")
                # frappe.log_error(frappe.get_traceback(), invoice_number)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                frappe.log_error("Ezy-invoicing generateIrn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
                logger.error(f"{invoice_number},     generateIrn,   {str(e)}")
                return {"success": False, "message": str(e)}
        
    except Exception as e:
        print(str(e), "generate Irn")
        print(traceback.print_exc())
        # frappe.log_error(frappe.get_traceback(),invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing generateIrn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"{invoice_number},     generateIrn,   {str(e)}")
        return {"success": False, "message": str(e)}
    


def attach_qr_code(invoice_number, gsp, code):
    try:
        invoice = frappe.get_doc('Invoices', invoice_number)
        company = frappe.get_doc('company', invoice.company)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company.site_name
        # path = folder_path + '/sites/' + get_site_name(frappe.local.request.host)
        path = folder_path + '/sites/' + site_folder_path
        src_pdf_filename = path + invoice.invoice_file
        dst_pdf_filename = path + "/private/files/" + invoice_number + 'withQr.pdf'
        # attaching qr code
        img_filename = path + invoice.qr_code_image
        # img_rect = fitz.Rect(250, 200, 340, 270)
        img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
                             company.qr_rect_y0, company.qr_rect_y1)
        document = fitz.open(src_pdf_filename)

        page = document[0]

        page.insertImage(img_rect, filename=img_filename)
        document.save(dst_pdf_filename)
        document.close()
        # attacing irn an ack
        dst_pdf_text_filename = path + "/private/files/" + invoice_number + 'withQrIrn.pdf'
        doc = fitz.open(dst_pdf_filename)
        
        if company.irn_details_page == "First":
            page = doc[0]
        else:
            page = doc[-1]
        # page = doc[0]
        # where = fitz.Point(15, 55)
        where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
        ackdate = invoice.ack_date
        ack_date = ackdate.split(" ")
        text = "IRN: " + invoice.irn_number +"          "+ "ACK NO: " + invoice.ack_no + "       " + "ACK DATE: " + ack_date[0]
        
        page.insertText(
            where,
            text,
            fontname="Roboto-Black",  # arbitrary if fontfile given
            fontfile=folder_path +
            company.font_file_path,  #fontpath,  # any file containing a font
            fontsize=7,  # default
            rotate=0,  # rotate text
            color=(0, 0, 0),  # some color (blue)
            overlay=True)
                
        doc.save(dst_pdf_text_filename)
        doc.close()

        files = {"file": open(dst_pdf_text_filename, 'rb')}
        payload = {
            "is_private": 1,
            "folder": "Home",
            "doctype": "Invoices",
            "docname": invoice_number,
            'fieldname': 'invoice_with_gst_details'
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        if 'message' in response:
            invoice.invoice_with_gst_details = response['message']['file_url']
            invoice.save()
        return {"message":"Qr Generated Succesfull","success":True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing attach_qr_code Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "attach qr code")


@frappe.whitelist()
def send_invoicedata_to_gcb(invoice_number):
    try:
        folder_path = frappe.utils.get_bench_path()

        doc = frappe.get_doc('Invoices', invoice_number)
        company = frappe.get_doc('company', doc.company)
        path = folder_path + '/sites/' + company.site_name
        file_name = invoice_number + 'b2cqr.png'
        dst_pdf_filename = path + "/private/files/" + file_name
        # if doc.b2c_qrimage:
        # 	attach_qr = attach_b2c_qrcode({
        # 		"invoice_number": invoice_number,
        # 		"company": doc.company
        # 	})
        # 	if attach_qr["success"] == False:
        # 		return {"success": False, "message": attach_qr["message"]}
        # 	else:
        # 		return {
        # 			"success": True,
        # 			"message": "QR-Code generated successfully"
        # 		}

        filename = invoice_number + doc.company + ".json"
        b2c_file = path + "/private/files/" + filename
        items_count = 0
        hsn_code = ""
        items = doc.items
        items_count = 0
        hsn_code = ""
        headers = {'Content-Type': 'application/json'}
        if company.block_irn == "True":
            return {"success":False,"message":"IRN/QR Services has been Blocked"}
        if company.b2c_qr_type == "Invoice Details":
            if company.proxy == 1:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://","@")
                proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            
            for xyz in items:
                if xyz.sac_code not in hsn_code:
                    hsn_code += xyz.sac_code + ", "
                items_count += 1
            b2c_data = {
                "invoice_number": doc.invoice_number,
                "invoice_type": doc.invoice_type,
                "invoice_date": str(doc.invoice_date),
                # "checkout_date": str(doc.checkout_date),
                "pms_invoice_summary": doc.total_invoice_amount,
                "irn": "N/A",
                "company_name": company.company_name,
                "guest_name": doc.guest_name,
                "issued_by": "ezyinvoicing",
                "items_count": items_count,
                "hsn_code": hsn_code.rstrip(', '),
                "company": company.name,
                "showpaybutton": company.b2c_online_payments
            }
            if company.pms_property_url:
                b2c_data["file_url"] = company.pms_property_url
            if company.pms_information_invoice_for_payment_qr == "Yes":
                payment_list = frappe.db.get_list("Invoice Payments",filters={"invoice_number":doc.invoice_number},fields=["item_value","date","payment","payment_reference"])
                if len(payment_list)>0:
                    for each in payment_list:
                        each["date"] = str(each["date"])
                    b2c_data["payments"] = payment_list
            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    json_response = requests.post(
                        "https://gst.caratred.in/ezy/api/addJsonToGcb",
                        headers=headers,
                        json=b2c_data,verify=False)
                else:
                    json_response = requests.post(
                        "https://gst.caratred.in/ezy/api/addJsonToGcb",
                        headers=headers,
                        json=b2c_data,verify=False)
                if json_response.status_code==200:
                    response = json_response.json()
                if json_response.status_code!=200:
                    return {
                        "success": False,
                        "message": "status code"+str(json_response.status_code)+"reason"+str(json_response.reason)
                    }
            else:
                print(proxies, "     proxy console")
                json_response = requests.post(
                    "https://gst.caratred.in/ezy/api/addJsonToGcb",
                    headers=headers,
                    json=b2c_data,
                    proxies=proxies,verify=False)
                response = json_response.json()
                if response["success"] == False:
                    return {
                        "success": False,
                        "message": response["message"]
                    }

            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4
            )
            qrurl = company.b2c_qr_url + response['data']
            qr.add_data(qrurl)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(dst_pdf_filename)
        elif company.b2c_qr_type == "Virtual Payment":

            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    generate_qr = requests.post(
                        "https://upiqr.in/api/qr?format=png",
                        headers=headers,
                        json={
                            "vpa": company.merchant_virtual_payment_address,
                            "name": company.merchant_name,
                            "txnReference": invoice_number,
                            "amount": '%.2f' % doc.pms_invoice_summary},
                        verify=False)
                else:
                    generate_qr = requests.post(
                        "https://upiqr.in/api/qr?format=png",
                        headers=headers,
                        json={
                            "vpa": company.merchant_virtual_payment_address,
                            "name": company.merchant_name,
                            "txnReference": invoice_number,
                            "amount": '%.2f' % doc.pms_invoice_summary},
                        verify=False)

            else:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    'https':
                    'https://' + company.proxy_username + ":" +
                    company.proxy_password + proxyhost}
                print(proxies, "     proxy console")
                generate_qr = requests.post(
                    "https://upiqr.in/api/qr?format=png",
                    headers=headers,
                    json={
                        "vpa": company.merchant_virtual_payment_address,
                        "name": company.merchant_name,
                        "txnReference": invoice_number,
                        "amount": '%.2f' % doc.pms_invoice_summary
                    },
                    proxies=proxies,verify=False)
            if generate_qr.status_code == 200:
                with open(dst_pdf_filename, "wb") as f:
                    f.write(generate_qr.content)
        else:
            return {
                "success":
                False,
                "message":
                "Please select any in 'B2C QR Code Type' in Company Details"
            }
        files = {"file": open(dst_pdf_filename, 'rb')}
        payload = {
            "is_private": 1,
            "folder": "Home",
            "doctype": "Invoices",
            "docname": invoice_number,
            'fieldname': 'b2c_qrimage'
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        if 'message' in response:
            doc.b2c_qrimage = response['message']['file_url']
            doc.name = invoice_number
            doc.irn_generated = "Success"
            doc.qr_code_generated = "Success"
            doc.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
            # attach_qr = attach_b2c_qrcode({
            # 	"invoice_number": invoice_number,
            # 	"company": doc.company
            # })
            # if attach_qr["success"] == False:
            # 	if os.path.exists(b2c_file):
            # 		os.remove(b2c_file)
            # 	if os.path.exists(dst_pdf_filename):
            # 		os.remove(dst_pdf_filename)
            # 	return {"success": False, "message": attach_qr["message"]}
            # if os.path.exists(b2c_file):
            # 	os.remove(b2c_file)
            # if os.path.exists(dst_pdf_filename):
            # 	os.remove(dst_pdf_filename)
            return {
                "success": True,
                "message": "QR-Code generated successfully",
                "invoice":doc
            }
    except Exception as e:
        print(e, "send invoicedata to gcb")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing send_invoicedata_to_gcb","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def cancel_irn(irn_number, gsp, reason, company, invoice_number):
    try:

        headers = {
            "user_name": gsp['data']['username'],
            "password": gsp['data']['password'],
            "gstin": gsp['data']['gst'],
            "requestid": str(random.randint(0, 1000000000000000000)),
            "Authorization": "Bearer " + gsp['data']['token'],
        }
        payload = {"irn": irn_number, "cnlrem": reason, "cnlrsn": "1"}
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                cancel_response = requests.post(gsp['data']['cancel_irn'],
                                                headers=headers,
                                                json=payload,verify=False)
            else:
                cancel_response = requests.post(gsp['data']['cancel_irn'],
                                                headers=headers,
                                                json=payload,verify=False)
        else:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                'https':
                'https://' + company.proxy_username + ":" +
                company.proxy_password + proxyhost}
            print(proxies, "     proxy console")
            cancel_response = requests.post(gsp['data']['cancel_irn'],
                                            headers=headers,
                                            json=payload,
                                            proxies=proxies,verify=False)
        if cancel_response.status_code == 200:
            insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","cancel_irn":'True',"status":"Success","company":company.name})
            insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
        else:
            insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","cancel_irn":'True',"status":"Failed","company":company.name})
            insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)									
        repsone = cancel_response.json()
        return repsone
    except Exception as e:
        print("cancel irn", e)
        # frappe.log_error(frappe.get_traceback(), invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing cancel_irn Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"{invoice_number},     cancel_irn,   {str(e)}")
        return {"success": False, "message": str(e)}




from version2_app.version2_app.doctype.ey_intigration.redo_qr import create_ey_qr_code

def create_qr_image(invoice_number, gsp):
    try:
        
        invoice = frappe.get_doc('Invoices', invoice_number)

        folder_path = frappe.utils.get_bench_path()
        company = frappe.get_doc('company', invoice.company)
        site_folder_path = company.site_name
        path = folder_path + '/sites/' + site_folder_path + "/private/files/"
        # print(path)
        if company.provider!='ey':
            headers = {
                "user_name": gsp['username'],
                "password": gsp['password'],
                "gstin": gsp['gst'],
                "requestid": str(random.randint(0, 1000000000000000000)),
                "Authorization": "Bearer " + gsp['token'],
                "Irn": invoice.irn_number
            }
            if company.irn_qr_size == "Small":
                    # "height":"150",
                # "width":"150"
                headers['height'] = "150"
                headers['width'] = "150"
            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    qr_response = requests.get(gsp['generate_qr_code'],
                                            headers=headers,
                                            stream=True,verify=False)
                else:
                    qr_response = requests.get(gsp['generate_qr_code'],
                                            headers=headers,
                                            stream=True,verify=False)							
            else:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    'https':
                    'https://' + company.proxy_username + ":" +
                    company.proxy_password + proxyhost}
                print(proxies, "     proxy console")
                qr_response = requests.get(gsp['generate_qr_code'],
                                        headers=headers,
                                        stream=True,
                                        proxies=proxies,verify=False)	
            if qr_response.status_code==200:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","create_qr_image":'True',"status":"Success","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
            else:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","create_qr_image":'True',"status":"Failed","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)								   					   
            file_name = invoice_number + "qr.png"
            full_file_path = path + file_name
            with open(full_file_path, "wb") as f:
                for chunk in qr_response.iter_content(1024):
                    f.write(chunk)

            files = {"file": open(full_file_path, 'rb')}
            payload = {
                "is_private": 1,
                "folder": "Home",
                "doctype": "Invoices",
                "docname": invoice_number,
                'fieldname': 'qr_code_image'
            }
            site = company.host
            upload_qr_image = requests.post(site + "api/method/upload_file",
                                            files=files,
                                            data=payload)
            response = upload_qr_image.json()
            if 'message' in response:
                invoice.qr_code_image = response['message']['file_url']
                invoice.save()
                frappe.db.commit()
                # attach_qr_code(invoice_number, gsp, invoice.company)
                return {"success": True,"message":"Qr Generated Successfully"}
            return {"success": True,"message":"Qr Generated Successfully"}
        else:
            return create_ey_qr_code(invoice_number,{})
    except Exception as e:
        print(e, "qr image")
        # frappe.log_error(frappe.get_traceback(),invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing create_qr_image Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"{invoice_number},     create_qr_image,   {str(e)}")
        return {"success": False, "message": str(e)}

from version2_app.version2_app.doctype.ey_intigration.irngeneration import ey_generate_einvoice

def postIrn(gst_data, gsp, company, invoice_number):
    try:
        # print(gst_data)
        if company.provider != 'ey':
            headers = {
                "user_name": gsp['username'],
                "password": gsp['password'],
                "gstin": gsp['gst'],
                "requestid": str(random.randint(0, 1000000000000000000)),
                "Authorization": "Bearer " + gsp['token']
            }
            if company.proxy == 0:
                if company.skip_ssl_verify == 0:
                    irn_response = requests.post(gsp['generate_irn'],
                                                headers=headers,
                                                json=gst_data,verify=False)
                else:
                    irn_response = requests.post(gsp['generate_irn'],
                                                headers=headers,
                                                json=gst_data,verify=False)

            else:
                proxyhost = company.proxy_url
                proxyhost = proxyhost.replace("http://", "@")
                proxies = {
                    'https':
                    'https://' + company.proxy_username + ":" +
                    company.proxy_password + proxyhost}
                print(proxies, "     proxy console")
                irn_response = requests.post(gsp['generate_irn'],
                                            headers=headers,
                                            json=gst_data,
                                            proxies=proxies,verify=False)

            # print(irn_response.text)
            if irn_response.status_code == 200:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","generate_irn":'True',"status":"Success","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                return irn_response.json()
            else:
                message_error = str(irn_response.text)
                logger.error(f"{invoice_number},     postIrn,   {message_error}")
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","generate_irn":'True',"status":"Failed","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                return {"success": False, 'message': irn_response.text}
            # print(irn_response.text)
        else:
            resp = ey_generate_einvoice(gst_data, gsp, company, invoice_number)
            # print(resp,"*********************")
            return resp
            # return {"success": False, 'message': resp}

    except Exception as e:
        print(e, "post irn")
        # frappe.log_error(frappe.get_traceback(), invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing postIrn Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"{invoice_number},     postIrn,   {str(e)}")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def create_invoice(data):
    try:

        if data['invoice_type'] == 'B2B':
            # check token is valid or not
            isValid = check_token_is_valid(company.name, company.mode)
            if isValid == True:
                # get taxpayer details
                tax_payer = get_tax_payer_details(data['gstNumber'],
                                                  company_code, api_details)
                # insert invoices
                a = insert_invoice(data, company_code, tax_payer)
            else:
                pass
        else:
            print("b2c")

        return True
    except Exception as e:
        print(e)


@frappe.whitelist()
def insert_invoice(data):
    # '''
    # insert invoice data     data, company_code, taxpayer,items_data
    # '''
    try:
        if "invoice_category" not in list(data['guest_data']):
            data['guest_data']['invoice_category'] = "Tax Invoice"
        if "invoice_object_from_file" not in data:
            data['invoice_object_from_file'] = " "
        company = frappe.get_doc('company',data['company_code'])
        sales_amount_before_tax = 0
        sales_amount_after_tax = 0
        value_before_gst = 0
        value_after_gst = 0
        other_charges_before_tax = 0
        other_charges = 0
        credit_value_before_gst = 0
        credit_value_after_gst = 0
        cgst_amount = 0
        sgst_amount = 0
        igst_amount = 0
        total_central_cess_amount = 0
        total_state_cess_amount = 0
        total_vat_amount =0
        discountAmount = 0
        credit_cgst_amount = 0
        credit_sgst_amount = 0
        credit_igst_amount = 0
        total_credit_central_cess_amount = 0
        total_credit_state_cess_amount = 0
        total_credit_vat_amount =0
        non_revenue_amount = 0
        has_discount_items = "No"
        has_credit_items = "No"
        irn_generated = "Pending"
        if "legal_name" not in data['taxpayer']:
            data['taxpayer']['legal_name'] = " "
        #calculat items
        if len(data['items_data'])>0:
            for item in data['items_data']:
                if item['taxable'] == 'No' and item['item_type'] != "Discount":
                    other_charges += float(item['item_value_after_gst'])
                    other_charges_before_tax += float(item['item_value'])
                    if data['guest_data']['invoice_category'] != "Credit Invoice":
                        total_vat_amount += float(item['vat_amount'])
                    else:
                        total_credit_vat_amount += float(item['vat_amount'])
                    if frappe.db.exists("SAC HSN CODES", {"sac_index":item["sac_index"], "ignore_non_taxable_items": 1}):
                        non_revenue_amount += float(item['item_value_after_gst'])
                elif item['taxable']=="No" and item['item_type']=="Discount":
                    discountAmount += item['item_value_after_gst'] 
                elif item['sac_code'].isdigit():
                    if "-" not in str(item['item_value']):
                        cgst_amount+=float(item['cgst_amount'])
                        sgst_amount+=float(item['sgst_amount'])
                        igst_amount+=float(item['igst_amount'])
                        total_central_cess_amount+=float(item['cess_amount'])
                        total_state_cess_amount +=float(item['state_cess_amount'])
                        value_before_gst += float(item['item_value'])
                        value_after_gst += float(item['item_value_after_gst'])
                        total_vat_amount += float(item['vat_amount'])
                        # print(value_before_gst,value_after_gst," ******")
                    else:
                        # cgst_amount+=item['cgst_amount']
                        # sgst_amount+=item['sgst_amount']
                        # igst_amount+=item['igst_amount']
                        # total_central_cess_amount+=item['cess_amount']
                        # total_state_cess_amount +=item['state_cess_amount']
                        credit_cgst_amount+=float(abs(item['cgst_amount']))
                        credit_sgst_amount+=float(abs(item['sgst_amount']))
                        credit_igst_amount+=float(abs(item['igst_amount']))
                        total_credit_central_cess_amount+=float(item['cess_amount'])
                        total_credit_state_cess_amount +=float(item['state_cess_amount'])
                        credit_value_before_gst += float(abs(item['item_value']))
                        credit_value_after_gst += float(abs(item['item_value_after_gst']))
                        total_credit_vat_amount += float(item['vat_amount'])
                else:
                    pass
        # pms_invoice_summary = value_after_gst
        # pms_invoice_summary_without_gst = value_before_gst
        if company.allowance_type=="Discount":
            discountAfterAmount = abs(discountAmount)+abs(credit_value_after_gst)
            discountBeforeAmount = abs(discountAmount)+abs(credit_value_before_gst)
            pms_invoice_summary = value_after_gst -discountAfterAmount
            pms_invoice_summary_without_gst = value_before_gst -discountBeforeAmount
            # credit_value_after_gst = 0
            # credit_value_before_gst = 0
            if pms_invoice_summary == 0:
                
                credit_value_after_gst = 0
            if credit_value_before_gst > 0:

                has_discount_items = "Yes"
            else:
                has_discount_items = "No"      
        else:
            pms_invoice_summary = value_after_gst - credit_value_after_gst
            pms_invoice_summary_without_gst = value_before_gst - credit_value_before_gst
            if credit_value_before_gst > 0:

                has_credit_items = "Yes"
            else:
                has_credit_items = "No"	
        cgst_amount = cgst_amount - credit_cgst_amount
        sgst_amount = sgst_amount - credit_sgst_amount
        igst_amount	= igst_amount - credit_igst_amount	
        total_central_cess_amount = total_central_cess_amount - total_credit_state_cess_amount
        total_state_cess_amount = total_state_cess_amount - total_credit_state_cess_amount
        total_vat_amount =  total_vat_amount - total_credit_vat_amount
        if (pms_invoice_summary > 0) or (credit_value_after_gst > 0):
            ready_to_generate_irn = "Yes"
        else:
            ready_to_generate_irn = "No"
        roundoff_amount = 0
        data['invoice_round_off_amount'] = roundoff_amount
        sales_amount_before_tax = value_before_gst + other_charges_before_tax 
        sales_amount_after_tax = value_after_gst + other_charges
        sales_amount_after_tax = sales_amount_after_tax - credit_value_after_gst
        sales_amount_before_tax = sales_amount_before_tax - credit_value_before_gst


        # if data['total_invoice_amount'] == 0 and len(data['items_data'])>0:
        # 	data['total_invoice_amount'] = sales_amount_after_tax
        # print(sales_amount_after_tax)	
        if '-' in str(sales_amount_after_tax):
            allowance_invoice = "Yes"
        else:
            allowance_invoice = "No"	 
        # print(allowance_invoice)	
        if data['guest_data']['room_number'] == 0 and '-' not in str(sales_amount_after_tax):
            # data['guest_data']['invoice_category'] = "Debit Invoice"
            debit_invoice = "Yes"
        else:
            debit_invoice = "No"	

        

        if data['total_invoice_amount'] == 0:
            total = (value_after_gst + other_charges) - credit_value_after_gst
            if (total>0 and total<1) or (total>-1 and total<1):
                data['total_invoice_amount'] = 0
            else:
                data['total_invoice_amount'] = value_after_gst + other_charges + credit_value_after_gst

        if "raise_credit" in data:
            data['total_invoice_amount'] = float(pms_invoice_summary+other_charges)#value_after_gst + other_charges + credit_value_after_gst
        if len(data['items_data'])==0:
            ready_to_generate_irn = "No"


        
        else:
            if len(data['items_data'])>0 and data['total_invoice_amount'] != 0:
                if company.only_b2c == "No":
                    roundoff_amount = float(data['total_invoice_amount']) - float(pms_invoice_summary+other_charges)
                    data['invoice_round_off_amount'] = roundoff_amount
                else:
                    roundoff_amount = 0
                    data['invoice_round_off_amount'] = 0
                    pms_invoice_summary = data['total_invoice_amount']
                    # other_charges = data['total_invoice_amount']
                    # other_charges_before_tax = data["total_invoice_amount"]
                    sales_amount_before_tax = data["total_invoice_amount"]
                    sales_amount_after_tax = data['total_invoice_amount']
                if abs(roundoff_amount)>6:
                # if company.name == "SMBKC-01":
                #     round_amount = 2
                # else:
                #     round_amount = 6
                    # if abs(roundoff_amount)>round_amount:
                    if int(data['total_invoice_amount']) != int(pms_invoice_summary+other_charges) and int(math.ceil(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.floor(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.ceil(data['total_invoice_amount'])) != int(math.floor(pms_invoice_summary+other_charges)):
                        
                        calculated_data = {"sales_amount_before_tax":sales_amount_before_tax,"sales_amount_after_tax":sales_amount_after_tax,"other_charges_before_tax":other_charges_before_tax,
                                "value_before_gst":value_before_gst,"value_after_gst":value_after_gst,"other_charges":other_charges,"credit_value_after_gst":credit_value_after_gst,
                                "credit_value_before_gst":credit_value_before_gst,"irn_generated":"Error","cgst_amount":cgst_amount,"sgst_amount":sgst_amount,"igst_amount":igst_amount,
                                "total_central_cess_amount":total_central_cess_amount,"total_state_cess_amount":total_state_cess_amount,"total_vat_amount":total_vat_amount,
                                "total_credit_state_cess_amount":total_credit_state_cess_amount,"total_credit_central_cess_amount":total_credit_central_cess_amount,"total_credit_vat_amount":total_credit_vat_amount,
                                "credit_cgst_amount":credit_cgst_amount,"credit_igst_amount":credit_igst_amount,"credit_sgst_amount":credit_sgst_amount,"pms_invoice_summary":pms_invoice_summary,
                                "pms_invoice_summary_without_gst":pms_invoice_summary_without_gst,"company":company}
                        
                        
                        TotalMismatchErrorAPI = TotalMismatchError(data,calculated_data)
                        if TotalMismatchErrorAPI['success']==True:
                            # items = [x for x in data['items_data'] if x['item_mode'] == "Debit"]
                            # if data['total_invoice_amount'] !=0:
                            items = data['items_data']
                            itemsInsert = insert_items(items, TotalMismatchErrorAPI['invoice_number'])
                            # insert_tax_summaries2(items, TotalMismatchErrorAPI['invoice_number'])
                            TaxSummariesInsert(items,TotalMismatchErrorAPI['invoice_number'])
                            hsnbasedtaxcodes = insert_hsn_code_based_taxes(
                                items, TotalMismatchErrorAPI['invoice_number'],"Invoice")
                            invoiceData = frappe.get_doc('Invoices',TotalMismatchErrorAPI['invoice_number'])	
                            if invoiceData.invoice_from=="Pms":
                                socket = invoiceCreated(invoiceData)	
                            return {"success": True,"data":TotalMismatchErrorAPI['data']}
                        
                        return{"success":False,"message":TotalMismatchErrorAPI['message']}
        # qr_generated = "Pending"
        if "taxpayer" in data and "email" in data:
            if "Arrival" in data["taxpayer"]["email"]:
                data["taxpayer"]["email"]=data["taxpayer"]["email"].replace("Arrival", "").strip()
        if len(data['items_data'])==0 or data['total_invoice_amount'] == 0:
            irn_generated = "Zero Invoice"
            taxpayer= {"legal_name": "","email":data['taxpayer']['email'],"address_1": "","address_2": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
            data['taxpayer'] =taxpayer
            data['guest_data']['invoice_type'] = "B2C"

            # if data['guest_data']['invoice_type']=="B2B":
            # 	irn_generated = "Zero Invoice"
            # 	qr_generated = "Pending"
            # else:
            # 	qr_generated = "Zero Invoice"
            # 	irn_generated = "NA"
        if "invoice_from" in data['guest_data']:
            invoice_from = data['guest_data']['invoice_from']
        else:
            invoice_from = "Pms"
        if "B2C_bulk_upload" in data:
            if data["B2C_bulk_upload"]:
                if data['guest_data']['invoice_type'] == "B2B":
                    pass
                    # irn_generated = "On Hold"

        if 'pos_checks' not in data['guest_data']:
            pos_checks = 0
        else:
            pos_checks = data['guest_data']['pos_checks']


        folder_path = frappe.utils.get_bench_path()
        with open(folder_path+"/"+"apps/version2_app/version2_app/version2_app/doctype/invoices/state_code.json") as f:
            json_data = json.load(f)
            for each in json_data:
                if company.state_code == each['tin']:
                    place_supplier_state_name = f"{each['state']}-({each['tin']})"

        if 'checkout_date' in data['guest_data']:
            if data['guest_data']['checkout_date'] != None:
                checkout_date = datetime.datetime.strptime(data['guest_data']['checkout_date'],'%d-%b-%y %H:%M:%S')
            else:
                checkout_date = None
        else:
            checkout_date = None

        invoice = frappe.get_doc({
            'doctype':
            'Invoices',
            'invoice_number':
            data['guest_data']['invoice_number'],
            'guest_name':
            data['guest_data']['name'],
            'ready_to_generate_irn':ready_to_generate_irn,
            'invoice_from':invoice_from,
            'gst_number':
            data['guest_data']['gstNumber'],
            'invoice_round_off_amount': data['invoice_round_off_amount'],
            'invoice_file':
            data['guest_data']['invoice_file'],
            'room_number':
            data['guest_data']['room_number'],
            'confirmation_number':
            data['guest_data']['confirmation_number'],
            'invoice_type':
            data['guest_data']['invoice_type'],
            'invoice_category':data['guest_data']['invoice_category'],
            'print_by': data['guest_data']['print_by'],
            'invoice_date':
            datetime.datetime.strptime(data['guest_data']['invoice_date'],
                                        '%d-%b-%y %H:%M:%S'),
            'checkout_date':checkout_date,
            # datetime.datetime.strptime(data['guest_data']['checkout_date'],
            #                             '%d-%b-%y %H:%M:%S') if "checkout_date" in data['guest_data'] else None,
            'legal_name':
            data['taxpayer']['legal_name'],
            'mode':company.mode,
            'address_1':
            data['taxpayer']['address_1'],
            'email':
            data['taxpayer']['email'],
            'trade_name':
            data['taxpayer']['trade_name'],
            'address_2':
            data['taxpayer']['address_2'],
            'phone_number':
            data['taxpayer']['phone_number'],
            'location':
            data['taxpayer']['location'],
            'pincode':
            data['taxpayer']['pincode'],
            'state_code':
            data['taxpayer']['state_code'],
            'amount_before_gst':
            round(value_before_gst, 2),
            "amount_after_gst":
            round(value_after_gst, 2),
            "other_charges":
            round(other_charges, 2),
            "other_charges_before_tax": round(other_charges_before_tax,2),
            "credit_value_before_gst":
            round(credit_value_before_gst, 2),
            "credit_value_after_gst":
            round(credit_value_after_gst, 2),
            "pms_invoice_summary_without_gst":
            round(pms_invoice_summary_without_gst, 2) ,
            "pms_invoice_summary":
            round(pms_invoice_summary, 2) ,
            "sales_amount_after_tax":round(sales_amount_after_tax,2),
            "sales_amount_before_tax":round(sales_amount_before_tax,2),
            'irn_generated':
            irn_generated,
            # 'qr_generated':qr_generated,
            'irn_cancelled':
            'No',
            'qr_code_generated':
            'Pending',
            'signed_invoice_generated':
            'No',
            'company':
            data['company_code'],
            'cgst_amount':
            round(cgst_amount, 2),
            'sgst_amount':
            round(sgst_amount, 2),
            'igst_amount':
            round(igst_amount, 2),
            'total_central_cess_amount':
            round(total_central_cess_amount, 2),
            'total_state_cess_amount':
            round(total_state_cess_amount, 2),
            'total_vat_amount':
            round(total_vat_amount, 2),
            'total_gst_amount':
            round(cgst_amount, 2) + round(sgst_amount, 2) +
            round(igst_amount, 2),
            'has_credit_items':
            has_credit_items,
            'total_invoice_amount': data['total_invoice_amount'],
            'has_discount_items':has_discount_items,
            'invoice_process_time':
            datetime.datetime.utcnow() - datetime.datetime.strptime(
                data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
            'credit_cgst_amount':round(credit_cgst_amount,2),
            'credit_sgst_amount':round(credit_sgst_amount,2),
            'credit_igst_amount':round(credit_igst_amount,2),
            'total_credit_state_cess_amount':round(total_credit_state_cess_amount,2),
            'total_credit_central_cess_amount':round(total_credit_central_cess_amount,2),
            'total_credit_vat_amount': round(total_credit_vat_amount,2),
            'credit_gst_amount': round(credit_cgst_amount,2) + round(credit_sgst_amount,2) + round(credit_igst_amount,2),
            "mode": company.mode,
            "place_of_supply": company.state_code,
            "sez": data["sez"] if "sez" in data else 0,
            "allowance_invoice":allowance_invoice,
            "invoice_object_from_file":json.dumps(data['invoice_object_from_file']),
            "converted_tax_to_credit": data["converted_tax_to_credit"] if "converted_tax_to_credit" in data else "No",
            "debit_invoice":debit_invoice,
            "folioid":data["folioid"] if "folioid" in data else "",
            "tax_invoice_referrence_number": data["tax_invoice_referrence_number"] if "tax_invoice_referrence_number" in data else "",
            "tax_invoice_referrence_date": data["tax_invoice_referrence_date"] if "tax_invoice_referrence_date" in data else "",
            "invoice_mismatch_while_bulkupload_auto_b2c_success_gstr1": data["invoice_mismatch_while_bulkupload_auto_b2c_success_gstr1"] if "invoice_mismatch_while_bulkupload_auto_b2c_success_gstr1" in data else 0,
            "non_revenue_amount": non_revenue_amount,
            "pos_checks": pos_checks,
            "place_of_supply_json" : place_supplier_state_name
        })

        if "sez" in data:
            invoice.arn_number = company.application_reference_number if company.application_reference_number and data["sez"]==1 else ""
        if data['amened'] == 'Yes':
            invCount = frappe.db.get_value('Invoices',{"invoice_number": data['guest_data']['invoice_number']},["invoice_number"], as_dict=1)
                # filters={
                #     'invoice_number':
                #     ['like', data['guest_data']['invoice_number'] + '-%']
                # })
            invoice.amended_from = invCount.invoice_number
            if "-" in invCount.invoice_number[-4:]:
                amenedindex = invCount.invoice_number.rfind("-")
                ameneddigit = int(invCount.invoice_number[amenedindex+1:])
                ameneddigit = ameneddigit+1 
                invoice.invoice_number = data['guest_data']['invoice_number'] + "-"+str(ameneddigit)
                # pass
            else:
                invoice.invoice_number = data['guest_data']['invoice_number'] + "-1"
        # print(invoice.allowance_invoice)
        frappe.log_error(invoice.invoice_number, "invoice_number")		
        v = invoice.insert(ignore_permissions=True, ignore_links=True)
        frappe.log_error(v.name, "check invoice number")
        data['invoice_number'] = v.name
        data['guest_data']['invoice_number'] = v.name
        # # insert items
        # items = [x for x in data['items_data'] if '-' not in str(x['item_value'])]
        items = data['items_data']
        # items = [x for x in data['items_data'] if x['item_mode'] == "Debit"]
        # if data['total_invoice_amount'] != 0:
        itemsInsert = insert_items(items, data['invoice_number'])
        # insert_tax_summaries2(items, data['invoice_number'])
        TaxSummariesInsert(items,data['invoice_number'])
        hsnbasedtaxcodes = insert_hsn_code_based_taxes(
            items, data['guest_data']['invoice_number'],"Invoice")
        # b2cattach = Invoices()
        invoice = frappe.get_doc("Invoices",v.name)	
        if data['guest_data']['invoice_type'] == "B2C" and data['total_invoice_amount'] != 0 and len(data['items_data'])>0:
            b2cAttachQrcode = send_invoicedata_to_gcb(data['invoice_number'])
            if b2cAttachQrcode["success"] == True:
                if invoice.invoice_from=="Pms":
                    socket = invoiceCreated(b2cAttachQrcode["invoice"])
            else:
                if invoice.invoice_from=="Pms":
                    socket = invoiceCreated(invoice)
            
            return {"success": True,"data":invoice}
        else:
            if v.irn_generated in ["Pending"] and company.allow_auto_irn == 1 and data['total_invoice_amount'] != 0:
                
                tax_payer_details =  frappe.get_doc('TaxPayerDetail',data['guest_data']['gstNumber'])
                if (v.has_credit_items == "Yes" and company.auto_adjustment in ["Manual","Automatic"]) or tax_payer_details.disable_auto_irn == 1 or tax_payer_details.tax_type=="SEZ" or v.sez==1:
                    pass
                else:
                    if v.invoice_from != "Web":
                        data = {'invoice_number': v.name,'generation_type': "System"}
                        if company.einvoice_missing_date_feature !=1:
                            irn_generate = generateIrn(data)
                        else:
                            if invoice.invoice_date <= company.einvoice_missing_start_date:
                                irn_generate = generateIrn(data)
                            else:
                                from frappe.utils import add_days, getdate,date_diff 
                                today = getdate()
                                eight_days_ago = date_diff(today,invoice.invoice_date)
                                if eight_days_ago <= 8:
                                    irn_generate = generateIrn(data)
                                else:
                                    print("Invoice date expired")
                                


        # if len(data['guest_data']['gstNumber']) < 15 and len(data['guest_data']['gstNumber'])>0:
        # 	error_data = {'invoice_number':data['guest_data']['invoice_number'],'guest_name':data['guest_data']['name'],"invoice_type":"B2B","invoice_file":data['guest_data']['invoice_file'],"room_number":data['guest_data']['room_number'],'irn_generated':"Error","qr_generated":"Pending",'invoice_date':data['guest_data']['invoice_date'],'pincode':" ","state_code":" ","company":company.name,"error_message":"Invalid GstNumber","items":items}
        # 	Error_Insert_invoice(error_data)
        # document_bin = update_document_bin(data['guest_data']['print_by'], data['guest_data']['invoice_type'],data['guest_data']['invoice_number'],data['guest_data']['invoice_file'])	
        get_invoice = frappe.get_doc("Invoices",data['invoice_number'])
        if get_invoice.invoice_from=="Pms":
            socket = invoiceCreated(get_invoice)
        return {"success": True,"data":get_invoice}
    except Exception as e:
        print(e, "insert invoice")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_invoice","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def insert_hsn_code_based_taxes(items, invoice_number,sacType):
    try:
        frappe.db.delete('SAC HSN Tax Summaries', {
                'parent': invoice_number})
        frappe.db.commit()

        sac_codes = []
        if len(items)>0:
            for item in items:
                # if sacType == "Credit":
                # 	item = item.__dict__
                if item['sac_code'] not in sac_codes and item['sac_code'].isdigit(
                ):
                    sac_codes.append(item['sac_code'])

            tax_data = []
            for sac in sac_codes:
                sac_tax = {
                    'cess':0,
                    'cgst': 0,
                    'sgst': 0,
                    'igst': 0,
                    'amount_before_gst':0,
                    'amount_after_gst':0,
                    'sac_hsn_code': sac,
                    'invoice_number': invoice_number,
                    'doctype': "SAC HSN Tax Summaries",
                    'parent': invoice_number,
                    'parentfield': 'sac_hsn_based_taxes',
                    'parenttype': "invoices",
                    "state_cess":0,
                    "vat":0,
                    "type":sacType
                }
                for item in items:
                    if item['sac_code'] == sac:
                        sac_tax['cgst'] += round(item['cgst_amount'],2)
                        sac_tax['sgst'] += round(item['sgst_amount'],2)
                        sac_tax['igst'] += round(item['igst_amount'],2)
                        sac_tax['cess'] += round(item['cess_amount'],2)
                        sac_tax["state_cess"] += round(item["state_cess_amount"],2)
                        sac_tax["vat"] += round(item["vat_amount"],2)
                        sac_tax['amount_before_gst'] += round(item['item_taxable_value'],2)
                        sac_tax['amount_after_gst'] += round(item['item_value_after_gst'],2)

                tax_data.append(sac_tax)
            for sac in tax_data:
                # sac['total_amount'] = sac['cgst'] + sac['sgst'] + sac['igst'] + sac['cess']
                doc = frappe.get_doc(sac)
                doc.insert(ignore_permissions=True, ignore_links=True)
                frappe.db.commit()
            return {"sucess": True, "data": 'doc'}
        return {"success":True, "data":'doc'}	
    except Exception as e:
        print(e, "insert hsn")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_hsn_code_based_taxes","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def insert_items(items, invoice_number):
    try:
        a = frappe.db.delete('Items', {'parent': invoice_number})
        b = frappe.db.commit()
        if len(items)>0:
            for item in items:
                item['item_value'] = round(item['item_value'],2)
                item['item_value_after_gst'] = round(item['item_value_after_gst'],2)
                item['parent'] = invoice_number
                if "check_number" in item and "reference_check_number" in item:
                    poss_check = frappe.db.get_value('POS Checks', {'pos_check_reference_number': item['reference_check_number']}, ["name"])
                    if poss_check:
                        item["pos_check"] = poss_check
                        frappe.db.sql("""update `tabPOS Checks` set attached_to='{}', sync = 'Yes' where name='{}'""".format(invoice_number, poss_check))
                        frappe.db.commit()
                        item["pos_check"] = poss_check
                # if item['sac_code'].isdigit():
                if "-" in str(item['item_value']):
                    item['is_credit_item'] = "Yes"
                else:
                    item['is_credit_item'] = "No"
                doc = frappe.get_doc(item)
                doc.insert(ignore_permissions=True, ignore_links=True)
            inv = frappe.get_doc('Invoices', invoice_number)
            company = frappe.get_doc('company',inv.company)
            if company.payment_reconciliation == 1:
                paymentsAndReferences({"company":inv.company,"invoice_number":invoice_number})
            return {"sucess": True, "data": 'doc'}
            
        return {"sucess": True, "data": 'doc'}
        # print(doc)
    except Exception as e:
        print(traceback.print_exc(),"**********  insert itemns api")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_items","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist()
def combine_pos_checks_with_invoice(invoice_number):
    try:
        company = frappe.get_last_doc("company")
        items = frappe.db.get_list('POS Checks', filters={'attached_to': invoice_number}, pluck="pos_bill")
        if len(items)>0:
            cwd = os.getcwd()
            site_name = cstr(frappe.local.site)
            result = fitz.open()
            for each in items:
                file_path = cwd + "/" + site_name + each
                with fitz.open(file_path) as mfile:
                    result.insertPDF(mfile)
            file_path = cwd + "/" + site_name + "/public/files/" + invoice_number + '-POS.pdf'
            result.save(file_path)
            files_new = {"file": open(file_path, 'rb')}
            payload_new = {'is_private': 1, 'folder': 'Home'}
            file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                        data=payload_new, verify=False).json()
            if "file_url" in file_response["message"].keys():
                os.remove(file_path)
            else:
                return {"success": False, "message": "something went wrong"}
            return {"success": True, "file_url": file_response["message"]["file_url"]}
        else:
            return {"success": False, "message": "No data found"}
    except Exception as e:
        print(traceback.print_exc(),"**********  insert itemns api")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_items","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def calulate_net_yes(data,sac_code_obj,companyDetails,sez,placeofsupply):
    try:
        if "calulation_type" in data:
            if data["calulation_type"] == "line_edit":
                item_gst_percentage = float(data["cgst"]) + float(data["sgst"])
                item_igst_percentage = float(data["igst"])
                state_cess = float(data["state_cess"])
                central_cess = float(data["cess"])
                vat = float(data["vat"])
                service_charge = data["service_charge"]
                if service_charge == "Yes":
                    tax_applies = data["service_charge_tax_applies"]
            else:
                item_gst_percentage = float(sac_code_obj.cgst) + float(sac_code_obj.sgst)
                item_igst_percentage = float(sac_code_obj.igst)
                state_cess = sac_code_obj.state_cess_rate
                central_cess = sac_code_obj.central_cess_rate
                vat = sac_code_obj.vat_rate
                service_charge = sac_code_obj.service_charge
                tax_applies = sac_code_obj.service_charge_tax_applies
        else:
            item_gst_percentage = float(sac_code_obj.cgst) + float(sac_code_obj.sgst)
            item_igst_percentage = float(sac_code_obj.igst)
            state_cess = sac_code_obj.state_cess_rate
            central_cess = sac_code_obj.central_cess_rate
            vat = sac_code_obj.vat_rate
            service_charge = sac_code_obj.service_charge
            tax_applies = sac_code_obj.service_charge_tax_applies
        if sac_code_obj.taxble == "Yes":
            if sac_code_obj.code == '996311' or sac_code_obj.code == "997321":
                if "calulation_type" in data:
                    if item_gst_percentage != float(sac_code_obj.cgst) + float(sac_code_obj.sgst):
                        gst_percentage = item_gst_percentage
                        igst_percentage = item_igst_percentage
                    else:
                        gst_percentage = item_gst_percentage
                        igst_percentage = item_igst_percentage
                else:
                    if sac_code_obj.accommodation_slab == 1:
                        calulateslab = (companyDetails.slab_12_ending_range*12)/100
                        slab_amount = calulateslab+companyDetails.slab_12_ending_range
                        starting_range = (companyDetails.slab_12_starting_range*12)/100
                        acc_starting_range = starting_range+companyDetails.slab_12_starting_range
                        print(slab_amount, acc_starting_range,"...............................")
                        if float(abs(data["item_value"])) > slab_amount:
                            gst_percentage = 18
                            igst_percentage = 18
                        elif float(abs(data["item_value"]))>=acc_starting_range and float(data["item_value"]) <= slab_amount:
                            gst_percentage = 12
                            igst_percentage = 12
                        else:
                            gst_percentage = 0
                            igst_percentage = 0
                            data['type'] = "Excempted"
                    else:
                        gst_percentage = item_gst_percentage
                        igst_percentage = item_igst_percentage
            else:
                gst_percentage = item_gst_percentage
                igst_percentage = item_igst_percentage
            if (sez == 1 and sac_code_obj.exempted == 0) or placeofsupply != companyDetails.state_code:
                data["sgst"] = 0
                data["cgst"] = 0
                data["igst"] = igst_percentage
                data['type'] = "Included"
            elif sez == 1 and sac_code_obj.exempted == 1:
                data["sgst"] = 0
                data["cgst"] = 0
                data["igst"] = 0
                data['type'] = "Excempted"
            else:
                data['cgst'] = gst_percentage/2
                data['sgst'] = gst_percentage/2
                data["igst"] = 0
                data['type'] = "Included"
        else:
            data["sgst"] = 0
            data["cgst"] = 0
            data["igst"] = 0
            data['type'] = "Non-Gst"
        if service_charge == "Yes":
            if "calulation_type" in data:
                if data["calulation_type"] == "line_edit":
                    service_charge_per = data["service_charge_rate"]
                else:
                    if sac_code_obj.one_sc_applies_to_all == 1:
                        service_charge_per = companyDetails.service_charge_percentage
                    else:
                        service_charge_per = sac_code_obj.service_charge_rate
            else:
                if sac_code_obj.one_sc_applies_to_all == 1:
                    service_charge_per = companyDetails.service_charge_percentage
                else:
                    service_charge_per = sac_code_obj.service_charge_rate
            if tax_applies != "No Tax":
                statecess_percentage = (service_charge_per*state_cess)/100
                centralcess_percentage = (service_charge_per*central_cess)/100
                if tax_applies != "Separate GST":
                    sc_gst_per = (service_charge_per*(data["sgst"]+data["cgst"]+data["igst"]))/100
                    vat_percentage = (service_charge_per*vat)/100
                else:
                    if "calulation_type" in data:
                        if data["calulation_type"] == "line_edit":
                            sc_gst_per = (service_charge_per*data["sc_gst_tax_rate"])/100
                        else:
                            sc_gst_per = (service_charge_per*sac_code_obj.sc_gst_tax_rate)/100
                    else:
                        sc_gst_per = (service_charge_per*sac_code_obj.sc_gst_tax_rate)/100
                    vat_percentage = 0
            else:
                statecess_percentage = 0
                centralcess_percentage = 0
                vat_percentage = 0
                sc_gst_per = 0
            service_charge_per = service_charge_per+statecess_percentage+centralcess_percentage+vat_percentage+sc_gst_per
        else:
            service_charge_per = 0
        total_gst_percentage = data["sgst"]+data["cgst"]+data["igst"]+service_charge_per+state_cess+central_cess+vat
        reverse_calculation = round(data['item_value'] * (100 / (total_gst_percentage + 100)),3)
        data["item_value"] = reverse_calculation
        return {"success":True,"data":data}
    except Exception as e:
        print(e,"calulate_net_yes")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing calulate_net_yes","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

@frappe.whitelist()
def calulate_items(data):
    # items, invoice_number,company_code
    try:
        total_items = []
        second_list = []
        companyDetails = frappe.get_doc('company', data['company_code'])
        if any("split_value" in check for check in data["items"]):
            non_split = list(sv for sv in data["items"] if "split_value" not in sv)
            data["items"] = list(st for st in data["items"] if "split_value" in st)
            sort_ids = [ sub['sort_order'] for sub in data["items"]]
            nonsplit = []
            for nsplit in non_split:
                if int(nsplit["sort_order"]) not in sort_ids:
                    nsplit["date"] = datetime.datetime.strptime(nsplit["date"],companyDetails.invoice_item_date_format).strftime('%Y-%m-%d %H:%M:%S')
                    nonsplit.append(nsplit)
            total_items.extend(nonsplit)
        if any("sacName" in checkname for checkname in data["items"]) and not any("split_value" in check for check in data["items"]):
            olditems = list(st for st in data["items"] if "sacName" not in st)
            for changedate_format in olditems:
                changedate_format["date"] = datetime.datetime.strptime(changedate_format["date"],companyDetails.invoice_item_date_format).strftime('%Y-%m-%d %H:%M:%S')
            total_items.extend(olditems)
            data["items"] = list(scn for scn in data["items"] if "sacName" in scn)
        if "guest_data" in list(data.keys()):
            invoice_category = data['guest_data']['invoice_category']
        else:
            invoice_category = "Tax Invoice"
        if invoice_category == "Tax Invoice" or invoice_category == "Debit Invoice":
            if companyDetails.allowance_type == "Credit":
                ItemMode = "Credit"
            else:
                ItemMode = "Discount"
        elif invoice_category == "Credit Invoice":
            ItemMode = "Credit"
        else:
            pass 
        data['invoice_item_date_format'] = companyDetails.invoice_item_date_format
        # companyDetails = frappe.get_doc('company', data['company_code'])
        if "sez" in data:
            sez = data["sez"]
            if sez == 0:
                doc = frappe.db.exists("Invoices",data["invoice_number"])
                if doc:
                    invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                    sez = invoice_doc.sez
        else:
            doc = frappe.db.exists("Invoices",data["invoice_number"])
            if doc:
                invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                sez = invoice_doc.sez
            else:
                sez = 0
        if "place_of_supply" in data:
            placeofsupply = data["place_of_supply"]
        else:
            doc = frappe.db.exists("Invoices",data["invoice_number"])
            if doc:
                invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                placeofsupply = invoice_doc.place_of_supply
                if not placeofsupply:
                    placeofsupply = companyDetails.state_code
            else:
                placeofsupply = companyDetails.state_code
        for item in data['items']:
            final_item = {}
            if "quantity" in list(item.keys()):
                final_item['unit_of_measurement']=item['unit_of_measurement']
                final_item['unit_of_measurement_description'] = item['unit_of_measurement_description']
                final_item['quantity'] = item['quantity']
            else:
                final_item['unit_of_measurement']= "OTH"
                final_item['unit_of_measurement_description'] = "OTHERS"
                final_item['quantity'] = 1
            scharge = companyDetails.service_charge_percentage
            
            acc_gst_percentage = 0.00
            acc_igst_percentage = 0.00
            if companyDetails.calculation_by == "Description":
                if companyDetails.number_in_description == 1:
                    item_description = (item['name']).strip()
                else:
                    item_description = item['name']
                sac_code_based_gst = frappe.db.get_list(
                    'SAC HSN CODES',
                    filters={'name': ['=',item_description]})
                if not sac_code_based_gst:
                    sac_code_based_gst = frappe.db.get_list(
                        'SAC HSN CODES',
                        filters={'name': ['like', item_description + '%']})
                    if len(sac_code_based_gst) > 0:
                        sac_names = list(map(lambda x : x['name'], sac_code_based_gst))
                        min_len_des = min(sac_names, key = len)
                        sac_code_based_gst = [{"name":min_len_des}]
                if len(sac_code_based_gst)>0:
                    sac_code_based_gst_rates = frappe.get_doc(
                    'SAC HSN CODES',sac_code_based_gst[0]['name'])	
                    SAC_CODE = sac_code_based_gst_rates.code 
                    if sac_code_based_gst_rates.ignore == 1:
                        continue 
                    item['item_type'] = sac_code_based_gst_rates.type
                else:
                    return{"success":False,"message":"SAC Code "+ item_description +" not found"}
                if item['sac_code'] == "No Sac" and SAC_CODE.isdigit():
                    item['sac_code'] = sac_code_based_gst_rates.code
                if "net" in item:
                    net_value = item["net"]
                else:
                    net_value = sac_code_based_gst_rates.net
                if net_value == "Yes":
                    item_data = calulate_net_yes(item,sac_code_based_gst_rates,companyDetails,sez,placeofsupply)
                    if item_data["success"] == True:
                        item = item_data["data"]
                    else:
                        return item_data
                if item['sac_code'] == '996311' or item['sac_code'] == "997321":
                    if sac_code_based_gst_rates.is_service_charge_item == 1 and companyDetails.enable_slab_for_room_service_charge == 1:
                        if "adjustment" in data:
                            acc_gst_percentage = item["cgst"]+item["sgst"]
                            acc_igst_percentage = item["igst"]
                        else:
                            percentage_gst = SCCheckRatePercentages(item, sez, placeofsupply, sac_code_based_gst_rates.exempted, companyDetails.state_code)
                            if percentage_gst["success"] == True:
                                acc_gst_percentage = percentage_gst["gst_percentage"]	
                                acc_igst_percentage = percentage_gst["igst_percentage"]
                            else:
                                {"success": False, "message": "error in slab helper function"}
                    else:
                        if "adjustment" in data:
                            acc_gst_percentage = item["cgst"]+item["sgst"]
                            acc_igst_percentage = item["igst"]
                        else:
                            percentage_gst = CheckRatePercentages(item, sez, placeofsupply, sac_code_based_gst_rates.exempted, companyDetails.state_code)
                            if percentage_gst["success"] == True:
                                acc_gst_percentage = percentage_gst["gst_percentage"]	
                                acc_igst_percentage = percentage_gst["igst_percentage"]
                            else:
                                {"success": False, "message": "error in slab helper function"}
                service_charge_name = (companyDetails.sc_name)
                if (service_charge_name != "" and companyDetails.enable_sc_from_folios == 1):
                    gst_value = 0
                    service_dict = {}
                    service_charge_name = service_charge_name.strip()
                    if companyDetails.adjustment_service_charge_list != "":
                        split_string = companyDetails.adjustment_service_charge_list.split(",")
                        remove_spaces = [num.strip() for num in split_string]
                    else:
                        remove_spaces = []
                    if item["name"] not in remove_spaces:
                        if service_charge_name in item["name"]:
                            scharge = companyDetails.service_charge_percentage
                            if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                                gst_percentage = 0
                                igst_percentage = companyDetails.sc_gst_percentage
                            elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                                gst_percentage = 0
                                igst_percentage = 0
                            else:
                                gst_percentage = companyDetails.sc_gst_percentage
                                igst_percentage = 0
                            sac_code_new = companyDetails.sc_sac_code
                            vat_rate_percentage = sac_code_based_gst_rates.vat_rate
                            scharge_value = item["item_value"]
                            if sac_code_based_gst_rates.service_charge_net == "Yes":
                                scharge_value_base = round(scharge_value * (100 / ((gst_percentage+igst_percentage) + 100)),3)
                                gst_value = scharge_value- scharge_value_base
                                scharge_value = scharge_value_base
                            if vat_rate_percentage>0 and sac_code_based_gst_rates.disable_vat_for_sc == 0:
                                vatamount = (vat_rate_percentage * scharge_value) / 100.0
                                service_dict['vat_amount'] = vatamount
                                service_dict['vat'] = vat_rate_percentage
                            else:
                                vatamount = 0
                                service_dict['vat_amount'] = 0
                                service_dict['vat'] = 0
                            if sac_code_based_gst_rates.central_cess_rate>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                                centralcessamount = (sac_code_based_gst_rates.central_cess_rate * scharge_value) / 100.0
                                service_dict['cess_amount'] = centralcessamount
                                service_dict['cess'] = sac_code_based_gst_rates.central_cess_rate
                            else:
                                centralcessamount = 0
                                service_dict['cess_amount'] = 0
                                service_dict['cess'] = 0
                            if sac_code_based_gst_rates.state_cess_rate>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                                statecessamount = (sac_code_based_gst_rates.state_cess_rate * scharge_value) / 100.0
                                service_dict['state_cess_amount'] = statecessamount
                                service_dict['state_cess'] = sac_code_based_gst_rates.state_cess_rate
                            else:
                                statecessamount = 0
                                service_dict['state_cess_amount'] = 0
                                service_dict['state_cess'] = 0	
                            if sez == 1 and sac_code_based_gst_rates.exempted == 1:
                                type_item = "Excempted"
                            else:
                                type_item = "Included"
                            if gst_value==0:
                                gst_value = (gst_percentage* scharge_value)/100.0
                                igst_value = (igst_percentage* scharge_value)/100.0
                            else:
                                igst_value = 0
                            if gst_percentage>0 or igst_percentage>0:
                                scTaxble = "Yes"
                            else:
                                scTaxble = sac_code_based_gst_rates.taxble		
                            service_dict['item_name'] = item['name']
                            service_dict['description'] = item['name']
                            service_dict['date'] = datetime.datetime.strptime(item['date'],data['invoice_item_date_format'])
                            service_dict['sac_code'] = sac_code_new
                            service_dict['sac_code_found'] = 'Yes'
                            service_dict['cgst'] = gst_percentage/2
                            service_dict['other_charges'] = 0
                            service_dict['cgst_amount'] = gst_value/2
                            service_dict['sgst'] = gst_percentage/2
                            service_dict['sgst_amount'] = gst_value/2
                            service_dict['igst'] = igst_percentage
                            service_dict['igst_amount'] = igst_value
                            service_dict['gst_rate'] = gst_percentage + igst_percentage
                            service_dict['item_value_after_gst'] = scharge_value + gst_value + vatamount + statecessamount + centralcessamount + igst_value
                            service_dict['item_taxable_value'] = scharge_value 
                            service_dict['item_value'] = scharge_value
                            service_dict['taxable'] = scTaxble#"Yes" if gst_percentage>0 else "No"
                            service_dict["sac_index"] = sac_code_based_gst_rates.sac_index
                            # service_dict['cess'] = 0
                            # service_dict['cess_amount'] = 0
                            # service_dict['state_cess'] = 0
                            # service_dict['state_cess_amount'] = 0
                            service_dict['type'] = type_item
                            service_dict['item_mode'] = ItemMode if "-" in str(scharge_value) else "Debit"
                            service_dict['item_type'] = sac_code_based_gst_rates.type
                            # service_dict['vat_amount'] = 0
                            # service_dict['vat'] = 0
                            sortorder = item['sort_order']
                            service_dict['sort_order'] = float(sortorder)
                            service_dict['doctype'] = 'Items'
                            service_dict['parentfield'] = 'items'
                            service_dict['parenttype'] = 'invoices'
                            service_dict['unit_of_measurement']= "OTH"
                            service_dict['quantity'] = 1
                            service_dict['unit_of_measurement_description'] = "OTHERS"
                            service_dict["is_service_charge_item"] = "Yes"
                            second_list.append(service_dict)
                            continue
                if  sac_code_based_gst_rates.service_charge == "Yes" and companyDetails.enable_sc_from_folios == 0:
                    gst_value = 0
                    service_dict = {}
                    if sac_code_based_gst_rates.one_sc_applies_to_all == 1:
                        scharge = companyDetails.service_charge_percentage
                    else:
                        scharge = sac_code_based_gst_rates.service_charge_rate
                    if sac_code_based_gst_rates.service_charge_tax_applies == "Apply From Parent":
                        if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                            gst_percentage = 0
                            igst_percentage = float(sac_code_based_gst_rates.igst)
                        elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                            gst_percentage = 0
                            igst_percentage = 0
                        else:
                            gst_percentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
                            igst_percentage = 0
                        sac_code_new = sac_code_based_gst_rates.code
                        vat_rate_percentage = sac_code_based_gst_rates.vat_rate
                    elif sac_code_based_gst_rates.service_charge_tax_applies == "Separate GST":
                        if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                            gst_percentage = 0
                            igst_percentage = sac_code_based_gst_rates.sc_gst_tax_rate
                        elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                            gst_percentage = 0
                            igst_percentage = 0
                        else:
                            gst_percentage = sac_code_based_gst_rates.sc_gst_tax_rate
                            igst_percentage = 0
                        # gst_percentage = sac_code_based_gst_rates.sc_gst_tax_rate
                        sac_code_new = sac_code_based_gst_rates.sc_sac_code
                        vat_rate_percentage = 0
                    else:
                        gst_percentage = 0
                        igst_percentage = 0
                        sac_code_new = sac_code_based_gst_rates.code
                        vat_rate_percentage = 0
                    # if companyDetails.reverse_calculation == 1 and net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1:
                    # 	if sac_code_based_gst_rates.taxble == "Yes":
                    # 		total_gst_percentage = gst_percentage+igst_percentage
                    # 		scharge_value_no = scharge
                    # 	else:
                    # 		total_gst_percentage = 0
                    # 		scharge_value_no = scharge + float("0."+str(int((gst_percentage+igst_percentage)/2)))
                    # 	base_valu_inc_sc = round(item['item_value'] * (100 / ((total_gst_percentage) + 100)),3)
                    # 	item['item_value'] = round(base_valu_inc_sc * (100 / (scharge_value_no + 100)),3)
                    # if (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 0) or (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 1) or (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1 and companyDetails.reverse_calculation == 0):
                    # 	base_value = round(item['item_value'] * (100 / ((gst_percentage+igst_percentage) + 100)),3) 
                    # 	scharge_value = (scharge * base_value) / 100.0
                    # 	gst_value = round((gst_percentage+igst_percentage)*scharge_value )/ 100.0
                    # 	if sac_code_based_gst_rates.service_charge_net == "Yes":
                    # 		scharge_value_base = round(scharge_value * (100 / ((gst_percentage+igst_percentage) + 100)),3)
                    # 		gst_value = scharge_value- scharge_value_base
                    # 		scharge_value = scharge_value_base
                    # 	item['base_value'] = base_value


                    # 	# gst_percentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
                    # else:
                    base_value = item['item_value']
                    scharge_value = (scharge * item['item_value']) / 100.0
                    if (item['sac_code'] == '996311' or item['sac_code'] == "997321") and sac_code_based_gst_rates.service_charge_tax_applies == "Apply From Parent":
                        gst_percentage = acc_gst_percentage
                        igst_percentage = acc_igst_percentage
                    if sac_code_based_gst_rates.service_charge_net == "Yes":
                        scharge_value_base = round(scharge_value * (100 / ((gst_percentage+igst_percentage) + 100)),3)
                        gst_value = scharge_value- scharge_value_base
                        scharge_value = scharge_value_base
                        
                    if vat_rate_percentage>0 and sac_code_based_gst_rates.disable_vat_for_sc == 0:
                        vatamount = (vat_rate_percentage * scharge_value) / 100.0
                        service_dict['vat_amount'] = vatamount
                        service_dict['vat'] = vat_rate_percentage
                    else:
                        vatamount = 0
                        service_dict['vat_amount'] = 0
                        service_dict['vat'] = 0
                    if sac_code_based_gst_rates.central_cess_rate>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                        centralcessamount = (sac_code_based_gst_rates.central_cess_rate * scharge_value) / 100.0
                        service_dict['cess_amount'] = centralcessamount
                        service_dict['cess'] = sac_code_based_gst_rates.central_cess_rate
                    else:
                        centralcessamount = 0
                        service_dict['cess_amount'] = 0
                        service_dict['cess'] = 0
                    if sac_code_based_gst_rates.state_cess_rate>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                        statecessamount = (sac_code_based_gst_rates.state_cess_rate * scharge_value) / 100.0
                        service_dict['state_cess_amount'] = statecessamount
                        service_dict['state_cess'] = sac_code_based_gst_rates.state_cess_rate
                    else:
                        statecessamount = 0
                        service_dict['state_cess_amount'] = 0
                        service_dict['state_cess'] = 0	
                    if sez == 1 and sac_code_based_gst_rates.exempted == 1:
                        type_item = "Excempted"
                    else:
                        type_item = "Included"
                    if gst_value==0:
                        gst_value = (gst_percentage* scharge_value)/100.0
                        igst_value = (igst_percentage* scharge_value)/100.0
                    else:
                        igst_value = 0
                    if gst_percentage>0 or igst_percentage>0:
                        scTaxble = "Yes"
                    else:
                        scTaxble = sac_code_based_gst_rates.taxble		
                    service_dict['item_name'] = item['name']+"-SC " + str(scharge)
                    service_dict['description'] = item['name']+"-SC " + str(scharge)
                    service_dict['date'] = datetime.datetime.strptime(item['date'],data['invoice_item_date_format'])
                    service_dict['sac_code'] = sac_code_new
                    service_dict['sac_code_found'] = 'Yes'
                    service_dict['cgst'] = gst_percentage/2
                    service_dict['other_charges'] = 0
                    service_dict['cgst_amount'] = gst_value/2
                    service_dict['sgst'] = gst_percentage/2
                    service_dict['sgst_amount'] = gst_value/2
                    service_dict['igst'] = igst_percentage
                    service_dict['igst_amount'] = igst_value
                    service_dict['gst_rate'] = gst_percentage + igst_percentage
                    service_dict['item_value_after_gst'] = scharge_value + gst_value + vatamount + statecessamount + centralcessamount + igst_value
                    service_dict['item_taxable_value'] = scharge_value 
                    service_dict['item_value'] = scharge_value
                    service_dict['taxable'] = scTaxble#"Yes" if gst_percentage>0 else "No"
                    service_dict["sac_index"] = sac_code_based_gst_rates.sac_index
                    # service_dict['cess'] = 0
                    # service_dict['cess_amount'] = 0
                    # service_dict['state_cess'] = 0
                    # service_dict['state_cess_amount'] = 0
                    service_dict['type'] = type_item
                    service_dict['item_mode'] = ItemMode if "-" in str(scharge_value) else "Debit"
                    service_dict['item_type'] = sac_code_based_gst_rates.type
                    # service_dict['vat_amount'] = 0
                    # service_dict['vat'] = 0
                    sortorder = str(item['sort_order'])+".1"
                    service_dict['sort_order'] = float(sortorder)
                    service_dict['doctype'] = 'Items'
                    service_dict['parentfield'] = 'items'
                    service_dict['parenttype'] = 'invoices'
                    service_dict['unit_of_measurement']= "OTH"
                    service_dict['quantity'] = 1
                    service_dict['unit_of_measurement_description'] = "OTHERS"
                    service_dict["is_service_charge_item"] = "Yes"
                    second_list.append(service_dict)
                    # second_list	
                # print(item)
                if sac_code_based_gst_rates.type == "Discount":
                        final_item['sac_code'] = 'No Sac'
                        final_item['sac_code_found'] = 'No'
                        final_item['cgst'] = 0
                        final_item['other_charges'] = 0
                        final_item['cgst_amount'] = 0
                        final_item['sgst'] = 0
                        final_item['sgst_amount'] = 0
                        final_item['igst'] = 0
                        final_item['igst_amount'] = 0
                        final_item['gst_rate'] = 0
                        final_item['item_value_after_gst'] = item['item_value']
                        final_item['item_value'] = item['item_value']
                        final_item['taxable'] = sac_code_based_gst_rates.taxble
                        final_item['cess'] = 0
                        final_item['cess_amount'] = 0
                        final_item['type'] = "Excempted"
                        final_item['item_type'] = "Discount"
                        final_item['item_mode'] = ItemMode
                        final_item['sort_order'] = item['sort_order']
                if sac_code_based_gst_rates.taxble == "Yes" and sac_code_based_gst_rates.type != "Discount":
                    if "-" in str(item['item_value']) and invoice_category == "Tax Invoice":
                        final_item['item_mode'] = ItemMode
                    elif invoice_category == "Credit Invoice":	
                        final_item['item_mode'] = "Credit"
                    else:
                        final_item['item_mode'] = "Debit"
                    # if sac_code_based_gst_rates.net == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])):
                    # if (net_value == "No") or (net_value == "Yes"):
                    if (item['sac_code'] == '996311' or item['sac_code'] == '997321') and sac_code_based_gst_rates.accommodation_slab == 1:
                        if acc_gst_percentage == 0 and acc_igst_percentage == 0:
                            final_item['cgst'] = 0
                            final_item['sgst'] = 0
                            final_item['igst'] = 0
                            final_item['type'] = "Excempted"
                        else:
                            final_item['cgst'] = acc_gst_percentage/2
                            final_item['sgst'] = acc_gst_percentage/2
                            final_item['igst'] = acc_igst_percentage
                            final_item['type'] = "Included"
                    else:
                        if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                            final_item["sgst"] = 0
                            final_item["cgst"] = 0
                            final_item["igst"] = float(sac_code_based_gst_rates.igst)
                            final_item['type'] = "Included"
                        elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                            final_item["sgst"] = 0
                            final_item["cgst"] = 0
                            final_item["igst"] = 0
                            final_item['type'] = "Excempted"
                        else:
                            final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
                            final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
                            final_item["igst"] = 0
                            final_item['type'] = "Included"
                    final_item['cgst_amount'] = round((item["item_value"]*(final_item['cgst']/100)),3)
                    final_item['sgst_amount'] = round((item["item_value"]*(final_item['sgst']/100)),3)
                    final_item['igst_amount'] = round((item["item_value"]*(final_item['igst']/100)),3)
                    final_item['gst_rate'] = final_item['cgst']+final_item['sgst']+final_item['igst']
                    final_item['item_value_after_gst'] = final_item['cgst_amount']+final_item['sgst_amount']+final_item['igst_amount']+item['item_value']
                    final_item['item_value'] = item['item_value']
                    # elif net_value == "Yes":
                    # 	calulate_net_yes(item,sac_code_based_gst_rates,companyDetails,sez,placeofsupply)
                    # 	if item['sac_code'] == '996311' or item['sac_code'] == '997321':
                    # 		percentage_gst = CheckRatePercentages(item, sez, placeofsupply, sac_code_based_gst_rates.exempted, companyDetails.state_code)
                    # 		if percentage_gst["success"] == True:
                    # 			acc_gst_percentage = percentage_gst["gst_percentage"]	
                    # 			acc_igst_percentage = percentage_gst["igst_percentage"]
                    # 		else:
                    # 			{"success": False, "message": "error in slab helper function"}
                    # 	if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                    # 		final_item["sgst"] = 0
                    # 		final_item["cgst"] = 0
                    # 		final_item["igst"] = float(sac_code_based_gst_rates.igst)
                    # 		final_item['type'] = "Included"
                    # 	elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                    # 		final_item["sgst"] = 0
                    # 		final_item["cgst"] = 0
                    # 		final_item["igst"] = 0
                    # 		final_item['type'] = "Excempted"
                    # 	else:
                    # 		final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
                    # 		final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
                    # 		final_item["igst"] = 0
                    # 		final_item['type'] = "Included"
                    # 	gst_percentage = final_item["cgst"]+final_item["sgst"]
                    # 	base_value = round(item['item_value'] * (100 / (gst_percentage + 100)),3)
                    # 	gst_value = item['item_value'] - base_value
                    # 	final_item['cgst_amount'] = round(gst_value / 2,3)
                    # 	final_item['sgst_amount'] = round(gst_value / 2,3)
                    # 	# final_item['igst'] = float(sac_code_based_gst_rates.igst)
                    # 	if float(final_item["igst"]) <= 0:
                    # 		final_item['igst_amount'] = 0
                    # 	else:
                    # 		base_value = item['item_value'] * (100 / (final_item["igst"] + 100))
                    # 		final_item['igst_amount'] = item['item_value'] - base_value
                    # 	final_item['gst_rate'] = gst_percentage + final_item["igst"]
                    # 	final_item['item_value_after_gst'] = item['item_value']
                    # 	final_item['item_value'] = base_value
                    final_item['other_charges'] = 0
                    final_item['sac_code_found'] = 'Yes'
                    final_item['taxable'] = sac_code_based_gst_rates.taxble
                    final_item['sort_order'] = item['sort_order']
                else:
                    # if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])) and sac_code_based_gst_rates.type != "Discount":
                    if (item['sac_code'] != "996311" or item['sac_code'] != "997321") and sac_code_based_gst_rates.taxble == "No":
                        if sac_code_based_gst_rates.ignore_non_taxable_items == 1:
                            gst_tax_percentage = float(sac_code_based_gst_rates.cgst)+float(sac_code_based_gst_rates.sgst)
                            gst_amount_value = (item['item_value'] * gst_tax_percentage)/100
                            final_item['item_value_after_gst'] = round(gst_amount_value+item["item_value"],3)
                            final_item['item_value'] = item['item_value']
                            final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
                            final_item['other_charges'] = 0
                            final_item['cgst_amount'] = gst_amount_value/2
                            final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
                            final_item['sgst_amount'] = gst_amount_value/2
                            final_item['igst'] = 0
                            final_item['igst_amount'] = 0
                            final_item['gst_rate'] = gst_tax_percentage
                            final_item['revenue_item'] = "Non-Revenue" if sac_code_based_gst_rates.ignore_non_taxable_items == 1 else "Revenue"
                        else:
                            # if (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 0) or (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 1) or (net_value == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1 and companyDetails.reverse_calculation == 0):
                            # 	calulate_net_yes(item,sac_code_based_gst_rates,companyDetails,sez,placeofsupply)
                            # 	vatcessrate = sac_code_based_gst_rates.state_cess_rate+sac_code_based_gst_rates.central_cess_rate+sac_code_based_gst_rates.vat_rate
                            # 	if "item_value_after_gst" in item and "split_value" not in item:
                            # 		final_item['item_value'] = item["item_value"]
                            # 		final_item['item_value_after_gst'] = item["item_value"]
                            # 	else:
                            # 		base_value = round(item['item_value'] * (100 / (vatcessrate + 100)),3)
                            # 		final_item['item_value'] = base_value
                            # 		final_item['item_value_after_gst'] = base_value
                            # 		item["item_value"] = base_value
                            # else:
                            final_item['item_value_after_gst'] = item['item_value']
                            final_item['item_value'] = item['item_value']
                            final_item['cgst'] = 0
                            final_item['other_charges'] = 0
                            final_item['cgst_amount'] = 0
                            final_item['sgst'] = 0
                            final_item['sgst_amount'] = 0
                            final_item['igst'] = 0
                            final_item['igst_amount'] = 0
                            final_item['gst_rate'] = 0
                        final_item['sort_order'] = item['sort_order']
                        if item['sac_code'].isdigit():
                            final_item['sac_code'] = item['sac_code']
                            final_item['sac_code_found'] = 'Yes'
                        else:
                            final_item['sac_code'] = 'No Sac'
                            final_item['sac_code_found'] = 'No'
                        final_item['taxable'] = sac_code_based_gst_rates.taxble
                        final_item['type'] = "Non-Gst"
                        # final_item['item_mode'] = "Debit"
                        companyDetails = frappe.get_doc('company', data['company_code'])
                        if invoice_category == "Tax Invoice" or invoice_category == "Debit Invoice":
                            if companyDetails.allowance_type == "Credit":
                                ItemMode = "Credit"
                            else:
                                ItemMode = "Discount"
                        elif invoice_category == "Credit Invoice":
                            ItemMode = "Credit"
                        else:
                            pass	
                        if "-" in str(item['item_value']):
                            ItemMode = "Credit"
                            companyDetails = frappe.get_doc('company', data['company_code'])
                            if invoice_category == "Tax Invoice" or invoice_category == "Debit Invoice":
                                if companyDetails.allowance_type == "Credit":
                                    ItemMode = "Credit"
                                else:
                                    ItemMode = "Discount"
                            elif invoice_category == "Credit Invoice":
                                ItemMode = "Credit"
                            else:
                                pass
                            final_item['item_mode'] = ItemMode
                        else:
                            final_item['item_mode'] = "Debit"
                # if "state_code" in data:
                #     if (data["company_code"] == "NKIP-01" or data["company_code"] == "CPK-01" or data["company_code"] == "KMH-01") and data["state_code"] == companyDetails.state_code:
                #         final_item["state_cess_amount"] = 0
                #         final_item['state_cess'] = 0
                #     else:
                #         final_item['state_cess'] = sac_code_based_gst_rates.state_cess_rate
                #         if sac_code_based_gst_rates.state_cess_rate > 0:
                #             final_item["state_cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.state_cess_rate/100))
                #         else:
                #             final_item["state_cess_amount"] = 0
                # else:
                final_item['state_cess'] = sac_code_based_gst_rates.state_cess_rate
                if sac_code_based_gst_rates.state_cess_rate > 0:
                    final_item["state_cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.state_cess_rate/100))
                else:
                    final_item["state_cess_amount"] = 0
                final_item['cess'] = sac_code_based_gst_rates.central_cess_rate
                if sac_code_based_gst_rates.central_cess_rate > 0:
                    final_item["cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.central_cess_rate/100))
                else:
                    final_item["cess_amount"] = 0
                final_item['vat'] = sac_code_based_gst_rates.vat_rate
                if sac_code_based_gst_rates.vat_rate > 0:
                    final_item["vat_amount"] = (item["item_value"]*(sac_code_based_gst_rates.vat_rate/100))
                    # if sac_code_based_gst_rates.service_charge == "Yes":
                    # 	vatservicecharge = (scharge * final_item["vat_amount"]) / 100.0	
                    # 	final_item["vat_amount"] = final_item["vat_amount"]+vatservicecharge
                else:
                    final_item["vat_amount"] = 0
                final_item['item_value_after_gst'] = final_item['item_value_after_gst']+final_item['cess_amount']+final_item['vat_amount']+final_item["state_cess_amount"]
            else:
                sac_code_based_gst_rates = frappe.get_doc(
                    'SAC HSN CODES',item["sac_code"])
                item['item_type'] = sac_code_based_gst_rates.type
                if sac_code_based_gst_rates.type == "Discount":
                        final_item['sac_code'] = 'No Sac'
                        final_item['sac_code_found'] = 'No'
                        final_item['cgst'] = 0
                        final_item['other_charges'] = 0
                        final_item['cgst_amount'] = 0
                        final_item['sgst'] = 0
                        final_item['sgst_amount'] = 0
                        final_item['igst'] = 0
                        final_item['igst_amount'] = 0
                        final_item['gst_rate'] = 0
                        final_item['item_value_after_gst'] = item['item_value']
                        final_item['item_value'] = item['item_value']
                        final_item['taxable'] = sac_code_based_gst_rates.taxble
                        final_item['cess'] = 0
                        final_item['cess_amount'] = 0
                        final_item['type'] = "Excempted"
                        final_item['item_type'] = "Discount"
                        final_item['item_mode'] = ItemMode
                if item['sac_code'] == '996311' or item['sac_code'] == "997321":
                    percentage_gst = CheckRatePercentages(item)
                    if percentage_gst["success"] == True:
                        acc_gst_percentage = percentage_gst["gst_percentage"]	
                    else:
                        {"success": False, "message": "error in slab helper function"}
                if sac_code_based_gst_rates.taxble == "Yes" and sac_code_based_gst_rates.type != "Discount":
                    if "-" in str(item['item_value']):
                        final_item['item_mode'] = ItemMode
                    else:
                        final_item['item_mode'] = "Debit"
                    # if sac_code_based_gst_rates.net == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])):
                    if sac_code_based_gst_rates.net == "No":
                        if (item['sac_code'] == '996311' or item['sac_code'] == "997321") and sac_code_based_gst_rates.accommodation_slab == 1:
                            if acc_gst_percentage == 0:
                                final_item['cgst'] = 0
                                final_item['sgst'] = 0
                                final_item['igst'] = 0
                                final_item['type'] = "Excempted"
                            else:
                                final_item['cgst'] = acc_gst_percentage/2
                                final_item['sgst'] = acc_gst_percentage/2
                                final_item['igst'] = 0
                                final_item['type'] = "Included"
                        else:
                            final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
                            final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
                            final_item['igst'] = float(sac_code_based_gst_rates.igst)
                        final_item['cgst_amount'] = round((item["item_value"]*(final_item['cgst']/100)),3)
                        final_item['sgst_amount'] = round((item["item_value"]*(final_item['sgst']/100)),3)
                        final_item['igst_amount'] = round((item["item_value"]*(final_item['igst']/100)),3)
                        final_item['gst_rate'] = final_item['cgst']+final_item['sgst']+final_item['igst']
                        final_item['item_value_after_gst'] = final_item['cgst_amount']+final_item['sgst_amount']+final_item['igst_amount']+item['item_value']
                        final_item['item_value'] = item['item_value']
                    elif sac_code_based_gst_rates.net == "Yes":
                        gst_percentage = (float(sac_code_based_gst_rates.cgst) + float(sac_code_based_gst_rates.sgst))
                        base_value = round(item['item_value'] * (100 / (gst_percentage + 100)),3)
                        gst_value = item['item_value'] - base_value
                        final_item['cgst'] = float(sac_code_based_gst_rates.cgst)
                        final_item['sgst'] = float(sac_code_based_gst_rates.sgst)
                        final_item['cgst_amount'] = round(gst_value / 2,3)
                        final_item['sgst_amount'] = round(gst_value / 2,3)
                        final_item['igst'] = float(sac_code_based_gst_rates.igst)
                        if float(sac_code_based_gst_rates.igst) <= 0:
                            final_item['igst_amount'] = 0
                        else:
                            gst_percentage = (float(sac_code_based_gst_rates.cgst) +
                                            float(sac_code_based_gst_rates.sgst))
                            base_value = item['item_value'] * (100 / (gst_percentage + 100))
                            final_item['igst_amount'] = item['item_value'] - base_value
                        final_item['gst_rate'] = float(sac_code_based_gst_rates.cgst)+float(sac_code_based_gst_rates.sgst)+float(sac_code_based_gst_rates.igst)
                        final_item['item_value_after_gst'] = item['item_value']
                        final_item['item_value'] = base_value
                    final_item['other_charges'] = 0
                    final_item['sac_code_found'] = 'Yes'
                    final_item['taxable'] = sac_code_based_gst_rates.taxble
                    final_item['type'] = "Included"
                    final_item['sort_order'] = item['sort_order']
                else:
                    # if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])) and sac_code_based_gst_rates.type != "Discount":
                    if (item['sac_code'] != "996311" or item['sac_code'] != "997321") and sac_code_based_gst_rates.taxble == "No":
                        final_item['sort_order'] = item['sort_order']
                        if item['sac_code'].isdigit():
                            final_item['sac_code'] = item['sac_code']
                            final_item['sac_code_found'] = 'Yes'
                        else:
                            final_item['sac_code'] = 'No Sac'
                            final_item['sac_code_found'] = 'No'
                        final_item['cgst'] = 0
                        final_item['other_charges'] = 0
                        final_item['cgst_amount'] = 0
                        final_item['sgst'] = 0
                        final_item['sgst_amount'] = 0
                        final_item['igst'] = 0
                        final_item['igst_amount'] = 0
                        final_item['gst_rate'] = 0
                        final_item['item_value_after_gst'] = item['item_value']
                        final_item['item_value'] = item['item_value']
                        final_item['taxable'] = sac_code_based_gst_rates.taxble
                        final_item['type'] = "Non-Gst"
                        final_item['item_mode'] = "Debit"
                final_item['state_cess'] = sac_code_based_gst_rates.state_cess_rate
                if sac_code_based_gst_rates.state_cess_rate > 0:
                    final_item["state_cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.state_cess_rate/100))
                else:
                    final_item["state_cess_amount"] = 0
                final_item['cess'] = sac_code_based_gst_rates.central_cess_rate
                if sac_code_based_gst_rates.central_cess_rate > 0:
                    final_item["cess_amount"] = (item["item_value"]*(sac_code_based_gst_rates.central_cess_rate/100))
                else:
                    final_item["cess_amount"] = 0
                final_item['vat'] = sac_code_based_gst_rates.vat_rate
                if sac_code_based_gst_rates.vat_rate > 0:
                    final_item["vat_amount"] = (item["item_value"]*(sac_code_based_gst_rates.vat_rate/100))
                    # if sac_code_based_gst_rates.service_charge == "Yes":
                        # vatservicecharge = (scharge * final_item["vat_amount"]) / 100.0	
                        # final_item["vat_amount"] = final_item["vat_amount"]+vatservicecharge
                else:
                    final_item["vat_amount"] = 0
                final_item['item_value_after_gst'] = final_item['item_value_after_gst']+final_item['cess_amount']+final_item['vat_amount']+final_item["state_cess_amount"]
            total_items.append({
                'doctype':
                'Items',
                'sac_code':
                item['sac_code'],
                'item_name':
                item['name'],
                'sort_order':final_item['sort_order'],
                "item_type":item['item_type'],
                'date':
                datetime.datetime.strptime(item['date'],
                                            data['invoice_item_date_format']),
                'cgst':
                final_item['cgst'],
                'cgst_amount':
                round(final_item['cgst_amount'], 2),
                'sgst':
                final_item['sgst'],
                'sgst_amount':
                round(final_item['sgst_amount'], 2),
                'igst':
                final_item['igst'],
                'igst_amount':
                round(final_item['igst_amount'], 2),
                'item_value':
                final_item['item_value'],
                'description':
                item['name'],
                'item_taxable_value':
                final_item['item_value'],
                'gst_rate':
                final_item['gst_rate'],
                'item_value_after_gst':
                round(final_item['item_value_after_gst'], 2),
                'cess':
                final_item['cess'],
                'cess_amount':
                final_item['cess_amount'],
                'state_cess':final_item["state_cess"],
                "state_cess_amount":final_item["state_cess_amount"],
                'parent':
                data['invoice_number'],
                'parentfield':
                'items',
                'parenttype':
                "invoices",
                'sac_code_found':
                final_item['sac_code_found'],
                'type':
                final_item['type'],
                'other_charges':
                final_item['other_charges'],
                
                'taxable':
                final_item['taxable'],
                'item_mode':final_item['item_mode'],
                "vat_amount":final_item["vat_amount"],
                "vat":final_item['vat'],
                "unit_of_measurement":final_item['unit_of_measurement'],
                "quantity":final_item['quantity'],
                "unit_of_measurement_description":final_item['unit_of_measurement_description'],
                "is_service_charge_item": "No",
                "sac_index": sac_code_based_gst_rates.sac_index,
                "line_edit_net":net_value,
                "item_reference":item["item_reference"] if "item_reference" in item else "",
                "check_number":item["check_number"] if "check_number" in item else "",
                "reference_check_number":item["reference_check_number"] if "reference_check_number" in item else "",
                "revenue_item": final_item['revenue_item'] if "revenue_item" in final_item else "Revenue"
            })
        total_items.extend(second_list)	
        return {"success": True, "data": total_items}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing calculation_api","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}



def insert_tax_summariesd(items, invoice_number):
    try:
        tax_list = []
        for item in items:
            if item['sgst'] > 0:
                dup_dict = {
                    'tax_type': 'SGST',
                    'tax_percentage': item['sgst'],
                    'amount': 0
                }
                if dup_dict not in tax_list:
                    tax_list.append(dup_dict)
            if item['cgst'] > 0:
                dup_dict = {
                    'tax_type': 'CGST',
                    'tax_percentage': item['cgst'],
                    'amount': 0
                }
                if dup_dict not in tax_list:
                    tax_list.append(dup_dict)
            if item['igst'] > 0:
                dup_dict = {
                    'tax_type': 'IGST',
                    'tax_percentage': item['igst'],
                    'amount': 0
                }
                if dup_dict not in tax_list:
                    tax_list.append(dup_dict)

        for tax in tax_list:
            for item in items:
                # print(item)
                if item['sgst'] > 0 and tax['tax_type'] == 'SGST' and item[
                        'sgst'] == tax['tax_percentage']:
                    tax['amount'] += item['sgst_amount']
                if item['cgst'] > 0 and tax['tax_type'] == 'CGST' and item[
                        'cgst'] == tax['tax_percentage']:
                    tax['amount'] += item['cgst_amount']
                if item['igst'] > 0 and tax['tax_type'] == 'IGST' and item[
                        'igst'] == tax['tax_percentage']:
                    tax['amount'] += item['igst_amount']

        for tax in tax_list:
            doc = frappe.get_doc({
                'doctype': 'Tax Summaries',
                'invoce_number': invoice_number,
                'tax_percentage': tax['tax_percentage'],
                'amount': tax['amount'],
                'tax_type': tax['tax_type'],
                'parent': invoice_number,
                'parentfield': 'gst_summary',
                'parenttype': "Invoices"
            })
            doc.insert(ignore_permissions=True)
        return {"success": True}
    except Exception as e:
        print('tax', e)
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_tax_summariesd","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {'succes': False, "message": str(e)}




def TaxSummariesInsert(items,invoice_number):
    try:
        frappe.db.delete('Tax Summaries', {
                'parent': invoice_number})
        frappe.db.commit()
        for each in items:
            if each['sgst']>0:
                tax_summary_sgst = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'SGST','tax_percentage':each['sgst']})
                tax_summary_sgst = [element for tupl in tax_summary_sgst for element in tupl]
                if len(tax_summary_sgst)==0 or tax_summary_sgst == ():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['sgst'],
                        'amount': each['sgst_amount'],
                        'tax_type': "SGST",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_sgst_update = frappe.get_doc('Tax Summaries',tax_summary_sgst[0])
                    tax_summary_sgst_update.amount = each['sgst_amount']+float(tax_summary_sgst_update.amount)			
                    tax_summary_sgst_update.save()
            if each['cgst']>0:
                tax_summary_cgst = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'CGST','tax_percentage':each['cgst']})
                tax_summary_cgst = [element for tupl in tax_summary_cgst for element in tupl]
                if len(tax_summary_cgst)==0 or tax_summary_cgst==():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['cgst'],
                        'amount': each['cgst_amount'],
                        'tax_type': "CGST",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_cgst_update = frappe.get_doc('Tax Summaries',tax_summary_cgst[0])
                    tax_summary_cgst_update.amount = each['cgst_amount']+float(tax_summary_cgst_update.amount)			
                    tax_summary_cgst_update.save()
            if each['igst']>0:
                tax_summary_igst = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'IGST','tax_percentage':each['igst']})
                tax_summary_igst = [element for tupl in tax_summary_igst for element in tupl]
                if len(tax_summary_igst)==0 or tax_summary_igst==():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['igst'],
                        'amount': each['igst_amount'],
                        'tax_type': "IGST",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_Igst_update = frappe.get_doc('Tax Summaries',tax_summary_igst[0])
                    tax_summary_Igst_update.amount = each['igst_amount']+float(tax_summary_Igst_update.amount)			
                    tax_summary_Igst_update.save()
            if each['vat']>0:
                tax_summary_vat = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'VAT','tax_percentage':each['vat']})
                tax_summary_vat = [element for tupl in tax_summary_vat for element in tupl]
                if len(tax_summary_vat)==0 or tax_summary_vat==():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['vat'],
                        'amount': each['vat_amount'],
                        'tax_type': "VAT",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_vat_update = frappe.get_doc('Tax Summaries',tax_summary_vat[0])
                    tax_summary_vat_update.amount = each['vat_amount']+float(tax_summary_vat_update.amount)			
                    tax_summary_vat_update.save()
            if each['cess']>0:
                tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'Central CESS','tax_percentage':each['cess']})
                tax_summary_cess = [element for tupl in tax_summary_cess for element in tupl]
                if len(tax_summary_cess)==0 or tax_summary_cess==():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['cess'],
                        'amount': each['cess_amount'],
                        'tax_type': "Central CESS",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_cess_update = frappe.get_doc('Tax Summaries',tax_summary_cess[0])
                    tax_summary_cess_update.amount = each['cess_amount']+float(tax_summary_cess_update.amount)			
                    tax_summary_cess_update.save()	
            if each['state_cess']>0:
                tax_summary_state_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'State CESS','tax_percentage':each['state_cess']})
                tax_summary_state_cess = [element for tupl in tax_summary_state_cess for element in tupl]
                if len(tax_summary_state_cess)==0 or tax_summary_state_cess==():
                    doc = frappe.get_doc({
                        'doctype': 'Tax Summaries',
                        'invoce_number': invoice_number,
                        'tax_percentage': each['state_cess'],
                        'amount': each['state_cess_amount'],
                        'tax_type': "State CESS",
                        'parent': invoice_number,
                        'parentfield': 'gst_summary',
                        'parenttype': "Invoices"
                    })
                    doc.insert(ignore_permissions=True)
                else:
                    tax_summary_state_cess_update = frappe.get_doc('Tax Summaries',tax_summary_state_cess[0])
                    tax_summary_state_cess_update.amount = each['state_cess_amount']+float(tax_summary_state_cess_update.amount)			
                    tax_summary_state_cess_update.save()
        return {"message": True,"success":True}
    except Exception as e:
        print(str(e),"      Insert Sac summaries")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing TaxSummariesInsert","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"message":str(e),"success":False}




# def insert_tax_summaries2(items,invoice_number):
# 	if len(items)>0:
# 		frappe.db.delete('Tax Summaries', {
# 				'parent': invoice_number})
# 		frappe.db.commit()	
# 		# print(items)
# 		df = pd.DataFrame(items)
# 		df = df.set_index('sgst')
# 		df['cess_duplicate'] = df['cess']
# 		df['state_cess_duplicate'] = df['state_cess']
# 		df['vat_duplication'] = df['vat']
# 		# df['igst_duplicate'] = df['igst']
# 		df1 = df.groupby(['cgst','cess_duplicate','state_cess_duplicate','vat_duplication'])[["cgst_amount", "sgst_amount","igst_amount","cess_amount","cess",'state_cess','vat',"state_cess_amount","vat_amount","igst","igst_amount"]].apply(lambda x : x.astype(float).sum())
# 		df1.reset_index(level=0, inplace=True) 
        
# 		df1.reset_index(level=0, inplace=True)
# 		df1.reset_index(level=0, inplace=True)
# 		df1.reset_index(level=0, inplace=True)
# 		df1['cess'] = df1['cess_duplicate']
# 		df1['state_cess'] = df1['state_cess_duplicate']
# 		df1['vat'] = df1['vat_duplication']
# 		data = df1.to_dict('records')

# 		for each in data:
# 			print(each)
# 			if each['cgst']>0:
                
# 				doc = frappe.get_doc({
# 					'doctype': 'Tax Summaries',
# 					'invoce_number': invoice_number,
# 					'tax_percentage': each['cgst'],
# 					'amount': each['cgst_amount'],
# 					'tax_type': "CGST",
# 					'parent': invoice_number,
# 					'parentfield': 'gst_summary',
# 					'parenttype': "Invoices"
# 				})
# 				doc.insert(ignore_permissions=True)
# 				doc = frappe.get_doc({
# 					'doctype': 'Tax Summaries',
# 					'invoce_number': invoice_number,
# 					'tax_percentage': each['cgst'],
# 					'amount': each['sgst_amount'],
# 					'tax_type': "SGST",
# 					'parent': invoice_number,
# 					'parentfield': 'gst_summary',
# 					'parenttype': "Invoices"
# 				})
# 				doc.insert(ignore_permissions=True)
# 			if each['igst_amount'] > 0:
# 				doc = frappe.get_doc({
# 					'doctype': 'Tax Summaries',
# 					'invoce_number': invoice_number,
# 					'tax_percentage': each['igst'],
# 					'amount': each['igst_amount'],
# 					'tax_type': "IGST",
# 					'parent': invoice_number,
# 					'parentfield': 'gst_summary',
# 					'parenttype': "Invoices"
# 				})
# 				doc.insert(ignore_permissions=True)
# 			if each['cess']>0:
# 				# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
# 				tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'Central CESS','tax_percentage':each['cess']})
# 				tax_summary_cess = [element for tupl in tax_summary_cess for element in tupl]
# 				if len(tax_summary_cess)==0:
# 					if each['cess_amount']>0:
# 						doc = frappe.get_doc({
# 						'doctype': 'Tax Summaries',
# 						'invoce_number': invoice_number,
# 						'tax_percentage': each['cess'],
# 						'amount': each['cess_amount'],
# 						'tax_type': "Central CESS",
# 						'parent': invoice_number,
# 						'parentfield': 'gst_summary',
# 						'parenttype': "Invoices"
# 							})
# 						doc.insert(ignore_permissions=True)	
# 				else:
# 					tax_summary_cess_update = frappe.get_doc('Tax Summaries',tax_summary_cess[0])
# 					tax_summary_cess_update.tax_percentage = each['cess_amount']+float(tax_summary_cess_update.tax_percentage)			
# 					tax_summary_cess_update.save()
# 			if each['state_cess']>0:
# 				# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
# 				tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'State CESS','tax_percentage':each['state_cess']})
# 				if tax_summary_cess is ():
# 					if each['state_cess_amount']>0:
# 						doc = frappe.get_doc({
# 						'doctype': 'Tax Summaries',
# 						'invoce_number': invoice_number,
# 						'tax_percentage': each['state_cess'],
# 						'amount': each['state_cess_amount'],
# 						'tax_type': "State CESS",
# 						'parent': invoice_number,
# 						'parentfield': 'gst_summary',
# 						'parenttype': "Invoices"
# 							})
# 						doc.insert(ignore_permissions=True)	
# 				else:
# 					tax_summary_state = [element for tupl in tax_summary_cess for element in tupl]
# 					tax_summary_cess_update = frappe.get_doc('Tax Summaries',tax_summary_state[0])
# 					tax_summary_cess_update.tax_percentage = each['state_cess_amount']+float(tax_summary_cess_update.tax_percentage)		
# 					tax_summary_cess_update.save()
# 			if each['vat']>0:
# 				# tax_summary_cess = frappe.db.get_list('Tax Summaries', filters={'parent': ['==', '']})
# 				tax_summary_cess = frappe.db.exists({'doctype': 'Tax Summaries','parent': invoice_number,'tax_type': 'VAT','tax_percentage':each['state_cess']})
# 				if tax_summary_cess is ():
# 					if each['vat_amount']>0:
# 						doc = frappe.get_doc({
# 						'doctype': 'Tax Summaries',
# 						'invoce_number': invoice_number,
# 						'tax_percentage': each['vat'],
# 						'amount': each['vat_amount'],
# 						'tax_type': "VAT",
# 						'parent': invoice_number,
# 						'parentfield': 'gst_summary',
# 						'parenttype': "Invoices"
# 							})
# 						doc.insert(ignore_permissions=True)	
# 				else:
# 					tax_summary_cess_update = frappe.db.get_doc('Tax Summaries',tax_summary_cess[0])
# 					tax_summary_cess_update.tax_percentage = each['vat_amount']+tax_summary_cess_update.tax_percentage			
# 					tax_summary_cess_update.save()	

def insert_tax_summaries(items, invoice_number):
    '''
    insert tax_summaries into tax_summaries table
    '''
    try:
        if len(items)>0:
            tax_summaries = []
            for item in items:
                if len(tax_summaries) > 0:
                    found = False
                    for tax in tax_summaries:
                        found = False
                        if item['sgst'] > 0:
                            if tax['tax_type'] == 'SGST' and tax[
                                    'tax_percentage'] == item['sgst']:
                                tax['amount'] += item['sgst_amount']
                                found = True
                        if item['cgst'] > 0:
                            if tax['tax_type'] == 'CGST' and tax[
                                    'tax_percentage'] == item['cgst']:

                                tax['amount'] += item['cgst_amount']
                                found = True
                        if item['igst'] > 0:
                            if tax['tax_type'] == 'IGST' and tax[
                                    'tax_percentage'] == item['igst']:
                                tax['amount'] += item['igst_amount']
                                found = True
                    if found == False:
                        if item['sgst'] > 0:
                            summary = {}
                            summary['tax_type'] = 'SGST'
                            summary['tax_percentage'] = item['sgst']
                            summary['amount'] = item['sgst_amount']
                            summary['invoice_number'] = invoice_number
                            tax_summaries.append(summary)
                        if item['cgst'] > 0:
                            summary = {}
                            summary['tax_type'] = 'CGST'
                            summary['tax_percentage'] = item['cgst']
                            summary['amount'] = item['cgst_amount']
                            summary['invoice_number'] = invoice_number
                            tax_summaries.append(summary)
                        if item['igst'] > 0:
                            summary = {}
                            summary['tax_type'] = 'IGST'
                            summary['tax_percentage'] = item['igst']
                            summary['amount'] = item['igst_amount']
                            summary['invoice_number'] = invoice_number
                            tax_summaries.append(summary)
                else:
                    if item['sgst'] > 0:
                        summary = {}
                        summary['tax_type'] = 'SGST'
                        summary['tax_percentage'] = item['sgst']
                        summary['amount'] = item['sgst_amount']
                        summary['invoice_number'] = invoice_number
                        tax_summaries.append(summary)
                    if item['cgst'] > 0:
                        summary = {}
                        summary['tax_type'] = 'CGST'
                        summary['tax_percentage'] = item['cgst']
                        summary['amount'] = item['cgst_amount']
                        summary['invoice_number'] = invoice_number
                        tax_summaries.append(summary)
                    if item['igst'] > 0:
                        summary = {}
                        summary['tax_type'] = 'IGST'
                        summary['tax_percentage'] = item['igst']
                        summary['amount'] = item['igst_amount']
                        summary['invoice_number'] = invoice_number
                        tax_summaries.append(summary)
            actual_summaries = [
                tax_summaries[0],
            ]
            for tax in tax_summaries:
                found = False
                for actual in actual_summaries:
                    found = False
                    if tax['tax_type'] == actual['tax_type'] and tax[
                            'tax_percentage'] == actual['tax_percentage']:
                        actual['amount'] += tax['amount']
                        found = True
                if found == False:
                    actual_summaries.append(tax)

            for i in actual_summaries:
                print(i)

            for tax in tax_summaries:

                doc = frappe.get_doc({
                    'doctype': 'Tax Summaries',
                    'invoce_number': tax['invoice_number'],
                    'tax_percentage': tax['tax_percentage'],
                    'amount': tax['amount'],
                    'tax_type': tax['tax_type'],
                    'parent': invoice_number,
                    'parentfield': 'gst_summary',
                    'parenttype': "Invoices"
                })
                doc.insert(ignore_permissions=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing insert_tax_summaries","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, 'insert tax summerie')


@frappe.whitelist()
def get_tax_payer_details(data):
    '''
    get TaxPayerDetail from gsp   gstNumber, code, apidata
    '''
    try:
        print(data["gstNumber"],">>>>>>>>>>>>>>>>>>>>>>>.....")
        company = frappe.get_doc('company',data['code'])
        headers = {'Content-Type': 'application/json'}
        tay_payer_details = frappe.db.get_value('TaxPayerDetail',data['gstNumber'])
        if tay_payer_details is None:
            if company.mode=="Production":
                if company.proxy == 1:
                    proxyhost = company.proxy_url
                    proxyhost = proxyhost.replace("http://","@")
                    proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                                    'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
                    json_response = requests.get(company.licensing_host+"/api/resource/TaxPayerDetail/"+data['gstNumber'],headers=headers,proxies=proxies,verify=False)
                else:
                    if company.skip_ssl_verify == 1:
                        json_response = requests.get(company.licensing_host+"/api/resource/TaxPayerDetail/"+data['gstNumber'],headers=headers,verify=False)
                    else:
                        json_response = requests.get(company.licensing_host+"/api/resource/TaxPayerDetail/"+data['gstNumber'],headers=headers,verify=False)
                if json_response.content:
                    response = request_get(
                        data['apidata']['get_taxpayer_details'] + data['gstNumber'],
                        data['apidata'], data['invoice'], data['code'])
                    
                    if response['success']:
                        company = frappe.get_doc('company',data['code'])
                        details = response['result']
                        if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
                            if (details['AddrBno'] != "") or (details['AddrBno'] !=
                                                                ""):
                                details['AddrBnm'] = details['AddrBno']
                        if (details['AddrBno'] == "") or (details['AddrBno'] == None):
                            if (details['AddrBnm'] != "") or (details['AddrBnm'] !=
                                                                None):
                                details['AddrBno'] = details['AddrBnm']
                        if (details['TradeName'] == "") or (details['TradeName']
                                                            == None):
                            if (details['LegalName'] != "") or (details['TradeName'] !=
                                                                None):
                                details['TradeName'] = details['LegalName']
                        if (details['LegalName'] == "") or (details['LegalName']
                                                            == None):
                            if (details['TradeName'] != "") or (details['TradeName'] !=
                                                                None):
                                details['LegalName'] = details['TradeName']
                        if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
                            details['AddrLoc'] = "      "

                        if len(details["AddrBnm"]) < 3:
                            details["AddrBnm"] = details["AddrBnm"] + "    "
                        if len(details["AddrBno"]) < 3:
                            details["AddrBno"] = details["AddrBno"] + "    "
                        # if "email" not in data:
                        #     data["email"]=" "
                        tax_payer = frappe.new_doc('TaxPayerDetail')
                        tax_payer.gst_number = details['Gstin']
                        tax_payer.email = data["email"] if "email" in data else ""
                        tax_payer.phone_number = " "
                        tax_payer.legal_name = details['LegalName']
                        tax_payer.address_1 = details['AddrBnm']
                        tax_payer.address_2 = details['AddrBno']
                        tax_payer.location = details['AddrLoc']
                        tax_payer.pincode = details['AddrPncd']
                        tax_payer.gst_status = details['Status']
                        tax_payer.tax_type = details['TxpType']
                        if company.disable_sez == 1:
                            tax_payer.tax_type = "REG"
                        tax_payer.company = data['code']
                        tax_payer.trade_name = details['TradeName']
                        tax_payer.state_code = details['StateCode']
                        tax_payer.last_fetched = datetime.date.today()
                        tax_payer.address_floor_number = details['AddrFlno']
                        tax_payer.address_street = details['AddrSt']
                        tax_payer.block_status = ''
                        tax_payer.status = details['Status']
                        if details['Status'] == "ACT":
                            tax_payer.status = 'Active'
                            doc = tax_payer.insert(ignore_permissions=True)
                            return {"success": True, "data": doc}
                        else:
                            tax_payer.status = 'In-Active'
                            doc = tax_payer.insert(ignore_permissions=True)
                            return {
                                "success": False,
                                "message": "Gst Number is Inactive"
                            }
                    else:
                        print("Unknown error in get taxpayer details get call  ",
                                response)
                        error_message = "Invalid GstNumber "+data['gstNumber']
                        frappe.log_error(frappe.get_traceback(), data['gstNumber'])
                        logger.error(f"{data['gstNumber']},     get_tax_payer_details,   {response['message']}")
                        return {
                            "success": False,
                            "message": error_message,
                            "response": response
                        }
                  
                else:
                    json_response['doctype'] ="TaxPayerDetail"
                    doc = frappe.get_doc(json_response)
                    doc.insert(ignore_permissions=True, ignore_links=True)
                    get_doc = frappe.get_doc('TaxPayerDetail', data['gstNumber'])
                    return {"success": True, "data": get_doc}
            else:
                print(data['gstNumber'],"-----------------")
                response = request_get(
                    data['apidata']['get_taxpayer_details'] + data['gstNumber'],
                    data['apidata'], data['invoice'], data['code'])
                if response['success']:
                    print(response,"_____________________")
                    company = frappe.get_doc('company',data['code'])
                    details = response['result']
                    if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
                        if (details['AddrBno'] != "") or (details['AddrBno'] !=
                                                            ""):
                            details['AddrBnm'] = details['AddrBno']
                    if (details['AddrBno'] == "") or (details['AddrBno'] == None):
                        if (details['AddrBnm'] != "") or (details['AddrBnm'] !=
                                                            None):
                            details['AddrBno'] = details['AddrBnm']
                    if (details['TradeName'] == "") or (details['TradeName']
                                                        == None):
                        if (details['LegalName'] != "") or (details['TradeName'] !=
                                                            None):
                            details['TradeName'] = details['LegalName']
                    if (details['LegalName'] == "") or (details['LegalName']
                                                        == None):
                        if (details['TradeName'] != "") or (details['TradeName'] !=
                                                            None):
                            details['LegalName'] = details['TradeName']
                    if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
                        details['AddrLoc'] = "      "
                    if "email" not in data:
                        data["email"]=""
                    if len(details["AddrBnm"]) < 3:
                        details["AddrBnm"] = details["AddrBnm"] + "    "
                    if len(details["AddrBno"]) < 3:
                        details["AddrBno"] = details["AddrBno"] + "    "
                    tax_payer = frappe.new_doc('TaxPayerDetail')
                    tax_payer.gst_number = details['Gstin']
                    tax_payer.email = data["email"]
                    tax_payer.phone_number = " "
                    tax_payer.legal_name = details['LegalName']
                    tax_payer.address_1 = details['AddrBnm']
                    tax_payer.address_2 = details['AddrBno']
                    tax_payer.location = details['AddrLoc']
                    tax_payer.pincode = details['AddrPncd']
                    tax_payer.gst_status = details['Status']
                    tax_payer.tax_type = details['TxpType']
                    if company.disable_sez == 1:
                        tax_payer.tax_type = "REG"
                    tax_payer.company = data['code']
                    tax_payer.trade_name = details['TradeName']
                    tax_payer.state_code = details['StateCode']
                    tax_payer.last_fetched = datetime.date.today()
                    tax_payer.address_floor_number = details['AddrFlno']
                    tax_payer.address_street = details['AddrSt']
                    tax_payer.block_status = ''
                    tax_payer.status = details['Status']
                    if details['Status'] == "ACT":
                        tax_payer.status = 'Active'
                        doc = tax_payer.insert(ignore_permissions=True)
                        return {"success": True, "data": doc}
                    else:
                        tax_payer.status = 'In-Active'
                        doc = tax_payer.insert(ignore_permissions=True)
                        return {
                            "success": False,
                            "message": "Gst Number is Inactive"
                        }
                else:
                    print("Unknown error in get taxpayer details get call  ",
                            response)
                    error_message = "Invalid GstNumber "+data['gstNumber']
                    frappe.log_error(frappe.get_traceback(), data['gstNumber'])
                    logger.error(f"{data['gstNumber']},     get_tax_payer_details,   {response['message']}")
                    return {
                        "success": False,
                        "message": error_message,
                        "response": response
                    }
        else:
            doc = frappe.get_doc('TaxPayerDetail', data['gstNumber'])
            headers = {'Content-Type': 'application/json'}
            return {"success": True, "data": doc}  
    except Exception as e:
        print(e, "get tax payers")
        # frappe.log_error(frappe.get_traceback())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing get_tax_payer_details Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"get_tax_payer_details,   {str(e)}")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def check_company_exist(code):
    try:
        company = frappe.get_doc('company', code)
        return {"success": True, "data": company}
    except Exception as e:
        print(e, "check company exist")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing check_company_exist","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def check_company_exist_for_Irn(code):
    try:
        company = frappe.get_doc('company', code)
        return {"success": True, "data": company}
    except Exception as e:
        print(e, "check company exist")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing check_company_exist_for_Irn","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def check_token_is_valid(data):
    try:
        login_gsp(data['code'], data['mode'])
        gsp = frappe.db.get_value(
            'GSP APIS', {"company": data['code']},
            ['gsp_test_token_expired_on', 'gsp_prod_token_expired_on'],
            as_dict=1)
        if gsp['gsp_test_token_expired_on'] != '' or gsp[
                'gsp_prod_token_expired_on']:
            expired_on = gsp['gsp_test_token_expired_on'] if data[
                'mode'] == 'Testing' else gsp['gsp_prod_token_expired_on']
            print(expired_on)
            return {"success": True}
        else:
            login_gsp(data['code'], data['mode'])
            return {"success": True}

    except Exception as e:
        print(e, "check token is valid")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing check_token_is_valid Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


from version2_app.version2_app.doctype.ey_intigration.api_urls import test_login,prod_login
import base64


def login_gsp(code,mode):
    try:
        company = frappe.get_doc('company',code)
        gsp = frappe.db.get_value('GSP APIS', {"company": code,"provider":company.provider}, [
                'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
                'gsp_prod_app_secret', 'gsp_test_app_secret', 'name',
                'gst__test_username','gst_test_password','gst__prod_username','gst_prod_password'
        ],as_dict=1)
        if company.provider != 'ey':
            # company = frappe.get_doc('company',code)						  
            if mode == 'Testing':
                headers = {
                    "gspappid": gsp["gsp_test_app_id"],
                    "gspappsecret": gsp["gsp_test_app_secret"],
                }
                login_response = request_post(gsp['auth_test'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_test_token_expired_on = login_response['expires_in']
                gsp_update.gsp_test_token = login_response['access_token']
                gsp_update.save(ignore_permissions=True)
                return True
            elif mode == 'Production':
                headers = {
                    "gspappid": gsp["gsp_prod_app_id"],
                    "gspappsecret": gsp["gsp_prod_app_secret"]
                }
                login_response = request_post(gsp['auth_prod'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_prod_token_expired_on = login_response['expires_in']
                gsp_update.gsp_prod_token = login_response['access_token']
                gsp_update.save(ignore_permissions=True)
            return True
        else:
            
            if mode == 'Testing':
                enocded_password = base64.b64encode(bytes(gsp["gst_test_password"], 'utf-8')) # bytes
                # base64_str = b.decode('utf-8') # convert bytes to string

                headers = {
                    'username':gsp["gst__test_username"],
                    'password':enocded_password.decode("utf-8") ,
                    "apiaccesskey": gsp["gsp_test_app_id"],
                }
                print(headers)
                login_response = request_post(gsp['auth_test'], code, headers,ey=True)
                print(login_response,"*************************")
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                # gsp_update.gsp_test_token_expired_on = login_response['expiry']
                gsp_update.gsp_test_token = login_response['accessToken']
                gsp_update.test_refresh_token = login_response['refreshToken']
                gsp_update.save(ignore_permissions=True)
                frappe.db.commit()
                return True
            elif mode == 'Production':
                enocded_password = base64.b64encode(bytes(gsp["gst_prod_password"], 'utf-8')) # bytes
                headers = {
                    'username':gsp["gst__prod_username"],
                    # 'password':enocded_password.decode("utf-8") ,
                    'password':gsp["gst_prod_password"],
                    "apiaccesskey": gsp["gsp_prod_app_id"],
                }
                login_response = request_post(gsp['auth_prod'], code, headers,ey=True)
                print('___________________________________')
                print(login_response)
                print('_______________________________________')
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_prod_token_expired_on = login_response['expiry']
                gsp_update.gsp_prod_token = login_response['accessToken']
                gsp_update.prod_refresh_token = login_response['refreshToken']
                gsp_update.save(ignore_permissions=True)
                frappe.db.commit()
                return True
            
    except Exception as e:
        insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Failed","company":code})
        insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing login_gsp Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "login gsp")

@frappe.whitelist()
def updatelogin_gsp(data,ey=False):
    try:
        if ey == False:
            code = data['code']
            mode = data['mode']
            # print("********** scheduler")
            gsp = frappe.db.get_value('GSP APIS', {"company": code,
                "provider":'Adaequare'}, [
                'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
                'gsp_prod_app_secret', 'gsp_test_app_secret', 'name'
            ],as_dict=1)
            if mode == 'Testing':
                headers = {
                    "gspappid": gsp["gsp_test_app_id"],
                    "gspappsecret": gsp["gsp_test_app_secret"],
                }
                # print(gsp['auth_test'], code, headers)
                login_response = request_post(gsp['auth_test'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_test_token_expired_on = login_response['expires_in']
                gsp_update.gsp_test_token = login_response['access_token']
                gsp_update.test_token_generated_on = datetime.datetime.now()
                gsp_update.save(ignore_permissions=True)
                return True
            elif mode == 'Production':
                headers = {
                    "gspappid": gsp["gsp_prod_app_id"],
                    "gspappsecret": gsp["gsp_prod_app_secret"]
                }
                login_response = request_post(gsp['auth_prod'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_prod_token_expired_on = login_response['expires_in']
                gsp_update.gsp_prod_token = login_response['access_token']
                gsp_update.prod_token_generated_on = datetime.datetime.now()
                gsp_update.save(ignore_permissions=True)
                return True
        else:
            code = data['code']
            mode = data['mode']
            # print("********** scheduler")
            gsp = frappe.db.get_value('GSP APIS', {"company": code}, [
                'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
                'gsp_prod_app_secret', 'gsp_test_app_secret', 'name'
            ],
                                    as_dict=1)
            if mode == 'Testing':
                headers = {
                    "gspappid": gsp["gsp_test_app_id"],
                    "gspappsecret": gsp["gsp_test_app_secret"],
                }
                login_response = request_post(gsp['auth_test'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_test_token_expired_on = login_response['expires_in']
                gsp_update.gsp_test_token = login_response['access_token']
                gsp_update.test_token_generated_on = datetime.datetime.now()
                gsp_update.save(ignore_permissions=True)
                return True
            elif mode == 'Production':
                headers = {
                    "gspappid": gsp["gsp_prod_app_id"],
                    "gspappsecret": gsp["gsp_prod_app_secret"]
                }
                login_response = request_post(gsp['auth_prod'], code, headers)
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Success","company":code})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
                gsp_update = frappe.get_doc('GSP APIS', gsp['name'])
                gsp_update.gsp_prod_token_expired_on = login_response['expires_in']
                gsp_update.gsp_prod_token = login_response['access_token']
                gsp_update.prod_token_generated_on = datetime.datetime.now()
                gsp_update.save(ignore_permissions=True)
                return True
    except Exception as e:
        insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","login":'True',"status":"Failed","company":code})
        insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing updatelogin_gsp Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "login gsp")

@frappe.whitelist()
def gsp_api_data(data,ey=False):
    try:
        provider = 'Adaequare' if ey==False else 'ey'
        print(provider,"*******",ey)
        mode = data['mode']
        gsp_apis = frappe.db.get_value('GSP APIS', {
            "company": data['code'],
            "name": provider,
        }, [
            'auth_test', 'cancel_test_irn', 'extract_prod_qr_code',
            'extract_test_qr_code', 'extract_test_signed_invoice',
            'generate_prod_irn', 'generate_test_irn',
            'generate_test_qr_code_image', 'get_tax_payer_prod',
            'get_tax_payer_test', 'get_test_irn', 'get_test_qr_image',
            'auth_prod', 'cancel_prod_irn', 'extract_prod_qr_code',
            'extract_prod_signed_invoice', 'generate_prod_irn',
            'generate_prod_qr_code_image', 'get_prod_irn', 'get_prod_qr_image',
            'get_tax_payer_prod', 'gsp_prod_app_id', 'gsp_prod_app_secret',
            'gsp_test_app_id', 'gsp_test_app_secret', 'gsp_test_token',
            'gst__prod_username', 'gst__test_username', 'gst_prod_password',
            'gst_test_password', 'gsp_prod_token', 'gst_test_number',
            'gst_prod_number',
        ],
                                        as_dict=1)
        api_details = dict()
        api_details['auth'] = gsp_apis[
            'auth_test'] if mode == 'Testing' else gsp_apis['auth_prod']
        api_details['generate_irn'] = gsp_apis[
            'generate_test_irn'] if mode == 'Testing' else gsp_apis[
                'generate_prod_irn']
        api_details['cancel_irn'] = gsp_apis[
            'cancel_test_irn'] if mode == 'Testing' else gsp_apis[
                'cancel_prod_irn']
        api_details['get_taxpayer_details'] = gsp_apis[
            'get_tax_payer_test'] if mode == 'Testing' else gsp_apis[
                'get_tax_payer_prod']
        api_details['generate_qr_code'] = gsp_apis[
            'generate_test_qr_code_image'] if mode == 'Testing' else gsp_apis[
                'generate_prod_qr_code_image']
        api_details['generate_signed_qr_code'] = gsp_apis[
            'extract_test_signed_invoice'] if mode == 'Testing' else gsp_apis[
                'extract_prod_signed_invoice']
        api_details['username'] = gsp_apis[
            'gst__test_username'] if mode == 'Testing' else gsp_apis[
                'gst__prod_username']
        api_details['password'] = gsp_apis[
            'gst_test_password'] if mode == 'Testing' else gsp_apis[
                'gst_prod_password']
        api_details['appId'] = gsp_apis[
            'gsp_test_app_id'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_app_id']
        api_details['secret'] = gsp_apis[
            'gsp_test_app_secret'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_app_secret']
        api_details['token'] = gsp_apis[
            'gsp_test_token'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_token']
        api_details['gst'] = gsp_apis[
            'gst_test_number'] if mode == 'Testing' else gsp_apis[
                'gst_prod_number']
        print(api_details)
        return {"success":True,"data":api_details}
    except Exception as e:
        print(e,"gsp api details")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing gsp_api_data Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
        


def gsp_api_data_for_irn(data):
    try:
        mode = data['mode']
        gsp_apis = frappe.db.get_value('GSP APIS', {
            "company": data['code'],
            "name": data['provider'],
        }, [
            'auth_test',
            'cancel_test_irn',
            'extract_prod_qr_code',
            'extract_test_qr_code',
            'extract_test_signed_invoice',
            'generate_prod_irn',
            'generate_test_irn',
            'generate_test_qr_code_image',
            'get_tax_payer_prod',
            'get_tax_payer_test',
            'get_test_irn',
            'get_test_qr_image',
            'auth_prod',
            'cancel_prod_irn',
            'extract_prod_qr_code',
            'extract_prod_signed_invoice',
            'generate_prod_irn',
            'generate_prod_qr_code_image',
            'get_prod_irn',
            'get_prod_qr_image',
            'get_tax_payer_prod',
            'gsp_prod_app_id',
            'gsp_prod_app_secret',
            'gsp_test_app_id',
            'gsp_test_app_secret',
            'gsp_test_token',
            'gst__prod_username',
            'gst__test_username',
            'gst_prod_password',
            'gst_test_password',
            'gsp_prod_token',
            'gst_test_number',
            'gst_prod_number',
        ],
                                       as_dict=1)
        api_details = dict()
        api_details['auth'] = gsp_apis[
            'auth_test'] if mode == 'Testing' else gsp_apis['auth_prod']
        api_details['generate_irn'] = gsp_apis[
            'generate_test_irn'] if mode == 'Testing' else gsp_apis[
                'generate_prod_irn']
        api_details['cancel_irn'] = gsp_apis[
            'cancel_test_irn'] if mode == 'Testing' else gsp_apis[
                'cancel_prod_irn']
        api_details['get_taxpayer_details'] = gsp_apis[
            'get_tax_payer_test'] if mode == 'Testing' else gsp_apis[
                'get_tax_payer_prod']
        api_details['generate_qr_code'] = gsp_apis[
            'generate_test_qr_code_image'] if mode == 'Testing' else gsp_apis[
                'generate_prod_qr_code_image']
        api_details['generate_signed_qr_code'] = gsp_apis[
            'extract_test_signed_invoice'] if mode == 'Testing' else gsp_apis[
                'extract_prod_signed_invoice']
        api_details['username'] = gsp_apis[
            'gst__test_username'] if mode == 'Testing' else gsp_apis[
                'gst__prod_username']
        api_details['password'] = gsp_apis[
            'gst_test_password'] if mode == 'Testing' else gsp_apis[
                'gst_prod_password']
        api_details['appId'] = gsp_apis[
            'gsp_test_app_id'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_app_id']
        api_details['secret'] = gsp_apis[
            'gsp_test_app_secret'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_app_secret']
        api_details['token'] = gsp_apis[
            'gsp_test_token'] if mode == 'Testing' else gsp_apis[
                'gsp_prod_token']
        api_details['gst'] = gsp_apis[
            'gst_test_number'] if mode == 'Testing' else gsp_apis[
                'gst_prod_number']
        # print(api_details)
        # print(api_details)
        return {"success": True, "data": api_details}
    except Exception as e:
        print(e, "gsp api details for irn")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing gsp_api_data_for_irn Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def request_post(url, code, headers=None,ey=False):
    try:
        print(url,headers,ey)
        company = frappe.get_doc('company', code)
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                data = requests.post(url, headers=headers,verify=False)
            else:
                data = requests.post(url, headers=headers,verify=False)	
        else:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                'https':
                'https://' + company.proxy_username + ":" +
                company.proxy_password + proxyhost}
            print(proxies, "     proxy console")
            data = requests.post(url, headers=headers, proxies=proxies,verify=False)
        if data.status_code == 200:
            response_data = data.json()
            if ey:
                if 'accessToken' in response_data:
                    return response_data
                else:
                    return {}
            else:
                if 'access_token' in response_data:
                    return response_data
                else:
                    print(response_data)
        else:
            print(data)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing request_post Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "request post")


def request_get(api, headers, invoice, code):
    try:
        headers = {
            "user_name": headers["username"],
            "password": headers["password"],
            "gstin": headers['gst'],
            "requestid": invoice + str(random.randrange(1, 10**4)),
            "Authorization": "Bearer " + headers['token']
        }
        company = frappe.get_doc('company', code)
        if company.proxy == 0:
            if company.skip_ssl_verify == 0:
                raw_response = requests.get(api, headers=headers,verify=False)
            else:
                raw_response = requests.get(api, headers=headers,verify=False)

        else:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://", "@")
            proxies = {
                'https':
                'https://' + company.proxy_username + ":" +
                company.proxy_password + proxyhost
            }
            print(proxies, "     proxy console")
            raw_response = requests.get(api, headers=headers, proxies=proxies,verify=False)
        # print(raw_response.json())
        if raw_response.status_code == 200:
            insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","tax_payer_details":'True',"status":"Success","company":code})
            insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
            return raw_response.json()
        else:
            insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","tax_payer_details":'True',"status":"Failed","company":code})
            insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
            print(raw_response.text)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing request_get Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "request get")


@frappe.whitelist()
def check_gstNumber_Length(data):

    print("Error:  *******The given gst number is not a vaild one**********")
    return {
        "success": False,
        "Message": "The given gst number is not a vaild one"
    }


@frappe.whitelist()
def check_invoice_file_exists(data):
    try:
        invoiceExists = frappe.get_value(
            'File', {"file_name": data['invoice'] + ".pdf"})

        if invoiceExists:
            # frappe.delete_doc('File', invoiceExists)

            filedata = frappe.get_doc('File', invoiceExists)

            return {"success": True, "data": filedata}
        return {"success": False, "message": "sample"}
    except Exception as e:
        print(e, "check file exist")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def check_invoice_exists(invoice_number):
    try:
        if len(invoice_number)>0:
            if frappe.db.exists("Invoices", {"invoice_number": invoice_number}):
                invoice_number = frappe.db.get_value("Invoices", {"invoice_number": invoice_number})
                invCount = frappe.get_doc('Invoices',invoice_number)
                if invCount:	
                    invoice_number = invCount.name
                    if invCount.docstatus==2 or invCount.credit_note_raised == "Yes":
                        AmenedinvCount = frappe.db.get_list(
                        'Invoices',
                        filters={
                            'invoice_number':
                            ['like', invoice_number+'-%']
                        })
                        if len(AmenedinvCount)>0:
                            invoice_number = AmenedinvCount[0]['name']

                invoiceExists = frappe.get_doc('Invoices', invoice_number)
                if invoiceExists:
                    return {"success": True, "data": invoiceExists}
            return {"success": False}
        return {"success":False}	
    except Exception as e:
        print(e, "check invoice exist")
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def Error_Insert_invoice(data):
    try:
        if "invoice_object_from_file" not in data:
            data['invoice_object_from_file'] = {"data":[]}
        if "invoice_from" in data:
            invoice_from = data['invoice_from']
        else:
            invoice_from = "Pms"
            data['invoice_from'] = "Pms" 
        if "sez" in data:
            sez = data["sez"]
        else:
            doc = frappe.db.exists("Invoices",data["invoice_number"])
            if doc:
                invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                sez = invoice_doc.sez
            else:
                sez = 0
        if "gst_number" in data:
            if data["gst_number"]==None:
                data["gst_number"]=""

        if len(data['gst_number'])<15 and len(data['gst_number'])>0:
            if 'items_data' not in list(data.keys()):
                data['items_data'] = []
            data_error = {'invoice_number':data['invoice_number'],'company_code':data['company_code'],'items_data':data['items_data'],'total_invoice_amount':data['total_invoice_amount']}
            if not frappe.db.exists('Invoices', data['invoice_number']):
                data['error_message'] = data['error_message']+" -'"+data['gst_number']+"'"
                if len(data['gst_number'])<15 and len(data['gst_number'])>0:
                    data['invoice_type']="B2B"
                    error_invoice_calculation(data_error,data)
                    if 'items_data' in list(data.keys()):
                        items = data['items_data']
                        itemsInsert = insert_items(items,data['invoice_number'])
                        # insert_tax_summaries2(items,data['invoice_number'])
                        TaxSummariesInsert(items,data['invoice_number'])
                        hsnbasedtaxcodes = insert_hsn_code_based_taxes(
                            items, data['invoice_number'],"Invoice")
                    
                    if frappe.db.exists('Invoices', data['invoice_number']):
                        invoice_bin = frappe.get_doc("Invoices", data['invoice_number'])
                        if invoice_bin.invoice_from=="Pms":
                            socket = invoiceCreated(invoice_bin)
                        return {"success":False,"message":"Error","name":data['invoice_number'],"data":invoice_bin}

        company = frappe.get_doc('company',data['company_code'])
        if not frappe.db.exists('Invoices', {"name": data['invoice_number'], "irn_generated": ["!=", "Cancelled"]}):
            invType = data['invoice_type']
            
            irn_generated = "Error"
            # qr_generated = "Error"
            
            if "Invalid GstNumber" in data['error_message']:
                data['invoice_type'] ="B2B"
            if "gst_number" not in data or "gstNumber" not in data:
                data['gst_number'] = ""
            
            if data["guest_name"]=="":
                data["guest_name"]="NA"

            folder_path = frappe.utils.get_bench_path()
            with open(folder_path+"/"+"apps/version2_app/version2_app/version2_app/doctype/invoices/state_code.json") as f:
                json_data = json.load(f)
                for each in json_data:
                    if company.state_code == each['tin']:
                        place_supplier_state_name = f"{each['state']}-({each['tin']})"

            if 'checkout_date' in data:
                if data['checkout_date'] != None:
                    checkout_date = datetime.datetime.strptime(data['checkout_date'],'%d-%b-%y %H:%M:%S')
                else:
                    checkout_date = None
            else:
                checkout_date = None

            invoice = frappe.get_doc({
                'doctype':
                'Invoices',
                'invoice_number':
                data['invoice_number'],
                'invoice_type':data['invoice_type'],
                'guest_name':
                data['guest_name'],
                'gst_number':data['gst_number'],
                # if len(data['gst_number'])==15:
                # 	'gst_number': data['gst_number'],


                'invoice_file':
                data['invoice_file'],
                'room_number':
                data['room_number'],
                'irn_generated':irn_generated,
                # 'qr_generated':qr_generated,
                'invoice_date':
                datetime.datetime.strptime(data['invoice_date'],
                                        '%d-%b-%y %H:%M:%S'),
                'checkout_date':checkout_date,
                # "checkout_date": datetime.datetime.strptime(data['checkout_date'],
                #                         '%d-%b-%y %H:%M:%S') if "checkout_date" in data else None,
                'legal_name':
                " ",
                'address_1':
                " ",
                'email':
                " ",
                'trade_name':
                " ",
                'address_2':
                " ",
                'phone_number':
                " ",
                'location':
                " ",
                'pincode':
                data['pincode'],
                'state_code':
                data['state_code'],
                'amount_before_gst':
                0,
                "amount_after_gst":
                0,
                "other_charges":
                0,  
                'mode':company.mode,
                'total_invoice_amount':data['total_invoice_amount'],
                'irn_cancelled':
                'No',
                'qr_code_generated':
                'Pending',
                'signed_invoice_generated':
                'No',
                'company':
                data['company_code'],
                'ready_to_generate_irn':
                "No",
                'error_message':
                data['error_message'],
                "place_of_supply":company.state_code,
                "sez":sez,
                "invoice_from":invoice_from,
                "folioid":data["folioid"] if "folioid" in data else "",
                "invoice_object_from_file":json.dumps(data['invoice_object_from_file']),
                "confirmation_number":data["confirmation_number"] if "confirmation_number" in data else "",
                "arn_number": company.application_reference_number if company.application_reference_number and sez==1 else "",
                "pos_checks": data["pos_checks"] if "pos_checks" in data else 0,
                "place_of_supply_json":place_supplier_state_name if place_supplier_state_name in data else None,
            })
            if 'amened' in data:
                if data['amened'] == 'Yes':
                    invCount = frappe.db.get_value('Invoices',{"invoice_number": data['invoice_number']},["invoice_number"], as_dict=1)
                    invoice.amended_from = invCount.invoice_number
                    if "-" in invCount.invoice_number[-4:]:
                        amenedindex = invCount.invoice_number.rfind("-")
                        ameneddigit = int(invCount.invoice_number[amenedindex+1:])
                        ameneddigit = ameneddigit+1 
                        invoice.invoice_number = data['invoice_number'] + "-"+str(ameneddigit)
                        # pass
                    else:
                        invoice.invoice_number = data['invoice_number'] + "-1"	
            v = invoice.insert(ignore_permissions=True, ignore_links=True)
            
            if 'items_data' in list(data.keys()):
                items = data['items_data']
                itemsInsert = insert_items(items,data['invoice_number'])
                # insert_tax_summaries2(items,data['invoice_number'])
                TaxSummariesInsert(items,data['invoice_number'])
                hsnbasedtaxcodes = insert_hsn_code_based_taxes(
                    items, data['invoice_number'],"Invoice")
                    
                # return {"success": True}
            if v.invoice_from=="Pms": 
                socket = invoiceCreated(invoice)
            return {"success":False,"message":"Error","data":v} 
        invoiceExists = frappe.get_doc('Invoices', data['invoice_number'])
        if len(data['gst_number'])<15 and len(data['gst_number'])>0:
            data['error_message'] = data['error_message']+" -'"+data['gst_number']+"'"
            invoiceExists.invoice_type = "B2B"
            invoiceExists.gst_number = data['gst_number']
        if invoiceExists.invoice_type == "B2B" and	invoiceExists.irn_generated == "Success":
            return {"success":True,"data":invoiceExists} 	
        else:
            if data['invoice_object_from_file'] == {"data":[]}:
                data['invoice_object_from_file'] = invoiceExists.invoice_object_from_file
            invoiceExists.error_message = data['error_message']
            if isinstance(data['invoice_object_from_file'], dict):
                data['invoice_object_from_file'] = json.dumps(data['invoice_object_from_file'])
                invoiceExists.invoice_object_from_file = data['invoice_object_from_file']
            else:
                invoiceExists.invoice_object_from_file = data['invoice_object_from_file']
            # if invoiceExists.invoice_type == "B2B":
            invoiceExists.ready_to_generate_irn = "No"
            if invoiceExists.gst_number == None:
                # if len(invoiceExists.gst_number)<15:
                    invoiceExists.gst_number = ""
            else:
                if len(invoiceExists.gst_number)<15:
                    invoiceExists.gst_number = ""

            # print(invoiceExists.gst_number,"/a/a")			
            invoiceExists.irn_generated = "Error"
            invoiceExists.total_invoice_amount = data['total_invoice_amount']
            # invoiceExists.qr_generated = "Pending"


            invoiceExists.save()
            
            if 'items_data' in list(data.keys()):
                items = data['items_data']
                itemsInsert = insert_items(items,data['invoice_number'])
                # insert_tax_summaries2(items,data['invoice_number'])
                TaxSummariesInsert(items,data['invoice_number'])
                hsnbasedtaxcodes = insert_hsn_code_based_taxes(
                    items, data['invoice_number'],"Invoice")
                    
            return {"success":True,"message":"Error Invoice","data":invoiceExists}
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing error_insert_invoice_api","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def attach_b2c_qrcode(data):
    try:
        invoice = frappe.get_doc('Invoices', data["invoice_number"])
        company = frappe.get_doc('company', invoice.company)
        folder_path = frappe.utils.get_bench_path()
        path = folder_path + '/sites/' + company.site_name
        attach_qrpath = path + "/private/files/" + data[
            "invoice_number"] + "attachb2cqr.pdf"
        src_pdf_filename = path + invoice.invoice_file
        img_filename = path + invoice.b2c_qrimage
        img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
                             company.qr_rect_y0, company.qr_rect_y1)
        document = fitz.open(src_pdf_filename)
        page = document[0]
        page.insertImage(img_rect, filename=img_filename)
        document.save(attach_qrpath)
        document.close()
        # dst_pdf_text_filename = path + "/private/files/" + data[
        # 	"invoice_number"] + 'withattachqr.pdf'
        # doc = fitz.open(attach_qrpath)
        # irn_number = ''.join(
        # 	random.choice(string.ascii_uppercase + string.ascii_lowercase +
        # 				  string.digits) for _ in range(50))
        # ack_no = str(randint(100000000000, 9999999999999))
        # ackdate = str(datetime.datetime.now())
        # ack_date = ackdate.split(" ")
        # text = "IRN: " + irn_number + "      " + "ACK NO: " + ack_no + "    " + "ACK DATE: " + ack_date[0]
        # if company.irn_details_page == "First":
        # 	page = doc[0]
        # else:
        # 	page = doc[-1]
        # where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
        # page.insertText(
        # 	where,
        # 	text,
        # 	fontname="Roboto-Black",  # arbitrary if fontfile given
        # 	fontfile=folder_path +
        # 	company.font_file_path,  #fontpath,  # any file containing a font
        # 	fontsize=6,  # default
        # 	rotate=0,  # rotate text
        # 	color=(0, 0, 0),  # some color (blue)
        # 	overlay=True)
        # doc.save(dst_pdf_text_filename)
        # doc.close()
        files_new = {"file": open(attach_qrpath, 'rb')}
        payload_new = {
            "is_private": 1,
            "folder": "Home",
            "doctype": "Invoices",
            "docname": data["invoice_number"],
            'fieldname': 'b2c_qrinvoice'
        }
        site = company.host
        upload_qrinvoice_image = requests.post(site + "api/method/upload_file",
                                               files=files_new,
                                               data=payload_new)
        attach_response = upload_qrinvoice_image.json()
        if 'message' in attach_response:
            invoice.b2c_qrinvoice = attach_response['message']['file_url']
            invoice.name = data["invoice_number"]
            invoice.irn_generated = "Success"
            invoice.qr_code_generated = "Success"
            invoice.save(ignore_permissions=True, ignore_version=True)
            frappe.db.commit()
            if os.path.exists(attach_qrpath):
                os.remove(attach_qrpath)
            return {"success": True, "message": "Qr Attached successfully"}
    except Exception as e:
        print(e, "attach b2c qrcode")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing attach_b2c_qrcode","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": e}

@frappe.whitelist()
def get_taxpayerdetails(data):
    try:
        company = frappe.get_last_doc("company")
        gspApiDataResponse = gsp_api_data({"code":company.name,"mode":company.mode,"provider":company.provider})
        if gspApiDataResponse['success'] == True:
            checkTokenIsValidResponse = check_token_is_valid({"code":company.name,"mode":company.mode})
            if checkTokenIsValidResponse['success'] == True:
                gst_data = gspApiDataResponse['data']
                response = request_get(
                    gst_data['get_taxpayer_details'] + data["gstNumber"],
                    gst_data, data['invoice_number'], company.name)
                if response['success']:
                    details = response['result']
                    if (details['AddrBnm'] == "") or (details['AddrBnm'] == None):
                        if (details['AddrBno'] != "") or (details['AddrBno'] !=
                                                            ""):
                            details['AddrBnm'] = details['AddrBno']
                    if (details['AddrBno'] == "") or (details['AddrBno'] == None):
                        if (details['AddrBnm'] != "") or (details['AddrBnm'] !=
                                                            None):
                            details['AddrBno'] = details['AddrBnm']
                    if (details['TradeName'] == "") or (details['TradeName']
                                                        == None):
                        if (details['LegalName'] != "") or (details['TradeName'] !=
                                                            None):
                            details['TradeName'] = details['LegalName']
                    if (details['LegalName'] == "") or (details['LegalName']
                                                        == None):
                        if (details['TradeName'] != "") or (details['TradeName'] !=
                                                            None):
                            details['LegalName'] = details['TradeName']
                    if (details['AddrLoc'] == "") or (details['AddrLoc'] == None):
                        details['AddrLoc'] = "      "

                    if len(details["AddrBnm"]) < 3:
                        details["AddrBnm"] = details["AddrBnm"] + "    "
                    if len(details["AddrBno"]) < 3:
                        details["AddrBno"] = details["AddrBno"] + "    "
                    if frappe.db.exists('TaxPayerDetail', data["gstNumber"]):
                        tax_payer = frappe.get_doc('TaxPayerDetail', data["gstNumber"])
                    else:
                        tax_payer = frappe.new_doc('TaxPayerDetail')
                        tax_payer.gst_number = details['Gstin']
                    tax_payer.email = " "
                    tax_payer.phone_number = " "
                    tax_payer.legal_name = details['LegalName']
                    tax_payer.address_1 = details['AddrBnm']
                    tax_payer.address_2 = details['AddrBno']
                    details["AddrLoc"] = details["AddrLoc"].strip()
                    if details['AddrBnm'].strip() != "" and details["AddrLoc"] == "":
                        tax_payer.location = details['AddrSt']
                        details["AddrLoc"] = details['AddrSt']
                    elif details['AddrBno'].strip() != "" and details['AddrLoc'] == "":
                        tax_payer.location = details['AddrBno']
                        details["AddrLoc"] = details['AddrBno']
                    else:
                        tax_payer.location = details['AddrLoc']
                    tax_payer.pincode = details['AddrPncd']
                    tax_payer.gst_status = details['Status']
                    tax_payer.tax_type = details['TxpType']
                    if company.disable_sez == 1:
                        tax_payer.tax_type = "REG"
                    tax_payer.company = company.name
                    tax_payer.trade_name = details['TradeName']
                    tax_payer.state_code = details['StateCode']
                    tax_payer.last_fetched = datetime.date.today()
                    tax_payer.address_floor_number = details['AddrFlno']
                    tax_payer.address_street = details['AddrSt']
                    tax_payer.block_status = ''
                    tax_payer.status = details['Status']
                    invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                    invoice_doc.gst_number = details['Gstin']
                    invoice_doc.legal_name = details['LegalName']
                    invoice_doc.trade_name = details['TradeName']
                    invoice_doc.state_code = details['StateCode']
                    invoice_doc.address_1 = details['AddrBnm']
                    invoice_doc.address_2 = details['AddrBno']
                    details["AddrLoc"] = details["AddrLoc"].strip()
                    if details['AddrBnm'].strip() != "" and details["AddrLoc"].strip() == "":
                        invoice_doc.location = details['AddrSt']
                        details["AddrLoc"] = details['AddrSt']
                    elif details['AddrBno'].strip() != "" and details['AddrLoc'].strip() == "":
                        invoice_doc.location = details['AddrBno']
                        details["AddrLoc"] = details['AddrBno']
                    else:
                        invoice_doc.location = details['AddrLoc']
                    invoice_doc.pincode = details['AddrPncd']
                    if details['Status'] == "ACT":
                        tax_payer.status = 'Active'
                        if frappe.db.exists('TaxPayerDetail', data["gstNumber"]):
                            tax_payer.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
                            invoice_doc.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
                        else:
                            tax_payer.insert(ignore_permissions=True)
                            frappe.db.commit()
                        return {"success": True, "data": tax_payer}
                    
                    else:
                        tax_payer.status = 'In-Active'
                        if frappe.db.exists('TaxPayerDetail', data["gstNumber"]):
                            tax_payer.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
                            invoice_doc.save(ignore_permissions=True, ignore_version=True)
                            frappe.db.commit()
                        else:
                            tax_payer.insert(ignore_permissions=True)
                            frappe.db.commit()
                        return {
                            "success": False,
                            "message": "Gst Number is Inactive"
                        }
                else:
                    print("Unknown error in get taxpayer details get call  ",
                            response)
                    error_message = "Invalid GstNumber "+data['gstNumber']
                    frappe.log_error(frappe.get_traceback(), data['gstNumber'])
                    logger.error(f"{data['gstNumber']},     get_tax_payer_details,   {response['message']}")
                    return {
                        "success": False,
                        "message": error_message,
                        "response": response
                    }
                # getTaxPayerDetailsResponse = get_tax_payer_details({"gstNumber":data["gstNumber"],"code":company.name,"invoice":data["invoice_number"],"apidata":gspApiDataResponse['data']})
                # if getTaxPayerDetailsResponse['success'] == True:
                #     return {"success":True,"data":getTaxPayerDetailsResponse['data'].__dict__}
                # else:
                #     return getTaxPayerDetailsResponse
            else:
                return checkTokenIsValidResponse
        else:
            return gspApiDataResponse
    except Exception as e:
        print(e, "attach b2c qrcode")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing get_taxpayerdetails","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": e}   


@frappe.whitelist()
def update_non_revenue_amount():
    try:
        get_non_revenue_list = frappe.db.get_list("SAC HSN CODES", filters = {"ignore_non_taxable_items": 1}, pluck="sac_index")
        if len(get_non_revenue_list) > 0:
            get_items = frappe.db.get_list("Items", filters = {"sac_index":["in",get_non_revenue_list]}, fields=["sum(item_value_after_gst) as item_value_after_gst", "parent"], group_by="parent")
            if len(get_items) > 0:
                for each in get_items:
                    invoice_doc = frappe.get_doc("Invoices",each["parent"])
                    invoice_doc.non_revenue_amount = each["item_value_after_gst"]
                    invoice_doc.save()
                    frappe.db.commit()
                return {"success": True}
        return {"success": False, "message": "No data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_non_revenue_amount","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
        return {"success": False, "message": e}  


@frappe.whitelist()
def update_non_revenue_codes():
    try:
        get_non_revenue_list = frappe.db.get_list("SAC HSN CODES", filters = {"ignore_non_taxable_items": 1}, pluck="sac_index")
        if len(get_non_revenue_list) > 0:
            get_items = frappe.db.get_list("Items", filters = {"sac_index":["in",get_non_revenue_list]}, fields=["parent", "sac_index", "name"])
            if len(get_items) > 0:
                for each in get_items:
                    sac_code = frappe.db.get_value("SAC HSN CODES",{"sac_index": each["sac_index"]},["code"])
                    frappe.db.sql("""update `tabItems` set sac_code='{}' where name='{}'""".format(sac_code, each["name"]))
                    # invoice_doc = frappe.get_doc("Invoices",each["parent"])
                    # invoice_doc.non_revenue_amount = each["item_value_after_gst"]
                    # invoice_doc.save()
                    frappe.db.commit()
            return {"success": True}
        return {"success": False, "message": "No data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_non_revenue_amount","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
        return {"success": False, "message": e}  


# @frappe.whitelist()
# def b2b_success_to_credit_note(data):
# 	try:
# 		invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
# 		# invoice_data = frappe.db.get_value('Invoices', data["invoice_number"], ['invoice_number', 'guest_name',"gst_number","invoice_file","room_number","invoice_type","invoice_date","legal_name","address_1","address_2","email","trade_name","phone_number","state_code","location","pincode","irn_cancelled","other_charges","company","confirmation_number","invoice_from","print_by","has_discount_items","invoice_category","sez","converted_from_b2b","allowance_invoice","converted_from_tax_invoices_to_manual_tax_invoices"], as_dict=1)
# 		invoice_data = frappe.db.get_all('Invoices', filters={"name":data["invoice_number"]},fields=["*"])
# 		total_data = {}
# 		if len(invoice_data) > 0:
# 			invoice_number_amend = invoice_data[0]["invoice_number"]+"-1"
# 			guest_data = {"name":invoice_data[0]["guest_name"],"invoice_number":invoice_number_amend,"membership":"","invoice_type":invoice_data[0]["invoice_type"],"gstNumber":invoice_data[0]["gst_number"],"room_number":invoice_data[0]["room_number"],"company_code":invoice_data[0]["company"],"confirmation_number":invoice_data[0]["confirmation_number"],"print_by":invoice_data[0]["print_by"],"invoice_category":"Credit Invoice","invoice_file":invoice_data[0]["invoice_file"],"start_time":str(datetime.datetime.utcnow())}
# 			guest_data["invoice_date"] = date_time_obj = datetime.datetime.strptime(str(invoice_data[0]["invoice_date"]),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
# 			item_data = frappe.db.get_list('Items',filters={"parent":data["invoice_number"]},fields=["*"])
# 			df = pd.DataFrame.from_records(item_data)
# 			group = df.groupby(["sac_code","gst_rate","type","vat","cess","state_cess","taxable"]).agg({'cgst_amount': 'sum','sgst_amount':'sum','igst_amount':'sum','item_value':'sum','item_taxable_value':'sum','item_value_after_gst':'sum',"cess_amount":'sum',"state_cess_amount":'sum',"vat_amount":'sum','discount_value':'sum','sac_code':"first","item_name":'first',"item_type":"first","cgst":"first","sgst":"first","igst":"first","cess":"first","state_cess":"first","description":"first","date":"first","type":"first","unit_of_measurement":"first","unit_of_measurement_description":"first","sac_index":"first","quantity":"first","is_service_charge_item":"first","parentfield":"first","parenttype":"first","taxable":"first","sort_order":"first","sac_code_found":"first","gst_rate":"first"})
# 			group["item_mode"] = "Credit"
# 			group["doctype"] = "Items"
# 			group["parent"] = invoice_number_amend
# 			group.loc[group["cgst_amount"] != 0, "cgst_amount"] = -abs(group["cgst_amount"])
# 			group.loc[group["sgst_amount"] != 0, "sgst_amount"] = -abs(group["sgst_amount"])
# 			group.loc[group["igst_amount"] != 0, "igst_amount"] = -abs(group["igst_amount"])
# 			group.loc[group["cess_amount"] != 0, "cess_amount"] = -abs(group["cess_amount"])
# 			group.loc[group["state_cess_amount"] != 0, "state_cess_amount"] = -abs(group["state_cess_amount"])
# 			group.loc[group["vat_amount"] != 0, "vat_amount"] = -abs(group["vat_amount"])
# 			group.loc[group["item_value"] != 0, "item_value"] = -abs(group["item_value"])
# 			group.loc[group["item_taxable_value"] != 0, "item_taxable_value"] = -abs(group["item_taxable_value"])
# 			group.loc[group["item_value_after_gst"] != 0, "item_value_after_gst"] = -abs(group["item_value_after_gst"])
# 			group.loc[group["item_value_after_gst"] != 0, "item_value_after_gst"] = -abs(group["item_value_after_gst"])
# 			group_data = group.to_dict('records')
# 			if invoice_data[0]["gst_number"] != "":
# 				taxpayer = frappe.get_doc("TaxPayerDetail",invoice_data[0]["gst_number"])
# 				total_data["taxpayer"] = taxpayer.__dict__
# 			else:
# 				taxpayer = {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
# 				total_data["taxpayer"] = taxpayer
# 			total_data["guest_data"] = guest_data
# 			total_data["items_data"] = group_data
# 			total_data["amened"] = ""
# 			total_data["invoice_number"] = invoice_number_amend
# 			total_data["sez"] = invoice_data[0]["sez"]
# 			total_data["converted_tax_to_credit"] = "Yes"
# 			total_data["company_code"] = invoice_data[0]["company"]
# 			total_data["total_invoice_amount"] = -abs(invoice_data[0]["total_invoice_amount"])
# 			insert_invoice(total_data)
# 	except Exception as e:
# 		print(e, "attach b2c qrcode")
# 		return {"success": False, "message": str(e)}

@frappe.whitelist()
def update_non_taxable(month,year,sac_index):
    try:
        start_date = year+'-'+month+"-01"
        end_date = str(date_util.get_last_day(start_date))
        frappe.db.set_value("Items", {"sac_index": sac_index,"taxable": "Yes"}, "taxable", "No")
        frappe.db.commit()
        get_invoice_list = frappe.db.get_list("Invoices", filters=[["invoice_date","between",[start_date, end_date]]], pluck="name")
        get_invoice_list = set(get_invoice_list)
        for each in get_invoice_list:
            get_items = frappe.db.get_list("Items", filters=[["taxable","=","No"],["parent","=",each]], fields=["sum(item_value) as item_value", "sum(item_value_after_gst) as item_value_after_gst","parent"])
            invoice_doc = frappe.get_doc("Invoices", each)
            if len(get_items)>0:
                if get_items[0]["item_value_after_gst"] and get_items[0]["item_value"]:
                    invoice_doc.other_charges = get_items[0]["item_value_after_gst"]
                    invoice_doc.other_charges_before_tax = get_items[0]["item_value"]
                change_base_value = frappe.db.get_list("Items", filters=[["taxable","=","Yes"],["parent","=",each]], fields=["sum(item_value) as item_value", "sum(item_value_after_gst) as item_value_after_gst","parent"])
                if len(change_base_value) > 0:
                    if change_base_value[0]["item_value"] and change_base_value[0]["item_value_after_gst"]:
                        invoice_doc.amount_before_gst = change_base_value[0]["item_value"]
                        invoice_doc.pms_invoice_summary_without_gst = change_base_value[0]["item_value"]
                        invoice_doc.amount_after_gst = change_base_value[0]["item_value_after_gst"]
                        invoice_doc.pms_invoice_summary = change_base_value[0]["item_value_after_gst"]
                invoice_doc.save()
                # frappe.db.set_value("Items", {"sac_index": sac_index,"taxable": "Yes", "parent": each}, "taxable", "No")
                frappe.db.commit()
            else:
                return False
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("update_non_taxable","line No:{}\n{}".format(exc_tb.tb_lineno,str(e)))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def generate_irn(data):
    data = json.loads(data)
    var = generateIrn(data)
    return var