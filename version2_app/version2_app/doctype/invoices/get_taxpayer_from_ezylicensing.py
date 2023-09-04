import frappe
import json
import requests
import traceback
import os, os.path,sys
from logging import exception
from frappe.utils import logger
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api")

@frappe.whitelist(allow_guest= True)
def gettaxpayer_from_gst(gstn):
    try:
        company = frappe.get_last_doc('company')
        gsp= frappe.get_last_doc('GSP APIS')
        # headers = {'Content-Type': 'application/json'}
        headers = {'Authorization': "token " + "8af689b810b7742" + ":" + "cbe1df1298593cb",}
        url = company.licensing_host + "/api/method/ezylicensing.ezylicensing.doctype.gst_api_intigration.get_taxpayer_details.get_gst_taxpayer_details?gstn=" + gstn
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                            'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            response = requests.get(url, headers=headers, proxies=proxies,verify=False)
        else:
            if company.skip_ssl_verify == 1:
                response = requests.get(url, headers=headers, verify=False)
            else:
                response = requests.get(url, headers=headers, verify=False)
        response_json = response.json()
        result = {
            'Gstin':None,
            'TradeName':None,
            'LegalName':None,
            'AddrBnm': None,
            'AddrBno': None,
            'AddrFlno': None,
            'AddrSt':None,
            'AddrLoc': None,
            'StateCode': None,
            'AddrPncd':None,
            'TxpType': None,
            'Status': None,
            'BlkStatus':None,
            'DtReg': None,
            'DtDReg': None
        }
       
        if response_json['message']['data']['success'] == True:
            raw_data = response_json['message']['data']['result']
            address = raw_data['pradr']['addr']

            folder_path = frappe.utils.get_bench_path()
            with open(folder_path+"/"+"apps/version2_app/version2_app/version2_app/doctype/invoices/state_code.json") as f:
                json_data = json.load(f)
                for each in json_data:
                    if address.get("stcd")== each['state']:
                        state_code = each['tin']
            
            for key ,value in address.items():
                if 'bnm' == key:
                    result.update({'AddrBnm':value})
                if 'bno' == key:
                    result.update({'AddrBno':value})
                if 'flno' == key:
                    result.update({'AddrFlno':value})
                if 'st' == key:
                    result.update({'AddrSt':value})
                if 'loc' == key:
                    result.update({'AddrLoc':value})
                if 'stcd' == key:
                    result.update({'StateCode':state_code}) 
                if 'pncd' == key:
                    result.update({'AddrPncd':value})
            
            for key , value in raw_data.items():
                if 'gstin' == key:
                    result.update({'Gstin':value})
                if 'tradeNam' == key:
                    result.update({'TradeName':value})
                if 'lgnm' == key:
                    result.update({'LegalName':value})
                if 'dty' == key:
                    result.update({'TxpType':value})
                if 'sts' == key:
                    result.update({'Status':value})
                # if 'sts' == key:
                #     result.update({'BlkStatus':value})
                if 'rgdt' == key:
                    result.update({'DtReg':value})
                # if 'sts' == key:
                #     result.update({'DtDReg':value})
                
            return {'success': True,'message': 'GSTIN details are fetched successfully','result':result}
        else:
            print("Unknown error in get taxpayer details get call  ",
                                response_json)
            error_message = "Invalid GstNumber "+ gstn
            frappe.log_error(frappe.get_traceback(), gstn)
            logger.error(f"{gstn},     gettaxpayer_from_gst,   {response_json['message']}")
            return {
                "success": False,
                "message": error_message,
                "response": response_json
            }
    except Exception as e:
        print(e, "get tax payers")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing gettaxpayer_from_gst Gst","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        logger.error(f"gettaxpayer_from_gst,   {str(e)}")
        return {"success": False, "message": {str(e)}}