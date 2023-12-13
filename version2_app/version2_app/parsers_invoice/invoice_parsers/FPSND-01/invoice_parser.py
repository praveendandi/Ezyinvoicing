import pdfplumber
from datetime import date
import datetime
import requests
import pandas as pd
import traceback,sys,os
import re
import json
import sys
import frappe
import itertools
from frappe.utils import get_site_name
from version2_app.version2_app.doctype.invoices.invoices import *
from version2_app.version2_app.doctype.payment_types.payment_types import *
from version2_app.version2_app.doctype.invoices.reinitate_invoice import Reinitiate_invoice
from version2_app.version2_app.doctype.invoices.credit_generate_irn import *
from version2_app.version2_app.doctype.invoices.invoice_helpers import update_document_bin
from version2_app.version2_app.doctype.information_folio.information_folio import insert_information_folio
from version2_app.version2_app.doctype.document_bin.document_bin import deletedocument
folder_path = frappe.utils.get_bench_path()

# site_folder_path = "mhkcp_local.com/"
# host = "http://localhost:8000/api/method/"


@frappe.whitelist()
def file_parsing(filepath):
    invoiceNumber = ''
    print_by = ''
    invoice_type_data = ""
    information_folio = "No"
    redg_card = 'No'
    paid_receipt = 'No'
    advance_deposit = 'No'
    payment_receipt = 'No'
    encashment = 'No'
    try:
        start_time = datetime.datetime.utcnow()
        companyCheckResponse = check_company_exist("FPSND-01")
        site_folder_path = companyCheckResponse['data'].site_name
        if "private" in filepath:
            file_path = folder_path+'/sites/'+site_folder_path+filepath
        else:
            file_path = folder_path+'/sites/'+site_folder_path+"/public"+filepath
        today = date.today()
        invoiceDate = today.strftime("%Y-%m-%d")
        content = []
        with pdfplumber.open(file_path) as pdf:
            count = len(pdf.pages)
            for index in range(count):
                first_page = pdf.pages[index]
                content.append(first_page.extract_text())

        raw_data = []
        for i in content:
            for j in i.splitlines():
                raw_data.append(j)

        data = []
        amened = ''
        entered = False
        guestDetailsEntered = False
        guestDeatils = []
        invoiceNumber = ''
        gstNumber = ''
        date_time_obj = ''
        total_invoice_amount = ''
        conf_number = ''
        membership = ''
        print_by = ''
        roomNumber = ""
        reupload = False
        invoice_category = "Tax Invoice"

        for i in raw_data:
            print(i)
            if 'GUEST REGISTRATION FORM' in i:
                redg_card = 'Yes'
                # create_doc(filepath, 'Redg Card')
            if 'PAID OUT' in i:
                paid_receipt = "Yes"
                create_doc(filepath, 'Paidout Receipts')
                break
            if 'ADVANCE DEPOSIT' in i:
                advance_deposit = "Yes"
                create_doc(filepath, 'Advance Deposits')
                break
            if 'PAYMENT RECEIPT' in i:
                payment_receipt = "Yes"
                create_doc(filepath, 'Payment Receipts')
                break
            if 'ENCASHMENT CERTIFICATE' in i:
                encashment = "Yes"
                create_doc(filepath, 'Encashment Certificates')
                break

            if "INFORMATION INVOICE" in i:
                information_folio = "Yes"
            if redg_card == "Yes":
                if "Confirmation No. :" in i:
                    confirmation_number = i.split(":")
                    conf_number = confirmation_number[-1].replace(" ", "")
                    create_doc(filepath, 'Redg Card', conf_number)
                    break
            if "Confirmation No :" in i:
                confirmation_number = i.split(":")
                conf_number = confirmation_number[-1].replace(" ", "")
            if "Total" in i and "IRN" in i:
                total_invoice = i.split(" ")
                total_invoice_amount = float(
                    total_invoice[-2].replace(",", ""))
            # if "Departure :" in i:
            #     depatureDateIndex = i.index('Departure')
            #     date_time_obj = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
            if "Original Bill  :" in i:
                # depatureDateIndex = i.index('Departure')
                # date_time_obj = ':'.join(i[depatureDateIndex:].split(':')[1:])[1:]
                date_time_obj = i.split(':')[-1].strip()
                date_time_obj = datetime.datetime.strptime(date_time_obj, '%d/%m/%y').strftime('%d-%b-%y %H:%M:%S')
            if "Room No. :" in i:
                room = i.split(":")
                roomNumber = room[-1]
                # roomNumber = ''.join(filter(lambda j: j.isdigit(), i))
            if "GST ID" in i:
                gstNumber = i.split(':')[1].replace(' ', '')
                gstNumber = gstNumber.replace("TAXINVOICE", "")
            if "Bill  No. :" in i:
                invoiceNumber = (i.split(':')[-1]).replace(" ", "").replace("-", " ")
            if "Bill To" in i:
                guestDetailsEntered = True
            if "Checkout By:" in i:
                guestDetailsEntered = False
            if guestDetailsEntered == True:
                guestDeatils.append(i)
            # if i in "Date Description Reference Debit Credit" or i in "Date Description Reference c Debit Credit":
            entered = True
            if 'CGST 6%=' in i:
                entered = False
            if 'Billing' in i:
                entered = False
            if 'Total' in i:
                entered = False
            if entered == True:
                data.append(i)
            if "Guest Name" in i:
                guestDeatils.append(i)
            if "Loyalty Number :" in i:
                Membership = i.split(":")
                membership = Membership[-1].replace(" ", "")
            if "Printed By / On :" in i:
                print_by = i.split(":")
                print_by = print_by[1].replace(" ", "")
        # print(information_folio)
        items = []
        itemsort = 0

        if redg_card == 'Yes' or paid_receipt == 'Yes' or advance_deposit == 'Yes' or payment_receipt == 'Yes' or encashment == 'Yes':
            return True

        for i in data:
            pattern = re.compile("^([0-9]{2}\/[0-9]{2}\/[0-9]{2})+")
            check_date = re.findall(pattern, i)
            if len(check_date) > 0:
                item = dict()
                item_value = ""
                dt = i.strip()
                for index, j in enumerate(i.split(' ')):
                    val = dt.split(" ")
                    if index == 0 and len(val) > 1:
                        item['date'] = j

                    if len(val) > 1:
                        item_value = val[-1]
                        item['item_value'] = float(item_value.replace(',', ''))
                    # else:
                    # 	item_value = val[-2]
                    # 	item['item_value'] = float(item_value.replace(',', ''))
                    if index == 1 and len(val) > 1:
                        starting_index = i.index(j)
                        if "~" in i:
                            ending_index = i.find("~")
                            item["name"] = (
                                (i[starting_index:ending_index]).strip()).replace("  ", " ")
                        else:
                            ending_index = i.find(item_value)
                            item["name"] = (
                                (i[starting_index:ending_index]).strip()).replace("  ", " ")
                    if len(val) > 1:
                        if 'SAC' in j:
                            item['sac_code'] = ''.join(
                                filter(lambda j: j.isdigit(), j))
                        else:
                            item['sac_code'] = "No Sac"
                    if len(val) > 1:
                        item['sort_order'] = itemsort+1
                itemsort += 1
                if item != {}:
                    items.append(item)

        total_items = []
        paymentTypes = GetPaymentTypes()
        payment_Types = [''.join(each) for each in paymentTypes['data']]
        for each in items:
            if "CGST" not in each["name"] and "SGST" not in each["name"] and "CESS" not in each["name"] and "VAT" not in each["name"] and "Cess" not in each["name"] and "Vat" not in each["name"] and "IGST" not in each["name"]:
                if each["name"] not in payment_Types:
                    total_items.append(each)

        guest = dict()
        # print(guestDeatils)
        for index, i in enumerate(guestDeatils):
            if index == 0:
                guest['name'] = i.split(':')[1]
            if index == 1:
                guest['address1'] = i
            if index == 2:
                guest['address2'] = i

        guest['invoice_number'] = invoiceNumber.replace(' ', '')

        guest['membership'] = membership
        guest['invoice_date'] = date_time_obj
        guest['items'] = total_items
        guest['invoice_type'] = 'B2B' if gstNumber != '' else 'B2C'
        guest['gstNumber'] = gstNumber
        guest['room_number'] = int(roomNumber) if roomNumber != '' else 0
        guest['company_code'] = "FPSND-01"
        guest['confirmation_number'] = conf_number
        guest['start_time'] = str(start_time)
        guest['print_by'] = print_by
        guest['invoice_category'] = invoice_category
        guest['total_invoice_amount'] = total_invoice_amount

        if information_folio == "Yes":
            print("/a/a/a/a/a/,pppppppppppp")
            # try:
            # 	frappe.db.delete('Document Bin', {'invoice_file': filepath})
            # 	frappe.db.commit()
            # 	print("doneeeeeeeee")
            # except Exception as e:
            # 	print(str(e),"/a/a/a/a///////////////////")
            deletedocumentbin = deletedocument(filepath)
            guest['total_invoice_amount'] = total_invoice_amount
            guest['invoice_file'] = filepath
            taxpayer = {"legal_name": "", "address_1": "", "address_2": "", "email": "",
                        "trade_name": "", "phone_number": "", "location": "", "pincode": "", "state_code": ""}
            if guest['invoice_type'] == 'B2B':
                gspApiDataResponse = gsp_api_data(
                    {"code": guest['company_code'], "mode": companyCheckResponse['data'].mode, "provider": companyCheckResponse['data'].provider})
                if gspApiDataResponse['success'] == True:
                    getTaxPayerDetailsResponse = get_tax_payer_details(
                        {"gstNumber": guest['gstNumber'], "code": guest['company_code'], "invoice": guest['invoice_number'], "apidata": gspApiDataResponse['data']})
                    if frappe.db.exists('Information Folio', conf_number):
                        info_doc = frappe.get_doc('Information Folio', conf_number)
                        info_doc.delete()
                        frappe.db.commit()
                    if getTaxPayerDetailsResponse['success'] == True:
                        information_folio_insert = insert_information_folio(
                            {"guest_data": guest, "company_code": guest['company_code'], "taxpayer": getTaxPayerDetailsResponse['data'].__dict__})
                    else:
                        information_folio_insert = insert_information_folio(
                            {"guest_data": guest, "company_code": guest['company_code'], "taxpayer": taxpayer})
            else:
                if frappe.db.exists('Information Folio', conf_number):
                    info_doc = frappe.get_doc('Information Folio', conf_number)
                    info_doc.delete()
                    frappe.db.commit()
                information_folio_insert = insert_information_folio(
                    {"guest_data": guest, "company_code": guest['company_code'], "taxpayer": taxpayer})

        else:
            check_invoice = check_invoice_exists(guest['invoice_number'])
            if check_invoice['success'] == True:
                inv_data = check_invoice['data']
                # print(inv_data.__dict__)
                if inv_data.docstatus == 2:
                    amened = 'Yes'
                else:
                    invoiceNumber = inv_data.name
                    guest['invoice_number'] = inv_data.name
                    amened = 'No'
                    if inv_data.invoice_type == "B2B":
                        if inv_data.irn_generated == "Pending" or inv_data.irn_generated == "Error":
                            reupload = True
                    else:
                        if inv_data.qr_generated == "Pending" or inv_data.irn_generated == "Error":
                            reupload = True

            company_code = {"code": "FPSND-01"}
            error_data = {"invoice_type": 'B2B' if gstNumber != '' else 'B2C', "invoice_number": invoiceNumber.replace(
                " ", ""), "company_code": "FPSND-01", "invoice_date": date_time_obj}
            error_data['invoice_file'] = filepath
            error_data['guest_name'] = guest['name']
            error_data['gst_number'] = gstNumber
            if guest['invoice_type'] == "B2C":
                error_data['gst_number'] == " "
            error_data['state_code'] = "36"
            error_data['room_number'] = guest['room_number']
            error_data['confirmation_number'] = conf_number
            error_data['pincode'] = "500082"
            error_data['total_invoice_amount'] = total_invoice_amount
            # gstNumber = "12345"
            # print(guest['invoice_number'])

            if len(gstNumber) < 15 and len(gstNumber) > 0:
                error_data['invoice_file'] = filepath
                error_data['error_message'] = "Invalid GstNumber"
                error_data['amened'] = amened

                errorcalulateItemsApiResponse = calulate_items({'items': guest['items'], "invoice_number": guest['invoice_number'],
                                                               "company_code": company_code['code'], "invoice_item_date_format": companyCheckResponse['data'].invoice_item_date_format})
                error_data['items_data'] = errorcalulateItemsApiResponse['data']
                errorInvoice = Error_Insert_invoice(error_data)
                print("Error:  *******The given gst number is not a vaild one**********")
                return {"success": False, "message": "Invalid GstNumber"}

            print(json.dumps(guest, indent=1))
            gspApiDataResponse = gsp_api_data(
                {"code": company_code['code'], "mode": companyCheckResponse['data'].mode, "provider": companyCheckResponse['data'].provider})
            if gspApiDataResponse['success'] == True:
                if guest['invoice_type'] == 'B2B':
                    checkTokenIsValidResponse = check_token_is_valid(
                        {"code": company_code['code'], "mode": companyCheckResponse['data'].mode})
                    if checkTokenIsValidResponse['success'] == True:
                        getTaxPayerDetailsResponse = get_tax_payer_details(
                            {"gstNumber": guest['gstNumber'], "code": company_code['code'], "invoice": guest['invoice_number'], "apidata": gspApiDataResponse['data']})
                        if getTaxPayerDetailsResponse['success'] == True:
                            calulateItemsApiResponse = calulate_items({'items': guest['items'], "invoice_number": guest['invoice_number'], "company_code": company_code[
                                                                      'code'], "invoice_item_date_format": companyCheckResponse['data'].invoice_item_date_format})
                            if calulateItemsApiResponse['success'] == True:
                                guest['invoice_file'] = filepath
                                if reupload == False:
                                    insertInvoiceApiResponse = insert_invoice({"guest_data": guest, "company_code": company_code['code'], "taxpayer": getTaxPayerDetailsResponse[
                                                                              'data'].__dict__, "items_data": calulateItemsApiResponse['data'], "total_invoice_amount": total_invoice_amount, "invoice_number": guest['invoice_number'], "amened": amened})
                                    if insertInvoiceApiResponse['success'] == True:
                                        print("Invoice Created",
                                              insertInvoiceApiResponse)
                                        return {"success": True, "message": "Invoice Created"}

                                    else:
                                        error_data['error_message'] = insertInvoiceApiResponse['message']
                                        error_data['amened'] = amened
                                        error_data["items_data"] = calulateItemsApiResponse['data']
                                        errorInvoice = Error_Insert_invoice(
                                            error_data)
                                        print("insertInvoiceApi fialed:  ",
                                              insertInvoiceApiResponse['message'])
                                        return {"success": False, "message": insertInvoiceApiResponse['message']}
                                else:
                                    insertInvoiceApiResponse = Reinitiate_invoice({"guest_data": guest, "company_code": company_code['code'], "taxpayer": getTaxPayerDetailsResponse[
                                                                                  'data'].__dict__, "items_data": calulateItemsApiResponse['data'], "total_invoice_amount": total_invoice_amount, "invoice_number": guest['invoice_number'], "amened": amened})
                                    if insertInvoiceApiResponse['success'] == True:
                                        print("Invoice Created",
                                              insertInvoiceApiResponse)
                                        return {"success": True, "message": "Invoice Created"}

                                    else:
                                        error_data['error_message'] = insertInvoiceApiResponse['message']
                                        error_data['amened'] = amened
                                        error_data["items_data"] = calulateItemsApiResponse['data']
                                        errorInvoice = Error_Insert_invoice(
                                            error_data)
                                        print("insertInvoiceApi fialed:  ",
                                              insertInvoiceApiResponse['message'])
                                        return {"success": False, "message": insertInvoiceApiResponse['message']}

                            else:

                                error_data['error_message'] = calulateItemsApiResponse['message']
                                error_data['amened'] = amened
                                errorInvoice = Error_Insert_invoice(error_data)
                                print("calulateItemsApi fialed:  ",
                                      calulateItemsApiResponse['message'])
                                return {"success": False, "message": calulateItemsApiResponse['message']}
                        else:
                            # print(error_data)
                            error_data['error_message'] = getTaxPayerDetailsResponse['message']
                            error_data['amened'] = amened
                            errorInvoice = Error_Insert_invoice(error_data)
                            return {"success": False, "message": getTaxPayerDetailsResponse['message']}
                    else:
                        # itsindex = checkTokenIsValidResponse['message']['message'].index("'")
                        error_data['error_message'] = checkTokenIsValidResponse['message']
                        error_data['amened'] = amened
                        errorInvoice = Error_Insert_invoice(error_data)
                        return {"success": False, "message": checkTokenIsValidResponse['message']}
                else:
                    taxpayer = {"legal_name": "", "address_1": "", "address_2": "", "email": "",
                                "trade_name": "", "phone_number": "", "location": "", "pincode": "", "state_code": ""}

                    calulateItemsApiResponse = calulate_items({'items': guest['items'], "invoice_number": guest['invoice_number'],
                                                              "company_code": company_code['code'], "invoice_item_date_format": companyCheckResponse['data'].invoice_item_date_format})
                    if calulateItemsApiResponse['success'] == True:
                        guest['invoice_file'] = filepath
                        if reupload == False:
                            insertInvoiceApiResponse = insert_invoice({"guest_data": guest, "company_code": company_code['code'], "items_data": calulateItemsApiResponse[
                                                                      'data'], "total_invoice_amount": total_invoice_amount, "invoice_number": guest['invoice_number'], "amened": amened, "taxpayer": taxpayer})
                            if insertInvoiceApiResponse['success'] == True:
                                print("B2C Invoice Created",
                                      insertInvoiceApiResponse)
                                return {"success": True, "message": "Invoice Created"}
                            else:

                                error_data['error_message'] = insertInvoiceApiResponse['message']
                                error_data['amened'] = amened
                                errorInvoice = Error_Insert_invoice(error_data)
                                print("B2C insertInvoiceApi fialed:  ",
                                      insertInvoiceApiResponse['message'])
                                return {"success": False, "message": insertInvoiceApiResponse['message']}
                        else:
                            insertInvoiceApiResponse = Reinitiate_invoice({"guest_data": guest, "company_code": company_code['code'], "items_data": calulateItemsApiResponse[
                                                                          'data'], "total_invoice_amount": total_invoice_amount, "invoice_number": guest['invoice_number'], "amened": amened, "taxpayer": taxpayer})
                            if insertInvoiceApiResponse['success'] == True:
                                print("B2C Invoice Created",
                                      insertInvoiceApiResponse)
                                return {"success": True, "message": "Invoice Created"}
                            else:
                                error_data['error_message'] = insertInvoiceApiResponse['message']
                                error_data['amened'] = amened
                                errorInvoice = Error_Insert_invoice(error_data)
                                print("B2C insertInvoiceApi fialed:  ",
                                      insertInvoiceApiResponse['message'])
                                return {"success": False, "message": insertInvoiceApiResponse['message']}

                    else:

                        error_data['error_message'] = calulateItemsApiResponse['message']
                        error_data['amened'] = amened
                        errorInvoice = Error_Insert_invoice(error_data)
                        print("B2C calulateItemsApi fialed:  ",
                              calulateItemsApiResponse['message'])
                        return {"success": False, "message": calulateItemsApiResponse['message']}
            else:
                error_data['error_message'] = gspApiDataResponse['message']
                error_data['amened'] = amened
                errorInvoice = Error_Insert_invoice(error_data)
                print("gspApiData fialed:  ", gspApiDataResponse['message'])
                return {"success": False, "message": gspApiDataResponse['message']}

    except Exception as e:

        print(traceback.print_exc())
        if information_folio == "No":
            update_document_bin(print_by, invoice_type_data,
                                invoiceNumber, str(e), filepath)


