from frappe.utils import today
import frappe
from ezy_gst.ezy_gst.doctype.gsp_util_module.login_status import check_gsp_session_status
from frappe.utils import data as date_util
from frappe.utils.dateutils import user_to_str
from ezy_gst.ezy_gst.doctype.gsp_util_module.utils import get_company_details, generate_request_id, return_api_based_on_mode
import requests
import os
import json
file_path = os.path.dirname(__file__)  # <-- absolute dir the script is in


@frappe.whitelist()
def retsave_b2b(company: str, month: str, year: str = None, otp=None,gstr_one_save_name=None):
    '''
    get data from b2b invoices from ezyinvoicing and push to gst portal using adeaqure API
    :param company_code: company_code string
    :param month: month str with mm format
    :parm year: year str with yyyy format and it is optional value
    '''
    try:
        company_code = company
        company = get_company_details(company_code)
        gsp_api_details = frappe.db.get_value(
            'GSP API Details', {'company': company_code}, ["username"], as_dict=1)

        token = check_gsp_session_status(company_code)
        if token.get("token") is not None:
            if year == None:
                year = date_util.getdate(today()).strftime("YYYY")
            start_date = year+'-'+month+"-01"
            # print(start_date)
            end_date = date_util.get_last_day(start_date)
            print(start_date, end_date)

            invoices = frappe.db.get_list('Invoices', filters=[['invoice_date', '<', end_date], ['invoice_date', '>', start_date],
                                                               ['company', '=', company_code], ["invoice_type", "=", "B2B"]],
                                          fields=['name', 'invoice_number', 'invoice_type', 'invoice_date', 'place_of_supply', 'total_invoice_amount', 'gst_number'])

            invoices_count = len(invoices)
            invoices_with_items = construct_b2b_data(invoices, company)
            ret_period = "0"+month+year
            retsave_response, request_id = push_to_save_api(
                invoices_with_items, company, ret_period, token, gsp_api_details, otp,gstr_one_save_name)
            if otp != None:
                save_b2b_retsave(company, invoices_count,
                                 ret_period, retsave_response, request_id)
                update_invoices_with_retsave_status(invoices)

            return {
                "success":True,
                "data":{
                    "request_id":request_id
                }
            }


        else:
            print("token error")
    except Exception as e:
        print(e)


def update_invoices_with_retsave_status(invoices: list):
    '''
    update invoice retsave status in invoices
    :param invoices: invoices list
    '''
    try:
        invoices_names = [invoice.name for invoice in invoices]
        values = {"invoices": invoices_names, "saved_date": today()}
        data = frappe.db.sql(
            """update `tabInvoices` set gstr_saved_status='saved',gstr_saved_date=%(saved_date)s where name in %(invoices)s""", values=values)
        print(data)
        frappe.db.commit()
    except Exception as e:
        pass


def save_b2b_retsave(company: dict, invoices_count: int, ret_period: str, ret_save_response: json, request_id: str):
    '''
    save retsave api response into gstr_one_saved_details doctype
    :param company: company dict
    :param invoices_count: invoices_count int
    :param ret_period: ret_period str
    :param response: response json
    :param request_id: request_id str
    '''
    try:
        gstr1_one_batch_save_doc = frappe.new_doc('Gstr One Saved Details')
        gstr1_one_batch_save_doc.company = company.name
        gstr1_one_batch_save_doc.b2b_count = invoices_count
        gstr1_one_batch_save_doc.request_id = request_id
        gstr1_one_batch_save_doc.period = ret_period
        gstr1_one_batch_save_doc.ret_save_response = str(ret_save_response)
        gstr1_one_batch_save_doc.insert()
    except Exception as e:
        print(e)


def push_to_save_api(invoices_with_items: list, company: dict, ret_period: str, token: str, gsp_api_details: dict, otp,gstr_one_save_name):
    '''
    post data to save api
    :param invoices_with_items: invoices_with_items list
    :param company: company dict
    :param ret_period: ret_period string
    :param token: token string
    :param gsp_api_details: gsp_api_details dict
    '''
    try:
        request_data = {
            "gstin": company.gst_number,
            "fp": ret_period,
            "gt": 3782969.01,  # TODO: have to understand and make changes
            "cur_gt": 3782969.01,  # TODO: have to understand and make changes
            "b2b": invoices_with_items
        }

        headers = {
            "username": gsp_api_details.username,
            "state-cd": company.state_code,
            "gstin": company.gst_number,
            "ret_period": ret_period,
            "Authorization": 'Bearer '+token.get("token"),
            "Content-Type": "application/json"
        }
        if gstr_one_save_name != None:
            saved_data = frappe.get_doc(
            'Gstr One Saved Details', gstr_one_save_name)
            headers["requestid"]= saved_data.request_id
        else:
            headers["requestid"]= generate_request_id(company, ret_period)

        if otp != None:
            headers['otp'] = otp
        json_request_data = json.dumps(request_data)
        # print(json_request_data)
        # print("______________")
        # print(headers)

        rel_path = 'apis.json'
        abs_file_path = os.path.join(file_path, rel_path)
        with open(abs_file_path) as f:
            api_list = json.load(f)

        ret_save_api = return_api_based_on_mode(company, api_list['ret_save'])
        print(ret_save_api)
        ret_save_resp = requests.put(
            url=ret_save_api, data=json_request_data,
            headers=headers)
        try:
            retsave = ret_save_resp.json()
            return retsave, headers['requestid']
        except ValueError:
            print(ret_save_resp.text)
            raise
    except Exception as e:
        print(e)


