from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import time
import os
import datetime



def TotalMismatchError(data,calculated_data):
    try:
        invoice = frappe.get_doc({
                'doctype':
                'Invoices',
                'invoice_number':
                data['guest_data']['invoice_number'],
                'guest_name':
                data['guest_data']['name'],
                'invoice_round_off_amount': data['invoice_round_off_amount'],
                'ready_to_generate_irn':"No",
                'invoice_from':"Pms",
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
                'irn_generated':
                "Error",
                'irn_cancelled':
                'No',
                'qr_code_generated':
                'Pending',
                'signed_invoice_generated':
                'No',
                'total_inovice_amount':data['total_invoice_amount'],
                'company':
                data['company_code'],
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
                'error_message':" Invoice Total Mismatch"
            })
        if data['amened'] == 'Yes':
            invCount = frappe.db.get_list(
                'Invoices',
                filters={
                    'invoice_number':
                    ['like', '%' + data['guest_data']['invoice_number'] + '%']
                })
            invoice.amended_from = invCount[0]['name']
            invoice.invoice_number = "Amened" + data['guest_data'][
                'invoice_number']
        v = invoice.insert(ignore_permissions=True, ignore_links=True)
        if data['amened'] == 'Yes':
            getInvoiceNUmber = frappe.db.get_value('Invoices', {
                'invoice_number':
                "Amened" + data['guest_data']['invoice_number']
            })
            # print(getInvoiceNUmber)
            updateInvoi = frappe.get_doc('Invoices', getInvoiceNUmber)
            # print(updateInvoi)
            updateInvoi.invoice_number = getInvoiceNUmber
            updateInvoi.save()

            data['invoice_number'] = getInvoiceNUmber
            data['guest_data']['invoice_number'] = getInvoiceNUmber

        return {"success":True,"invoice_number":data['guest_data']['invoice_number'],'items':data['items_data']}
    except Exception as e:
        return {"success":False,"message":str(e)}    

def CheckRatePercentages(data):
    try:
        if data['item_value']>1000 and data['item_value']<=7500:
            gst_percentage = 12
        elif data['item_value'] > 7500:
            gst_percentage = 18
        elif data['item_value'] == 1000:
            gst_percentage = 0
        else:
            gst_percentage = 0
        return {"success":True,"gst_percentage":gst_percentage}
    except Exception as e:
        return {"success":False,"message":str(e)}