from PyPDF2 import PdfFileWriter, PdfFileReader
import frappe
import requests
import os,sys,traceback
import random
from version2_app.version2_app.doctype.invoices.invoices import create_qr_image, gsp_api_data,send_invoicedata_to_gcb
from version2_app.version2_app.doctype.invoices.credit_generate_irn import create_credit_qr_image
from version2_app.version2_app.doctype.ey_intigration.redo_qr import create_ey_qr_code

@frappe.whitelist()
def AttachQrCodeInInvoice(invoice_number):
    try:
        invoice = frappe.get_doc('Invoices', invoice_number)
        company = frappe.get_doc('company',invoice.company)
        
        if invoice.invoice_type == "B2B":
            folder_path = frappe.utils.get_bench_path()
            # print(folder_path,":::::::::::::::::")
            if invoice.qr_code_image == None:
                companyData = {"code":company.name,"mode":company.mode,"provider":company.provider}
                GSP_details = gsp_api_data(companyData)
                gsp=GSP_details['data']
                create = create_qr_image(invoice_number,GSP_details['data'])
                if invoice.has_credit_items == "Yes":
                    if invoice.credit_qr_code_image == None: 
                        credit_create = create_credit_qr_image(invoice_number,GSP_details['data']) 
                        if credit_create['success'] ==True:
                            return {"message":credit_create['message'],"success":True}
                        else:
                            return {"message":credit_create['message'],"success":False} 
                    else:
                        qr_code= create_ey_qr_code(invoice_number)   
                        return {"message":"Qr Generated Successfully","success":True} 
                        # if create['success'] == True:         
                        #     return {"message":create['message'],"success":True}
                        # else:
                        #     return {"message":create['message'],"success":False}
            else:
                qr_code= create_ey_qr_code(invoice_number)   
                return {"message":"Qr Generated Successfully","success":True} 
              
        else:
            attachb2cqr = send_invoicedata_to_gcb(invoice_number)
            return attachb2cqr
    except Exception as e:
        print(str(e),"      Api attach qr code")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing AttachQrCodeInInvoice","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}            
