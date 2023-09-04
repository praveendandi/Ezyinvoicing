from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import pandas as pd
import numpy as np
import time
import os,sys,traceback
import datetime
import json

import traceback
from frappe.utils import logger


def TotalMismatchError(data,calculated_data):
    try:
        if "invoice_from" in data['guest_data']:
            invoice_from = data['guest_data']['invoice_from']
        else:
            invoice_from = "Pms"	
        invType = data['guest_data']['invoice_type']
        irn_generated = "Error"  
        if data['guest_data']['room_number'] == 0 and '-' not in str(calculated_data['sales_amount_after_tax']):
            # data['guest_data']['invoice_category'] = "Debit Invoice"
            debit_invoice = "Yes"
        else:
            debit_invoice = "No" 
        companyDetails = frappe.get_doc("company",data['company_code'])
        if '-' in str(calculated_data['sales_amount_after_tax']):
            allowance_invoice = "Yes"
        else:
            allowance_invoice = "No"
        # print(jhasdjkasjdh)
        if 'pos_checks' not in data['guest_data']:
            pos_checks = 0
        else:
            pos_checks = data['guest_data']['pos_checks']
        
        folder_path = frappe.utils.get_bench_path()
        with open(folder_path+"/"+"apps/version2_app/version2_app/version2_app/doctype/invoices/state_code.json") as f:
            json_data = json.load(f)
            for each in json_data:
                if companyDetails.state_code == each['tin']:
                    place_supplier_state_name = f"{each['state']}-({each['tin']})"
        
        invoice = frappe.get_doc({
                'doctype':
                'Invoices',
                'invoice_number':
                data['guest_data']['invoice_number'],
                'guest_name':
                data['guest_data']['name'],
                'invoice_round_off_amount': data['invoice_round_off_amount'],
                'ready_to_generate_irn':"No",
                'invoice_from':invoice_from,
                'gst_number':
                data['guest_data']['gstNumber'],
                'invoice_file':
                data['guest_data']['invoice_file'],
                'room_number':
                data['guest_data']['room_number'],
                'print_by': data['guest_data']['print_by'],
                'confirmation_number':
                data['guest_data']['confirmation_number'],
                'invoice_type':
                data['guest_data']['invoice_type'],
                'invoice_date':
                datetime.datetime.strptime(data['guest_data']['invoice_date'],
                                        '%d-%b-%y %H:%M:%S'),
                'legal_name':
                data['taxpayer']['legal_name'],
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
                'invoice_category':data['guest_data']['invoice_category'],
                'amount_before_gst':
                round(calculated_data['value_before_gst'], 2),
                "amount_after_gst":
                round(calculated_data['value_after_gst'], 2),
                "other_charges":
                round(calculated_data['other_charges'], 2),
                "other_charges_before_tax":round(calculated_data['other_charges_before_tax'],2),
                "credit_value_before_gst":
                round(calculated_data['credit_value_before_gst'], 2),
                "credit_value_after_gst":
                round(calculated_data['credit_value_after_gst'], 2),
                "pms_invoice_summary_without_gst":
                round(calculated_data['pms_invoice_summary_without_gst'], 2) ,
                "pms_invoice_summary":
                round(calculated_data['pms_invoice_summary'], 2) ,
                'irn_generated':irn_generated,
                # 'qr_generated':qr_generated,
                'irn_cancelled':
                'No',
                'qr_code_generated':
                'Pending',
                'signed_invoice_generated':
                'No',
                'total_invoice_amount':data['total_invoice_amount'],
                'company':
                data['company_code'],
                'mode': calculated_data['company'].mode,
                'cgst_amount':
                round(calculated_data['cgst_amount'], 2),
                'sgst_amount':
                round(calculated_data['sgst_amount'], 2),
                'igst_amount':
                round(calculated_data['igst_amount'], 2),
                'total_central_cess_amount':
                round(calculated_data['total_central_cess_amount'], 2),
                'total_state_cess_amount':
                round(calculated_data['total_state_cess_amount'], 2),
                'total_vat_amount':
                round(calculated_data['total_vat_amount'], 2),
                'total_gst_amount':
                round(calculated_data['cgst_amount'], 2) + round(calculated_data['sgst_amount'], 2) +
                round(calculated_data['igst_amount'], 2),
                'sales_amount_after_tax':round(calculated_data['sales_amount_after_tax'],2),
                'sales_amount_before_tax': round(calculated_data['sales_amount_before_tax'],2),
                'has_credit_items':
                "No",
                'has_discount_items':'No',
                'invoice_process_time':
                datetime.datetime.utcnow() - datetime.datetime.strptime(
                    data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
                'credit_cgst_amount':round(calculated_data['credit_cgst_amount'],2),
                'credit_sgst_amount':round(calculated_data['credit_sgst_amount'],2),
                'credit_igst_amount':round(calculated_data['credit_igst_amount'],2),
                'total_credit_state_cess_amount':round(calculated_data['total_credit_state_cess_amount'],2),
                'total_credit_central_cess_amount':round(calculated_data['total_credit_central_cess_amount'],2),
                'total_credit_vat_amount': round(calculated_data['total_credit_vat_amount'],2),
                'credit_gst_amount': round(calculated_data['credit_cgst_amount'],2) + round(calculated_data['credit_sgst_amount'],2) + round(calculated_data['credit_igst_amount'],2),	
                'error_message':" Invoice Total Mismatch",
                "place_of_supply":companyDetails.state_code,
                "sez":data["sez"] if "sez" in data else 0,
                "allowance_invoice":allowance_invoice,
                "debit_invoice":debit_invoice,
                "invoice_object_from_file":json.dumps(data['invoice_object_from_file']),
                "place_of_supply_json" : place_supplier_state_name
            })
        if data['amened'] == 'Yes':
            invCount = frappe.db.get_list(
                'Invoices',
                filters={
                    'invoice_number':
                    ['like', '%' + data['guest_data']['invoice_number'] + '%']
                })
            invoice.amended_from = invCount[0]['name']
            invoice.invoice_number = data['guest_data'][
                'invoice_number'] + "-1"
        v = invoice.insert(ignore_permissions=True, ignore_links=True)
        invName = v.name
        if data['amened'] == 'Yes':
            getInvoiceNUmber = frappe.db.get_value('Invoices', {
                'invoice_number': data['guest_data']['invoice_number'] + "-1"
            })
            # print(getInvoiceNUmber)
            updateInvoi = frappe.get_doc('Invoices', getInvoiceNUmber)
            # print(updateInvoi)
            invName = updateInvoi.name

            updateInvoi.invoice_number = getInvoiceNUmber
            updateInvoi.save()

            data['invoice_number'] = getInvoiceNUmber
            data['guest_data']['invoice_number'] = getInvoiceNUmber
        updateInvoi = frappe.get_doc('Invoices', invName)
        return {"success":True,"invoice_number":data['guest_data']['invoice_number'],'items':data['items_data'],"data":updateInvoi}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing TotalMismatchError","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}    
        

