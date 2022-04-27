import requests
import frappe
from ezy_gst.ezy_gst.doctype.gsp_util_module.utils import get_company_details, generate_request_id, return_api_based_on_mode, generate_headers_based_on_api
from ezy_gst.ezy_gst.doctype.gsp_util_module.login_status import check_gsp_session_status
import json
import os
file_path = os.path.dirname(__file__)  # <-- absolute dir the script is in


@frappe.whitelist()
def submit_gstr_one(company: str, ret_period: str, otp=None):
    '''
    submit saved data to gstr one 
    :param ret_period: ret_period string
    :param company_code: company_code string
    '''
    try:
        company_code = company
        company = get_company_details(company_code)
        token = check_gsp_session_status(company_code)
        if token.get("token") is not None:
            headers = generate_headers_based_on_api(
                company_code, ret_period, token, True, otp)
            rel_path = 'apis.json'

            abs_file_path = os.path.join(file_path, rel_path)
            with open(abs_file_path) as f:
                api_list = json.load(f)
            ret_submit_api = return_api_based_on_mode(
                company, api_list['ret_submit'])
            request_data = {
                "gstin": company.gst_number,
                "ret_period": ret_period
            }
            json_request_data = json.dumps(request_data)
            submit_b2b_resp = requests.post(
                url=ret_submit_api, headers=headers, data=json_request_data)
            try:
                submitb2b = submit_b2b_resp.json()
                return submitb2b
                # return retsave, headers['requestid']
            except ValueError:
                print(submit_b2b_resp.text)
                raise

    except Exception as e:
        print(e)
