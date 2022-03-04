# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

import base64

import frappe
import requests
from frappe.model.document import Document
import sys, traceback, datetime
from frappe.utils.background_jobs import enqueue
from version2_app.passport_scanner.doctype.dropbox.ocr_details import scan_aadhar
import datetime




classify_api = 'http://localhost:5000/predict'
detection_api = 'http://localhost:5000/detect'


class Dropbox(Document):
    pass

@frappe.whitelist(allow_guest=True)
def create_doc_using_base_files(reservation_number: str,image_1: str =None,image_2: str=None,image_3:str = None,guest_name:str='Guest'):
    # '''
    # create dropbox based on base64 file using fijtsu scanner
    # '''
    # try:
        company = frappe.get_last_doc("company")
        print(company.classfiy_api)
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path+'/sites/'+company.site_name
        front = ''
        back = ''
        front_doc_type = ''
        if image_1:
            image_1_response = requests.post(company.classfiy_api, json={"base": image_1},verify=False)
            try:
                image_1_response = image_1_response.json()
                front_doc_type = image_1_response['doc_type']
                del image_1_response['base']
                doc_type = detect_front_back(image_1_response['doc_type'])
                if doc_type == '':
                    front = image_1
                else:
                    back = image_1
                
            except ValueError:
                raise

        if image_2:
            image_2_response = requests.post(company.classfiy_api, json={"base": image_2})
            try:
                image_2_response = image_2_response.json()
                if front_doc_type == '':
                    front_doc_type = image_2_response['doc_type']
                del image_2_response['base']
                # print(image_2_response)
                doc_type = detect_front_back(image_2_response['doc_type'])
                if back == '':
                    back = image_2
                else:
                    front = image_2
                # print(doc_type)

            except ValueError:
                raise

        if image_3:
            image_3_response = requests.post(company.classfiy_api, json={"base": image_3},verify=False)
            try:
                image_3_response = image_3_response.json()
                del image_3_response['base']
                # print(image_3_response)
            except ValueError:
                raise

       
        
        
        if "voter_back" in front_doc_type or 'voter_front' in front_doc_type:
            id_type = 'voterid'
        elif "businessCard" in front_doc_type:
            id_type = 'aadhaar'
        elif "invoice" in front_doc_type:
            id_type = 'invoice'
        elif "driving_back" in front_doc_type or "driving_front" in front_doc_type:
            id_type = 'driving'
        elif "panFront" in front_doc_type:
            id_type = 'pan'
        elif "passport_back" in front_doc_type or 'passport_front' in front_doc_type:
            id_type = 'indianpassport'
        elif "printed_visa" in front_doc_type or 'written_visa' in front_doc_type:
            id_type = 'indianpassport'
        elif "oci" in front_doc_type:
            id_type = 'oci'
        elif "aadhar_front" in front_doc_type or 'aadhar_back' in front_doc_type:
            id_type = 'aadhaar'
        else:
            id_type = 'others'

        reseravtions_data = get_reservation_details(reservation_number)
        dropbox_exist = frappe.db.exists(
            {'doctype': 'Dropbox', 'reservation_no': reservation_number})

        new_dropbox = frappe.new_doc('Dropbox')
        new_dropbox.reservation_no = reservation_number
        new_dropbox.id_type = id_type
        new_dropbox.front = front
        new_dropbox.guest_name = guest_name

        if reseravtions_data:
            # if dropbox_exist:
            #     last_drop_box = frappe.get_last_doc('Dropbox', reservation_number) 
            #     if 'Guest' in last_drop_box.guest_name:
            #         new_dropbox.guest_name = 'Guest' + str(int(last_drop_box.guest_name.split('Guest')[1])+1)
            #     else:
            #         new_dropbox.guest_name = 'Guest-1'
                
            #     new_dropbox.room = reseravtions_data['room_no']
            #     new_dropbox.no_of_guests = reseravtions_data['no_of_adults'] + \
            #         reseravtions_data['no_of_children']
            # else:
            #     new_dropbox.guest_name = reseravtions_data['guest_first_name']
            #     new_dropbox.room = reseravtions_data['room_no']
            #     new_dropbox.no_of_guests = reseravtions_data['no_of_adults'] + \
            #         reseravtions_data['no_of_children']
            new_dropbox.reservation_found = 1
        else:
            new_dropbox.reservation_found = 0
        


        new_precheckin = frappe.new_doc("Precheckins")
        if image_1 and front != '':
            image_1_url = convert_base64_to_image(image_1, image_1_response['doc_type'], site_folder_path, company)
            if 'message' in image_1_url:
                new_precheckin.image_1 = image_1_url['message']['file_url']
                new_precheckin.guest_first_name = guest_name
                new_dropbox.front = image_1_url['message']['file_url']
        
        if image_2 and back != '':
            image_2_url = convert_base64_to_image(image_2, image_2_response['doc_type'],site_folder_path, company)
            if 'message' in image_2_url:
                new_precheckin.image_2 = image_2_url['message']['file_url']
                new_dropbox.back = image_2_url['message']['file_url']

        

        new_precheckin.confirmation_number = reservation_number
        # print(reseravtions_data)
        if reseravtions_data:
            new_precheckin.insert()
            new_dropbox.merged = "Merged"
            new_dropbox.merged_to = reservation_number
            new_dropbox.merged_on = datetime.datetime.now()

        new_dropbox.insert(ignore_permissions=True)
        # enqueue(
        #     extract_text,
        #     queue="default",
        #     timeout=800000,
        #     event="data_extraction",
        #     now=False,
        #     data = {"dropbox":new_dropbox,
        #     "image_1":image_1,
        #     "image_2":image_2
        #     },
        #     is_async = True,
        # )
        # if company.scan_ezy_module:
        #     if new_dropbox.id_type == 'aadhaar':
        #         enqueue(
        #             scan_aadhar,
        #             queue="default",
        #             timeout=800000,
        #             event="vision_api_extraction",
        #             now=True,
        #             data = {
        #             "front_base_image":front,
        #             "back_base_image":back,
        #             "dropbox":new_dropbox,
        #             "company":company
        #             },
        #             is_async = True,
        #         )
        return {
            "success": True,
            "Message":"Dropbox created successfully"
        }
    # except Exception as e:
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     frappe.log_error(
    #         "create_doc_using_base_files", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
    #     print(e)
    #     return {
    #         "success": False,
    #         "Message":"Error while Dropbox creating Please try again"
    #     }

def extract_text(data:dict):
    '''
    extract details from doc type
    :param name: dropbox name
    '''
    try:
        company = frappe.get_last_doc("company")
        # print(data.__dict__)
        details= {}
        if data['image_1']:
            image_1_response = requests.post(company.detection_api, json={"base": data['image_1'],"thresh":0.5})
            try:
                image_1_response = image_1_response.json()
                print(image_1_response)
                for key in image_1_response:
                    if 'aadhar_no' in key:
                        print(image_1_response[key]['data'])
                        if image_1_response[key]['data']:
                            details['aadhar_no'] = image_1_response[key]['data']
                    elif 'aadhar_front_details' in key:
                        if image_1_response[key]['data']:
                            for aadhar_front_details in image_1_response[key]['data']:
                                details[aadhar_front_details]=image_1_response[key]['data'][aadhar_front_details]
 
            except ValueError:
                raise
            
        if data['image_2']:
            image_2_response = requests.post(detection_api, json={"base": data['image_2'],"thresh":0.5})
            try:
                image_2_response = image_2_response.json()
                print(image_2_response)
                for key in image_2_response:
                    if 'Aadhar_Back_No' in key:
                        print(image_2_response[key]['data'])
                        if image_2_response[key]['data']:
                            details['aadhar_back_no'] = image_2_response[key]['data']
                    elif 'aadhar_back_details' in key:
                        if image_2_response[key]['data']:
                            details['aadhar_address'] = image_2_response[key]['data']

                # print(image_2_response)
            except ValueError:
                raise

        print(details)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "extract_text", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        print(e)




def create_guest_details(dropbox):
    '''
    create guest details if scan ezy enabled
    '''
    try:
        company = frappe.get_last_doc("company")
        if dropbox.id_type == 'aadhar':
            pass
        elif dropbox.id_type == 'voterid':
            pass
        elif dropbox.id_type == 'driving':
            pass
        elif dropbox.id_type == 'indianpassport':
            pass
        # elif dropbox.id_type == 'driving':
        #     pass
        
    except Exception as e:
        print(e)

        

def create_scanned_doc(file_path: str):
    '''
    create scanned document
    :param path: path of the uploaded file
    '''
    try:
        company = frappe.get_last_doc("company")
        file_name = file_path.rsplit('/', 1)[1]

        reservation_number = file_name.split('_')[0]
        full_file_path = frappe.utils.get_bench_path() + "/sites/" + \
            frappe.utils.get_path('public', 'files', file_name)[2:]

        with open(full_file_path, 'rb') as image_file:
            encode_string = base64.b64encode(image_file.read())
            base_date = encode_string.decode('utf-8')
        class_response = requests.post(company.classfiy_api, json={"base": base_date})
        try:
            class_response = class_response.json()
            # print(class_response)
        except ValueError:
            # print(class_response.text)
            raise

        label = class_response['doc_type']
        id_type = 'aadhaar'
        front = ''
        back = ''

        # classes = {"0": 'aadhar_back',
        #    "1": 'aadhar_front', 
        #    "2": 'driving_back', 
        #    "3": 'driving_front', 
        #    "4": 'passport_back', 
        #    "5": 'passport_front', 
        #    "6": 'printed_visa', 
        #    "7": 'voter_back', 
        #    "8": 'voter_front', 
        #    "9": 'written_visa'}

        if "voter_back" in label or 'voter_front' in label:
            id_type = 'voterid'
        elif "businessCard" in label:
            id_type = 'aadhaar'
        elif "invoice" in label:
            id_type = 'invoice'
        elif "driving_back" in label or "driving_front" in label:
            id_type = 'driving'
        elif "panFront" in label:
            id_type = 'pan'
        elif "passport_back" in label or 'passport_front' in label:
            id_type = 'indianpassport'
        elif "printed_visa" in label or 'written_visa' in label:
            id_type = 'indianpassport'
        elif "oci" in label:
            id_type = 'oci'
        elif "aadhar_front" in label or 'aadhar_back' in label:
            id_type = 'aadhaar'
        else:
            id_type = 'others'

        dropbox_exist = frappe.db.exists(
            {'doctype': 'Dropbox', 'reservation_no': reservation_number})

        reseravtions_data = get_reservation_details(reservation_number)

        if dropbox_exist:
            new_dropbox = frappe.get_doc('Dropbox', dropbox_exist[0])
            if reseravtions_data:
                new_dropbox.guest_name = reseravtions_data['guest_first_name']
                new_dropbox.room = reseravtions_data['room_no']
                new_dropbox.no_of_guests = reseravtions_data['no_of_adults'] + \
                    reseravtions_data['no_of_children']
                new_dropbox.reservation_found = 1

            else:
                new_dropbox.reservation_found = 0
            
            new_dropbox.append("images", {
                "image_path": file_path,
                "image_full_path":full_file_path,
                "frontback": detect_front_back(label),
                "id_type": id_type,
                "filename": file_path.rsplit('/', 1)[1],
                "merged":0

            })
            new_dropbox.save()
            if reseravtions_data:
                merge_reservation(new_dropbox,company)

        else:
            new_dropbox = frappe.new_doc('Dropbox')
            new_dropbox.reservation_no = reservation_number
            if reseravtions_data:
                new_dropbox.guest_name = reseravtions_data['guest_first_name']
                new_dropbox.room = reseravtions_data['room_no']
                new_dropbox.no_of_guests = reseravtions_data['no_of_adults'] + \
                    reseravtions_data['no_of_children']
                new_dropbox.reservation_found = 1
            else:
                new_dropbox.reservation_found = 0
            new_dropbox.append("images", {
                "image_path": file_path,
                "image_full_path":full_file_path,
                "frontback": detect_front_back(label),
                "id_type": id_type,
                "filename": file_path.rsplit('/', 1)[1],
                "merged":0
            })
            new_dropbox.insert()
            if reseravtions_data:
                merge_reservation(new_dropbox,company)
    except Exception as e:
        print(e)


def detect_front_back(label: str):
    '''
    arrange front and back based on lable
    :param label : label string
    '''
    try:
        if 'front' in label:
            return 'Front'
        elif 'back' in label:
            return 'Back'
        elif 'printedVisa' in label or 'writtenVisa' in label or 'visa' in label:
            return 'Back'
        elif 'businessCard' in label:
            return 'Front'
        else:
            return 'Front'
    except Exception as e:
        print(e)


def get_reservation_details(reseravtion: str):
    '''
    get reservation details from pre-arrivals for guest count, and room number
    :param reservation : reservation number
    '''
    try:
        pre_arrival_details = frappe.db.get_value(
            'Arrival Information', {'confirmation_number': reseravtion}, ['guest_first_name', 'no_of_adults', 'no_of_children', 'room_no'], as_dict=1)
        # print(pre_arrival_details)
        if pre_arrival_details:
            return pre_arrival_details
        else:
            return None
    except Exception as e:
        print(e)


def merge_reservation(new_dropbox,company):
    '''
    merge reservation to prechickin
    '''
    try:
        precheckin_exist = frappe.db.exists(
            {'doctype': 'Precheckins', 'confirmation_number': new_dropbox.reservation_no})
        if precheckin_exist:
            pre_arrival_details = frappe.get_last_doc('Precheckins', filters={"confirmation_number": new_dropbox.reservation_no})
            pre_arrival_details = frappe.get_doc('Precheckins',pre_arrival_details.name)
            print(pre_arrival_details.__dict__)
            if 'Guest' in pre_arrival_details.guest_first_name:
                count = int(pre_arrival_details.guest_first_name.split('-')[1])+1
                guest_name = 'Guest-'+str(count)
                create_precheckin(new_dropbox,company,guest_name)
            else:
                guest_name = 'Guest-1'
                create_precheckin(new_dropbox,company,guest_name)

            
        else:
            create_precheckin(new_dropbox,company)
            # image_1 = ''
            # image_2 = ''
            # if (len(new_dropbox.images)%2) == 0:
            #     for i in new_dropbox.images:
                    
            #         if (i.idx%2) != 0 and i.merged == 0: 
            #             with open(i.image_full_path, "rb") as image_file:
            #                 base = base64.b64encode(image_file.read())
            #             name = new_dropbox.reservation_no+i.id_type+i.filename
            #             image_1_upload = convert_base64_to_image(base,name,i.image_full_path,company)
            #             image_1 = image_1_upload["message"]["file_url"]

            #         elif (i.idx%2) == 0 and i.merged == 0:
            #             with open(i.image_full_path, "rb") as image_file:
            #                 base = base64.b64encode(image_file.read())
            #             image_2_upload = convert_base64_to_image(base,name,i.image_full_path,company)
            #             image_2 = image_2_upload["message"]["file_url"]

                    
            #         if (i.idx%2) == 0 and i.merged == 0:
            #             new_pre_arrival= frappe.new_doc('Precheckins')
            #             new_pre_arrival.confirmation_number = new_dropbox.reservation_no
            #             new_pre_arrival.guest_first_name = new_dropbox.guest_name
            #             new_pre_arrival.image_1 = image_1
            #             new_pre_arrival.image_2 = image_2
            #             new_pre_arrival.save()

            #     for i in new_dropbox.images:
            #         i.merged = 1
            #     new_dropbox.save()
                    


    except Exception as e:
        print(str(e),"error")


def create_precheckin(new_dropbox,company,guest_name=None):
    '''
    create precheckin 
    '''
    try:
        image_1 = ''
        image_2 = ''
        if (len(new_dropbox.images)%2) == 0:
            for i in new_dropbox.images:
                if (i.idx%2) != 0 and i.merged == 0: 
                    with open(i.image_full_path, "rb") as image_file:
                        base = base64.b64encode(image_file.read())
                    name = new_dropbox.reservation_no+i.id_type+i.filename
                    image_1_upload = convert_base64_to_image(base,name,i.image_full_path,company)
                    image_1 = image_1_upload["message"]["file_url"]

                elif (i.idx%2) == 0 and i.merged == 0:
                    with open(i.image_full_path, "rb") as image_file:
                        base = base64.b64encode(image_file.read())
                    image_2_upload = convert_base64_to_image(base,name,i.image_full_path,company)
                    image_2 = image_2_upload["message"]["file_url"]

                
                if (i.idx%2) == 0 and i.merged == 0:
                    new_pre_arrival= frappe.new_doc('Precheckins')
                    new_pre_arrival.confirmation_number = new_dropbox.reservation_no
                    new_pre_arrival.guest_first_name = new_dropbox.guest_name
                    if guest_name:
                        new_pre_arrival.confirmation_number = new_dropbox.reservation_no + guest_name.split('-')[1]
                        new_pre_arrival.guest_first_name = guest_name
                    new_pre_arrival.image_1 = image_1
                    new_pre_arrival.image_2 = image_2
                    new_pre_arrival.save()
            
            for i in new_dropbox.images:
                print(image_1,i.image_full_path)
                if image_1 ==  i.image_1:
                    pass
                # i.merged_to = new_dropbox.reservation_no
                # if guest_name:
                #     print(guest_name.split('-')[1],"guestname")
                #     i.merged_to = new_dropbox.reservation_no + guest_name.split('-')[1]
                # i.merged = 1

            if len(new_dropbox.images) >= new_dropbox.no_of_guests:
                new_dropbox.merged = 'Merged'
            elif len(new_dropbox.images) > 1:
                new_dropbox.merged = 'Partial Merged'
            new_dropbox.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "create_precheckin", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))


def convert_base64_to_image(base,name,site_folder_path,company):
    try:
        print(name)
        file = site_folder_path+"/private/files/"+name+".png"
        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, 'rb')}
        payload = {
            "is_private": 0,
            "folder": "Home",
            # "doctype": "Precheckins",
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        if 'message' in response:
            return response
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}



# def convert_base64_to_image(base,name,file_path,company):
#     try:
#         file = file_path
#         # res = bytes(base, 'utf-8')
#         with open(file, "wb") as fh:
#             fh.write(base64.b64decode(base))
#         files = {"file": open(file, 'rb')}
#         payload = {
#             "is_private": 0,
#             "folder": "Home"
#         }
#         site = company.host
#         upload_qr_image = requests.post(site + "api/method/upload_file",
#                                         files=files,
#                                         data=payload)
#         response = upload_qr_image.json()
#         if 'message' in response:
#             return response
#     except Exception as e:
#         # exc_type, exc_obj, exc_tb = sys.exc_info()
#         # frappe.log_error("Scan-Guest Details Opera","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
#         return {"success":False,"message":str(e)}