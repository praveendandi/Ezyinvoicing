import requests
import pandas as pd

apiUrl = 'http://localhost:8080/OpenKM/services/rest/'
file_path = "D:\code\finaljan.xls"



def create_folder(name):
    '''
    create folder 
    '''
    foderApi = 'folder/createSimple'
    data = "/okm:root" + name
    print(data)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    response = requests.post(apiUrl + foderApi,
                             headers=headers,
                             data=data,
                             auth=('okmAdmin', 'admin'))
    print(response.text)


# create_folder("test")


def create_file(filepath, file,name):
    '''
    create file in specific folder
    '''
    print(file)
    try:
        filepath = filepath.replace("  "," ")
        fileApi = 'document/createSimple'
        headers = {
            'Accept': 'application/json',
        }
        files = {
            'docPath': (None, '/okm:root' + filepath+'/'+name),
            'content': ("document", open(file, 'rb')),
        }
        print('/okm:root' + filepath+'/'+name)
        response = requests.post(apiUrl + fileApi,
                                headers=headers,
                                files=files,
                                auth=('okmAdmin', 'admin'))
        print(response.text)
        return response.json()
        
    except Exception as e:
        print(str(e).split(),"error")
        if "[Errno 2] No such file or directory:" in str(e):
            return False

        elif 'ItemExistsException' in response.text:
            return 'Duplicate'
        elif 'PathNotFoundException' in response.text:
            return 'Folder not avaliable in openkm'
      


# create_file()


def add_meta_group(nodeId):
    '''
    add meta data to document
    '''
    headers = {
        'Accept': 'application/json',
    }
    metaGroupApi = 'propertyGroup/addGroup?nodeId=' + nodeId + '&grpName=okg:gwm'
    response = requests.put(apiUrl + metaGroupApi,
                            headers=headers,
                            auth=('okmAdmin', 'admin'))
    # print(response.text)
    return response.text


# add_meta_group()


def add_meta_data(uuid, name,village,type,filenumber,pagecount):
    '''
    add meta data to doc
    '''
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/xml',
    }
    metaDataApi = 'propertyGroup/setPropertiesSimple?nodeId=' + uuid + '&grpName=okg:gwm'
    data = '<simplePropertiesGroup><simplePropertyGroup><name>okp:gwm.name</name><value>' + name + '</value></simplePropertyGroup><simplePropertyGroup><name>okp:gwm.village</name><value>' + village + '</value></simplePropertyGroup><simplePropertyGroup><name>okp:gwm.type</name><value>' + type + '</value></simplePropertyGroup><simplePropertyGroup><name>okp:gwm.filenumber</name><value>' + filenumber + '</value></simplePropertyGroup><simplePropertyGroup><name>okp:gwm:pagecount</name><value>' + pagecount + '</value></simplePropertyGroup></simplePropertiesGroup>'
    response = requests.put(apiUrl + metaDataApi,
                            headers=headers,
                            data=data,
                            auth=('okmAdmin', 'admin'))
    print(response.text,"**********")
    return response.text


# add_meta_data()

import os
import random
import string

p = '/Users/sumanthreddy/Desktop/projects/openkm/files'


def tree_printer(root):
    #print(root)
    for root, dirs, files in os.walk(root):
        #print(dirs)
        for d in dirs:
            text_path = os.path.join(root, d)
            if len(text_path.split(p)) > 1:
                folder_path = ''
                for index, i in enumerate(
                        text_path.split(p)[1].split('/')[1:]):
                    if len(text_path.split(p)[1].split('/')[1:]) == index + 1:
                        folder_path = folder_path + i
                    else:
                        folder_path = folder_path + i + '/'
                print(folder_path)
                create_folder(folder_path)
            # print(os.path.join(root, d))
        for f in files:
            text_path = os.path.join(root, f)
            if len(text_path.split(p)) > 1:
                file_path = ''
                for index, i in enumerate(
                        text_path.split(p)[1].split('/')[1:]):
                    if len(text_path.split(p)[1].split('/')[1:]) == index + 1:
                        file_path = file_path + i
                    else:
                        file_path = file_path + i + '/'
                # print(file_path, text_path)
                # file_resp = create_file(file_path, text_path)
                # metaGroup = add_meta_group(file_resp['uuid'])
                # print(metaGroup)
                # letters = string.ascii_lowercase
                # numbers = string.digits
                # metaData = add_meta_data(
                #     file_resp['uuid'],
                #     ''.join(random.choice(letters) for i in range(10)),
                #     ''.join(random.choice(numbers) for i in range(10)))
                # print(metaData)

                # print(file_path)

            # print(os.path.join(root, f))
            # print(f, "files")


