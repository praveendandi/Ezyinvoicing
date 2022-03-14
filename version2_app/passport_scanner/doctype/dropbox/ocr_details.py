import frappe
import time
import base64
import requests
import sys
import sys, traceback, datetime
import re
from collections import defaultdict, OrderedDict
from difflib import get_close_matches
from datetime import date, datetime


def scan_aadhar(data:dict):
    '''
    send aadhar to vision api for details
    :param front_base_image: front image base 64
    :param back_base_image: front image base 64
    :param dropbox: dropbox
    :param company: company
    '''
    try:
        if data['front_base_image'] != '':
            
            #  data = {
            #             "front_base_image":front,
            #             "back_base_image":back,
            #             "dropbox":new_dropbox,
            #             "company":company
            aadhar_front_text = aadhar_detect_text(data['front_base_image'], 'front')
            print(aadhar_front_text,"hell")
            if aadhar_front_text["success"] != False:
                print(aadhar_front_text)
                # if os.path.isfile(face) is True:
                #     with open(face, 'rb') as image:
                #         image_string = base64.b64encode(image.read()).decode()
                #     faceimage_size = ('{:,.0f}'.format(
                #         os.path.getsize(face)/float(1 << 10))+" KB")
                #     os.remove(face)
                #     details['face'] = image_string
                #     details['doc_type'] = 'front'
                # if 'error' in details.keys():
                #     if len(details.keys()) == 1:
                #         details['success'] = False
                #         return details
                #     elif len(aadhar_front_text.keys()) > 1:
                #         return ({"success": True, "aadhar_details": details})
                # elif 'error' not in details.keys():
                #     return ({"success": True, "aadhar_details": details})

                # return {"success": False,"error": aadhar_text["message"],"aadhar_details":{"base64_string": cropped_aadhar},"message":"Unable to scan Aadhar"}
        if data['back_base_image'] != '':
            aadhar_back_text = aadhar_detect_text(data['back_base_image'], 'back')
            if aadhar_back_text["success"] != False:
                print(aadhar_back_text,"hello")




        # base = frappe.local.form_dict.get("aadhar_image")
        # doc_type = frappe.local.form_dict.get("scanView")
        # company = frappe.get_last_doc('company')
        # api_time = time.time()
        # # base = data['aadhar_image']
        # # doc_type = data['scanView']
        # imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # # I assume you have a way of picking unique filenames
        # filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        # with open(filename, 'wb') as f:
        #     f.write(imgdata)
        # details = ''
        # croppedaadhar = image_processing(filename)
        # if croppedaadhar["success"] == False:
        #     return {"success": False,"error": croppedaadhar["message"],"message":"Unable to scan Aadhar"}
        # cropped_aadhar = croppedaadhar["data"]
        # aadhar_text = aadhar_detect_text(base, doc_type)
        # if aadhar_text["success"] == False:
        #     return {"success": False,"error": aadhar_text["message"],"aadhar_details":{"base64_string": cropped_aadhar},"message":"Unable to scan Aadhar"}
        # details = aadhar_text["data"]
        # details['base64_string'] = cropped_aadhar
        # image_string = ' '
        # rand_int = str(datetime.now())
        # face_detect = detect_faces(filename, rand_int)
        # if face_detect["success"] == False:
        #     return {"success": False,"error": face_detect["message"],"aadhar_details":{"base64_string": cropped_aadhar},"message":"Unable to scan Aadhar"}
        # face = face_detect["data"]
        # os.remove(filename)
        # if doc_type == 'front':
        #     if os.path.isfile(face) is True:
        #         with open(face, 'rb') as image:
        #             image_string = base64.b64encode(image.read()).decode()
        #         faceimage_size = ('{:,.0f}'.format(
        #             os.path.getsize(face)/float(1 << 10))+" KB")
        #         os.remove(face)
        #         details['face'] = image_string
        #         details['doc_type'] = 'front'
        #     if 'error' in details.keys():
        #         if len(details.keys()) == 1:
        #             details['success'] = False
        #             return details
        #         elif len(details.keys()) > 1:
        #             return ({"success": True, "aadhar_details": details})
        #     elif 'error' not in details.keys():
        #         return ({"success": True, "aadhar_details": details})
        # elif doc_type == 'back':
        #     if 'error' in details.keys():
        #         details['success'] = False
        #         return details
        #     elif 'error' not in details.keys():
        #         details['doc_type'] = 'back'
        #         return ({"success": True, "aadhar_details": details})

    except IndexError as e:
        print(e)
        # company = frappe.get_last_doc('company')
        # api_time =time.time()
        # base = frappe.local.form_dict.get("aadhar_image")
        # doc_type = frappe.local.form_dict.get("scanView")
        # imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # # I assume you have a way of picking unique filenames
        # filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        # with open(filename, 'wb') as f:
        #     f.write(imgdata)

        # details = {"base64_string": cropped_aadhar}
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # frappe.log_error("SignEzy scan_aadhar","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return ({"error": str(e), "success": False, "aadhar_details": "details","message":"Unable to scan Aadhar"})
    except Exception as e:
        print(e)
        # company = frappe.get_last_doc('company')
        # base = frappe.local.form_dict.get("aadhar_image")
        # doc_type = frappe.local.form_dict.get("scanView")
        # imgdata = base64.b64decode(base)
        # rand_no = str(datetime.now())
        # # I assume you have a way of picking unique filenames
        # filename = basedir + company.site_name + "/private/files/aadhardoc.jpeg"
        # with open(filename, 'wb') as f:
        #     f.write(imgdata)

        # croppedaadhar = image_processing(filename)
        # if croppedaadhar["success"] == False:
        #     return {"success": False,"error": croppedaadhar["message"],"message":"Unable to scan Aadhar"}
        # cropped_aadhar = croppedaadhar["data"]
        # details = {"base64_string": cropped_aadhar}
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # frappe.log_error("SignEzy scan_aadhar","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return ({"error": str(e), "success": False, "aadhar_details": "details","message":"Unable to scan Aadhar"})


