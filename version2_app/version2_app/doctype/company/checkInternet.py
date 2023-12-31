import frappe
import requests,os,sys,traceback
@frappe.whitelist(allow_guest=True)
def CheckInternetConnection():
    try:
        company = frappe.get_last_doc('company')
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                            'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
                                }
            url = "https://google.com"
            print(proxies)
            res = requests.get(url,proxies=proxies,verify=False)
        else:
            
            url = "https://google.com"
            if company.skip_ssl_verify == 0:
                res = requests.get(url)
            else:
                res = requests.get(url,verify=False)

        print(res.status_code)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(str(e), "      CheckInternet")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Ezy-invoicing CheckInternetConnection","line No:{}\n{}".format(exc_tb.tb_lineno,traceback.format_exc()))
        return False        