def CheckRatePercentages(data, sez, placeofsupply, exempted, state_code):
    try:
        companyDetails = frappe.get_last_doc('company')

        if "tax_identification" in data:
            if data["tax_identification"] == "Yes":
                if placeofsupply != state_code:
                    igst_percentage = data["tax_rate"]
                    gst_percentage = 0
                elif sez == 1:
                    if exempted == 1:
                        gst_percentage = 0
                        igst_percentage = 0
                    else:
                        igst_percentage = data["tax_rate"]
                        gst_percentage = 0
                else:
                    gst_percentage = data["tax_rate"]
                    igst_percentage = 0
                return {"success":True,"gst_percentage":gst_percentage,"igst_percentage":igst_percentage}

        if abs(data['item_value'])>=companyDetails.slab_12_starting_range and abs(data['item_value'])<=companyDetails.slab_12_ending_range:
            gst_percentage = 12
        elif abs(data['item_value']) > companyDetails.slab_12_ending_range:
            gst_percentage = 18
        else:
            gst_percentage = 0
        if placeofsupply != state_code:
            igst_percentage = gst_percentage
            gst_percentage = 0
        elif sez == 1:
            if exempted == 1:
                gst_percentage = 0
                igst_percentage = 0
            else:
                igst_percentage = gst_percentage
                gst_percentage = 0
        else:
            gst_percentage = gst_percentage
            igst_percentage = 0
        return {"success":True,"gst_percentage":gst_percentage,"igst_percentage":igst_percentage}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing CheckRatePercentages","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}

