import socket

import frappe



@frappe.whitelist(allow_guest=True)
def CheckInternetConnection():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            print('Clossing socket')
            sock.close
        return True
    except OSError:
        pass
    return False