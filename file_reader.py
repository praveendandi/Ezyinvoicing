
import threading
import glob
import requests 
def printit():
	try:
		# threading.Timer(5.0, printit).start()
		file_list = glob.glob("/home/caratred/Desktop/test/*.pdf")
		data = {"company":"HICC-01","host":"http://192.168.1.61:8000/api/method/"}
		if len(file_list)>0:
			for each in file_list:
				files_new = {'file': open(each, 'rb')}
				print(files_new)
				payload = {
					'is_private': 1,
					'folder': 'Home',
					'doctype': 'invoices',
					'docname': data["company"],
					'fieldname':'invoice'}
				print(payload,data)	
				file_res = requests.post(data['host']+"upload_file",files=files_new, data=payload)
				print("--------------------")						
				print(file_res.json())						

		print("Hello, World!")
	except Exception as e:
		print(str(e))
# printit()

def getfiles():
	file_list = glob.glob("/home/caratred/Desktop/test/*.pdf")
	upload_files(file_list)

def upload_files(file_list):
	for each in file_list:
		data = {"company":"HICC-01","host":"http://192.168.1.61:8000/api/method/"}
		print(each)
		files_new = {'file': open(each, 'rb')}
		print(files_new)
		payload = {
			'is_private': 1,
			'folder': 'Home',
			'doctype': 'invoices',
			'docname': data["company"],
			'fieldname':'invoice'}
		print(payload,data)	
		file_res = requests.post(data['host']+"upload_file",files=files_new, data=payload)
		print("--------------------")						
		print(file_res.json())
		getfiles()

getfiles()