def SCCheckRatePercentages(data, sez, placeofsupply, exempted, state_code):
    try:
        companyDetails = frappe.get_last_doc('company')
        if abs(data['item_value'])>=companyDetails.sc_slab_12_starting_range and abs(data['item_value'])<=companyDetails.sc_slab_12_end_range:
            gst_percentage = 12
        elif abs(data['item_value']) > companyDetails.sc_slab_12_end_range:
            gst_percentage = 18
        else:
            gst_percentage = 0
        if placeofsupply != state_code:
            igst_percentage = gst_percentage
            gst_percentage = 0
        elif sez == 1:
            if exempted == 1:
                gst_percentage = 0
                igst_percentage = 0
            else:
                igst_percentage = gst_percentage
                gst_percentage = 0
        else:
            gst_percentage = gst_percentage
            igst_percentage = 0
        return {"success":True,"gst_percentage":gst_percentage,"igst_percentage":igst_percentage}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing SCCheckRatePercentages","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}



def error_invoice_calculation(data,data1):
    try:
        if "invoice_object_from_file" not in data1:
            data1['invoice_object_from_file'] = {"data":[]}
        company = frappe.get_doc('company',data['company_code'])
        invType = data1['invoice_type']
        # if invType == "B2B":
        irn_generated = "Error"
        # qr_generated = "Pending"
        if "invoice_from" in data1:
            invoice_from = data1['invoice_from']
        else:
            invoice_from = "Pms"
        if "place_of_supply" in data1:
            place_of_supply = data1['place_of_supply']
        else:
            doc = frappe.db.exists("Invoices",data1['invoice_number'])
            if doc:
                invoice_doc = frappe.get_doc("Invoices",data1['invoice_number'])
                place_of_supply = invoice_doc.place_of_supply
                if not place_of_supply:
                    place_of_supply = company.state_code
            else:
                place_of_supply = company.state_code
        invoice = frappe.get_doc({
            'doctype':
            'Invoices',
            'invoice_number':
            data1['invoice_number'],
            'invoice_type':data1['invoice_type'],
            'guest_name':
            data1['guest_name'],
            # if len(data['gst_number'])==15:
            # 	'gst_number': data['gst_number'],


            'invoice_file':
            data1['invoice_file'],
            "invoice_from":invoice_from,
            'room_number':
            data1['room_number'],
            'irn_generated':irn_generated,
            # 'qr_generated':qr_generated,
            'invoice_date':
            datetime.datetime.strptime(data1['invoice_date'],
                                    '%d-%b-%y %H:%M:%S'),
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
            data1['pincode'],
            'state_code':
            data1['state_code'],
            'amount_before_gst':
            0,
            "amount_after_gst":
            0,
            "other_charges":
            0,  
            'mode':company.mode,
            'irn_cancelled':
            'No',
            'qr_code_generated':
            'Pending',
            'signed_invoice_generated':
            'No',
            'company':
            data1['company_code'],
            'ready_to_generate_irn':
            "No",
            'error_message':
            data1['error_message'],
            "invoice_object_from_file":json.dumps(data1['invoice_object_from_file']),
            "place_of_supply" : place_of_supply
        })
        v = invoice.insert(ignore_permissions=True, ignore_links=True)

        
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
        
        for item in data['items_data']:
            if item['taxable'] == 'No' and item['item_type'] != "Discount":
                other_charges += item['item_value_after_gst']
                other_charges_before_tax += item['item_value']
                total_vat_amount += item['vat_amount']
            elif item['taxable']=="No" and item['item_type']=="Discount":
                discountAmount += item['item_value_after_gst'] 
            elif item['sac_code'].isdigit():
                if "-" not in str(item['item_value']):
                    cgst_amount+=item['cgst_amount']
                    sgst_amount+=item['sgst_amount']
                    igst_amount+=item['igst_amount']
                    total_central_cess_amount+=item['cess_amount']
                    total_state_cess_amount +=item['state_cess_amount']
                    value_before_gst += item['item_value']
                    value_after_gst += item['item_value_after_gst']
                    total_vat_amount += item['vat_amount']
                    # print(value_before_gst,value_after_gst," ******")
                else:
                    # cgst_amount+=item['cgst_amount']
                    # sgst_amount+=item['sgst_amount']
                    # igst_amount+=item['igst_amount']
                    # total_central_cess_amount+=item['cess_amount']
                    # total_state_cess_amount +=item['state_cess_amount']
                    credit_cgst_amount+=abs(item['cgst_amount'])
                    credit_sgst_amount+=abs(item['sgst_amount'])
                    credit_igst_amount+=abs(item['igst_amount'])
                    total_credit_central_cess_amount+=item['cess_amount']
                    total_credit_state_cess_amount +=item['state_cess_amount']
                    credit_value_before_gst += abs(item['item_value'])
                    credit_value_after_gst += abs(item['item_value_after_gst'])
                    total_credit_vat_amount += item['vat_amount']
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
        # if (pms_invoice_summary > 0) or (credit_value_after_gst > 0):
        #     ready_to_generate_irn = "Yes"
        # else:
        #     ready_to_generate_irn = "No"
        roundoff_amount = 0
        data['invoice_round_off_amount'] = roundoff_amount
        
        sales_amount_before_tax = value_before_gst + other_charges_before_tax 
        sales_amount_after_tax = value_after_gst + other_charges
        sales_amount_after_tax = sales_amount_after_tax - credit_value_after_gst
        sales_amount_before_tax = sales_amount_before_tax - credit_value_before_gst
        if data['total_invoice_amount'] == 0:
            ready_to_generate_irn = "No"
        else:
            roundoff_amount = data['total_invoice_amount'] - (pms_invoice_summary+other_charges)
            data['invoice_round_off_amount'] = roundoff_amount
        if data1['room_number'] == 0 and '-' not in str(sales_amount_after_tax):
            
            debit_invoice = "Yes"
        else:
            debit_invoice = "No" 
        doc = frappe.get_doc('Invoices',data['invoice_number'])
        doc.total_invoice_amount = data['total_invoice_amount']	
        
        doc.mode = company.mode
        
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
        doc.ready_to_generate_irn = 'No'
        doc.cgst_amount=round(cgst_amount,2)
        doc.sgst_amount=round(sgst_amount,2)
        doc.igst_amount=round(igst_amount,2)
        doc.total_gst_amount = round(cgst_amount,2) + round(sgst_amount,2) + round(igst_amount,2)
        doc.irn_cancelled='No'
        # doc.qr_code_generated='Pending'
        doc.signed_invoice_generated='No'
        # doc.company=data['company_code']
        # doc.print_by = data['guest_data']['print_by']
        doc.total_credit_central_cess_amount =  round(total_credit_central_cess_amount,2)
        doc.total_credit_state_cess_amount = round(total_credit_state_cess_amount,2)
        doc.total_credit_vat_amount = round(total_credit_vat_amount,2)
        doc.credit_cgst_amount = round(credit_cgst_amount,2)
        doc.credit_sgst_amount = round(credit_sgst_amount,2)
        doc.credit_igst_amount = round(credit_igst_amount,2)
        doc.credit_gst_amount = round(credit_cgst_amount,2) + round(credit_sgst_amount,2) + round(credit_igst_amount,2)	
        doc.has_credit_items = has_credit_items
        doc.mode = company.mode
        doc.invoice_round_off_amount = roundoff_amount
        doc.debit_invoice = debit_invoice
        doc.save(ignore_permissions=True, ignore_version=True)
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing error_invoice_calculation","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        print(traceback.format_exc())
        return False




