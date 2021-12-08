# Copyright (c) 2021, caratred and contributors
# For license information, please see license.txt

# import frappe
from random import triangular
from re import U
from frappe.model.document import Document
import frappe, json
import base64,requests
from frappe.utils.background_jobs import enqueue
import datetime

# from frappe.utils import datetime
class TempDocDetails(Document):
	pass



detection_api = 'http://localhost:5000/detect'


def update_document_details(doc,method=None):
	try:
		enqueue(
            create_passport_details,
            queue="default",
            timeout=800000,
            event="update_temp_doc_details",
            now=True,
            data = doc,
            is_async = True,
            )
		return True
	except Exception as e:
		print(e)

def create_passport_details(data):
	try:
		guest_details = {}
		img2_thresh = 0.3
		if(data.resident_of_india == "No"):
			img2_thresh = 0.2

		doc = data
		company = frappe.get_doc("company",doc.company)
		folder_path = frappe.utils.get_bench_path()
		site_folder_path = folder_path+'/sites/'+company.site_name
		image_1_file_path = site_folder_path+'/public'+doc.image_1
		with open(image_1_file_path, "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
		data = {"thresh":0.3,"base":encoded_string.decode("utf-8") }
		rep = requests.post(detection_api,json=data)
		print(rep.text)
		# print(doc.resident_of_india,doc.guest_id_type)
		if(doc.resident_of_india == "No" and doc.guest_id_type == 'passport'):
			passport_mrz= rep.json()
			mrz_data = passport_mrz_post_processing(passport_mrz)

			for i in mrz_data:
				if 'predection' in i.keys():
					if i['predection'] == 'mrz':
						guest_details['passport_details'] = i['data']



		image_2_file_path = site_folder_path+'/public'+doc.image_2
		with open(image_2_file_path, "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
		data = {"thresh":img2_thresh,"base":encoded_string.decode("utf-8") }
		rep = requests.post(detection_api,json=data)
		if(doc.resident_of_india == "No" and doc.guest_id_type == 'passport'):
			visa_mrz= rep.json()
			mrz_data = visa_mrz_post_processing(visa_mrz)
			# guest_details['visa_details'] = mrz_data
			for i in mrz_data:
				if 'predection' in i.keys():
					if i['predection'] == 'Visa_mrz':
						guest_details['visa_details'] = i['data']

		
		guest_details['precheckin_data'] = {
			"confirmation_number":doc.confirmation_number,
			"postal_code":doc.zip_code,
			"city":doc.guest_city,
			"address":doc.address1,
			"guest_phone_number":doc.guest_phone_number
		}
		# print(guest_details)
		insert_into_guest_details(guest_details)
		# print(rep.json())
	except Exception as e:
		print(e)


def insert_into_guest_details(data):
	try:
		# print(data)
		guest_details = {}
		
		today = str(datetime.date.today())
		current_time = datetime.datetime.now().strftime('%H:%M:%S')
		gender = ''
		guest_precheckin_data = {
            "address":data['precheckin_data']['address'],
			"checkin_date":today,
			"checkin_time":current_time,
			"city":data['precheckin_data']['city'],
			"confirmation_number":data['precheckin_data']['confirmation_number'],
			"contact_phone_no":data['precheckin_data']['guest_phone_number'],
			"no_of_nights":"",
			"permanent_mobile_no":data['precheckin_data']['guest_phone_number'],
			"permanent_phone_no":data['precheckin_data']['guest_phone_number'],
			"postal_code":data['precheckin_data']['postal_code']
		}
		guest_details= {**guest_precheckin_data,**guest_details}
		if 'passport_details' in data.keys():
			gender = 'F'
			if data['passport_details']['sex'] == '0':
				gender = 'M'
			
			guest_passport_data= {
				"country":data['passport_details']['country'],
				# "date_of_arrival_in_india":"",
				"date_of_birth":data['passport_details']['birth_date'],
				"gender":gender,
				"given_name":data['passport_details']['name'],
				"guest_full_name":data['passport_details']['name']+' '+data['passport_details']['surname'],
				"nationality":data['passport_details']['nationality'],
				"passport_date_of_issue":data['passport_details']['nationality'],
				"passport_number":data['passport_details']['document_number'],
				# "passport_place_of_issued_city":data['passport_details']['nationality'],
				# "passport_place_of_issued_country":data['passport_details']['nationality'],
				"passport_valid_till":data['passport_details']['expiry_date'],
				"surname":data['passport_details']['surname'],
		    }
			guest_details= {**guest_passport_data,**guest_details}


		if 'visa_details' in data.keys():
			guest_visa_details={
				"visa_date_of_issue":"",
				"visa_number":data['visa_details']['document_number'],
				"visa_place_of_issued_city":data['visa_details']['country'],
				"visa_place_of_issued_country":data['visa_details']['country'],
				# "visa_sub_type":data['visa_details']['country'],
				"visa_type":data['visa_details']['document_type'],
				"visa_valid_till":data['visa_details']['expiry_date'],
			}
			# print(guest_visa_details)
			guest_details= {**guest_visa_details,**guest_details}


		# print(guest_details)
		return guest_details
		
	except Exception as e:
		print(e)


def passport_mrz_post_processing(data):
	try:

		for i in data:
			if 'predection' in i.keys():
				if i['predection'] == 'mrz':
					if i['data'] is not None:
						i['data']['nationality'] =  i['data']['country']
						birth_date_string = i['data']["birth_date"][0:2]+'/'+ i['data']["birth_date"][2:4]+'/'+i['data']["birth_date"][4:]
						expiry_date_string  = i['data']["expiry_date"][0:2]+'/'+ i['data']["expiry_date"][2:4]+'/'+i['data']["expiry_date"][4:]
						i['data']["birth_date"] = datetime.datetime.strptime(birth_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
						i['data']["expiry_date"] = datetime.datetime.strptime(expiry_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
		return data
	except Exception as e:
		print(e,"passport extraction")


def visa_mrz_post_processing(data):
	try:
		for i in data:
			if 'predection' in i.keys():
				if i['predection'] == 'Visa_mrz':
					if i['data'] is not None:
						i['data']['nationality'] =  i['data']['country']
						birth_date_string = i['data']["birth_date"][0:2]+'/'+ i['data']["birth_date"][2:4]+'/'+i['data']["birth_date"][4:]
						expiry_date_string  = i['data']["expiry_date"][0:2]+'/'+ i['data']["expiry_date"][2:4]+'/'+i['data']["expiry_date"][4:]
						i['data']["birth_date"] = datetime.datetime.strptime(birth_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
						i['data']["expiry_date"] = datetime.datetime.strptime(expiry_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
		return data
	except Exception as e:
		print(e,"visa extraction")