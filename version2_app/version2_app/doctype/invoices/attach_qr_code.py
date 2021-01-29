from PyPDF2 import PdfFileWriter, PdfFileReader
# import fitz
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
            if invoice.qr_code_image == None:
                companyData = {"code":company.name,"mode":company.mode,"provider":company.provider}
                GSP_details = gsp_api_data(companyData)
                gsp=GSP_details['data']
                create = create_qr_image(invoice_number,GSP_details['data'])
                if invoice.has_credit_items == "Yes":
                    if invoice.credit_qr_code_image == None: 
                        create_create = create_credit_qr_image(invoice_number,GSP_details['data'])   
                        return {"message":"Qr Redo Succesfull","success":True}
                return {"message":"Qr Redo Succesfull","success":True}    
            return {"message":"Qr Redo Failed","success":True}
                
            
              
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
                invoice.irn_generated = "Success"
                invoice.qr_code_generated = "Success"
                invoice.save(ignore_permissions=True, ignore_version=True)
                if os.path.exists(attach_qrpath):
                    os.remove(attach_qrpath)
                return {"success": True, "message": "Qr Attached successfully"}
            return {"success":False,"message":attach_response['message']}
    except Exception as e:
        print(str(e),"      Api attach qr code")
        return {"success":False,"message":str(e)}            