def update_document_bin(print_by,invoice_type,invoiceNumber,error_log,filepath):
    try:
        document_printed = "No"
        if len(invoiceNumber)>0:
            inv = frappe.get_doc("Invoices",invoiceNumber)
            if inv:
                error_log = ""
                document_printed = "Yes"
            else:
                document_printed = "No"	
        if "Duplicate" in error_log:
            error_log = "Invoice Already Printed"		
        bin_name = frappe.db.get_value('Document Bin',{'invoice_file': filepath})
        bin_doc = frappe.get_doc("Document Bin",bin_name)
        bin_doc.print_by = print_by
        bin_doc.document_type = invoice_type
        bin_doc.invoice_number = invoiceNumber
        bin_doc.error_log = error_log
        bin_doc.document_printed = document_printed
        bin_doc.save(ignore_permissions=True,ignore_version=True)
        frappe.log_error(traceback.print_exc())
    except Exception as e:
        # frappe.log_error(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing update_document_bin","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}


def calulate_b2c_items(data=None):
    try:
        total_invoice_amount = 0
        for each in data:
            total_invoice_amount += each["item_value_after_gst"]
        return {"success":True,"total_invoice_amount":total_invoice_amount}
    except Exception as e:
        # frappe.log_error(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing calulate_b2c_items","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
    

