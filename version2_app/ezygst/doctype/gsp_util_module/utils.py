import frappe
from frappe.utils import data as date_util
from frappe.utils import today
from pymysql.constants.ER import NO
import requests
import time
from datetime import datetime


def get_company_details(company_code: str) -> dict:
    '''
    get company details by company code
    :param company_code: company_code string
    '''
    try:
        company = frappe.get_doc('company', company_code)
        return company
    except Exception as e:
        print(e)


def get_ret_saved_details(name):
    '''
    get ret saved deatils by name
    '''
    try:
        resaved_details = frappe.get_doc('Gstr One Saved Details', name)
        return resaved_details
    except Exception as e:
        print(e)


def generate_request_id(company: str, ret_period: str = None) -> str:
    '''
    generate request id for api
    :param company_code: company_code string
    :param ret_period: company_code string
    '''
    try:
        now = datetime.now()
        epoch = time.mktime(now.timetuple())
        print(epoch)

        if ret_period:
            return company.name+'_'+ret_period+'_'+str(epoch).replace('.0', '')
        else:
            return company.name+'_'+str(epoch).replace('.0', '')
    except Exception as e:
        print(e)


def return_api_based_on_mode(company: str, api: str):
    '''
    return api based on compnay mode
    :param company: company_code string
    :param api: company_code string
    '''
    try:
        if company.environment != "Testing":
            return api.replace('/test', '')
        else:
            return api
    except Exception as e:
        print(e)


def generate_headers_based_on_api(company_code: str, ret_period: str, token: dict,required_otp:bool=False,otp:str=None) -> dict:
    '''
    :param company_code: company_code string

    generate headers based api
    '''
    try:
        company = get_company_details(company_code)
        gsp_api_details = frappe.db.get_value(
            'GSP API Details', {'company': company_code}, ["username"], as_dict=1)

        
        headers = {
            "username": gsp_api_details.username,
            "state-cd": company.state_code,
            "gstin": company.gst_number,
            "ret_period": ret_period,
            "Authorization": 'Bearer '+token.get("token"),
            "Content-Type": "application/json",
            "requestid": generate_request_id(company, ret_period),
        }
        if required_otp==True:
            if otp != None:
                headers['otp'] = otp
            elif company.environment != "Testing":
                raise 'Otp required'
            else:
                headers['otp'] = '575757'

        print(headers)
        return headers
    except Exception as e:
        print(e)
