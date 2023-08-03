import frappe
import requests
import json
import sys, os, traceback
import text_to_image
from frappe.utils import logger
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


frappe.utils.logger.set_log_level("DEBUG")

@frappe.whitelist()
def sendInvoicesToWhatsApp(data):
    try:
        company = frappe.get_last_doc('company')
        # notid_data = frappe.db.get_list('WhatsApp Credentials', {'notification_type': data['notification_type']}, ['scenario_key', 'template_name','notification_type','api_key','api'])
        if company.whats_app == 1:
            invData = frappe.get_doc('Invoices',data['invoice_number'])
            print(company.domain_url+invData.invoice_file,"-------------------")
            headers = {'Authorization': 'App '+company.api_key}# 2e9e6626d70f854946b88eb638fbe03b-953c7fcf-71ef-433a-a48a-1ad7855a4089'}
            input_data={"scenarioKey": company.scenario_key,
                    "destinations": [
                        {
                            "to": {
                                "phoneNumber": data['mobileNumber']
                            }
                        }
                    ],
                    "whatsApp": {
                        "templateName": "invoice",
                        "mediaTemplateData": {
                            "header": {"documentUrl":company.domain_url+invData.invoice_file,"documentFilename":"Invoice"+data['invoice_number']},
                            "body": {
                                "placeholders": [invData.guest_name,str(invData.invoice_date)]
                            }
                        },
                        "language": "en"
                    }
                }
            r = requests.post(company.api, data=json.dumps(input_data), headers=headers)
            print(r.status_code)
            print(r.json())		
            return {"success":True, "message":"Invoice sent successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("SignEzy sendInvoicesToWhatsApp","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"success": False, "message": str(e)}


# @frappe.whitelist()
# def sendPOSBillsToWhatsApp(data):
#     try:
#         company = frappe.get_last_doc('company')
#         # notid_data = frappe.db.get_list('WhatsApp Credentials', {'notification_type': data['notification_type']}, ['scenario_key', 'template_name','notification_type','api_key','api'])
#         if company.whats_app == 1:
#             invData = frappe.get_doc('Pos Bills',data['name'])
#             # img = Image.new('RGB', (350, 600), color = (79, 109, 137))
#             # d = ImageDraw.Draw(img)
#             # d.text((20,10), invData.raw_text.replace("/n",""), fill=(255,255,0))
#             # img.save('/home/caratred/pil_text.png')
#             # print(company.domain_url+invData.invoice_file,"-------------------")
#             headers = {'Authorization': 'App '+company.api_key}# 2e9e6626d70f854946b88eb638fbe03b-953c7fcf-71ef-433a-a48a-1ad7855a4089'}
#             input_data={"scenarioKey": company.scenario_key,
#                     "destinations": [
#                         {
#                             "to": {
#                                 "phoneNumber": data['mobileNumber']
#                             }
#                         }
#                     ],
#                     "whatsApp": {
#                         "templateName": "dinner_reminder",
#                         "mediaTemplateData": {
#                             # "header": {"documentUrl":company.domain_url+invData.invoice_file,"documentFilename":"Invoice"+data['invoice_number']},
#                             "body": {
#                                 "placeholders": [invData.raw_text.replace("/n","")]
#                             }
#                         },
#                         "language": "en"
#                     }
#                 }
#             r = requests.post(company.api, data=json.dumps(input_data), headers=headers)
#             print(r.status_code)
#             print(r.json())		
#             return {"success":True, "message":"Invoice sent successfully"}
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         frappe.log_error("SignEzy sendInvoicesToWhatsApp","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
#         return {"success": False, "message": str(e)}