def check_accommodation(data):
    try:
        if len(data) > 0:
            companyDetails = frappe.get_last_doc('company')
            df = pd.DataFrame.from_records(data)
            df[['sac_code', 'taxable', "accommodation_slab"]] = df.apply(lambda df: get_sac_code(df['name']), axis=1, result_type='expand')
            acc_df = df[(df['sac_code'] == '996311') & (df['taxable'] == "Yes")]
            if len(acc_df) > 0:
                group_acc = acc_df.groupby("date").agg({"item_value": "sum", "sac_code": "first"}).reset_index()
                group_acc["tax_rate"] = 12
                group_acc.loc[group_acc['item_value'] > companyDetails.slab_12_ending_range,'tax_rate'] = 18
                group_acc.loc[group_acc['item_value'] > companyDetails.slab_12_ending_range,'tax_identification'] = "Yes"
                group_acc.drop(["item_value"], axis=1, inplace=True)
                merge_df = pd.merge(df, group_acc, how='left', on=['date', 'sac_code'])
                merge_df["tax_rate"].replace({np.NAN: 0.0}, inplace=True)
                merge_df["tax_identification"].replace({np.NAN: "No"}, inplace=True)
                data = merge_df.to_dict('records')
                return {"success": True, "data": data}
            return {"success": True, "data": data}
    except Exception as e:
        # frappe.log_error(traceback.print_exc())
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("check_accommodation","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}
    

def get_sac_code(desc):
    sac_code_based_gst = frappe.db.get_list(
                    'SAC HSN CODES', filters={'name': ['=',desc]})
    if not sac_code_based_gst:
        sac_code_based_gst = frappe.db.get_list(
            'SAC HSN CODES',
            filters={'name': ['like', desc + '%']})
        if len(sac_code_based_gst) > 0:
            sac_names = list(map(lambda x : x['name'], sac_code_based_gst))
            min_len_des = min(sac_names, key = len)
            sac_code_based_gst = [{"name":min_len_des}]
    if len(sac_code_based_gst)>0:
        sac_code_based_gst_rates = frappe.get_doc('SAC HSN CODES',sac_code_based_gst[0]['name'])
        sac_code = sac_code_based_gst_rates.code
        taxable_value = sac_code_based_gst_rates.taxble
        accommodation_slab = sac_code_based_gst_rates.accommodation_slab
    else:
        sac_code = "No SAC"
        taxable_value = "Not defined"
        accommodation_slab = 0
    return (sac_code, taxable_value, accommodation_slab)
