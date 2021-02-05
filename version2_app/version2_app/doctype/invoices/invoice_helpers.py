from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_site_name
import time
import os
import datetime



def TotalMismatchError(data,calculated_data):
    try:
        invType = data['guest_data']['invoice_type']
        irn_generated = "Error"   
        companyDetails = frappe.get_doc("company",data['company_code'])
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
                'total_inovice_amount':data['total_invoice_amount'],
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
                "place_of_supply":companyDetails.state_code
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
        

def CheckRatePercentages(data, sez, placeofsupply, exempted, state_code):
    try:
        if data['item_value']>1000 and data['item_value']<=7500:
            gst_percentage = 12
        elif data['item_value'] > 7500:
            gst_percentage = 18
        elif data['item_value'] == 1000:
            gst_percentage = 0
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
        return {"success":False,"message":str(e)}



def error_invoice_calculation(data,data1):
    # print(data1)
    company = frappe.get_doc('company',data['company_code'])
    invType = data1['invoice_type']
    # if invType == "B2B":
    irn_generated = "Error"
    # qr_generated = "Pending"


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
        data1['error_message']
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
    # print(data['items_data'])
    # if data['guest_data']['invoice_type'] == "B2B":
    #     irn_generated = "Pending"
    # else:
    #     irn_generated = "NA"
    # if "legal_name" not in data['taxpayer']:
    #     data['taxpayer']['legal_name'] = " "
    #calculat items
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

    doc = frappe.get_doc('Invoices',data['invoice_number'])
    doc.total_invoice_amount = data['total_invoice_amount']	
    # doc.invoice_number=data['guest_data']['invoice_number']
    # doc.guest_name=data['guest_data']['name']
    # doc.gst_number=data['guest_data']['gstNumber']
    # doc.invoice_category=data['guest_data']['invoice_category']
    # doc.invoice_file=data['guest_data']['invoice_file']
    # doc.room_number=data['guest_data']['room_number']
    # doc.invoice_type=data['guest_data']['invoice_type']
    # doc.invoice_date=datetime.datetime.strptime(data['guest_data']['invoice_date'],'%d-%b-%y %H:%M:%S')
    # doc.legal_name=data['taxpayer']['legal_name']
    # doc.address_1=data['taxpayer']['address_1']
    # doc.email=data['taxpayer']['email']
    # doc.confirmation_number = data['guest_data']['confirmation_number']
    # doc.trade_name=data['taxpayer']['trade_name']
    # doc.address_2=data['taxpayer']['address_2']
    # doc.phone_number=data['taxpayer']['phone_number']
    doc.mode = company.mode
    # doc.location=data['taxpayer']['location']
    # doc.pincode=data['taxpayer']['pincode']
    # state_code=data['taxpayer']['state_code']
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
    doc.save(ignore_permissions=True, ignore_version=True)
    return True
