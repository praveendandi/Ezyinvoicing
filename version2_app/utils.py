import base64
import frappe
import requests
import os
import sys
import json
from weasyprint import HTML
from frappe.utils import cstr


def html_to_pdf(html_data, filename, name, etax=False):
    try:
        company = frappe.get_last_doc('company')
        if not company.host:
            return {'success': False, 'message': "please specify host in company"}
        cwd = os.getcwd()
        site_name = cstr(frappe.local.site)
        htmldoc = HTML(string=html_data, base_url="")
        file_path = cwd + "/" + site_name + "/public/files/" + filename + name + '.pdf'
        htmldoc.write_pdf(file_path)
        files_new = {"file": open(file_path, 'rb')}
        payload_new = {'is_private': 1, 'folder': 'Home', 'doctype': 'Summaries',
                       'docname': name, 'fieldname': filename}
        file_response = requests.post(company.host+"api/method/upload_file", files=files_new,
                                      data=payload_new).json()
        frappe.log_error(json.dumps(file_response), html_to_pdf)
        if "file_url" in file_response["message"].keys():
            os.remove(file_path)
        else:
            return {"success": False, "message": "something went wrong"}
        return {"success": True, "file_url": file_response["message"]["file_url"]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("html_to_pdf",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}
    

@frappe.whitelist()
def convert_image_to_base64(image):
    try:
        company = frappe.get_last_doc("company")
        folder_path = frappe.utils.get_bench_path()
        file_path1 = (
            folder_path
            + "/sites/"
            + company.site_name
            + image
        )
        with open(file_path1, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        encoded_str = encoded_string.decode("utf-8")
        return {"success": True, "data": encoded_str}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("convert_image_to_base64",
                         "line No:{}\n{}".format(exc_tb.tb_lineno, str(e)))
        return {"success": False, "message": str(e)}