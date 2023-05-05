import requests
import json
import frappe,sys,traceback
import paytmchecksum as PaytmChecksum
from datetime import datetime



@frappe.whitelist()
def paytmIntegrate(total_amount,check_no,outlet):
    try:
        paytmParams = dict()
        now = datetime.now()
        date_time = now.strftime("%d%m%Y")
        get_doc= frappe.get_doc('Paytm Settings')
        secret_key = get_doc.get_password(fieldname='merchant_key',raise_exception=True)
        # client = get_doc.Client(auth=(get_doc.merchant_key, sec))
        paytmParams["body"] = {
            "mid"           : get_doc.merchant_id,
            "orderId"       : date_time+check_no,
            "amount"        : total_amount,
            "businessType"  : "UPI_QR_CODE",
            "posId"         : outlet
        }
        checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), secret_key)

        paytmParams["head"] = {
            "clientId"	        : "C11",
            "version"	        : "v1",
            "signature"         : checksum
        }

        post_data = json.dumps(paytmParams)

        # for Staging
        # url = "https://securegw-stage.paytm.in/paymentservices/qr/create"

        # for Production
        url = "https://securegw.paytm.in/paymentservices/qr/create"
        response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
        if "body" in response.keys():
            return {"success":True,"short_url":response["body"]["qrData"]}
        else:
            return response
    except Exception as e:
        print(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-paytmIntegrate","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success":False,"message":str(e)}