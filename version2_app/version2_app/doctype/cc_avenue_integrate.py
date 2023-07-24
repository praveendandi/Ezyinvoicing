import requests
import json
from requests.api import get
import frappe,sys,traceback
from datetime import datetime
import qrcode


@frappe.whitelist(allow_guest=True)
def ccAvenueIntegrate(total_amount,check_no,outlet_name):
	try:
		get_outlet = frappe.get_doc('Outlets',outlet_name)
		if get_outlet.payment_gateway == "CCAvenue":
			now = datetime.now()
			date_time = now.strftime("%d%m%Y")
			get_doc= frappe.get_doc('CCAvenue Settings')
			data = {
			'p_merchant_id' : get_doc.merchant_id,
			'p_order_id' : date_time+check_no,
			'p_currency' : "INR",
			'p_amount' : total_amount,
			'p_redirect_url' : get_doc.redirect_url,
			'p_cancel_url' : get_doc.cancel__url,
			'p_language' : "English",
			'p_merchant_param1' : outlet_name,
			'p_merchant_param2' : 'merchant_param2',
			'p_merchant_param3' : 'merchant_param3',
			'p_merchant_param4' : 'merchant_param4',
			'p_merchant_param5' : 'merchant_param5',
			"accessCode" : get_doc.access_code,
			"workingKey" : get_doc.working_key,
			}
			paymentServiceUrl ='http://35.244.19.176:8081/'
			data = requests.post(paymentServiceUrl+'payment',json=data)
			qr_url = "https://www.ezyinvoicing.com/cc-payment.html?html="+data.text
			qr = qrcode.QRCode(
					version=1,
					box_size=2,
					border=5)
			qr.add_data(qr_url)
			qr.make(fit=True)
			img = qr.make_image(fill='black', back_color='white')
			img.save('Qrcode.png')


	except Exception as e:
		print(str(e))
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Ezy-paytmIntegrate","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
		return {"success":False,"message":str(e)}
