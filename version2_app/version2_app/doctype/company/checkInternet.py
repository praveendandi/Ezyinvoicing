import socket
import requests
import frappe



@frappe.whitelist(allow_guest=True)
def CheckInternetConnection():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        company = frappe.get_last_doc('company')
        # print(company.__dict__)
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
            proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            url = "https://google.com"
            print(proxies, "     proxy console")
            res = requests.get(url,proxies=proxies,verify=False)
        else:
            url = "https://google.com"
            res = requests.get(url)
        print(res.status_code)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(str(e), "check internet connection")
        return False