# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr, encode
from frappe.utils.password import check_password
from frappe.model.document import Document
from frappe.utils import  date_diff, today
import datetime
import pandas as pd






class Routes(Document):
    pass


@frappe.whitelist()
def user_by_roles_companies():
    values = frappe.db.sql('''select `tabHas Role`.role, `tabUser`.username,`tabUser`.email, `tabUser`.full_name,`tabUser`.enabled,`tabUser`.first_name,`tabUser`.full_name from `tabUser` inner join `tabHas Role` on `tabUser`.email=`tabHas Role`.parent where `tabUser`.username  not like 'adm%' and `tabHas Role`.role like 'ezy%' and `tabHas Role`.role not like 'EzyInvoicing%'  order by `tabUser`.email ''', as_dict=1)
    return values


@frappe.whitelist(allow_guest=True)
def reset_initial_password(user):
    try:
        get_user_details = frappe.db.sql(
            ''' select * from `tabUser` Where email = '{user}' or username = '{username}' '''.format(user=user, username=user), as_dict=1)
        if len(get_user_details) <= 0:
            return {'success': False,
                    "message": f'No user found with this email {user}',
                    "email": get_user_details[0]['email'],
                    "username": get_user_details[0]['username']}
        if get_user_details[0]['last_active'] == None:
            return {'user': get_user_details[0]['email'], 'success': True, "message": "New login force to reset"}
        else:
            return {'user': get_user_details[0]['email'], 'success': False, "message": "Old login"}
    except Exception as e:
        return {"message":"Invalid User"}
       
    

@frappe.whitelist(allow_guest=True)
def change_old_password(user, pwd):
    try:
        confirm_pwd = check_password(
            user, pwd, doctype="User", fieldname="password", delete_tracker_cache=True)
        if confirm_pwd == user:
            return {'success': True, "message": "Password matched"}
        else:
            return {'success': False, "message": "Password not matched"}
    except Exception as e:
        return {"message":"Incorrect User or Password"}
    

@frappe.whitelist(allow_guest=True)
def reset_password_reminder(username):
    last_password_reset_date = frappe.db.get_list('User',filters={'username':username},fields=['last_password_reset_date']) or today()
    reset_pwd_after_days =frappe.db.get_single_value("System Settings", "force_user_to_reset_password")
    start_date = datetime.datetime.now() + datetime.timedelta(reset_pwd_after_days)
    days = (datetime.datetime.now()-start_date).days
    return {"no of days left to change password":days}