def create_doc(file_path, docType, conf_number=""):
    company = frappe.get_doc("company","FPSND-01")
    if docType == 'Redg Card':
        doc = frappe.get_doc({
            'doctype': docType,
            'redg_file': file_path,
            "confirmation_number":conf_number})
        doc.insert()
        if company.direct_print_without_push_to_tab == 1:
            if file_path.count("@-") == 2:
                get_values = {}
                if conf_number != "":
                    if frappe.db.exists("Arrival Information",conf_number):
                        get_values = frappe.db.get_value("Arrival Information",conf_number,["guest_email_address","guest_phone_no"],as_dict=1)
                workstation = re.search('@-(.*)@-', file_path)
                workstation = workstation.group(1)
                if frappe.db.exists({"doctype":"Tablet Config","work_station":workstation,"mode":"Active"}):
                    # tabletconfig = frappe.get_doc({"doctype":"Tablet Config","work_station":workstation,"mode":"Active"})
                    tabletconfig = frappe.db.get_value("Tablet Config",{"work_station":workstation,"mode":"Active"},["work_station","tablet","username","work_station_socket_id","tablet_socket_id","mode","device_name"], as_dict=1)
                    data = {'tablet_config': tabletconfig,'doc_data': doc.__dict__,'uuid':tabletconfig.tablet,"guest_details":get_values}
                    data['uuid'] = tabletconfig.tablet
                    frappe.publish_realtime(
                        "custom_socket", {'message': 'Push To Tab', 'data': data})
                    return {"success":True, "data":data}
    else:
        doc = frappe.get_doc({
            'doctype': docType,
            'file_path': file_path})
        doc.insert()
        if company.direct_print_without_push_to_tab == 1:
            if file_path.count("@-") == 2:
                get_values = {}
                # if conf_number != "":
                #     if frappe.db.exists("Arrival Information",conf_number):
                #         get_values = frappe.db.get_value("Arrival Information",conf_number,["guest_email_address","guest_phone_no"],as_dict=1)
                workstation = re.search('@-(.*)@-', file_path)
                workstation = workstation.group(1)
                if frappe.db.exists({"doctype":"Tablet Config","work_station":workstation,"mode":"Active"}):
                    # tabletconfig = frappe.get_doc({"doctype":"Tablet Config","work_station":workstation,"mode":"Active"})
                    tabletconfig = frappe.db.get_value("Tablet Config",{"work_station":workstation,"mode":"Active"},["work_station","tablet","username","work_station_socket_id","tablet_socket_id","mode","device_name"], as_dict=1)
                    data = {'tablet_config': tabletconfig,'doc_data': doc.__dict__,'uuid':tabletconfig.tablet,"guest_details":{}}
                    data['uuid'] = tabletconfig.tablet
                    frappe.publish_realtime(
                        "custom_socket", {'message': 'Push To Tab', 'data': data})
                    return {"success":True, "data":data}

