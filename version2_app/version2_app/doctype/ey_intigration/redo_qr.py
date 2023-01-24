import frappe
import requests
import sys
import random
from frappe.utils import logger
from version2_app.version2_app.doctype.ey_intigration.api_urls import test_irn,prod_irn
from version2_app.version2_app.doctype.ey_intigration.api_urls import test_redo_qr,prod_redo_qr
import base64
import traceback
import qrcode




def create_ey_qr_code(invoice_number,data ={}):
    try:
        
        invoice = frappe.get_doc('Invoices', invoice_number)

        folder_path = frappe.utils.get_bench_path()
        company = frappe.get_doc('company', invoice.company)
        site_folder_path = company.site_name
        path = folder_path + '/sites/' + site_folder_path + "/private/files/"						   					   
        file_name = invoice.name+"b2b" + "qr.png"
        full_file_path = path + file_name
        # print(full_file_path)
        if len(data.keys())>0:
            if invoice.invoice_category == "Tax Invoice":
                category = "INV"
            elif invoice.invoice_category == "Debit Invoice":	
                category = "DBN"
            else:
                category = "CRN"
            
            payload = {
                    "Irn": invoice.irn_number,
                    "suppGstin":invoice.gst_number,
                    "docNo": invoice.name,
                    "docDate": invoice.invoice_date,
                    "docType": category
            }
            gsp = frappe.db.get_value('GSP APIS', {"company": company.name,
                    "provider":company.provider}, [
                    'auth_test', 'auth_prod', 'gsp_test_app_id', 'gsp_prod_app_id',
                    'gsp_prod_app_secret', 'gsp_test_app_secret', 'name',
                    'gst__test_username','gst_test_password','gst__prod_username','gst_prod_password',
                    'gsp_test_token','gsp_prod_token'
            ],as_dict=1)
            if company.mode == 'Testing':
                headers = {
                    "accessToken":gsp.gsp_test_app_id,
                    "apiaccesskey":gsp.gsp_test_token,
                    "Content-Type": 'application/json',
                }
                if company.proxy == 0:
                    if company.skip_ssl_verify == 0:
                        qr_response = requests.post(test_redo_qr,
                                                headers=headers,
                                                json=payload,
                                                # stream=True,
                                                verify=False)
                    else:
                        qr_response = requests.post(test_redo_qr,
                                                # headers=headers,
                                                json=payload,
                                                # stream=True,
                                                verify=False)							
                else:
                    proxyhost = company.proxy_url
                    proxyhost = proxyhost.replace("http://", "@")
                    proxies = {
                        'https':
                        'https://' + company.proxy_username + ":" +
                        company.proxy_password + proxyhost}
                    # print(proxies, "     proxy console")
                    qr_response = requests.post(test_redo_qr,
                                            headers=headers,
                                            json=payload,
                                            # stream=True,
                                            proxies=proxies,verify=False)
            else:
                headers = {
                    "apiaccesskey": gsp.gsp_prod_app_id,
                    "accessToken": gsp.gsp_prod_token,
                    "Content-Type": 'application/json',
                }
                if company.proxy == 0:
                    if company.skip_ssl_verify == 0:
                        qr_response = requests.post(prod_redo_qr,
                                                headers=headers,
                                                json=payload,
                                                # stream=True,
                                                verify=False)
                    else:
                        qr_response = requests.post(prod_redo_qr,
                                                headers=headers,
                                                json=payload,
                                                # stream=True,
                                                verify=False)							
                else:
                    proxyhost = company.proxy_url
                    proxyhost = proxyhost.replace("http://", "@")
                    proxies = {
                        'https':
                        'https://' + company.proxy_username + ":" +
                        company.proxy_password + proxyhost}
                    # print(proxies, "     proxy console")
                    qr_response = requests.post(prod_redo_qr,
                                            headers=headers,
                                            # stream=True,
                                            json=payload,
                                            proxies=proxies,verify=False)
            # print(qr_response.text)
            if qr_response.status_code==200:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","create_qr_image":'True',"status":"Success","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)
            else:
                insertGsPmetering = frappe.get_doc({"doctype":"Gsp Metering","create_qr_image":'True',"status":"Failed","company":company.name})
                insertGsPmetering.insert(ignore_permissions=True, ignore_links=True)

            # print(qr_response.text)
            # print(qr_response.json)
        else:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4
            )
            qr.add_data(invoice.qr_code)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(full_file_path)
            
            # print(invoice.qr_code)
            # # imgdata = base64.b64decode(invoice.qr_code)
            # # print(imgdata,"7777777777777777777")
            # # filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
            # with open(full_file_path, 'wb') as f:
            #     f.write(invoice.qr_code)	
        		   					   
        

        # with open(full_file_path, "wb") as f:
        #     for chunk in qr_response.iter_content(1024):
        #         f.write(chunk)

        files = {"file": open(full_file_path, 'rb')}
        print(full_file_path)
        payload = {
            "is_private": 1,
            "folder": "Home",
            "doctype": "Invoices",
            "docname": invoice_number,
            'fieldname': 'qr_code_image'
        }
        site = company.host
        upload_qr_image = requests.post(site + "api/method/upload_file",
                                        files=files,
                                        data=payload)
        response = upload_qr_image.json()
        
        if 'message' in response:
            invoice.qr_code_image = response['message']['file_url']
            invoice.save()
            frappe.db.commit()
            # attach_qr_code(invoice_number, gsp, invoice.company)
            return {"success": True,"message":"Qr Generated Successfully"}
        return {"success": True,"message":"Qr Generated Successfully"}
        
    except Exception as e:
        print(e, "error")
        # frappe.log_error(frappe.get_traceback(), invoice_number)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing qr code","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        # logger.error(f"{invoice_number},     ey qr code,   {str(e)}")
        return {"success": False, "message": str(e)}