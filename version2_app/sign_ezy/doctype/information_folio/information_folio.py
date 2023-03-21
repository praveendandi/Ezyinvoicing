# -*- coding: utf-8 -*-
# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe,os
import datetime
import json
import requests,base64,traceback,sys
from frappe.utils import cstr, get_site_name, logger, random_string


class InformationFolio(Document):
	pass


@frappe.whitelist()
def insert_information_folio(data):
    items_data = json.dumps({"data": data['guest_data']['items']})
    company = frappe.get_doc('company', data['company_code'])
    check_inf_folio = frappe.get_list('Information Folio', filters={
                                      'name': data['guest_data']['confirmation_number']})
    if len(check_inf_folio) == 0:
        inf_folio = frappe.get_doc({
            'doctype':
                'Information Folio',
                'guest_name':
                data['guest_data']['name'],
                'invoice_from': "Pms",
                'gst_number':
                data['guest_data']['gstNumber'],
                'invoice_file':
                data['guest_data']['invoice_file'],
                'room_number':
                data['guest_data']['room_number'],
                'confirmation_number':
                data['guest_data']['confirmation_number'],
                'invoice_type':
                data['guest_data']['invoice_type'],
                'invoice_category': data['guest_data']['invoice_category'],
                'print_by': data['guest_data']['print_by'],
                'invoice_date':
                datetime.datetime.strptime(data['guest_data']['invoice_date'],
                                           '%d-%b-%y %H:%M:%S'),
                'legal_name':
                data['taxpayer']['legal_name'],
                'mode': company.mode,
                'address_1':
                data['taxpayer']['address_1'],
                'email':
                data['taxpayer']['email'],
                'trade_name':
                data['taxpayer']['trade_name'],
                'address_2':
                data['taxpayer']['address_2'],
                'phone_number':
                data['taxpayer']['phone_number'],
                'location':
                data['taxpayer']['location'],
                'pincode':
                data['taxpayer']['pincode'],
                'state_code':
                data['taxpayer']['state_code'],
                'company':
                data['company_code'],
                'total_invoice_amount': data['guest_data']['total_invoice_amount'],
                'invoice_process_time':
                datetime.datetime.utcnow() - datetime.datetime.strptime(
                    data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f"),
                "mode": company.mode,
                "place_of_supply": company.state_code,
                "items": items_data
        })
        inf_folio.save()
        return {"success": True}
    else:
        updateinf_folio = frappe.get_doc(
            'Information Folio', check_inf_folio[0])
        updateinf_folio.items = items_data
        updateinf_folio.guest_name = data['guest_data']['name']
        updateinf_folio.invoice_from = "Pms"
        updateinf_folio.gst_number = data['guest_data']['gstNumber']
        updateinf_folio.invoice_file = data['guest_data']['invoice_file']
        updateinf_folio.room_number = data['guest_data']['room_number']
        updateinf_folio.confirmation_number = data['guest_data']['confirmation_number']
        updateinf_folio.invoice_type = data['guest_data']['invoice_type']
        updateinf_folio.invoice_category = data['guest_data']['invoice_category']
        updateinf_folio.print_by = data['guest_data']['print_by']
        updateinf_folio.invoice_date = datetime.datetime.strptime(
            data['guest_data']['invoice_date'], '%d-%b-%y %H:%M:%S')
        updateinf_folio.legal_name = data['taxpayer']['legal_name']
        updateinf_folio.mode = company.mode
        updateinf_folio.address_1 = data['taxpayer']['address_1']
        updateinf_folio.email = data['taxpayer']['email']
        updateinf_folio.trade_name = data['taxpayer']['trade_name']
        updateinf_folio.address_2 = data['taxpayer']['address_2']
        updateinf_folio.phone_number = data['taxpayer']['phone_number']
        updateinf_folio.location = data['taxpayer']['location']
        updateinf_folio.pincode = data['taxpayer']['pincode']
        updateinf_folio.state_code = data['taxpayer']['state_code']
        updateinf_folio.company = data['company_code']
        updateinf_folio.total_invoice_amount = data['guest_data']['total_invoice_amount']
        updateinf_folio.invoice_process_time = datetime.datetime.utcnow(
        ) - datetime.datetime.strptime(data['guest_data']['start_time'], "%Y-%m-%d %H:%M:%S.%f")
        updateinf_folio.mode = company.mode
        updateinf_folio.place_of_supply = company.state_code
        updateinf_folio.save()
        return {"success": True}


@frappe.whitelist(allow_guest=True)
def update_signature(name=None, signature=None, agree=0, work_station=None, tab=None, doctype=None):
    # print(name,signature,agree,work_station,tab,doctype)
    
    if len(signature)>10:
        cwd = os.getcwd()
        company = frappe.get_last_doc("company")
        site_name = cstr(frappe.local.site)
        site_folder_path = f'{cwd}/{site_name}'
        
        signature_file_url = convert_base64_to_image(signature,name,site_folder_path,company)
        # /home/caratred/Desktop/projects/frappe-bench/sites/kochi_marriott/public/files
        print(signature_file_url['message']['file_url'],"******************************8")
        # folder_path = frappe.utils.get_bench_path()
        # site_folder_path = company.site_name
        # file = site_folder_path + "/private/files/" + name + ".png"
        signature_file =site_folder_path+'/public'+signature_file_url['message']['file_url']
        # path = '/home/caratred/Desktop/projects/frappe-bench/sites/kochi_marriott/public/files/4000-2387022d5d5a.png'
        create_thumbnail(signature_file,2000)
        
        if signature_file_url != False:                                
            invoice_doc = frappe.db.set_value('Invoices', name,
                                    {'signature':signature,"agree":agree,"signature_file":signature_file_url['message']['file_url']})
            
    else:
        doc = frappe.db.set_value(doctype, name,
                              {'signature':signature,"agree":agree})
    create_bbox(name)
    # if company.name == 'NHA-01' and company.name == 'KMH-01':
    #     create_bbox(name)
    # else:
    #     create_bbox(name)
    frappe.db.commit()
    data = {
        'name': name,
        'signature': signature,
        'work_station': work_station,
        'agree': agree,
        'tab': tab
    }
    frappe.publish_realtime(
        "custom_socket", {'message': 'Signature Updated', 'data': data})
    frappe.publish_realtime(
        "custom_socket", {'message': doctype+' Signature Updated', 'data': data})
    

    

    return True



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
  image.save(path, **options)
  return image




import frappe
import pdfplumber
import sys, traceback
import pdfplumber
import fitz
def create_bbox(name):
    try:
        # print("HITTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        doc = frappe.get_doc('Invoices',name)
        if doc.invoice_from in ["Web", "Pms"] and doc.signature_file is not None and doc.signature_file != '':
            folder_path = frappe.utils.get_bench_path()
            company = frappe.get_doc('company', doc.company)
            site_folder_path = company.site_name
            file_path = folder_path+'/sites/'+site_folder_path+doc.invoice_file
            # print(doc.invoice_file)
            # signature_file = folder_path+'/sites/'+site_folder_path+doc.signature_file
            signature_file =folder_path+'/sites/'+site_folder_path+'/public'+doc.signature_file

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
                rect = fitz.Rect(x0, top, x1+100, bottom)  # define your rectangle here
                # image_file = signature_file, 'rb'
                each_page.insertImage(rect, filename=signature_file)
                # page.draw_rect(rect,  color = (0, 1, 0), width = 2)
                original_name,extension = file_path.split('.')
                document.save(original_name+'signed.pdf')
                files = {"file": open(original_name+'signed.pdf', "rb")}
                payload = {
                        "is_private": 1,
                        "folder": "Home",
                        "doctype": "Invoices",
                        "fieldname": "name",
                        "docname":name
                }
                site = company.host
                upload_qr_image = requests.post(
                        site + "api/method/upload_file", files=files, data=payload
                )
                response = upload_qr_image.json()
                print(response)
                
                # original_name,extension = doc.invoice_file.split("/")[-1].split('.pdf')


                doc = frappe.get_doc('Invoices',name)
                doc.invoice_file = response['message']['file_url']
                # print(f'/private/files/{original_name}signed.pdf',"55555555555555555555555555555555555555555")
                doc.save()
                frappe.db.commit()
                # print("HITTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
                os.remove(file_path)

                # document.save(file_path,incremental=True)
                            
            # doc.save()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_bbox","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


def convert_base64_to_image(base, name, site_folder_path, company):
    try:
        # print(base.split('data:image/png;base64,')[1])
        file = site_folder_path + "/private/files/" + name + ".png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base.split('data:image/png;base64,')[1]))
        files = {"file": open(file, "rb")}
        payload = {
            "is_private": 0,
            "folder": "Home"
            # "doctype": "Precheckins",
        }
        site = company.host
        upload_qr_image = requests.post(
            site + "api/method/upload_file", files=files, data=payload
        )
        response = upload_qr_image.json()
        if "message" in response:
            return response
        else:
            return False
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "Scan-Guest Details Opera",
            "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()),
        )
        return {"success": False, "message": str(e)}