def aadhar_detect_text(image_file, doc_type):
    try:
        remove = ['GOVERNMENT OF INDIA', 'Government of India', 'Year of Birth',
                  '/ Male', 'GOVERNMENT OF IND', 'Nent of India', 'GOVERMENTER']
        unlike = ['UNIQUE IDENTIFICATION AUTHORITY', 'OF INDIA', 'Identification', 'Bengaluru-560001', '-500001', '500001', 'Bengaluru-580001', '560001', ' WWW', 'WWW', '-560001', '-560101', '560101', 'uidai', 'Aam Admi ka', 'VvV', 'he', 'uldai', 'uldal', 'govin', 'www', 'A Unique Identification', 'Www', 'in', 'gov', 'of India', 'uidai', 'INDIA', 'India', 'www', 'I', '1B 1ST', 'MERI PEHACHAN', '1E 1B', 'MERA AADHAAR',
                  'Unique Identification Authority', 'of India', 'UNQUE IDENTIFICATION AUTHORITY', '1800 180 1947', '1800180 1947', 'Admi ka Adhikar', 'w', 'ww', 'S', 's', '1800 180 17', 'WWW', 'dai', 'uidai', 'Address', '1809 180 1947', 'help', 'AADHAAR', '160 160 1947', 'Aadhaar', '180 18167', 'Aadhaar-Aam Admi ka Adhikar', 'gov in', '1947', 'MERA AADHAAR MERI PEHACHAN', '38059606 3964', '8587 1936 9174', 'Unique Identification Authority of India']
        req_start = time.time()
        text_data = text_getter(image_file)
        if text_data["success"] == False:
            return {"success": False, "message": text_data["message"]}
        text = text_data["data"]
        block = str(text).split('\n')
        if doc_type == 'front':
            abc = [str(x) for x in block]
            dob_in = re.compile(
                '[0-9]{4}|[0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4}')
            date = dob_in.findall(text)
            date_of_birth = date[0]
            for y in date:
                find_date = re.search(
                    r'([0-9]{2}\/[0-9]{2}\/[0-9]{4}|[0-9]{2}\-[0-9]{2}\-[0-9]{4})', y)
                if find_date:
                    date_of_birth = y
            gender_list = ['MALE', 'FEMALE', 'Male', 'Female']
            gender = ''
            for x in block:
                for y in gender_list:
                    if y in x:
                        gender = y
            da_find = re.compile(
                '([0-9]{2,4} [0-9]{2,4} [0-9]{2,4}|[0-9]+ [0-9]+|[0-9]{12})')
            number = da_find.findall(text)
            number = [x for x in number if len(x) > 6]
            uid = number[0]
            for x in number:
                find_uid = re.search(r'([0-9]+ [0-9]+ [0-9]+)', x)
                if find_uid:
                    uid = x
            uid_number = re.sub(' ', '', uid)
            if len(uid_number) != 12:
                uid = ''
            if date_of_birth in uid:
                date_of_birth = ''
            na_find = re.compile(
                '([a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+ [a-zA-Z]+|[a-zA-Z]+)')
            noun = na_find.findall(text)
            noun = [x for x in noun if x not in remove if 'GOVERNMENT' not in x if 'Government' not in x if 'Govern' not in x if 'GOVERN' not in x if 'Gove' not in x if 'GOVE' not in x if 'ERNMENT' not in x if 'ernment' not in x]
            person_details = {"Date_of_birth": date_of_birth,
                             "sex": gender, "uid": uid, "name": noun[0]}
            return {"success": True,"data": person_details}
        elif doc_type == 'back':

            final_address = []
            for x in block:
                if 'Address' in x:
                    abc = block.index(x)
            
            if 'abc' in locals():
                address = block[abc:]
            else:
                address = block
            regex = re.compile('([^a-zA-Z0-9-,./ ]|Address|govin|ligovin|help|No|www|o  |uidai)')
            cannot = ([regex.sub('', i) for i in address])
            cannot = [x for x in cannot if x not in unlike]
            unique_list = list(OrderedDict((element, None)
                                           for element in cannot))
            for x in unique_list:
                abc = x.lstrip('  ')
                abc = x.lstrip(' -')
                abc = x.lstrip(' ')
                final_address.append(abc)                    
            ind = [final_address.index(x) for x in final_address if re.search('([0-9]{6})', x)]
            final_address = final_address[:ind[len(ind)-1]+1]
            abc = ' '.join(x for x in final_address)
            final = abc.split()
            final_address = list(OrderedDict((element, None)
                                             for element in final))
            person_address = ' '.join(x for x in final_address)
            pin_code = re.findall('([0-9]{6})', person_address)
            [final_address.remove(x) for x in final_address if re.search('([0-9]{6})', x)]
            final_address.append(pin_code[0])
            person_address = ' '.join(x for x in final_address)
            pin_get = re.findall('[0-9]{6}', person_address)
            postal_code = ''
            state = ''
            address1 = ""  
            address2 = ""
            person_address = person_address.replace("W|O","").replace("W/O","").replace("w/o","").replace("w|o","").replace("D/O","").replace("d/o","").replace("d|o","").replace("D|O","").replace("d/o","").replace("s/o","").replace("s/o","").replace("S/O","").replace("s/o","").replace("S|O","").replace("s/o","").replace("s|o","")
            split_address = person_address.split(" ")
            if len(split_address) > 2:
                if split_address[0] == "DIO" or split_address[0] == "WIO" or split_address[0] == "AND" or split_address[0] == "SIO":
                    split_address.pop(0)
                if split_address[1] == "DIO" or split_address[1] == "WIO" or split_address[1] == "AND" or split_address[1] == "SIO" or split_address[1] == "WIO" or split_address[1] == "BO":
                    split_address.pop(1)
                person_address = " ".join(split_address)
            if person_address != "":
                if re.search("\d{6}",person_address):
                    postal_code_data = re.match('^.*(?P<zipcode>\d{6}).*$', person_address).groupdict()['zipcode']
                    postal_code = postal_code_data if len(postal_code_data) == 6 else ''
                if "," in person_address:
                    split_address = person_address.split(",")
                    address1 = ','.join(split_address[:len(split_address)//2])
                    address2 = ','.join(split_address[len(split_address)//2:])
                else:
                    split_address = person_address.split(" ")
                    address1 = ' '.join(split_address[:len(split_address)//2])
                    address2 = ' '.join(split_address[len(split_address)//2:])
            return {"success": True,"data": {'person_address': person_address, "postal_code": postal_code, "state": state, "address1":address1, "address2":address2}}
    except Exception as e:
        print(e,"teset")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("SignEzy aadhar_detect_text","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return ({"success":False, "error": str(e), "message":"Unable to scan your id"})




def text_getter(image_file):
    try:
        # print(image_file)
        company = frappe.get_last_doc('company')
        url = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAWvJ0ftbmjXxz8-nfgU1OYw9bbYCRQnq0'
        header = {'Content-Type': 'application/json'}
        body = {
            'requests': [{
                'image': {
                    'content': image_file,
                },
                'features': [{
                    'type': 'DOCUMENT_TEXT_DETECTION',
                    'maxResults': 100,
                }],
                "imageContext": {
                    "languageHints": ["en-t-iO-handwrit"]
                }
            }]
        }
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            response = requests.post(
                url, headers=header, json=body, proxies=proxies).json()
        else:
            response = requests.post(url, headers=header, json=body).json()
        text = response['responses'][0]['textAnnotations'][0]['description'] if len(
            response['responses'][0]) > 0 else ''
        return {"success":True, "data":text}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("SignEzy text_getter","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "error": str(e), "message":"Unable to scan your id"}