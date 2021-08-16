from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import requests
import datetime
import json
import random
import traceback,os,sys
import string,math
from frappe.utils import get_site_name
import time
import pandas as pd
from version2_app.version2_app.doctype.invoices.invoice_helpers import TotalMismatchError, CheckRatePercentages, update_document_bin
from version2_app.version2_app.doctype.invoices.invoices import insert_items,insert_hsn_code_based_taxes,send_invoicedata_to_gcb,TaxSummariesInsert,generateIrn,calulate_items,insert_invoice,calulate_net_yes
from version2_app.version2_app.doctype.invoices.invoice_helpers import CheckRatePercentages
from PyPDF2 import PdfFileWriter, PdfFileReader

# 
# update_document_bin(print_by,document_type,"","Duplicate",filepath)
@frappe.whitelist()
def Reinitiate_invoice(data):
    '''
    insert invoice data     data, company_code, taxpayer,items_data
    '''
    try:
        generateb2cQr = True
        if data['total_invoice_amount'] =="":
            data['total_invoice_amount'] = 0

        total_invoice_amount = data['total_invoice_amount']
        # del data['total_invoice_amount']
        company = frappe.get_doc('company',data['company_code'])
        if "place_of_supply" in data:
            place_of_supply = data['place_of_supply']
        else:
            doc = frappe.db.exists("Invoices",data['guest_data']['invoice_number'])
            if doc:
                invoice_doc = frappe.get_doc("Invoices",data['guest_data']['invoice_number'])
                place_of_supply = invoice_doc.place_of_supply
                if not place_of_supply:
                    place_of_supply = company.state_code
            else:
                place_of_supply = company.state_code
        if "invoice_object_from_file" not in data:
            data['invoice_object_from_file'] = " "	
        else:
            data['invoice_object_from_file'] = json.dumps(data['invoice_object_from_file'])
        # if "raise_credit" in data['guest_data']:

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
        # cess_amount = 0
        total_central_cess_amount = 0
        total_state_cess_amount = 0
        total_vat_amount =0
        discountAmount = 0
        credit_cgst_amount = 0
        credit_sgst_amount = 0
        credit_igst_amount = 0
        # credit_cess_amount = 0
        total_credit_central_cess_amount = 0
        total_credit_state_cess_amount = 0
        total_credit_vat_amount =0
        has_discount_items = "No"
        has_credit_items = "No"
        # print(data['items_data'])
        irn_generated = "Pending"
        if "legal_name" not in data['taxpayer']:
            data['taxpayer']['legal_name'] = " "
        if "gstNumber" not in data['guest_data']:
            data['guest_data']['gstNumber'] = ""
        #calculat items
        if len(data['items_data'])>0:
            for item in data['items_data']:
                if item['taxable'] == 'No' and item['item_type'] != "Discount":
                    other_charges += float(item['item_value_after_gst'])
                    other_charges_before_tax += float(item['item_value'])
                    total_vat_amount += float(item['vat_amount'])
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
        if len(data['items_data'])==0 and data['total_invoice_amount'] == 0:
            taxpayer= {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
            data['taxpayer'] =taxpayer
            data['guest_data']['invoice_type'] = "B2C"
            
        if company.allowance_type=="Discount":
            discountAfterAmount = abs(discountAmount)+abs(credit_value_after_gst)
            discountBeforeAmount = abs(discountAmount)+abs(credit_value_before_gst)
            pms_invoice_summary = value_after_gst - discountAfterAmount
            pms_invoice_summary_without_gst = value_before_gst - discountBeforeAmount
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

        invoice_round_off_amount = 0	
        sales_amount_before_tax = value_before_gst + other_charges_before_tax 
        sales_amount_after_tax = value_after_gst + other_charges
        sales_amount_after_tax = sales_amount_after_tax - credit_value_after_gst
        sales_amount_before_tax = sales_amount_before_tax - credit_value_before_gst
        # if total_invoice_amount==0 and len(data['items_data'])>0:
        # 	total_invoice_amount = sales_amount_after_tax
        # 	data['total_invoice_amount'] = sales_amount_after_tax

        
        if data['total_invoice_amount'] == 0:
            total = (value_after_gst + other_charges) - credit_value_after_gst
            if (total>0 and total<1) or (total>-1 and total<1):
                data['total_invoice_amount'] = 0
            else:
                data['total_invoice_amount'] = value_after_gst + other_charges + credit_value_after_gst
        if "address_1" not in data['taxpayer']:
            data['taxpayer']['address_1'] = data['taxpayer']['address_2']	
        if '-' in str(sales_amount_after_tax):
            allowance_invoice = "Yes"
        else:
            allowance_invoice = "No"
        if data['guest_data']['room_number'] == 0 and '-' not in str(sales_amount_after_tax):
            # data['guest_data']['invoice_category'] = "Debit Invoice"
            # invoice_category = "Debit Invoice"
            debit_invoice="Yes"
        else:
            debit_invoice="No"
        if "gstNumber" not in data['guest_data']:
            data['guest_data']['gstNumber'] = ""
        if "confirmation_number" not in data['guest_data']:
            data['guest_data']['confirmation_number'] = ""


        doc = frappe.get_doc('Invoices',data['guest_data']['invoice_number'])
        # if data['guest_data']['room_number'] == 0 and '-' not in str(sales_amount_after_tax):
        # 	data['guest_data']['invoice_category'] = "Debit Invoice"
        # 	invoice_category = "Debit Invoice"
        # else:
        # 	invoice_category = doc.invoice_category	
        invoice_from = doc.invoice_from
        
        converted_from_tax_invoices_to_manual_tax_invoices = doc.converted_from_tax_invoices_to_manual_tax_invoices
        doc.total_inovice_amount = total_invoice_amount
        doc.invoice_number=data['guest_data']['invoice_number']
        doc.guest_name=data['guest_data']['name']
        doc.gst_number=data['guest_data']['gstNumber']
        doc.invoice_file=data['guest_data']['invoice_file']
        if data['invoice_object_from_file'] == " ":
            data['invoice_object_from_file'] = doc.invoice_object_from_file
        doc.room_number=data['guest_data']['room_number']
        doc.invoice_type=data['guest_data']['invoice_type']
        doc.invoice_date=datetime.datetime.strptime(data['guest_data']['invoice_date'],'%d-%b-%y %H:%M:%S')
        doc.legal_name=data['taxpayer']['legal_name']
        doc.address_1=data['taxpayer']['address_1']
        doc.email=data['taxpayer']['email']
        doc.confirmation_number = data['guest_data']['confirmation_number']
        doc.trade_name=data['taxpayer']['trade_name']
        doc.address_2=data['taxpayer']['address_2']
        doc.phone_number=data['taxpayer']['phone_number']
        doc.mode = company.mode
        doc.location=data['taxpayer']['location']
        doc.pincode=data['taxpayer']['pincode']
        doc.state_code=data['taxpayer']['state_code']
        doc.amount_before_gst=round(value_before_gst, 2)
        doc.amount_after_gst=round(value_after_gst, 2)
        doc.credit_value_before_gst=round(credit_value_before_gst,2)
        doc.credit_value_after_gst=round(credit_value_after_gst,2)
        doc.pms_invoice_summary_without_gst=pms_invoice_summary_without_gst
        doc.pms_invoice_summary= pms_invoice_summary
        doc.other_charges= other_charges
        doc.other_charges_before_tax = other_charges_before_tax
        doc.sales_amount_after_tax = sales_amount_after_tax
        doc.sales_amount_before_tax = sales_amount_before_tax
        doc.total_central_cess_amount= total_central_cess_amount
        doc.total_state_cess_amount = total_state_cess_amount
        doc.total_vat_amount = total_vat_amount
        doc.ready_to_generate_irn = ready_to_generate_irn
        doc.invoice_category = data['guest_data']['invoice_category'] if "invoice_category" in data['guest_data'] else "Tax Invoice"
        # doc.place_of_supply = place_of_supply
        # doc.sez = data["sez"] if "sez" in data else doc.sez
        doc.cgst_amount=round(cgst_amount,2)
        doc.sgst_amount=round(sgst_amount,2)
        doc.igst_amount=round(igst_amount,2)
        doc.total_gst_amount = round(cgst_amount,2) + round(sgst_amount,2) + round(igst_amount,2)
        
        doc.irn_cancelled='No'
        doc.qr_code_generated='Pending'
        doc.signed_invoice_generated='No'
        doc.company=data['company_code']
        doc.print_by = data['guest_data']['print_by']
        doc.total_credit_central_cess_amount =  round(total_credit_central_cess_amount,2)
        doc.total_credit_state_cess_amount = round(total_credit_state_cess_amount,2)
        doc.total_credit_vat_amount = round(total_credit_vat_amount,2)
        doc.credit_cgst_amount = round(credit_cgst_amount,2)
        doc.credit_sgst_amount = round(credit_sgst_amount,2)
        doc.credit_igst_amount = round(credit_igst_amount,2)
        doc.credit_gst_amount = round(credit_cgst_amount,2) + round(credit_sgst_amount,2) + round(credit_igst_amount,2)	
        doc.has_credit_items = has_credit_items
        doc.mode = company.mode
        doc.allowance_invoice = allowance_invoice
        doc.debit_invoice = debit_invoice
        

        doc.irn_generated=irn_generated
        print(data['total_invoice_amount'],type(data['total_invoice_amount']))
        invoice_round_off_amount =  float(data['total_invoice_amount']) - float(abs(pms_invoice_summary+other_charges))
        if converted_from_tax_invoices_to_manual_tax_invoices == "No" or invoice_from != "Web": 
            if len(data['items_data'])==0:
                doc.ready_to_generate_irn = "No"
                doc.irn_generated = "Zero Invoice"
                doc.invoice_type = "B2C"
                generateb2cQr = False
            else:
                if abs(invoice_round_off_amount)>6:
                    if int(data['total_invoice_amount']) != int(pms_invoice_summary+other_charges) and int(math.ceil(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.floor(data['total_invoice_amount'])) != int(math.ceil(pms_invoice_summary+other_charges)) and int(math.ceil(data['total_invoice_amount'])) != int(math.floor(pms_invoice_summary+other_charges)):
                        generateb2cQr = False
                        doc.error_message = " Invoice Total Mismatch"
                        doc.irn_generated = "Error"
                        doc.ready_to_generate_irn = "No"
                # else:
                # 	doc.irn_generated ="Pending"
                # 	doc.ready_to_generate_irn = "Yes"		
        else:
            if len(data['items_data'])==0 and data['total_invoice_amount'] == 0 and invoice_from != "Web":
                doc.ready_to_generate_irn = "No"
                doc.irn_generated = "Zero Invoice"
                generateb2cQr = False
            else:
                invoice_round_off_amount = 0

                generateb2cQr = True
                doc.irn_generated = "Pending"
                doc.ready_to_generate_irn = "Yes"
        if invoice_from != "Web":		
            if data['total_invoice_amount'] == 0 or data['total_invoice_amount'] == 0.0:
                doc.ready_to_generate_irn = "No"
                doc.irn_generated = "Zero Invoice"
                doc.invoice_type = "B2C"
                generateb2cQr = False
        else:
            doc.ready_to_generate_irn = "Yes"
            doc.irn_generated = "Pending"
            invoice_round_off_amount = 0

        doc.total_invoice_amount = data["total_invoice_amount"]
        doc.place_of_supply = place_of_supply
        doc.invoice_round_off_amount = invoice_round_off_amount	
        doc.invoice_object_from_file = data['invoice_object_from_file']
        doc.save()
        

        items = data['items_data']
        # items = [x for x in items if x['sac_code']!="Liquor"]

        itemsInsert = insert_items(items,data['guest_data']['invoice_number'])
        # insert tax summaries
        # insert_tax_summaries(items_data, data['invoice_number'])
        taxSummariesInsert = TaxSummariesInsert(items, data['guest_data']['invoice_number'])
        # insert sac code based taxes
        hsnbasedtaxcodes = insert_hsn_code_based_taxes(items, data['guest_data']['invoice_number'],"Invoice")
        invoice_data = frappe.get_doc('Invoices',data['guest_data']['invoice_number'])
        if data['guest_data']['invoice_type'] == "B2C" and generateb2cQr == True:
            send_invoicedata_to_gcb(invoice_data.name)
        

        if invoice_data.invoice_type == "B2B" and invoice_data.invoice_from=="Pms":
            tax_payer_details =  frappe.get_doc('TaxPayerDetail',data['guest_data']['gstNumber'])
            if invoice_data.irn_generated == "Pending" and company.allow_auto_irn == 1:
                if (invoice_data.has_credit_items == "Yes" and company.auto_adjustment in ["Manual","Automatic"]) or tax_payer_details.disable_auto_irn == 1 or tax_payer_details.tax_type=="SEZ" or invoice_data.sez==1:
                    pass
                else:
                    data = {'invoice_number': invoice_data.name,'generation_type': "System"}
                    irn_generate = generateIrn(data)	

        returnData = frappe.get_doc('Invoices',invoice_data.name)
        # if returnData.invoice_from=="Pms":		
        #     update_document_bin(returnData.print_by,returnData.invoice_category,"","Duplicate",returnData.invoice_file)	
        
        return {"success":True,"data":returnData}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing Reinitiate_invoice","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e,"reinitaite invoice", traceback.print_exc())
        return {"success":False,"message":str(e)}

@frappe.whitelist()
def reprocess_calulate_items(data):
    # items, invoice_number,company_code
    try:
        final_data = {}
        total_items = []
        second_list = []
        item_list = []
        data['guest_data']['invoice_date'] = datetime.datetime.strptime(data['guest_data']['invoice_date'],"%Y-%m-%d").strftime('%d-%b-%y %H:%M:%S')
        companyDetails = frappe.get_doc('company', data["guest_data"]['company_code'])
        invoice_details = frappe.get_doc('Invoices', data["invoice_number"])
        if "place_of_supply" in data:
            placeofsupply = data["place_of_supply"]
        else:
            doc_invoice = frappe.db.exists("Invoices",data["invoice_number"])
            if doc_invoice:
                invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
                placeofsupply = invoice_doc.place_of_supply
            else:
                placeofsupply = companyDetails.state_code
        if "sez" in data:
            sez = data["sez"]
        else:
            sez = 0
        for each_item in data['items_data']:
            if sez == 0:
                if each_item["is_manual_edit"] == "Yes":
                    if "manual_edit" not in each_item:
                        each_item["date"] = datetime.datetime.strptime(each_item["date"],'%Y-%m-%d').strftime("%d-%m-%y")
                        total_items.append(each_item)
                        continue
                    else:
                        if each_item["manual_edit"] == "No":
                            each_item["date"] = datetime.datetime.strptime(each_item["date"],'%Y-%m-%d').strftime("%d-%m-%y")
                            total_items.append(each_item)
                            continue
            else:
                if invoice_details.sez == 1 and sez != 0:
                    if "manual_edit" not in each_item:
                        each_item["date"] = datetime.datetime.strptime(each_item["date"],'%Y-%m-%d').strftime("%d-%m-%y")
                        total_items.append(each_item)
                        continue
                    else:
                        if each_item["manual_edit"] == "No":
                            each_item["date"] = datetime.datetime.strptime(each_item["date"],'%Y-%m-%d').strftime("%d-%m-%y")
                            total_items.append(each_item)
                            continue
            if (each_item["is_service_charge_item"] == "No" and isinstance(each_item["sort_order"], int) and companyDetails.enable_sc_from_folios == 0) or ((each_item["is_service_charge_item"] == "Yes" or each_item["is_service_charge_item"] == "No") and companyDetails.enable_sc_from_folios == 1):
                final_item = {}
                if companyDetails.allowance_type == "Credit":
                    ItemMode = "Credit"
                else:
                    ItemMode = "Discount"
                acc_gst_percentage = 0.00
                acc_igst_percentage = 0.00
                total_items_data = {}
                if companyDetails.number_in_description == 1:
                    item_description_each = (each_item['item_name'].rstrip(string.digits)).strip()
                else:
                    item_description_each = each_item['item_name']
                sac_code_based_gst = frappe.db.get_list('SAC HSN CODES', filters={'name': ['=',item_description_each]})
                if not sac_code_based_gst:
                    sac_code_based_gst = frappe.db.get_list('SAC HSN CODES', filters={'name': ['like', '%' + item_description_each.strip() + '%']})
                if len(sac_code_based_gst)>0:
                    sac_code_based_gst_rates = frappe.get_doc(
                    'SAC HSN CODES',sac_code_based_gst[0]['name'])	
                    SAC_CODE = sac_code_based_gst_rates.code 
                    if sac_code_based_gst_rates.ignore == 1:
                        continue 
                    each_item['item_type'] = sac_code_based_gst_rates.type
                else:
                    return{"success":False,"message":"SAC Code "+ item_description_each+" not found"}
                # sac_code_based_gst_rates = frappe.get_doc('SAC HSN CODES',each_item['item_name'])
                if "manual_edit" in each_item:
                    if each_item["manual_edit"] == "Yes":
                        if placeofsupply != companyDetails.state_code:
                            total_items_data["igst"] = float(each_item["igst"])
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                        elif sez == 1:
                            if sac_code_based_gst_rates.exempted == 0:
                                total_items_data["igst"] = float(each_item["igst"])
                                total_items_data["cgst"] = 0
                                total_items_data["sgst"] = 0
                            else:
                                total_items_data["cgst"] = 0
                                total_items_data["sgst"] = 0
                                total_items_data["igst"] = 0
                        elif sez == 0 or placeofsupply == companyDetails.state_code:
                            total_items_data["cgst"] = float(each_item["cgst"])
                            total_items_data["sgst"] = float(each_item["sgst"])
                            total_items_data["igst"] = 0
                        else:
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                            total_items_data["igst"] = 0
                        total_items_data["vat"] = float(each_item["vat"])
                        total_items_data["state_cess"] = float(each_item["state_cess"])
                        total_items_data["cess"] = float(each_item["cess"])
                        if "discount_value" in each_item:
                            total_items_data["discount_value"] = float(each_item["discount_value"])
                        else:
                            total_items_data["discount_value"] = 0
                        if "net" in each_item:
                            total_items_data["net"] = each_item["net"]
                        else:
                            total_items_data["net"] =  sac_code_based_gst_rates.net
                        if "quantity" in each_item:
                            total_items_data["quantity"] = each_item["quantity"]
                        else:
                            total_items_data["quantity"] = 1
                        if "service_chargeEdit" in each_item:
                            total_items_data["service_charge"] = "Yes" if each_item["service_chargeEdit"] == True else "No"
                        else:
                            total_items_data["service_charge"] = sac_code_based_gst_rates.service_charge
                            if total_items_data["service_charge"] == "Yes":
                                if sac_code_based_gst_rates.one_sc_applies_to_all == 1:
                                    each_item["service_charge_rate"] = companyDetails.service_charge_percentage
                                else:
                                    each_item["service_charge_rate"] = sac_code_based_gst_rates.service_charge_rate
                                each_item["service_charge_tax_applies"] = sac_code_based_gst_rates.service_charge_tax_applies
                                each_item["sc_gst_tax_rate"] = sac_code_based_gst_rates.sc_gst_tax_rate
                                each_item["sc_sac_code"] = sac_code_based_gst_rates.sc_sac_code
                        total_items_data["date"] = each_item['date']
                        total_items_data["manual_edit"] = each_item["manual_edit"]
                        if total_items_data["service_charge"] == "Yes":
                            if "service_charge_rate" in each_item:
                                total_items_data["service_charge_rate"] = float(each_item["service_charge_rate"])
                            else:
                                each_item["service_charge_rate"] = sac_code_based_gst_rates.service_charge_rate
                            total_items_data["service_charge_tax_applies"] = each_item["service_charge_tax_applies"]
                            if total_items_data["service_charge_tax_applies"] == "Seperate GST":
                                total_items_data["service_charge_tax_applies"] = "Separate GST"
                                total_items_data["sc_gst_tax_rate"] = float(each_item["sc_gst_tax_rate_value"])
                                total_items_data["sc_sac_code"] = each_item["sc_sac_code_value"]
                    else:
                        # total_items_data["cgst"] = sac_code_based_gst_rates.cgst
                        # total_items_data["sgst"] = sac_code_based_gst_rates.sgst
                        # total_items_data["igst"] = sac_code_based_gst_rates.igst
                        if placeofsupply != companyDetails.state_code:
                            total_items_data["igst"] = sac_code_based_gst_rates.igst
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                        elif sez == 1:
                            if sac_code_based_gst_rates.exempted == 0:
                                total_items_data["igst"] = sac_code_based_gst_rates.igst
                                total_items_data["cgst"] = 0
                                total_items_data["sgst"] = 0
                            else:
                                total_items_data["cgst"] = 0
                                total_items_data["sgst"] = 0
                                total_items_data["igst"] = 0
                        elif sez == 0 or placeofsupply == companyDetails.state_code:
                            total_items_data["cgst"] = sac_code_based_gst_rates.cgst
                            total_items_data["sgst"] = sac_code_based_gst_rates.sgst
                            total_items_data["igst"] = 0
                        else:
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                            total_items_data["igst"] = 0
                        total_items_data["vat"] = sac_code_based_gst_rates.vat_rate
                        total_items_data["state_cess"] = sac_code_based_gst_rates.state_cess_rate
                        total_items_data["cess"] = sac_code_based_gst_rates.central_cess_rate
                        total_items_data["service_charge"] = sac_code_based_gst_rates.service_charge
                        total_items_data["date"] = each_item['date']
                        total_items_data["manual_edit"] = "No"
                        total_items_data["discount_value"] = 0
                        total_items_data["net"] =  sac_code_based_gst_rates.net
                        total_items_data["quantity"] = 1
                        if sac_code_based_gst_rates.service_charge == "Yes":
                            if sac_code_based_gst_rates.one_sc_applies_to_all == 1:
                                total_items_data["service_charge_rate"] = companyDetails.service_charge_percentage
                            else:
                                total_items_data["service_charge_rate"] = sac_code_based_gst_rates.service_charge_rate
                            total_items_data["service_charge_tax_applies"] = sac_code_based_gst_rates.service_charge_tax_applies
                            total_items_data["sc_gst_tax_rate"] = sac_code_based_gst_rates.sc_gst_tax_rate
                            total_items_data["sc_sac_code"] = sac_code_based_gst_rates.sc_sac_code
                else:
                    if placeofsupply != companyDetails.state_code:
                        total_items_data["igst"] = sac_code_based_gst_rates.igst
                        total_items_data["cgst"] = 0
                        total_items_data["sgst"] = 0
                    elif sez == 1:
                        if sac_code_based_gst_rates.exempted == 0:
                            total_items_data["igst"] = sac_code_based_gst_rates.igst
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                        else:
                            total_items_data["cgst"] = 0
                            total_items_data["sgst"] = 0
                            total_items_data["igst"] = 0
                    elif sez == 0 or placeofsupply == companyDetails.state_code:
                        total_items_data["cgst"] = sac_code_based_gst_rates.cgst
                        total_items_data["sgst"] = sac_code_based_gst_rates.sgst
                        total_items_data["igst"] = 0
                    else:
                        total_items_data["cgst"] = 0
                        total_items_data["sgst"] = 0
                        total_items_data["igst"] = 0
                    total_items_data["vat"] = sac_code_based_gst_rates.vat_rate
                    total_items_data["state_cess"] = sac_code_based_gst_rates.state_cess_rate
                    total_items_data["cess"] = sac_code_based_gst_rates.central_cess_rate
                    total_items_data["service_charge"] = sac_code_based_gst_rates.service_charge
                    total_items_data["date"] = each_item['date']
                    total_items_data["manual_edit"] = "No"
                    total_items_data["discount_value"] = 0
                    total_items_data["net"] =  sac_code_based_gst_rates.net
                    total_items_data["quantity"] = 1
                    if sac_code_based_gst_rates.service_charge == "Yes":
                        if sac_code_based_gst_rates.one_sc_applies_to_all == 1:
                            total_items_data["service_charge_rate"] = companyDetails.service_charge_percentage
                        else:
                            total_items_data["service_charge_rate"] = sac_code_based_gst_rates.service_charge_rate
                        total_items_data["service_charge_tax_applies"] = sac_code_based_gst_rates.service_charge_tax_applies
                        total_items_data["sc_gst_tax_rate"] = sac_code_based_gst_rates.sc_gst_tax_rate
                        total_items_data["sc_sac_code"] = sac_code_based_gst_rates.sc_sac_code
                total_items_data["sac_code"] = each_item["sac_code"]
                total_items_data["sort_order"] = each_item["sort_order"]
                total_items_data["item_name"] = each_item['item_name']
                total_items_data["item_value"] = each_item["item_value"]
                total_items_data["unit_of_measurement_description"] = each_item["unit_of_measurement_description"]
                total_items_data["unit_of_measurement"] = each_item["unit_of_measurement"]
                total_items_data["sac_index"] = sac_code_based_gst_rates.sac_index
                total_items_data["item_value_after_gst"] = each_item["item_value_after_gst"]
                total_items_data["line_edit_net"] = each_item["line_edit_net"]
                item_list.append(total_items_data)
        for service_charge_items in total_items:
            if service_charge_items["is_service_charge_item"] == "Yes":
                for new in item_list:
                    if int(new["sort_order"]) == int(service_charge_items["sort_order"]):
                        del total_items[total_items.index(service_charge_items)]
        for item in item_list:
            item_date = item['date']
            day = item_date[8:]
            year = item_date[2:4]
            month = item_date[4:8]
            item["item_value"] = item["item_value"]-item["discount_value"]
            date_item = day+month+year
            if companyDetails.number_in_description == 1:
                item_description = (item['item_name'].rstrip(string.digits)).strip()
            else:
                item_description = item['item_name']
            sac_code_based_gst = frappe.db.get_list('SAC HSN CODES', filters={'name': ['=',item_description]})
            if not sac_code_based_gst:
                sac_code_based_gst = frappe.db.get_list('SAC HSN CODES', filters={'name': ['like', '%' + item_description.strip() + '%']})
            if len(sac_code_based_gst)>0:
                sac_code_based_gst_rates = frappe.get_doc(
                'SAC HSN CODES',sac_code_based_gst[0]['name'])	
                SAC_CODE = sac_code_based_gst_rates.code 
                if sac_code_based_gst_rates.ignore == 1:
                    continue
            else:
                return{"success":False,"message":"SAC Code "+ item_description+" not found"}
            if sac_code_based_gst_rates.code == '996311' or sac_code_based_gst_rates.code == '997321':
                percentage_gst = CheckRatePercentages(item, sez, placeofsupply, sac_code_based_gst_rates.exempted, companyDetails.state_code)
                if percentage_gst["success"] == True:
                    acc_gst_percentage = percentage_gst["gst_percentage"]
                    acc_igst_percentage = percentage_gst["igst_percentage"]
                else:
                    {"success": False, "message": "error in slab helper function"}
            service_charge_name = (companyDetails.sc_name)
            if (service_charge_name != "" and companyDetails.enable_sc_from_folios == 1 and item["manual_edit"] == "No"):
                service_charge_name = service_charge_name.strip()
                if service_charge_name in item["item_name"]:
                    if placeofsupply != companyDetails.state_code:
                        item["igst"] = companyDetails.sc_gst_percentage
                        item["cgst"] = 0
                        item["sgst"] = 0
                    elif sez == 1:
                        if sac_code_based_gst_rates.exempted == 0:
                            item["igst"] = companyDetails.sc_gst_percentage
                            item["cgst"] = 0
                            item["sgst"] = 0
                        else:
                            item["cgst"] = 0
                            item["sgst"] = 0
                            item["igst"] = 0
                    elif sez == 0 or placeofsupply == companyDetails.state_code:
                        item["cgst"] = float(companyDetails.sc_gst_percentage)/2
                        item["sgst"] = float(companyDetails.sc_gst_percentage)/2
                        item["igst"] = 0
                    else:
                        item["cgst"] = 0
                        item["sgst"] = 0
                        item["igst"] = 0
            if item["net"] == "Yes":
                if sac_code_based_gst_rates.net == "Yes" and item["line_edit_net"] == "Yes":
                    for item_each in data['items_data']:
                        if isinstance(item_each["sort_order"], float):
                            if item["sort_order"] == int(item_each["sort_order"]):
                                item["item_value"] = item["item_value_after_gst"]+item_each["item_value_after_gst"]
                        else:
                            if item["service_charge"] == "No":
                                item["item_value"] = item["item_value_after_gst"]
                else:
                    if item["line_edit_net"] == "Yes":
                        item["item_value"] = item["item_value_after_gst"]
                        find_sc = [item for item in data["items_data"] if isinstance(item["sort_order"], float)]
                        for item_each in find_sc:
                            if isinstance(item_each["sort_order"], float):
                                if item["sort_order"] == int(item_each["sort_order"]):
                                    item["item_value"] = item["item_value_after_gst"]+item_each["item_value_after_gst"]
                item["calulation_type"] = "line_edit"
                item_data = calulate_net_yes(item,sac_code_based_gst_rates,companyDetails,sez,placeofsupply)
                if item_data["success"] == True:
                    item = item_data["data"]
                else:
                    return item_data
            else:
                if item["line_edit_net"] == "Yes":
                    item["item_value"] = item["item_value_after_gst"]
                    find_sc = [item for item in data["items_data"] if isinstance(item["sort_order"], float)]
                    for item_each in find_sc:
                        if isinstance(item_each["sort_order"], float):
                            if item["sort_order"] == int(item_each["sort_order"]):
                                item["item_value"] = item["item_value_after_gst"]+item_each["item_value_after_gst"]
            if companyDetails.enable_sc_from_folios == 0:
                if item["service_charge"] == "Yes":
                    gst_value = 0
                    service_dict = {}
                    if item["service_charge_tax_applies"] == "Apply From Parent":
                        gst_percentage = float(item["cgst"])+float(item["sgst"])
                        igst_percentage = float(item["igst"])
                        sac_code_new = sac_code_based_gst_rates.code
                        vat_rate_percentage = item["vat"]
                    elif item["service_charge_tax_applies"] == "Separate GST":
                        if (sez == 1 and sac_code_based_gst_rates.exempted == 0) or placeofsupply != companyDetails.state_code:
                            igst_percentage = item["sc_gst_tax_rate"]
                            gst_percentage = 0
                            sac_code_new = item["sc_sac_code"]
                            vat_rate_percentage = 0
                        elif sez == 1 and sac_code_based_gst_rates.exempted == 1:
                            igst_percentage = 0
                            gst_percentage = 0
                            sac_code_new = item["sc_sac_code"]
                            vat_rate_percentage = 0
                        else:
                            gst_percentage = item["sc_gst_tax_rate"]
                            igst_percentage = 0
                            sac_code_new = item["sc_sac_code"]
                            vat_rate_percentage = 0
                    else:
                        gst_percentage = 0
                        igst_percentage = 0
                        sac_code_new = sac_code_based_gst_rates.code
                        vat_rate_percentage = 0
                    # if (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 0) or (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 1) or (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1 and companyDetails.reverse_calculation == 0):
                    # 	base_value = round(item['item_value'] * (100 / ((gst_percentage+igst_percentage) + 100)),3) 
                    # 	gst_value = item['item_value']- base_value
                    # 	scharge_value = (item["service_charge_rate"] * base_value) / 100.0
                    # 	if sac_code_based_gst_rates.service_charge_net == "Yes":
                    # 		scharge_value_base = round(scharge_value * (100 / ((gst_percentage+igst_percentage) + 100)),3)
                    # 		gst_value = scharge_value- scharge_value_base
                    # 		scharge_value = scharge_value_base
                    # 	item['base_value'] = base_value
                    # 	igst_value = igst_percentage
                    # else:
                    base_value = item['item_value']
                    scharge_value = (item["service_charge_rate"] * item['item_value']) / 100.0
                    if (sac_code_based_gst_rates.code == '996311' or sac_code_based_gst_rates.code == '997321') and item["service_charge_tax_applies"] == "Apply From Parent":	
                        if item["manual_edit"] == "Yes":
                            gst_percentage = float(item["cgst"])+float(item["sgst"])
                            igst_percentage = float(item["igst"])
                        else:
                            gst_percentage = acc_gst_percentage
                            igst_percentage = acc_igst_percentage
                    if sac_code_based_gst_rates.service_charge_net == "Yes":
                        scharge_value_base = round(scharge_value * (100 / ((gst_percentage+igst_percentage) + 100)),3)
                        gst_value = scharge_value- scharge_value_base
                        scharge_value = scharge_value_base
                    if vat_rate_percentage>0:
                        vatamount = (vat_rate_percentage * scharge_value) / 100.0
                        service_dict['vat_amount'] = vatamount
                        service_dict['vat'] = vat_rate_percentage
                    else:
                        vatamount = 0
                        service_dict['vat_amount'] = 0
                        service_dict['vat'] = 0
                    if item["cess"]>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                        centralcessamount = (item["cess"] * scharge_value) / 100.0
                        service_dict['cess_amount'] = centralcessamount
                        service_dict['cess'] = item["cess"]
                    else:
                        centralcessamount = 0
                        service_dict['cess_amount'] = 0
                        service_dict['cess'] = 0
                    if item["state_cess"]>0 and sac_code_based_gst_rates.disable_cess_for_sc == 0:
                        statecessamount = (item["state_cess"] * scharge_value) / 100.0
                        service_dict['state_cess_amount'] = statecessamount
                        service_dict['state_cess'] = item["state_cess"]
                    else:
                        statecessamount = 0
                        service_dict['state_cess_amount'] = 0
                        service_dict['state_cess'] = 0	
                    # if  sac_code_based_gst_rates.taxble=="No" and sac_code_based_gst_rates.
                    if gst_value==0:
                        gst_value = (float(gst_percentage)* scharge_value)/100.0
                        igst_value = (float(igst_percentage)* scharge_value)/100.0
                    if sez == 1 and sac_code_based_gst_rates.exempted == 1:
                        type_item = "Excempted"
                    else:
                        type_item = "Included"
                    if gst_percentage>0 or igst_percentage>0:
                        scTaxble = "Yes"
                    else:
                        scTaxble = sac_code_based_gst_rates.taxble	
                    service_dict['item_name'] = item['item_name']+"-SC " + str(item["service_charge_rate"])
                    service_dict['description'] = item['item_name']+"-SC " + str(item["service_charge_rate"])
                    service_dict['date'] = date_item
                    service_dict['sac_code'] = sac_code_new
                    service_dict['sac_code_found'] = 'Yes'
                    service_dict['cgst'] = int(gst_percentage)/2
                    service_dict['other_charges'] = 0
                    service_dict['cgst_amount'] = gst_value/2
                    service_dict['sgst'] = int(gst_percentage)/2
                    service_dict['sgst_amount'] = gst_value/2
                    service_dict['igst'] = igst_percentage
                    service_dict['igst_amount'] = igst_value
                    service_dict['gst_rate'] = int(gst_percentage)+int(igst_percentage)
                    service_dict['item_value_after_gst'] = scharge_value + gst_value + vatamount + statecessamount + centralcessamount + igst_value
                    service_dict['item_taxable_value'] = scharge_value 
                    service_dict['item_value'] = scharge_value
                    service_dict['taxable'] = "Yes" if gst_percentage>0 else "No"
                    service_dict['unit_of_measurement']= item["unit_of_measurement"]
                    service_dict['quantity'] = item["quantity"]
                    service_dict['unit_of_measurement_description'] = item["unit_of_measurement_description"]
                    # service_dict['cess'] = 0
                    # service_dict['cess_amount'] = 0
                    # service_dict['state_cess'] = 0
                    # service_dict['state_cess_amount'] = 0
                    service_dict['type'] = type_item
                    service_dict['item_mode'] = ItemMode if "-" in str(scharge_value) else "Debit"
                    service_dict['item_type'] = sac_code_based_gst_rates.type
                    service_dict["sac_index"] = sac_code_based_gst_rates.sac_index
                    # service_dict['vat_amount'] = 0
                    # service_dict['vat'] = 0
                    sortorder = str(item['sort_order'])+".1"
                    service_dict['sort_order'] = float(sortorder)
                    service_dict['doctype'] = 'Items'
                    service_dict['parentfield'] = 'items'
                    service_dict['parenttype'] = 'invoices'
                    service_dict["is_manual_edit"] = item["manual_edit"]
                    service_dict["is_service_charge_item"] = item["service_charge"]
                    service_dict["exempted"] = sac_code_based_gst_rates.exempted
                    service_dict["discount_value"] = 0
                    second_list.append(service_dict)
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
            if sac_code_based_gst_rates.taxble == "Yes" and sac_code_based_gst_rates.type != "Discount":
                if "-" in str(item['item_value']):
                    final_item['item_mode'] = ItemMode
                else:
                    final_item['item_mode'] = "Debit"
                # if sac_code_based_gst_rates.net == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])):
                # if (item["net"] == "No") or (companyDetails.reverse_calculation == 1 and item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1):
                if (item['sac_code'] == '996311' or item['sac_code'] == '997321') and sac_code_based_gst_rates.accommodation_slab == 1 and item["manual_edit"] != "Yes":
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
                    final_item['cgst'] = float(item["cgst"])
                    final_item['sgst'] = float(item["sgst"])
                    final_item['igst'] = float(item["igst"])
                    final_item['type'] = "Included"
                final_item['cgst_amount'] = round((item["item_value"]*(final_item['cgst']/100)),3)
                final_item['sgst_amount'] = round((item["item_value"]*(final_item['sgst']/100)),3)
                final_item['igst_amount'] = round((item["item_value"]*(final_item['igst']/100)),3)
                final_item['gst_rate'] = final_item['cgst']+final_item['sgst']+final_item['igst']
                final_item['item_value_after_gst'] = final_item['cgst_amount']+final_item['sgst_amount']+final_item['igst_amount']+item['item_value']
                final_item['item_value'] = item['item_value']
                # elif (item["net"] == "Yes" and (item['sac_code'] != "996311" or item['sac_code'] != '997321') and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 0) or (item["net"] == "Yes" and (item['sac_code'] != "996311" or item['sac_code'] != '997321') and sac_code_based_gst_rates.inclusive_of_service_charge == 1 and companyDetails.reverse_calculation == 0) or (item["net"] == "Yes" and (item['sac_code'] != "996311" or item['sac_code'] != '997321') and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 1):
                # 	gst_percentage = (float(item["cgst"]) + float(item["sgst"]))
                # 	base_value = round(item['item_value'] * (100 / (gst_percentage + 100)),3)
                # 	gst_value = item['item_value'] - base_value
                # 	final_item['cgst'] = float(item["cgst"])
                # 	final_item['sgst'] = float(item["sgst"])
                # 	final_item['cgst_amount'] = round(gst_value / 2,3)
                # 	final_item['sgst_amount'] = round(gst_value / 2,3)
                # 	final_item['igst'] = float(item["igst"])
                # 	if float(item["igst"]) <= 0:
                # 		final_item['igst_amount'] = 0
                # 	else:
                # 		base_value = item['item_value'] * (100 / (float(item["igst"]) + 100))
                # 		final_item['igst_amount'] = item['item_value'] - base_value
                # 	final_item['gst_rate'] = gst_percentage+final_item['igst']
                # 	final_item['item_value_after_gst'] = item['item_value']
                # 	final_item['item_value'] = base_value
                # 	if sez == 1 and sac_code_based_gst_rates.exempted == 1:
                # 		final_item["type"] = "Included"
                # 	else:
                # 		final_item['type'] = "Excempted"
                final_item['other_charges'] = 0
                final_item['sac_code_found'] = 'Yes'
                final_item['taxable'] = sac_code_based_gst_rates.taxble
                final_item['sort_order'] = item['sort_order']
            # elif sac_code_based_gst_rates.exempted == 1 and sac_code_based_gst_rates.taxble == "Yes":
            # 	final_item['cgst'] = 0
            # 	final_item['sgst'] = 0
            # 	final_item['igst'] = 0
            # 	final_item['type'] = "Excempted"
            # 	final_item['cgst_amount'] = 0
            # 	final_item['sgst_amount'] = 0
            # 	final_item['igst_amount'] = 0
            # 	final_item['gst_rate'] = 0
            # 	final_item['item_value_after_gst'] = item['item_value']
            # 	final_item['item_value'] = item['item_value']
            # 	final_item['other_charges'] = 0
            # 	final_item['sac_code_found'] = 'Yes'
            # 	final_item['taxable'] = sac_code_based_gst_rates.taxble
            # 	final_item['sort_order'] = item['sort_order']
            # 	if "-" in str(item['item_value']):
            # 		final_item['item_mode'] = ItemMode
            # 	else:
            # 		final_item['item_mode'] = "Debit"
            else:
                # if item['sac_code'] != "996311" and sac_code_based_gst_rates.taxble == "No" and not (("Service" in item['name']) or ("Utility" in item['name'])) and sac_code_based_gst_rates.type != "Discount":
                if (item['sac_code'] != "996311" or item['sac_code'] != "997321") and sac_code_based_gst_rates.taxble == "No":
                    # if (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 0) or (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 0 and companyDetails.reverse_calculation == 1) or (item["net"] == "Yes" and sac_code_based_gst_rates.inclusive_of_service_charge == 1 and companyDetails.reverse_calculation == 0):
                    # 	vatcessrate = item["state_cess"]+item["cess"]+item["vat"]
                    # 	if "item_value_after_gst" in item:
                    # 		base_value = round(item['item_value_after_gst'] * (100 / (vatcessrate + 100)),3)
                    # 		final_item['item_value'] = base_value
                    # 		final_item['item_value_after_gst'] = base_value
                    # 		item["item_value"] = base_value
                    # else:
                    final_item['item_value_after_gst'] = item['item_value']
                    final_item['item_value'] = item['item_value']
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
                    # final_item['item_mode'] = "Debit"
                    if "-" in str(item['item_value']):
                        final_item['item_mode'] = ItemMode
                    else:
                        final_item['item_mode'] = "Debit"
            final_item['state_cess'] = item["state_cess"]
            if final_item['state_cess'] > 0:
                final_item["state_cess_amount"] = (item["item_value"]*(final_item['state_cess']/100))
            else:
                final_item["state_cess_amount"] = 0
            final_item['cess'] = item["cess"]
            if final_item['cess'] > 0:
                final_item["cess_amount"] = (item["item_value"]*(final_item['cess']/100))
            else:
                final_item["cess_amount"] = 0
            final_item['vat'] = item["vat"]
            if final_item['vat'] > 0:
                final_item["vat_amount"] = (item["item_value"]*(final_item['vat']/100))
                # if sac_code_based_gst_rates.service_charge == "Yes":
                # 	vatservicecharge = (scharge * final_item["vat_amount"]) / 100.0	
                # 	final_item["vat_amount"] = final_item["vat_amount"]+vatservicecharge
            else:
                final_item["vat_amount"] = 0
            final_item['item_value_after_gst'] = final_item['item_value_after_gst']+final_item['cess_amount']+final_item['vat_amount']+final_item["state_cess_amount"]
            if sez == 1 and sac_code_based_gst_rates.exempted == 1:
                final_item['type'] = "Excempted"
            total_items.append({
                'doctype':
                'Items',
                'sac_code':
                item['sac_code'],
                'item_name':
                item['item_name'],
                'sort_order':final_item['sort_order'],
                "item_type":sac_code_based_gst_rates.type,
                'date':date_item,
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
                item['item_name'],
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
                "is_manual_edit":item["manual_edit"],
                "is_service_charge_item": "No",
                "exempted":sac_code_based_gst_rates.exempted,
                "sac_index": sac_code_based_gst_rates.sac_index,
                'unit_of_measurement': item["unit_of_measurement"],
                'quantity': item["quantity"],
                'unit_of_measurement_description': item["unit_of_measurement_description"],
                "discount_value" : item["discount_value"],
                "line_edit_net": item["net"]
            })
        total_items.extend(second_list)
        for xyz in total_items:
            xyz["date"] = datetime.datetime.strptime(xyz["date"],"%d-%m-%y").strftime('%Y-%m-%d %H:%M:%S')
        final_data.update({"guest_data":data["guest_data"], "taxpayer":data["taxpayer"],"items_data":total_items,"company_code":data["company_code"],"total_invoice_amount":data["total_inovice_amount"],"invoice_number":data["invoice_number"],"sez":sez,"place_of_supply":placeofsupply})
        reinitiate = Reinitiate_invoice(final_data)
        doc_inv = frappe.get_doc("Invoices",data["invoice_number"])
        doc_inv.sez = sez
        doc_inv.save(ignore_permissions=True)
        if reinitiate["success"] == True:
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
        print(e, "calculation api")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing reprocess_calulate_items","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def auto_adjustment(data):
    try:
        invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
        # invoice_data = frappe.db.get_value('Invoices', data["invoice_number"], ['invoice_number', 'guest_name',"gst_number","invoice_file","room_number","invoice_type","invoice_date","legal_name","address_1","address_2","email","trade_name","phone_number","state_code","location","pincode","irn_cancelled","other_charges","company","confirmation_number","invoice_from","print_by","has_discount_items","invoice_category","sez","converted_from_b2b","allowance_invoice","converted_from_tax_invoices_to_manual_tax_invoices"], as_dict=1)
        invoice_data = frappe.db.get_all('Invoices', filters={"name":data["invoice_number"]},fields=["*"])
        company = frappe.get_doc('company',invoice_doc.company)
        if len(invoice_data) > 0:
            invoice_date = date_time_obj = datetime.datetime.strptime(str(invoice_data[0]["invoice_date"]),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            item_data = frappe.db.get_list('Items',filters={"parent":data["invoice_number"],"is_service_charge_item":"No"},fields=["*"])
            for item_each in item_data:
                sac_code_based_gst = frappe.db.get_list('SAC HSN CODES',filters={'name': ['=',item_each["description"]]})
                if not sac_code_based_gst:
                    sac_code_based_gst = frappe.db.get_list('SAC HSN CODES',filters={'name': ['like', '%' + item_each["description"] + '%']})
                if len(sac_code_based_gst)>0:
                    sac_code_based_gst_rates = frappe.get_doc('SAC HSN CODES',sac_code_based_gst[0]['name'])
                if sac_code_based_gst_rates.net == "Yes":
                    item_each["item_value"] = item_each["item_value_after_gst"]
            negative_data = [items for items in item_data if items["item_value"]<0]
            positive_data = [items for items in item_data if items["item_value"]>0]
            # df = pd.DataFrame.from_records(negative_data)
            # group = df.groupby(["sac_code","gst_rate","type","taxable"]).agg({'cgst_amount': 'sum','sgst_amount':'sum','igst_amount':'sum','item_value':'sum','item_taxable_value':'sum','item_value_after_gst':'sum',"cess_amount":'sum',"state_cess_amount":'sum',"vat_amount":'sum','discount_value':'sum','sac_code':"first","item_name":'first',"item_type":"first","cgst":"first","sgst":"first","igst":"first","cess":"first","state_cess":"first","description":"first","date":"first","type":"first","unit_of_measurement":"first","unit_of_measurement_description":"first","sac_index":"first","quantity":"first","is_service_charge_item":"first","parentfield":"first","parenttype":"first","taxable":"first","sort_order":"first","sac_code_found":"first","gst_rate":"first"})
            # group_data = group.to_dict('records')
            value = 0
            for each in negative_data:
                for item in positive_data:
                    if each["sac_code"] == item["sac_code"] and each["gst_rate"] == item["gst_rate"] and each["type"] == item["type"] and each["taxable"] == item["taxable"] and item["item_value"] == abs(each["item_value"]):
                        value = item['item_value'] - abs(each["item_value"])
                        positive_data.remove(item)
                        each["item_value"] = value

            negative_total = [items for items in negative_data if items["item_value"] != 0]
            if (negative_total != [] and positive_data != []):
                for each_item in negative_data:
                    for items in positive_data:
                        if each_item["sac_code"] == items["sac_code"] and each_item["gst_rate"] == items["gst_rate"] and each_item["type"] == items["type"] and each_item["taxable"] == items["taxable"] and items["item_value"] != 0 and each_item["item_value"] != 0:
                            value = items["item_value"] - abs(each_item["item_value"])
                            if value == 0:
                                positive_data.remove(items)
                                each_item["item_value"] = 0
                            elif value < 0:
                                each_item["item_value"] = value
                                items["item_value"] = 0
                            else:
                                each_item["item_value"] = 0
                                items["item_value"] = value
            items_total = [items for items in positive_data if items["item_value"] != 0]
            items_total.extend([items for items in negative_data if abs(items["item_value"]) != 0])
            total_items = []
            for items in items_total:
                item_date = datetime.datetime.strptime(str(items["date"]),'%Y-%m-%d').strftime(company.invoice_item_date_format)
                total_items.append({"date":item_date, "item_value":items["item_value"],"sac_code":items["sac_code"],"sort_order":int(items["sort_order"]),"name":items["description"],"sgst":items["sgst"],"cgst":items["sgst"],"igst":items["igst"]})
            calulate_items_data = {"items":total_items,"invoice_number":data["invoice_number"],"company_code":company.name,"invoice_item_date_format":company.invoice_item_date_format,"sez":invoice_doc.sez,"adjustment":"Yes"}
            calulate_response = calulate_items(calulate_items_data)
            if calulate_response["success"] == False:
                return {"success": False, "message": calulate_response["message"]}
            guest_data = {"name":invoice_data[0]["guest_name"],"items":calulate_items_data,"invoice_date":invoice_date,"invoice_number":invoice_doc.invoice_number,"membership":"","invoice_type":invoice_data[0]["invoice_type"],"gstNumber":invoice_data[0]["gst_number"],"room_number":invoice_data[0]["room_number"],"company_code":invoice_data[0]["company"],"confirmation_number":invoice_data[0]["confirmation_number"],"print_by":invoice_data[0]["print_by"],"invoice_category":invoice_doc.invoice_category,"invoice_file":invoice_data[0]["invoice_file"],"start_time":str(datetime.datetime.utcnow())}
            if invoice_data[0]["gst_number"] != "":
                taxpayer = frappe.get_doc("TaxPayerDetail",invoice_data[0]["gst_number"])
                tax_payer = taxpayer.__dict__
            else:
                taxpayer = {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
                tax_payer = taxpayer
            reinitate = Reinitiate_invoice({"guest_data":guest_data,"items_data":calulate_response["data"],"sez":invoice_doc.sez,"total_invoice_amount":invoice_doc.total_invoice_amount,"taxpayer":tax_payer,"invoice_number":invoice_doc.invoice_number,"company_code":company.name})
            if reinitate["success"] == False:
                return {"success": False, "message": reinitate["message"]}
            return {"success": True, "message": "Adjustment was successfully adjusted"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing auto_adjustment","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(e, "auto_adjustment")
        return {"success": False, "message": str(e)}

@frappe.whitelist(allow_guest=True)
def b2b_success_to_credit_note(data):
    try:
        user = frappe.session.user
        invoice_doc = frappe.get_doc("Invoices",data["invoice_number"])
        company = frappe.get_doc('company',invoice_doc.company)
        # invoice_data = frappe.db.get_value('Invoices', data["invoice_number"], ['invoice_number', 'guest_name',"gst_number","invoice_file","room_number","invoice_type","invoice_date","legal_name","address_1","address_2","email","trade_name","phone_number","state_code","location","pincode","irn_cancelled","other_charges","company","confirmation_number","invoice_from","print_by","has_discount_items","invoice_category","sez","converted_from_b2b","allowance_invoice","converted_from_tax_invoices_to_manual_tax_invoices"], as_dict=1)
        invoice_data = frappe.db.get_all('Invoices', filters={"name":data["invoice_number"]},fields=["*"])
        total_data = {}
        # print(invoice_data)
        if len(invoice_data) > 0:
            invoice_number = data["invoice_number"]+"CN"
            invoice_date = datetime.datetime.strptime(str(datetime.datetime.today().date()),'%Y-%m-%d').strftime('%d-%b-%y %H:%M:%S')
            item_data = frappe.db.get_list('Items',filters={"parent":data["invoice_number"],"is_service_charge_item":"No"},fields=["*"])
            for item_each in item_data:
                sac_code_based_gst = frappe.db.get_list('SAC HSN CODES',filters={'name': ['=',item_each["description"]]})
                if not sac_code_based_gst:
                    sac_code_based_gst = frappe.db.get_list('SAC HSN CODES',filters={'name': ['like', '%' + item_each["description"] + '%']})
                if len(sac_code_based_gst)>0:
                    sac_code_based_gst_rates = frappe.get_doc('SAC HSN CODES',sac_code_based_gst[0]['name'])
                if sac_code_based_gst_rates.net == "Yes":
                    if sac_code_based_gst_rates.code == '996311':
                        item_each["item_value"] = item_each["item_taxable_value"]
                    else:	
                        item_each["item_value"] = item_each["item_value_after_gst"]
            total_items = []
            if invoice_doc.has_credit_items == "Yes":
                negative_data = [items for items in item_data if items["item_value"]<0]
                positive_data = [items for items in item_data if items["item_value"]>0]
                # df = pd.DataFrame.from_records(negative_data)
                # group = df.groupby(["sac_code","gst_rate","type","taxable"]).agg({'cgst_amount': 'sum','sgst_amount':'sum','igst_amount':'sum','item_value':'sum','item_taxable_value':'sum','item_value_after_gst':'sum',"cess_amount":'sum',"state_cess_amount":'sum',"vat_amount":'sum','discount_value':'sum','sac_code':"first","item_name":'first',"item_type":"first","cgst":"first","sgst":"first","igst":"first","cess":"first","state_cess":"first","description":"first","date":"first","type":"first","unit_of_measurement":"first","unit_of_measurement_description":"first","sac_index":"first","quantity":"first","is_service_charge_item":"first","parentfield":"first","parenttype":"first","taxable":"first","sort_order":"first","sac_code_found":"first","gst_rate":"first"})
                # group_data = group.to_dict('records')
                value = 0
                for each in negative_data:
                    for item in positive_data:
                        if each["sac_code"] == item["sac_code"] and each["gst_rate"] == item["gst_rate"] and each["type"] == item["type"] and each["taxable"] == item["taxable"] and item["item_value"] == abs(each["item_value"]):
                            value = item['item_value'] - abs(each["item_value"])
                            positive_data.remove(item)
                            each["item_value"] = value

                negative_total = [items for items in negative_data if items["item_value"] != 0]
                if (negative_total != [] and positive_data != []):
                    for each_item in negative_data:
                        for items in positive_data:
                            if each_item["sac_code"] == items["sac_code"] and each_item["gst_rate"] == items["gst_rate"] and each_item["type"] == items["type"] and each_item["taxable"] == items["taxable"] and items["item_value"] != 0 and each_item["item_value"] != 0:
                                value = items["item_value"] - abs(each_item["item_value"])
                                if value == 0:
                                    positive_data.remove(items)
                                    each_item["item_value"] = 0
                                elif value < 0:
                                    each_item["item_value"] = value
                                    items["item_value"] = 0
                                else:
                                    each_item["item_value"] = 0
                                    items["item_value"] = value
                item_data = [items for items in negative_data if items["item_value"] != 0]
                if len(item_data) > 0:
                    return {"success": False, "message": "Please adjust the items manually before converting to credit."}
                item_data.extend([items for items in positive_data if abs(items["item_value"]) != 0])
            for items in item_data:
                item_date = datetime.datetime.strptime(str(items["date"]),'%Y-%m-%d').strftime(company.invoice_item_date_format)
                total_items.append({"date":item_date, "item_value":-abs(items["item_value"]),"sac_code":items["sac_code"],"sort_order":int(items["sort_order"]),"name":items["description"],"sgst":items["sgst"],"cgst":items["sgst"],"igst":items["igst"]})
            calulate_items_data = {"items":total_items,"invoice_number":invoice_number,"company_code":company.name,"invoice_item_date_format":company.invoice_item_date_format,"sez":invoice_doc.sez}
            calulate_response = calulate_items(calulate_items_data)
            if calulate_response["success"] == False:
                return {"success": False, "message": calulate_response["message"]}
            guest_data = {"name":invoice_data[0]["guest_name"],"items":calulate_items_data,"invoice_date":invoice_date,"invoice_number":invoice_number,"membership":"","invoice_type":invoice_data[0]["invoice_type"],"gstNumber":invoice_data[0]["gst_number"],"room_number":invoice_data[0]["room_number"],"company_code":invoice_data[0]["company"],"confirmation_number":invoice_data[0]["confirmation_number"],"print_by":invoice_data[0]["print_by"],"invoice_category":"Credit Invoice","invoice_file":invoice_data[0]["invoice_file"],"start_time":str(datetime.datetime.utcnow()),"invoice_from":"Web"}
            if invoice_data[0]["gst_number"] != "":
                taxpayer = frappe.get_doc("TaxPayerDetail",invoice_data[0]["gst_number"])
                tax_payer = taxpayer.__dict__
            else:
                taxpayer = {"legal_name": "","address_1": "","address_2": "","email": "","trade_name": "","phone_number": "","location": "","pincode": "","state_code": ""}
                tax_payer = taxpayer
            reinitate = insert_invoice({"guest_data":guest_data,"items_data":calulate_response["data"],"sez":invoice_doc.sez,"total_invoice_amount":-abs(invoice_doc.total_invoice_amount),"taxpayer":tax_payer,"invoice_number":invoice_number,"company_code":company.name,"amened":"No","converted_tax_to_credit":"Yes","tax_invoice_referrence_number":invoice_doc.name,"raise_credit":"Yes"})
            if reinitate["success"] == False:
                return {"success": False, "message": reinitate["message"]}
            doc_invoice = frappe.get_doc("Invoices",data["invoice_number"])
            doc_invoice.credit_note_raised = "Yes"
            doc_invoice.save(ignore_permissions=True,ignore_version=True)
            if data['taxinvoice'] == "Yes":
                raise_credit_taxinvoice(data['invoice_number'],data['invoice_date'],data['taxinvoice_number'])
            # subject1 = 'Credit Note Created and Invoice Number is {}'.format(invoice_number)
            # parent_activity = frappe.get_doc({'doctype': 'Version','data': '<!DOCTYPE html><html><body><p>{}</p></body></html>'.format(subject1),"ref_doctype":"Invoices","docname":data["invoice_number"]})
            # parent_activity.insertS(ignore_permissions=True,ignore_version=True)
            # frappe.db.commit()
            # if data['tax_invoice'] == "Yes":

            return {"success": True, "message": "Credit Note Raised Successfully"}

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing b2b_success_to_credit_note","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(traceback.print_exc(), "raise credit")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def raise_credit_taxinvoice(invoice_number,invdate,taxinvoice_number):
    try:
        doc_details = frappe.get_doc("Invoices",invoice_number)
        data = dict(doc_details.__dict__)

        data['name'] = taxinvoice_number
        data['invoice_number'] = data['name']
        data['irn_generated'] = "Pending"
        data['qr_code_generated'] = "Pending"
        data['signed_invoice_generated']= 'No'
        data['invoice_date'] = invdate
        # items = data['items']
        items = [item.__dict__ for item in data['items']]
        del data['items']
        del data['gst_summary']
        del data['sac_hsn_based_taxes']
        del data['irn_number']
        del data['qr_code']
        del data['qr_code_image']
        del data['signed_invoice']
        del data['ack_no']
        del data['ack_date']
        del data['error_message']
        del data['irn_generated_time']
        del data['credit_signed_invoice_generated']
        del data['credit_irn_cancelled']
        del data['irn_process_time']
        del data['irn_generated_type']
        del data['credit_note_raised']
        insertdoc = frappe.get_doc(data)

        insertdoc.insert(ignore_permissions=True, ignore_links=True)
        itemsInsert = insert_items(items,data['name'])
        taxSummariesInsert = TaxSummariesInsert(items, data['name'])
        hsnbasedtaxcodes = insert_hsn_code_based_taxes(items, data['name'],"Invoice")
    except Exception as e:
        print(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing raise_credit_taxinvoice","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}