# tree_printer(p)



p = 'D:\GWMC'

def createFile(path):
    print(os.walk(path))
    for root, dirs, files in os.walk(path):
        #print(dirs)
        for d in dirs:
            text_path = os.path.join(root, d)
            #print(text_path)
            if len(text_path.split(p)) > 1:
                folder_path = ''
                #print(text_path.split(p)[1].split('\/'))
                for index, i in enumerate(
                        text_path.split(p)[1].split('\/')):
                    if len(text_path.split(p)[1].split('\/')) == index + 1:
                        folder_path = folder_path + i
                    else:
                        folder_path = folder_path + i + '/'
                x = folder_path.replace(os.sep, "/")
                print(x,"hie")
                create_folder(x)

#createFile("D:\GWMC")

import time

def upload_files(root,f,meta):
       
    file_resp = create_file(root, f,meta['filenumber'])
    if file_resp != False and file_resp != 'Duplicate' and file_resp != 'Folder not avaliable in openkm':
        metaGroup = add_meta_group(file_resp['uuid'])
        #print(metaGroup,"*(**********************************************************")
        #numbers = string.digits
        #print(meta)
        #time.sleep(1)
        metaData = add_meta_data(
            file_resp['uuid'],
            meta['name'],
            meta['village'],
            meta['type'],
            meta['filenumber'],
            meta['pagecount']
            )
        #print(metaData,"<<<<<<<<<<")

        #print(file_path)

        #print(os.path.join(root, f))
        #print(f, "files")
    elif file_resp == 'Duplicate' :
        pass
    elif file_resp == 'Folder not avaliable in openkm':
        return "Folder not avaliable in openkm"
    else:
        print("elase")
        return "no file found"





def read_xl():
    
    xl_file = pd.read_excel("D://code//finaljan-8.xls",sheet_name="Sheet1",dtype = str)
    #print(xl_file.columns)
    xl_file.dropna(how='all', axis=1, inplace=True)
    xl_file.fillna('', inplace=True)
    xl_file['estatus'] = ''	
    #print(xl_file['File path'])
    for index, row in xl_file.iterrows():
        # print(row['Location'], row['Type of File '])
        # tree_printer(row['Location'])
        file_numbers = row['FILE NUMBERS'].strip()
        file_name = row['File name'].strip()
        if(row['File path'] != ''):
            meta = {
                 "name":file_name,
                 "village":row['VILLAGE'],
                 "type":row['Type OF FILE'],
                 "filenumber":file_numbers,
                 "pagecount":row['Page count']
            }
            file_paths = row['File path'].replace('D:\GWMC','')
            file_name = file_paths[file_paths.rindex(os.sep)+1:]
            folder_path = file_paths+'/'
            replace_forward_slash = folder_path.replace(os.sep,'/')
            full_file_path = row['File path']+file_numbers
            full_file_path = full_file_path.replace(os.sep,'//')
            print(full_file_path)
            #print(row['Location']+'.pdf')
            print(full_file_path)
            rep = upload_files(replace_forward_slash,full_file_path ,meta)
            print(rep)
            row['estatus'] = rep

    xl_file.to_csv(r'D:\code\export_dataframe_new.csv', index = False, header=True)
           

read_xl()
#open('D://GWMC//GOA FINAL RWODATA//PDF//100 TPD MSW  Treatment Facility Calangute_North Goa_Part-1//100 TPD MSW Treatment Facility Calangute_North Goa_Part-1.pdf','rb')

