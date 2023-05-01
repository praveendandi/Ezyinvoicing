# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.password import check_password
from frappe.model.document import Document
from datetime import date
import datetime
import sys, traceback
from frappe import _


class Routes(Document):
    pass


@frappe.whitelist()
def user_by_roles_companies():
    user_details = frappe.db.get_list("User",['email','first_name','last_name','full_name','username','enabled',],{'username':('not like',('%adm%')),'email':('not like',('guest@example.com'))})
    for i in user_details:
        get_role = frappe.db.get_list("Has Role",{'parent':i['email'],'role':('Like',('%ezy-%'))},['role'])
        if len(get_role) >0:
            i['role'] = get_role[0]['role']
        else:
            i['role'] = None
        get_company = frappe.db.get_list('User Permission',{'user':i['email']},['for_value'])
        if len(get_company)>0:
            i['for_value'] = get_company[0]['for_value']
        else:
            i['for_value'] = None
    return user_details
   


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
        if get_user_details[0]['last_active'] == None and get_user_details[0]['last_password_reset_date'] == None:
            return {'user': get_user_details[0]['email'], 'success': True, "message": "New login force to reset"}
        else:
            if get_user_details[0]['last_active'] != None or get_user_details[0]['last_password_reset_date'] != None:
                last_password_reset_date = frappe.db.get_list('User',filters={'username':user},fields=['last_password_reset_date'], ignore_permissions=True)
                date_obj = last_password_reset_date[0]['last_password_reset_date']
                reset_pwd_after_days =frappe.db.get_single_value("System Settings", "force_user_to_reset_password")
                int_days = int(date_obj.strftime("%d"))
                if reset_pwd_after_days >= int_days:
                    remaining_days = reset_pwd_after_days - int_days
                    if remaining_days == 0:
                        return {"message":"The password of your account has expired."}
                return {'user': get_user_details[0]['email'], 'success': False, "message": "Old login","remaining_days":remaining_days}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("reset_initial_password","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return {"message":"Invalid User"}
       
    

@frappe.whitelist(allow_guest=True)
def change_old_password(user, pwd):
    try:
        confirm_pwd = check_password(
            user, pwd, doctype="User", fieldname="password", delete_tracker_cache=True)
        frappe.log_error("change_old_password",confirm_pwd)

        print(user,pwd,"....................")
        if confirm_pwd == user:
            return {'success': True, "message": "Password matched"}
        else:
            return {'success': False, "message": "Password not matched"}
    except Exception as e:
        return {"message":"Incorrect User or Password"}


@frappe.whitelist(allow_guest=True)
def update_pwd(email,last_password_reset_date,new_password):
    doc = frappe.get_doc("User", email)
    doc.last_password_reset_date = last_password_reset_date
    doc.new_password = new_password
    doc.save(ignore_permissions=True)
    return email

    