def construct_b2b_data(invoices: list, company: dict):
    '''
    construct b2b data as per gsp api need
    '''
    try:
        retsave_date = []
        for invoice in invoices:
            # print(invoice)
            buyer_gst_nbr = invoice['gst_number']
            if company.environment == "Testing":
                buyer_gst_nbr = "27ASZPA8657N2ZM"
            retsave_invoice = {
                "ctin": buyer_gst_nbr,
                "inv": [{
                    "inum": invoice["invoice_number"],
                    "idt": invoice["invoice_date"].strftime("%d-%m-%Y"),
                    "val": float(invoice["total_invoice_amount"]),
                    "pos": invoice["place_of_supply"],
                    "rchrg": 'N',  # TODO: have to add in ezyinvocing for record purpose
                    "inv_typ": "R",  # TODO: have to add in ezyinvocing for record purpose
                    "diff_percent": 0.65,  # TODO: have to check
                    "itms": []
                }]}

            group_by_gst_rate = '''
            SELECT 
            gst_rate,
            SUM(item_taxable_value) as item_taxable_value,
            SUM(igst_amount) as igst_amount,
            SUM(central_cess_amount) as central_cess_amount,
            SUM(state_cess_amount) as state_cess_amount,
            SUM(cgst_amount) as cgst_amount,
            SUM(sgst_amount) as sgst_amount
            FROM `tabItems` 
            where parent = {parent} GROUP BY gst_rate
            '''.format(parent=invoice['name'])
            # items = frappe.db.get_list('Items', filters=[['parent', '=', invoice['name']]],
            # group_by='gst_rate',
            # fields=['name', 'gst_rate', 'item_taxable_value','igst_amount', 'cgst_amount', 'sgst_amount','central_cess_amount','state_cess_amount'])
            # print(items)
            items = frappe.db.sql(group_by_gst_rate, as_dict=1)
            # print(items)
            for index, item in enumerate(items):
                # print(item,)
                retsave_invoice["inv"][0]['itms'].append({
                    "num": index+1,
                    "itm_det": {
                        "rt": float(item["gst_rate"]),
                        "txval": float(item["item_taxable_value"]),
                        "iamt": float(item["igst_amount"]),
                        "csamt": float(item['central_cess_amount']+item['state_cess_amount']),
                        "camt": float(item["cgst_amount"]),
                        "samt": float(item["sgst_amount"]),
                    }
                })
            retsave_date.append(retsave_invoice)
        return retsave_date
    except Exception as e:
        print(e)


@frappe.whitelist()
def ret_save_submit_with_otp(gstr_one_save_name: str, otp=None):
    '''
    submit otp for retsave api
    :param gstr_one_save_name: gstr_one_save_name string
    :param otp: otp int
    '''
    try:
        saved_data = frappe.get_doc(
            'Gstr One Saved Details', gstr_one_save_name)
        company = get_company_details(saved_data.company)
        gsp_api_details = frappe.db.get_value(
            'GSP API Details', {'company': company.name}, ["username"], as_dict=1)
        if company.environment == 'Testing':
            otp = 575757

        token = check_gsp_session_status(company.name)
        if token.get("token") is not None:
            headers = {
                "username": gsp_api_details.username,
                "state-cd": company.state_code,
                "gstin": company.gst_number,
                "ret_period": saved_data.period,
                "otp": str(otp),
                "Authorization": 'Bearer '+token.get("token"),
                "requestid": saved_data.request_id
            }
            rel_path = 'apis.json'
            abs_file_path = os.path.join(file_path, rel_path)
            with open(abs_file_path) as f:
                api_list = json.load(f)

            ret_save_api = return_api_based_on_mode(
                company, api_list['ret_save'])
            ret_save_resp = requests.put(
                url=ret_save_api, headers=headers)
            try:
                retsave = ret_save_resp.json()
                return retsave
            except ValueError:
                print(ret_save_resp.text)
                raise
        else:
            raise
    except Exception as e:
        print(e)
