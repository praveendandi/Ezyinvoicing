from frappe.utils import today
from frappe.utils import data as date_util
from ezy_gst.ezy_gst.doctype.gsp_util_module.login_status import check_gsp_session_status
from ezy_gst.ezy_gst.doctype.gsp_util_module.utils import get_company_details, get_ret_saved_details,return_api_based_on_mode
import frappe
import requests
import os
import json
file_path = os.path.dirname(__file__)  # <-- absolute dir the script is in


@frappe.whitelist()
def get_gstr_1_request_status(name: str):
    '''
    get request status by request id
    :param name: name string
    :param company_code: company_code string
    '''
    try:
        ret_saved_deatils = get_ret_saved_details(name)
        company = get_company_details(ret_saved_deatils.company)
        gsp_api_details = frappe.db.get_value(
            'GSP API Details', {'company': company.name}, ["username"], as_dict=1)
        token = check_gsp_session_status(company.name)
        if token.get("token") is not None:
            rel_path = 'apis.json'
            abs_file_path = os.path.join(file_path, rel_path)
            with open(abs_file_path) as f:
                api_list = json.load(f)
            print(company.environment)
            ret_status_api =  return_api_based_on_mode(company,api_list['ret_status'])

            ret_status_api = ret_status_api.replace(
                'GSTNUMBER', company.gst_number)
            ret_status_api = ret_status_api.replace(
                'RETRUNPERIOD', ret_saved_deatils.period)
            headers = {
                "username": gsp_api_details.username,
                "state-cd": company.state_code,
                "gstin": company.gst_number,
                "ret_period": ret_saved_deatils.period,
                "Authorization": 'Bearer '+token.get("token"),
                "requestid": ret_saved_deatils.request_id
            }
            ret_status_resp = requests.get(url=ret_status_api, headers=headers)
            try:
                retstatus = ret_status_resp.json()
                update_retstatus_details(retstatus, ret_saved_deatils)
                return retstatus
            except ValueError:
                print(ret_status_resp.text)
                raise

    except Exception as e:
        print(e)


def update_retstatus_details(retstatus_response: json, ret_saved_deatils):
    '''
    update retstatus api response 
    '''
    try:
        ret_saved_deatils.ret_status_response = str(retstatus_response)
        ret_saved_deatils.save()
        return ret_saved_deatils
    except Exception as e:
        print(e)
