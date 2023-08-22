import frappe 
import fitz  # PyMuPDF
from frappe.utils import cstr
import sys
import requests


@frappe.whitelist()
def remove_copy_of_invoice(invoice_number):
    try:
        invoice = frappe.get_doc('Invoices', invoice_number)
        company = frappe.get_doc('company',invoice.company)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = company.site_name
        path = folder_path + '/sites/' + site_folder_path
        filename = invoice.invoice_file
        dst_pdf_text_filename = path + "/private/files/" + 'whitepage.pdf'
        invoice_file_path = path + filename
        if company.name == "NCO-01" or company.name == "NICO-01" :
            pdf_document = fitz.open(invoice_file_path)
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text_instances = page.search_for("COPY OF INVOICE")
            for rect in text_instances:
                x0, y0, x1, y1 = rect
                page.draw_rect(fitz.Rect(x0, y0, x1, y1), fill=(1, 1, 1))
        pdf_document.save(dst_pdf_text_filename)
        pdf_document.close() 
        files = {"file": open(dst_pdf_text_filename, 'rb')}
        payload = {
                'is_private': 1,
                'folder': 'Home',
                'doctype': 'invoices',
                'docname': company.name,
                'fieldname': 'invoice'
                }
        file_response = requests.post(company.host+"api/method/upload_file", files=files,data=payload, verify=False)                            
        response = file_response.json()
        if 'message' in response:
            invoice.invoice_file = response['message']['file_url']
            invoice.save()
        return response['message']['file_url']     
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("remove_copy_of_invoice",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return{"success": False, "message": str(e) }


