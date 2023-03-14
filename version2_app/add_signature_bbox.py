import frappe
import pdfplumber
import sys, traceback


def create_bbox(doc,method=None):
    try:
        if doc.invoice_from in ["Web", "Pms"]:
            folder_path = frappe.utils.get_bench_path()
            company = frappe.get_doc('company', doc.company)
            site_folder_path = company.site_name
            file_path = folder_path+'/sites/'+site_folder_path+doc.invoice_file

            x0,x1,top, bottom = '','','',''

            with pdfplumber.open(file_path) as pdf:
                count = len(pdf.pages)
                for index in range(count):
                    first_page = pdf.pages[index]
                    for word in first_page.extract_words():
                        if word['text'] in ['Signature','signature','SIGNATURE']:
                            print(word)
                            x0 = word['x0']
                            x1 = word['x1']
                            top = word['top']
                            bottom = word['bottom']
            doc.x0 = x0
            doc.x1 = x1
            doc.top = top
            doc.bottom = bottom

            doc.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing manualTax_credit_to_debit","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}