from PyPDF2 import PdfFileWriter, PdfFileReader
import frappe
import requests
import os
import random
from version2_app.version2_app.doctype.invoices.invoices import create_qr_image, gsp_api_data,send_invoicedata_to_gcb
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
            attachb2cqr = send_invoicedata_to_gcb(invoice_number)
            return attachb2cqr
    except Exception as e:
        print(str(e),"      Api attach qr code")
        return {"success":False,"message":str(e)}            
