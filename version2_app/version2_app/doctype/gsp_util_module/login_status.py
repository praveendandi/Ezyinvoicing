import frappe
import json
import os
import datetime
from frappe.utils import data as date_util
from frappe.utils import today
from frappe.utils import dateutils


import requests
file_path = os.path.dirname(__file__) #<-- absolute dir the script is in


def check_gsp_session_status(company_code)->dict:
    '''
    check token validity if not valid do login 

    :param company_code: string
    '''
    try:
        token_data = dict()
        gsp = frappe.db.get_value('GSP API Details', {'company':company_code}, ['expires_in', 'api_token','app_id','app_secret','name','token_created_on'], as_dict=1)
        if gsp.api_token == None or gsp.api_token == '':
            data = gsp_login(gsp.name,gsp.app_id,gsp.app_secret,company_code)
            token_data['token'] = data.api_token
        else:
            seconds = int(gsp.expires_in)
            seconds_in_day = 60 * 60 * 24
            days = seconds // seconds_in_day
            date_time = date_util.add_to_date(None,days=days,as_string=True)
            token_create_date = date_util.get_date_str(gsp.token_created_on)
            difference_date = date_util.date_diff(date_time,token_create_date)
            if difference_date<=1:
                data = gsp_login(gsp.name,gsp.app_id,gsp.app_secret,company_code)
                token_data['token'] = data.api_token
            else:
                token_data['token'] = gsp.api_token

        return token_data
    except Exception as e:
        #todo make logger
        print(e)



def gsp_login(name,app_id,app_secret,company_code) -> dict:
    '''
    Login with gsp using company app_id and app_secret
    :param name: string
    :param app_id: string
    :param app_secret: string
    :param company_code: string
    '''
    try:
        rel_path = 'apis.json'
        abs_file_path = os.path.join(file_path, rel_path)
        with open(abs_file_path) as f:
            api_list = json.load(f)
        headers = {
            "gspappid": app_id,
            "gspappsecret": app_secret,
        }
        login = requests.post(url=api_list['login_api'],headers=headers)
        try:
            login_response = login.json()
            login_deatils = frappe.get_doc('GSP API Details',name)
            login_deatils.expires_in = login_response['expires_in']
            login_deatils.api_token = login_response['access_token']
            login_deatils.token_created_on = today()
            login_deatils.save()
            login_deatils = frappe.get_doc('GSP API Details',name)
            # print(login_deatils.__dict__)
            return login_deatils
        except ValueError:
            print(login.text,"error")
            raise
    except Exception as e:
        #todo make logger
        print(e)

