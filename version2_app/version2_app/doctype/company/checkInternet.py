<<<<<<< HEAD
import socket
import requests
=======
>>>>>>> fff32afe5ef5984707a07b0e169e82f2965b29d2
import frappe
import requests
@frappe.whitelist(allow_guest=True)
def CheckInternetConnection():
    try:
        company = frappe.get_last_doc('company')
        # print(company.__dict__)
        if company.proxy == 1:
            proxyhost = company.proxy_url
            proxyhost = proxyhost.replace("http://","@")
<<<<<<< HEAD
            proxies = {'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost}
            url = "https://google.com"
            print(proxies, "     proxy console")
            res = requests.get(url,proxies=proxies,verify=False)
=======
            proxies = {'http':'http://'+company.proxy_username+":"+company.proxy_password+proxyhost,
                            'https':'https://'+company.proxy_username+":"+company.proxy_password+proxyhost
                                }
            url = "https://google.com"
            print(proxies)
            res = requests.get(url,proxies=proxies)
>>>>>>> fff32afe5ef5984707a07b0e169e82f2965b29d2
        else:
            url = "https://google.com"
            res = requests.get(url)
        print(res.status_code)
        if res.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(str(e), "      CheckInternet")
        return False        

