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



# detection_api = 'http://localhost:5000/detect'
detection_api = 'https://api.caratred.com/detect'



def update_document_details(doc,method=None):
	try:
		enqueue(
            create_passport_details,
            queue="default",
            timeout=800000,
            event="update_temp_doc_details",
            now=False,
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
		# print(rep.text)
		# print(doc.resident_of_india,doc.guest_id_type)
		if(doc.resident_of_india == "No" and doc.guest_id_type == 'passport'):
			guest_details["passport_details"]={}
			passport_mrz= rep.json()
			mrz_data = passport_mrz_post_processing(passport_mrz)

			if 'passport_details' in mrz_data.keys():
				guest_details['passport_details'] = mrz_data['passport_details']

			if 'passport_place_of_birth' in mrz_data.keys():
				guest_details['passport_details']['passport_place_of_birth'] = mrz_data['passport_place_of_birth']['data']
			if 'passport_date_of_issue' in mrz_data.keys():
				guest_details['passport_details']['passport_date_of_issue'] = mrz_data['passport_date_of_issue']['data']
		else:

			local_front_id_details= rep.json()
			if 'Aadhar_Front' in local_front_id_details.keys():
				# print(local_front_id_details)
				guest_details["aadhar_front_details"] = local_front_id_details





		image_2_file_path = site_folder_path+'/public'+doc.image_2
		with open(image_2_file_path, "rb") as image_file:
			encoded_string = base64.b64encode(image_file.read())
		data = {"thresh":img2_thresh,"base":encoded_string.decode("utf-8") }
		rep = requests.post(detection_api,json=data)
		# print(rep.text)
		if(doc.resident_of_india == "No" and doc.guest_id_type == 'passport'):
			guest_details["visa_details"]={}
			visa_mrz= rep.json()
			mrz_data = visa_mrz_post_processing(visa_mrz)

			
			if 'visa_details' in visa_mrz.keys():
				guest_details['visa_details'] = visa_mrz['visa_details']


			if 'visa_no_of_entries' in visa_mrz.keys():
				guest_details['visa_details']['visa_no_of_entries'] = visa_mrz['visa_no_of_entries']
			if 'visa_date_of_issue' in visa_mrz.keys():
				guest_details['visa_details']['visa_date_of_issue'] = visa_mrz['visa_date_of_issue']
			if 'visa_type' in visa_mrz.keys():
				guest_details['visa_details']['visa_type'] = visa_mrz['visa_type']
		else:
			local_back_id_details= rep.json()
			if 'aadhar_back_details' in local_back_id_details.keys():
				guest_details["aadhar_back_details"] = local_back_id_details
				# print(local_back_id_details)	

		
		guest_details['precheckin_data'] = {
			"confirmation_number":doc.confirmation_number,
			# "postal_code":doc.zip_code,
			# "city":doc.guest_city,
			# "address":doc.address1,
			# "guest_phone_number":doc.guest_phone_number
		}
		# print(guest_details)
		parse_guest_details(guest_details)
		
		# print(rep.json())
	except Exception as e:
		print(e)





def parse_guest_details(data):
	try:
		# print(data)

		guest_details = {}
		
		today = str(datetime.date.today())
		current_time = datetime.datetime.now().strftime('%H:%M:%S')
		gender = ''
		guest_precheckin_data = {
            # "address":data['precheckin_data']['address'],
			"checkin_date":today,
			"checkin_time":current_time,
			# "city":data['precheckin_data']['city'],
			"confirmation_number":data['precheckin_data']['confirmation_number'],
			# "contact_phone_no":data['precheckin_data']['guest_phone_number'],
			"no_of_nights":"",
			# "permanent_mobile_no":data['precheckin_data']['guest_phone_number'],
			# "permanent_phone_no":data['precheckin_data']['guest_phone_number'],
			# "postal_code":data['precheckin_data']['postal_code']
		}
		guest_details= {**guest_precheckin_data,**guest_details}
		if 'passport_details' in data.keys():
			gender = 'F'
			if data['passport_details']['data']['sex'] == '0':
				gender = 'M'
			
			guest_passport_data= {
				"country":data['passport_details']['data']['country'],
				# "date_of_arrival_in_india":"",
				"date_of_birth":data['passport_details']['data']['birth_date'],
				"gender":gender,
				"given_name":data['passport_details']['data']['name'],
				"guest_full_name":data['passport_details']['data']['name']+' '+data['passport_details']['data']['surname'],
				"nationality":data['passport_details']['data']['nationality'],
				"passport_date_of_issue":data['passport_details']['passport_date_of_issue'],
				"passport_number":data['passport_details']['data']['document_number'],
				# "passport_place_of_issued_city":data['passport_details']['data']['passport_place_of_issued_city'],
				# "passport_place_of_issued_country":data['passport_details']['nationality'],
				"passport_valid_till":data['passport_details']['data']['expiry_date'],
				"surname":data['passport_details']['data']['surname'],
				"passport_place_of_birth":data['passport_details']['passport_place_of_birth']

		    }
			guest_details= {**guest_passport_data,**guest_details}

		
		if 'visa_details' in data.keys():
			guest_visa_details={
				"visa_date_of_issue":data['visa_details']['visa_date_of_issue']['data'],
				"visa_number":data['visa_details']['data']['document_number'],
				"visa_place_of_issued_city":data['visa_details']['data']['country'],
				"visa_place_of_issued_country":data['visa_details']['data']['country'],
				# "visa_sub_type":data['visa_details']['country'],
				"visa_type":data['visa_details']['visa_type']['data'],
				"visa_valid_till":data['visa_details']['data']['expiry_date'],
				# "no_entries":data['visa_details']['visa_no_of_entries'],
				"visa_no_of_entries":data['visa_details']['visa_no_of_entries']['data'],
			}
			# print(guest_visa_details)
			guest_details= {**guest_visa_details,**guest_details}

		if 'aadhar_front_details' in data.keys():
			guest_front_aadhar_details={
				"local_id_number":data['aadhar_front_details']['aadhar_no']['data'],
				"dob":data['aadhar_front_details']['aadhar_front_details']['data']['dob'],
				"name":data['aadhar_front_details']['aadhar_front_details']['data']['name'],
				"gender":data['aadhar_front_details']['aadhar_front_details']['data']['gender'],
				"given_name":data['aadhar_front_details']['aadhar_front_details']['data']['name'],

			}
			guest_details= {**guest_front_aadhar_details,**guest_details}
		
		if 'aadhar_back_details' in data.keys():
			print(data,"&&&&&&&&&&&&&&&&&&7")
			guest_back_aadhar_details={
				"aadhar_address":data['aadhar_back_details']['aadhar_back_details']['data']
			}
			guest_details= {**guest_back_aadhar_details,**guest_details}
		return create_temp_precheckin_doc(guest_details)
		
	except Exception as e:
		print(e)


def create_temp_precheckin_doc(guest_details):
	try:
		guest_details['doctype'] = 'Temp Doc Details'
		print(json.dumps(guest_details, indent = 3))
		doc = frappe.get_doc(guest_details)
		doc.insert()

		print(json.dumps(guest_details, indent = 3))
		
	except Exception as e:
		print("error wihle create temp doc",e)




def aadhar_details_parsing():
	'''
	post processing of aadhar details
	'''
	try:
		pass
	except Exception as e:
		pass


def passport_mrz_post_processing(data):
	try:
		# print(data)
		
		if 'passport_details' in data.keys():
			if data['passport_details'] is not None:
				data['passport_details']['data']['nationality'] =  data['passport_details']['data']['country']
				birth_date_string = data['passport_details']['data']["birth_date"][0:2]+'/'+ data['passport_details']['data']["birth_date"][2:4]+'/'+data['passport_details']['data']["birth_date"][4:]
				expiry_date_string  = data['passport_details']['data']["expiry_date"][0:2]+'/'+ data['passport_details']['data']["expiry_date"][2:4]+'/'+data['passport_details']['data']["expiry_date"][4:]
				data['passport_details']['data']["birth_date"] = datetime.datetime.strptime(birth_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
				data['passport_details']['data']["expiry_date"] = datetime.datetime.strptime(expiry_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
				
					


		return data
	except Exception as e:
		print(e,"passport extraction")


def visa_mrz_post_processing(data):
	try:
		if 'visa_details' in data.keys():
			if data['visa_details'] is not None:
				data['visa_details']['data']['nationality'] = data['visa_details']['data']['country']
				birth_date_string = data['visa_details']['data']["birth_date"][0:2]+'/'+ data['visa_details']['data']["birth_date"][2:4]+'/'+data['visa_details']['data']["birth_date"][4:]
				expiry_date_string  = data['visa_details']['data']["expiry_date"][0:2]+'/'+ data['visa_details']['data']["expiry_date"][2:4]+'/'+data['visa_details']['data']["expiry_date"][4:]
				data['visa_details']['data']["birth_date"] = datetime.datetime.strptime(birth_date_string, "%y/%m/%d").strftime("%Y-%m-%d")
				data['visa_details']['data']["expiry_date"] = datetime.datetime.strptime(expiry_date_string, "%y/%m/%d").strftime("%Y-%m-%d")

			
		return data
	except Exception as e:
		print(e,"visa extraction")