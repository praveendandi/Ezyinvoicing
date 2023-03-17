# import frappe
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
                            rect = fitz.Rect(x0, top, x1+100, bottom)  # define your rectangle here
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


import numpy as np

def remove_background(image, bg_color=255):
    # assumes rgb image (w, h, c)
    intensity_img = np.mean(image, axis=2)

    # identify indices of non-background rows and columns, then look for min/max indices
    non_bg_rows = np.nonzero(np.mean(intensity_img, axis=1) != bg_color)
    non_bg_cols = np.nonzero(np.mean(intensity_img, axis=0) != bg_color)
    r1, r2 = np.min(non_bg_rows), np.max(non_bg_rows)
    c1, c2 = np.min(non_bg_cols), np.max(non_bg_cols)

    # return cropped image
    return image[r1:r2+1, c1:c2+1, :]



from PIL import Image, ImageChops

def trim(im, border):
  bg = Image.new(im.mode, im.size, border)
  diff = ImageChops.difference(im, bg)
  bbox = diff.getbbox()
  if bbox:
    return im.crop(bbox)

def create_thumbnail(path, size):
  image = Image.open(path)
  name, extension = path.split('.')
  options = {}
  if 'transparency' in image.info:
    options['transparency'] = image.info["transparency"]
  
  image.thumbnail((size, size), Image.ANTIALIAS)
  image = trim(image, 255) ## Trim whitespace
  image.save(name + '_new.' + extension, **options)
  return image

# path = '/home/caratred/Desktop/projects/frappe-bench/sites/kochi_marriott/public/files/4000-2387022d5d5a.png'
# create_thumbnail(path,300)