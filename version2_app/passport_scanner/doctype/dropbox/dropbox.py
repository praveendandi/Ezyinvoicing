# Copyright (c) 2022, caratred and contributors
# For license information, please see license.txt

import base64

import frappe
import requests
from frappe.model.document import Document
import sys
import traceback
import datetime
from frappe.utils.background_jobs import enqueue
from version2_app.passport_scanner.doctype.dropbox.ocr_details import scan_aadhar
import datetime
import re
# from frappe.utils.data import format_datetime
import time





class Dropbox(Document):
    pass


@frappe.whitelist(allow_guest=True)
def create_doc_using_base_files(reservation_number: str, image_1: str = None, image_2: str = None, image_3: str = None, guest_name: str = 'Guest'):
    '''
    create dropbox based on base64 file using fijtsu scanner
    '''
    try:
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path+'/sites/'+company.site_name
        front = ''
        back = ''
        front_doc_type = ''
        front_detected_doc_type = None
        back_detected_doc_type = None
        if image_1:
            image_1_response = requests.post(company.classfiy_api, json={
                                             "base": image_1}, verify=False)
            try:
                image_1_response = image_1_response.json()
                front_doc_type = image_1_response['doc_type']
                front_detected_doc_type = image_1_response['doc_type']
                del image_1_response['base']

                doc_type = detect_front_back(image_1_response['doc_type'])
                if doc_type == '' or doc_type == 'Front':
                    front = image_1

                else:
                    back = image_1

            except ValueError:
                raise

        if image_2:
            image_2_response = requests.post(
                company.classfiy_api, json={"base": image_2})
            try:
                image_2_response = image_2_response.json()
                if front_doc_type == '':
                    front_doc_type = image_2_response['doc_type']
                del image_2_response['base']
                # print(image_2_response)
                doc_type = detect_front_back(image_2_response['doc_type'])
                back_detected_doc_type = image_2_response['doc_type']
                if back == '' or doc_type == 'Back':
                    back = image_2
                else:
                    front = image_2
                # print(doc_type)

            except ValueError:
                raise

        if image_3:
            image_3_response = requests.post(company.classfiy_api, json={
                                             "base": image_3}, verify=False)
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
        if front != '':
            ts = time.time()
            image_1_url = convert_base64_to_image(
                front, reservation_number+id_type+str(ts), site_folder_path, company)
            if 'message' in image_1_url:
                new_precheckin.image_1 = image_1_url['message']['file_url']
                new_precheckin.guest_first_name = guest_name
                new_dropbox.front = image_1_url['message']['file_url']

        if back != '':
            ts = time.time()
            image_2_url = convert_base64_to_image(
                back, reservation_number+id_type+str(ts), site_folder_path, company)
            if 'message' in image_2_url:
                new_precheckin.image_2 = image_2_url['message']['file_url']
                new_dropbox.back = image_2_url['message']['file_url']

        new_precheckin.confirmation_number = reservation_number
        # print(reseravtions_data)
        if reseravtions_data:
            new_precheckin.guest_id_type = id_type
            new_precheckin.insert(ignore_permissions=True)
            new_dropbox.merged = "Merged"
            new_dropbox.merged_to = reservation_number
            new_dropbox.merged_on = datetime.datetime.now()
            new_dropbox.ocr_process_status 

        new_dropbox.insert(ignore_permissions=True)
        if reseravtions_data:
            enqueue(
                extract_text,
                queue="default",
                timeout=800000,
                event="data_extraction",
                now=False,
                data={"dropbox": new_dropbox,
                    "image_1": image_1,
                    "image_2": image_2,
                    "id_type": id_type,
                    "front_detected_doc_type":front_detected_doc_type,
                    "back_detected_doc_type":back_detected_doc_type
                    },
                is_async=True,
            )
       
        return {
            "success": True,
            "Message": "Dropbox created successfully"
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "create_doc_using_base_files", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        print(e)
        return {
            "success": False,
            "Message": "Error while Dropbox creating Please try again"
        }


def extract_text(data: dict):
    '''
    extract details from doc type
    :param name: dropbox name
    '''
    try:
        thresh = 0.5
        
        if data['id_type'] == 'indianpassport':
            thresh = 0.5
        company = frappe.get_last_doc("company")
        details = {}
        if data['image_1']:
            image_1_response = requests.post(company.detection_api, json={
                                             "base": data['image_1'], "thresh": thresh,"class":data['front_detected_doc_type']})
            try:
                image_1_response = image_1_response.json()
                # print(image_1_response)
                for key in image_1_response:
                    if 'aadhar_no_details' in key:
                        if image_1_response[key]:
                            details['AADHAR_NO'] = image_1_response[key]['aadhar_no']
                    elif 'aadhar_front_details' in key:
                        if image_1_response[key]['aadhar_front_details']:
                            for aadhar_front_details in image_1_response[key]['aadhar_front_details']:
                                details[aadhar_front_details] = image_1_response[key]['aadhar_front_details'][aadhar_front_details]
                    elif 'passport_details' in key:
                        if image_1_response[key]['passport_details']:
                            for passport_details in image_1_response[key]['passport_details']:
                                details[passport_details] = image_1_response[key]['passport_details'][passport_details]
            except ValueError:
                raise

        if data['image_2']:
            image_2_response = requests.post(
                company.detection_api, json={"base": data['image_2'], "thresh": thresh,"class":data['back_detected_doc_type']})
                # company.detection_api, json={"base": data['image_2'], "thresh": thresh,"class":'printed_visa'})
            try:
                image_2_response = image_2_response.json()
                # print(image_2_response)
                for key in image_2_response:
                    if 'aadhar_back_details' in key:
                        if image_2_response[key]['aadhar_back_details']:
                            for aadhar_back_details in image_2_response[key]['aadhar_back_details']:
                                details[aadhar_back_details] = image_2_response[key]['aadhar_back_details'][aadhar_back_details]
                    elif 'aadhar_back_no_details' in key:
                        if image_2_response[key]:
                            details['AADHAR_BACK_NO'] = image_2_response[key]['aadhar_back_no']
                    elif 'visa_details' in key:
                        if len(image_2_response[key]['visa_details'])>0:
                            if image_1_response[key]['visa_details']:
                                for visa_details in image_1_response[key]['visa_details']:
                                    details[visa_details] = image_1_response[key]['visa_details'][visa_details]
                    
            
                # print(image_2_response)
            except ValueError:
                raise

        if 'merged_to' in data.keys():
            data['dropbox'].reservation_no = data['merged_to']
        
        # print(details)
        if data['id_type'] == 'aadhaar':
            create_guest_update_precheckin_details(details, data['dropbox'])

        elif data['id_type'] == 'indianpassport':
            create_passport_guest_update_precheckin_details(details, data['dropbox'])

        

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "extract_text", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        print(e)



def create_passport_guest_update_precheckin_details(details, dropbox):
    '''
    create guest details if scan ezy exists
    update precheckin based on aadhar details
    '''
    try:
        main_guest = True
        if 'Guest' not in dropbox.guest_name:
            main_guest = False
        guest_details = {
            'doctype': 'Guest Details',
            'confirmation_number': dropbox.reservation_no,
            # 'nationality':"IND",
            # 'country':'IND',
            'id_image1':dropbox.front,
            'id_image2':dropbox.back,
            'id_type':'passport',
            'main_guest':main_guest,
            'whether_employed_in_india':'N',
            "status": "In House",
        }
        guest_details['given_name'] = dropbox.guest_name
        for key in details:
            if key == "name":
                guest_details['guest_full_name'] = details[key]
                guest_details['given_name'] = details[key]
            elif key == "document_number":
                guest_details['passport_no'] = details[key]
            elif key == "surname":
                guest_details['passport_no'] = details[key]
            # elif key == 'birth_date':
            #     guest_details['date_of_birth'] = details[key]
            elif key == 'sex':
                guest_details['gender'] = details[key]
            elif key == 'nationality':
                guest_details['nationality'] = details[key]
                guest_details['country'] = details[key]

            elif key == 'expiry_date':
                guest_details['passport_valid_till'] = details[key]
            # elif key == 'expiry_date':
            #     guest_details['passport_valid_till'] = details[key]
            
            # passport_place_of_issued_country
            # passport_place_of_issued_city
            # passport_date_of_issue
            # visa_number
            # visa_place_of_issued_country
            # visa_place_of_issued_city
            # visa_date_of_issue
            # visa_valid_till
            # visa_type
            # visa_sub_type


            
        new_guest_details = frappe.get_doc(guest_details)
        new_guest_details.insert()
        print(guest_details,"guest deatils")
        frappe.db.set_value('Task', 'TASK00002', 'subject', 'New Subject')

        arrival_info = frappe.get_doc('Arrival Information',dropbox.reservation_no)
        arrival_info.status = 'Scanned'
        arrival_info.save()


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "create_passport_guest_update_precheckin_details", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        print(e)


def create_guest_update_precheckin_details(details, dropbox):
    '''
    create guest details if scan ezy exists
    update precheckin based on aadhar details
    '''
    try:
        # print(details,dropbox,"hey hiee")
        main_guest = True
        if 'Guest' not in dropbox.guest_name:
            main_guest = False
        aadhar_details = {
            'doctype': 'Guest Details',
            'confirmation_number': dropbox.reservation_no,
            'nationality':"IND",
            'country':'IND',
            'id_image1':dropbox.front,
            'id_image2':dropbox.back,
            'id_type':'aadhaar',
            'main_guest':main_guest,
            'whether_employed_in_india':'N',
            "status": "In House"
        }
        for key in details:
            if key == 'ADRESS':
                address = re.sub(r"[\n\t\s]*", "", details[key])
                aadhar_details["address"] = address
            elif key == 'AADHAR_NO':
                aadhar_details["local_id_number"] = details[key]
            elif key == 'NAME':
                if main_guest:
                    aadhar_details["guest_full_name"] = dropbox.guest_name
                    aadhar_details["given_name"] = details[key]
                else:
                    aadhar_details["guest_full_name"] = details[key]
                    aadhar_details["given_name"] = details[key]
            elif key == 'DOB':
                # print(format_datetime(details[key],'mm/dd/yyyy'))
                # aadhar_details["date_of_birth"] = format_datetime(details[key],'mm/dd/yyyy')
                # dob = datetime.datetime.strptime("details[key]", '%d/%m/%Y').strftime('%Y/%m/%d')
                # # datetime.datetime.strptime("details[key]", '%m/%d/%Y').strftime('%m/%d/%Y')
                # aadhar_details["date_of_birth"] = dob
                pass

            elif key == 'GENDER':
                aadhar_details["gender"] = 'M' if details[key] == 'Male' else 'F'
            elif key == 'STATE':
                pass
                # aadhar_details["gender"] = details[key]
            elif key == 'PINCODE':
                pincode = re.sub('\D', '', details[key])
                aadhar_details["postal_code"] = pincode
            elif key == 'LOCATION' or key == 'CITY':
                if key == 'CITY':
                    aadhar_details["city"] = details[key]
                else:
                    if 'city' not in aadhar_details:
                        aadhar_details["city"] = details[key]
            elif key == 'AADHAR_BACK_NO':
                pass
            elif key == 'AADHAR_BACK_DETAILS':
                pass

        new_guest_details = frappe.get_doc(aadhar_details)
        new_guest_details.insert()

        # arrival_info = frappe.get_doc({'doctype': 'Arrival Information',"confirmation_number":dropbox.reservation_no})
        arrival_info = frappe.get_doc('Arrival Information',dropbox.reservation_no)

        arrival_info.status = 'Scanned'
        arrival_info.save()

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "create_guest_update_precheckin_details", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        print(e)


@frappe.whitelist(allow_guest=True)
def check_drop_exist(reservation_number: str, guest_name: str):
    '''
    check dropbox exist or not
    :param name: dropbox name
    '''
    try:
        dropbox_exist = frappe.db.exists(
            "Dropbox", {"reservation_no": reservation_number, "guest_name": guest_name})
        if dropbox_exist:
            return {
                'success': True,
                'found': True,
                'message': "Dropbox already exist"
            }
        else:
            return {
                'success': True,
                'found': False,
                'message': "Dropbox not exist"
            }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(
            "check_drop_exist", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        return {
            'success': False,
            'message': "Error while checking Dropbox exist"
        }



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
            'Arrival Information', {'confirmation_number': reseravtion}, ['guest_first_name', 'no_of_adults', 'no_of_children', 'room_number'], as_dict=1)
        # print(pre_arrival_details)
        if pre_arrival_details:
            return pre_arrival_details
        else:
            return None
    except Exception as e:
        print(e)



def convert_base64_to_image(base, name, site_folder_path, company):
    try:
        file = site_folder_path+"/private/files/"+name+".jpg"

        # res = bytes(base, 'utf-8')
        with open(file, "wb") as fh:
            fh.write(base64.b64decode(base))
        files = {"file": open(file, 'rb')}
        payload = {
            "is_private": 0,
            "folder": "Home"
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
        frappe.log_error("Scan-Guest Details Opera",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}


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

def merge_guest_to_guest_details(doc, method=None):
    '''
    merge guest to guest details
    '''
    try:
        # drop_box = frappe.get_doc("Dropbox", name)
        # print(drop_box)
        # return True
        # print(doc.__dict__)
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        site_folder_path = folder_path+'/sites/'+company.site_name+'/public'
        if doc.front:
            front_file_path = site_folder_path + doc.front
            with open(front_file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            image_1 = encoded_string.decode("utf-8")
        if doc.back:
            back_file_path = site_folder_path + doc.front
            with open(back_file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            image_2 = encoded_string.decode("utf-8")
        
        enqueue(
                extract_text,
                queue="default",
                timeout=800000,
                event="data_extraction",
                now=False,
                data={"dropbox": doc,
                    "image_1": image_1,
                    "image_2": image_2,
                    "id_type": doc.id_type,
                    "front_detected_doc_type":doc.id_type,
                    "back_detected_doc_type":doc.id_type,
                    "merged_to": doc.merged_to,
                    },
                is_async=True,
            )
        return True
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("merge_guest_to_guest_details",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}