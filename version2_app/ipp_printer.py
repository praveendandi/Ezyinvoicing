# import asyncio
# import os,shlex
# import frappe
# from subprocess import Popen, PIPE, STDOUT
# def safe_decode(string, encoding='utf-8'):
#     try:
#         string = string.decode(encoding)
#     except Exception:
#         pass
#     return string

# def main():
#     abs_path = os.path.dirname(os.getcwd())
#     company = frappe.db.get_list('company',['name','ipp_port','folios_folder_path'])
#     if len(company)>0:
#         folder_path = abs_path+company[0]["folios_folder_path"]+company[0]["name"]
#         if not os.path.isdir(folder_path):
#             os.mkdir(folder_path)
#         commands = "python -m ippserver --host 0.0.0.0 --port "+company[0]["ipp_port"]+" save --pdf "+folder_path
#         terminal = Popen(shlex.split(commands), stdin=PIPE, stdout=PIPE, stderr=STDOUT)
#         output = safe_decode(terminal.stdout.read(1))
        
# main()
