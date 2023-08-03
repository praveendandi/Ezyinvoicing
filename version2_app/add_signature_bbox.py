from PIL import Image, ImageChops
import sys, traceback
import pdfplumber
import fitz

def trim(im, border):
  bg = Image.new(im.mode, im.size, border)
  diff = ImageChops.difference(im, bg)
  bbox = diff.getbbox()
  if bbox:
    return im.crop(bbox)

def create_thumbnail(path, size):
  image = Image.open(path)
  #name, extension = path.split('.')
  options = {}
  if 'transparency' in image.info:
    options['transparency'] = image.info["transparency"]
  
  image.thumbnail((size, size), Image.ANTIALIAS)
  image = trim(image, 255) ## Trim whitespace
  image.save(path, **options)
  return image



def create_bbox():
    try:
        if True:
        
            file_path = '/home/caratred/Desktop/projects/frappe-bench/sites/kochi_marriott/private/files/job-@COKMCDTH442TL8M@000106a2a9.pdf'
            signature_file = '/home/caratred/Desktop/projects/frappe-bench/sites/kochi_marriott/public/files/4000-238702731be4.png'

            create_thumbnail(signature_file,5000)
            x0,x1,top, bottom = '','','',''

            with pdfplumber.open(file_path) as pdf:
                count = len(pdf.pages)
                for index in range(count):
                    first_page = pdf.pages[index]
                    words = first_page.extract_words()
                    for word in words:
                      
                        if word['text'] in ['SIGNATURE','Signature']:
                            
                            x0 = word['x0']
                            x1 = word['x1']
                            top = word['top']
                            bottom = word['bottom']

                document = fitz.open(file_path)
                each_page = document[-1]  # get first page
                # rect = fitz.Rect(x0, top, x1+100, bottom)  # define your rectangle here
                print(x0,top,x1,bottom)
                rect = fitz.Rect(x0+50, top-100, x1+100,bottom+100) # define your rectangle here
                each_page.insertImage(rect, filename=signature_file)
                print(file_path,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                print(file_path.split('.'),"&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                original_name,extension = file_path.split('.pdf')
                document.save('/home/caratred/Documents/signed.pdf')

    except Exception as e:
        print(e)
        return {"success": False, "message": str(e)}
    
create_bbox()