from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz
import frappe
import requests
import os
import random
from version2_app.version2_app.doctype.invoices.invoices import create_qr_image, gsp_api_data
from version2_app.version2_app.doctype.invoices.credit_generate_irn import create_credit_qr_image

@frappe.whitelist(allow_guest=True)
def AttachQrCodeInInvoice(invoice_number):
    try:
        invoice = frappe.get_doc('Invoices', invoice_number)
        company = frappe.get_doc('company',invoice.company)
        if invoice.invoice_type == "B2B":
            folder_path = frappe.utils.get_bench_path()
            if invoice.qr_code_image == "":
                companyData = {"code":company.name,"mode":company.mode,"provider":company.provider}
                GSP_details = gsp_api_data(companyData)
                gsp=GSP_details['data']
                create = create_qr_image(invoice_number,GSP_details['data'])
                return {"message":"Qr Redo Succesfull","success":True}
            
            site_folder_path = company.site_name
            print("/aaaaaaaaaaaaaaa")
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
            if response['message']['file_url']:
                invoice.invoice_with_gst_details = response['message']['file_url']
                invoice.save()
                if invoice.has_credit_items=="Yes":
                    if invoice.qr_code_image == "":
                        companyData = {"code":company.name,"mode":company.mode,"provider":company.provider}
                        GSP_details = gsp_api_data(companyData)
                        gsp=GSP_details['data']
                        create = create_credit_qr_image(invoice_number,GSP_details['data'])
                        return {"message":"Qr Redo Succesfull","success":True}
                    site_folder_path = company.site_name
                    path = folder_path + '/sites/' + site_folder_path
                    src_pdf_filename = path + invoice.invoice_file
                    dst_pdf_filename = path + "/private/files/" + invoice_number + 'withcreditQr.pdf'
                    # attaching qr code
                    img_filename = path + invoice.credit_qr_code_image
                    # img_rect = fitz.Rect(250, 200, 340, 270)
                    img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
                                        company.qr_rect_y0, company.qr_rect_y1)
                    document = fitz.open(src_pdf_filename)

                    page = document[0]

                    page.insertImage(img_rect, filename=img_filename)
                    document.save(dst_pdf_filename)
                    document.close()
                    # attacing irn an ack
                    dst_pdf_text_filename = path + "/private/files/" + invoice_number + 'withCreditQrIrn.pdf'
                    doc = fitz.open(dst_pdf_filename)
                    
                    if company.irn_details_page == "First":
                        page = doc[0]
                    else:
                        page = doc[-1]
                    # page = doc[0]
                    # where = fitz.Point(15, 55)
                    where = fitz.Point(company.irn_text_point1, company.irn_text_point2)
                    ackdate = invoice.credit_ack_date
                    credit_ack_date = ackdate.split(" ")
                    text = "IRN: " + invoice.credit_irn_number +"          "+ "ACK NO: " + invoice.credit_ack_no + "       " + "ACK DATE: " + credit_ack_date[0]
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
                    if response['message']['file_url']:
                        
                        invoice.invoice_with_gst_details = response['message']['file_url']
                        invoice.save()
                        return {"message":"Qr Redo Succesfull","success":True}
                    return{"message":response['message'],"success":False}    
                return {"message":"Qr Redo Succesfull","success":True}
            return{"message":response['message'],"success":False}    
        else:
            folder_path = frappe.utils.get_bench_path()
            path = folder_path + '/sites/' + company.site_name
            attach_qrpath = path + "/private/files/" + invoice_number + "attachb2cqr.pdf"
            src_pdf_filename = path + invoice.invoice_file
            img_filename = path + invoice.b2c_qrimage
            img_rect = fitz.Rect(company.qr_rect_x0, company.qr_rect_x1,
                                company.qr_rect_y0, company.qr_rect_y1)
            document = fitz.open(src_pdf_filename)
            page = document[0]
            page.insertImage(img_rect, filename=img_filename)
            document.save(attach_qrpath)
            document.close()
            
            files_new = {"file": open(attach_qrpath, 'rb')}
            payload_new = {
                "is_private": 1,
                "folder": "Home",
                "doctype": "Invoices",
                "docname": invoice_number,
                'fieldname': 'b2c_qrinvoice'
            }
            site = company.host
            upload_qrinvoice_image = requests.post(site + "api/method/upload_file",
                                                files=files_new,
                                                data=payload_new)
            attach_response = upload_qrinvoice_image.json()
            if attach_response['message']['file_url']:
                invoice.b2c_qrinvoice = attach_response['message']['file_url']
                invoice.name = invoice_number
                invoice.qr_generated = "Success"
                invoice.qr_code_generated = "Success"
                invoice.save(ignore_permissions=True, ignore_version=True)
                if os.path.exists(attach_qrpath):
                    os.remove(attach_qrpath)
                return {"success": True, "message": "Qr Attached successfully"}
            return {"success":False,"message":attach_response['message']}
    except Exception as e:
        print(str(e),"      Api attach qr code")
        return {"success":False,"message":str(e)}            
