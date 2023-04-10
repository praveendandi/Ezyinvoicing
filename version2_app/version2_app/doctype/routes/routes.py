# Copyright (c) 2023, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr, encode
from frappe.utils.password import check_password
from frappe.model.document import Document

class Routes(Document):
	pass


@frappe.whitelist()
def user_by_roles_companies():
    values =frappe.db.sql('''select `tabHas Role`.role, `tabUser`.username,`tabUser`.email, `tabUser`.full_name,`tabUser`.enabled,`tabUser`.first_name,`tabUser`.full_name from `tabUser` inner join `tabHas Role` on `tabUser`.email=`tabHas Role`.parent where `tabUser`.username  not like 'adm%' and `tabHas Role`.role like 'ezy%' and `tabHas Role`.role not like 'EzyInvoicing%'  order by `tabUser`.email ''',as_dict=1)
    return values,


@frappe.whitelist(allow_guest=True)
def reset_initial_password(user):
    get_user_details = frappe.db.sql(''' select * from `tabUser` Where email = '{user}' '''.format(user=user),as_dict=1)
    if len(get_user_details) <= 0:
        return {'success':False,"message":f'No user found with this email {user}'}
    if get_user_details[0]['last_active'] == None:
        return {'user':get_user_details[0]['email'],'success':True,"message":"New login force to reset"}
    else:
        return {'user':get_user_details[0]['email'],'success':False,"message":"Old login"}
    
    

@frappe.whitelist()
def change_old_password(user,pwd):
    confirm_pwd = check_password(user, pwd, doctype="User", fieldname="password", delete_tracker_cache=True)
    if confirm_pwd == user:
        return {'success':True,"message":"Password matched"}
    else:
        return {'success':False,"message":"Password not matched"}



