from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
import frappe

abs_path = os.path.dirname(os.getcwd())
company = frappe.db.get_list('company',['name','ipp_port','folios_folder_path'])
print(company)
folder_path = abs_path+company[0]["folios_folder_path"]+company[0]["name"]
class MyHandler(PatternMatchingEventHandler):
    patterns=["*.pdf"]
    # This function is for data parsing 
    def process(self, event):
        print("=========================")
    def on_created(self, event):
        self.process(event)



if __name__ == '__main__':
    my_logger.info("Started")
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(MyHandler(), path=folder_path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
