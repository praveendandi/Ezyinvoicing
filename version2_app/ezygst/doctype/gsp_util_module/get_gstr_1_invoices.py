from ezy_gst.ezy_gst.doctype.gsp_util_module.utils import get_company_details, generate_request_id, return_api_based_on_mode, generate_headers_based_on_api
from ezy_gst.ezy_gst.doctype.gsp_util_module.login_status import check_gsp_session_status

import frappe
import requests
import os
import json
file_path = os.path.dirname(__file__)  # <-- absolute dir the script is in


@frappe.whitelist()
def get_gst_saved_invoices(company: str, ret_period: str):
    '''
    get saved invoices from gstr portal
    :param company_code: company_code string
    :param ret_period: ret_period string
    '''
    try:
        company_code = company
        company = get_company_details(company_code)

        token = check_gsp_session_status(company_code)
        if token.get("token") is not None:
            headers = generate_headers_based_on_api(
                company_code, ret_period, token)

            rel_path = 'apis.json'
            abs_file_path = os.path.join(file_path, rel_path)
            with open(abs_file_path) as f:
                api_list = json.load(f)

            get_b2b_api = return_api_based_on_mode(
                company, api_list['get_b2b'])
            get_b2b_api = get_b2b_api.replace(
                'GSTNUMBER', company.gst_number)
            get_b2b_api = get_b2b_api.replace(
                'RETRUNPERIOD', ret_period)
            print(headers)
            get_b2b_resp = requests.get(
                url=get_b2b_api, headers=headers)
            try:
                getb2b = get_b2b_resp.json()
                insert_gstr_one_saved_date(getb2b)
                return {"sucess":True}
                # return retsave, headers['requestid']
            except ValueError:
                print(get_b2b_resp.text)
                raise

    except Exception as e:
        print(e)


def insert_gstr_one_saved_date(invoices:dict):
    '''
    insert gstr one save data
    :param invoices: invoices dict
    '''
    try:
        print(invoices)
        invoices = invoices['b2b'][0]['inv']
        for invoice in invoices:
            inv = frappe.new_doc('GSTR One Saved Invoices')
            inv.invoice_number = invoice['inum']
            inv.invoice_type = invoice['inv_typ']
            inv.invoice_date = invoice['idt']
            inv.invoice_total_value = invoice['val']
            inv.place_of_supply = invoice['pos']
            inv.chksum = invoice['chksum']
            items = []
            for item in invoice['itms']:
                items.append({
                    "cgst_amount":item['itm_det']['camt'],
                    "sgst_amount":item['itm_det']['samt'],
                    "igst_amount":item['itm_det']['iamt'],
                    "gst_rate":item['itm_det']['rt'],
                    "cess_amount":item['itm_det']['csamt'],
                    "taxvalue":item['itm_det']['txval']
                })
            inv.insert()
            ezy_invoice = frappe.get_doc('Invoices', invoice['inum'])
            ezy_invoice.gstr_filed = True
            ezy_invoice.save()


    except Exception as e:
        print(e)
