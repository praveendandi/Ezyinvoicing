import frappe
import pdfplumber
import sys, traceback
import pdfplumber
import fitz


def create_bbox(doc,method=None):
    try:
        if doc.invoice_from in ["Web", "Pms"] and doc.signature_file is not None and doc.signature_file != '':
            folder_path = frappe.utils.get_bench_path()
            company = frappe.get_doc('company', doc.company)
            site_folder_path = company.site_name
            file_path = folder_path+'/sites/'+site_folder_path+doc.invoice_file
            signature_file = folder_path+'/sites/'+site_folder_path+doc.signature_file
            x0,x1,top, bottom = '','','',''

            with pdfplumber.open(file_path) as pdf:
                count = len(pdf.pages)
                for index in range(count):
                    first_page = pdf.pages[index]
                    words = first_page.extract_words()
                    for word in words:
                        if word['text'] in ['SIGNATURE']:
                            x0 = word['x0']
                            x1 = word['x1']
                            top = word['top']
                            bottom = word['bottom']
                            document = fitz.open(file_path)
                            page = document[index]  # get first page
                            rect = fitz.Rect(x0+50, top+50, top, bottom)  # define your rectangle here
                            image_file = signature_file, 'rb'
                            page.InsertImage(rect, filename=image_file)
                            # page.draw_rect(rect,  color = (0, 1, 0), width = 2)
                            document.save(file_path)
                            
            # doc.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_bbox","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}
    






# import fitz

# doc = fitz.open(file_path)
# page = doc[0]  # get first page
# rect = fitz.Rect(x0+50, top+50, top, bottom)  # define your rectangle here
# text = page.get_textbox(rect)  # get text from rectangle
# clean_text = ' '.join(text.split())
# page.draw_rect(rect,  color = (0, 1, 0), width = 2)
# doc.save('./name.pdf')

# # page.draw_rect(rect, color=[0,1,1,0], overlay=False,width=0.5,fill_opacity=1,fill=fill_color)


# print(clean_text)