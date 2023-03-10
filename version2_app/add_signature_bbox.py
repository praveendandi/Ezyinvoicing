import frappe
import pdfplumber


def create_bbox(doc,method=None):
    folder_path = frappe.utils.get_bench_path()
    company = frappe.get_doc('company', doc.company)
    site_folder_path = company.site_name
    file_path = folder_path+'/sites/'+site_folder_path+doc.invoice_file

    print(file_path)
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

