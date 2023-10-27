import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit, Output, ViewChild } from '@angular/core';
import { Observable } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { FileQueueObject, FileuploadProgressbarService } from './fileupload-progressbar.service';

@Component({
  selector: 'app-fileupload-progressbar',
  templateUrl: './fileupload-progressbar.component.html',
  styleUrls: ['./fileupload-progressbar.component.scss']
})
export class FileuploadProgressbarComponent implements OnInit,OnDestroy {

  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  @Output() onCompleteItem = new EventEmitter();

  @ViewChild('fileInput') fileInput;
  queue: Observable<FileQueueObject[]>;
  progressInfos: any =[];

  constructor(
    public uploader: FileuploadProgressbarService,public http : HttpClient) {

  }

  ngOnInit() {
    // this.queue = this.uploader.queue;
    // this.uploader.onCompleteItem = this.completeItem;
    this.uploader.uploadedFiles.pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      console.log(res,'-------------',res?.attached_to_doctype)
      this.uploader.clearQueue()
      res?.files.forEach((result:any)=>{
        let data ={
          files:result.file,
          is_private : res.is_private,
          upload_type: res.type,
          folder:res.folder,
          date:res.date,
          doctype:res.doctype,
          attached_to_doctype:res?.attached_to_doctype,
          attached_to_name:res?.attached_to_name
        }

        this.uploader.addToQueue(data);
      })
      // console.log( this.uploader.queue)
      this.queue = this.uploader.queue;
      console.log(this.queue)
      this.uploader.onCompleteItem = this.completeItem;

      console.log('jsjsjsj')
      setTimeout(() => {
        console.log('loading')
        this.uploader.uploadAll()
      }, 500);
    })


  }

  completeItem = (item: FileQueueObject, response: any) => {
    this.onCompleteItem.emit({ item, response });
  }

  addToQueue() {
    const fileBrowser = this.fileInput.nativeElement;
    console.log(this.uploader)

    this.uploader.addToQueue(fileBrowser.files);
    // console.log(this.uploader)
  }
  async filesUploads(selectedFiles){
    const apiCalls = selectedFiles.map((info,idx) => {
      return new Promise((resolve, reject) => {
        console.log(info)
        this.progressInfos[idx] = { uploadProgress: 0, parserProgress: 0, color: 'info', fileName: info.file.name};
        let data = new Date().toISOString().replace(/[\-\.\:ZT]/g,"");
        let fileName = "pos-"+data+"dwt.pdf"
         var formData = new FormData();
         formData.append('file', info.file, fileName);
         formData.append('is_private', '1');
         formData.append('folder', 'Home');
         formData.append('doctype', Doctypes.posChecks);
         formData.append('attached_to_doctype', info.attached_to_doctype);
         formData.append('attached_to_name', info.attached_to_name);
         this.http.post(ApiUrls.uploadFile,formData,{
          reportProgress: true, observe: "events",
         }).subscribe((event:any)=>{
           if(event){
            if (event.type === HttpEventType.UploadProgress) {
              this.progressInfos[idx].uploadProgress = Math.round((100 * (event.loaded / event.total)));
            }
            if (event.type === HttpEventType.Response) {
              let responseParser:any = event.body
              // this.allFilesUplaoded = true;
              if(responseParser?.message){
                this.progressInfos[idx].color = 'success';
                resolve(idx);
              }else{
                this.progressInfos[idx].color = 'danger';
                resolve(idx);
              }
            }

           }}, err => {
            this.progressInfos[idx].value = 0;
            this.progressInfos[idx].color = 'danger';
            // this.message = 'Could not upload the file:' + info.file.name;
          })
         })
    });
    await Promise.all(apiCalls);
    // this.allFilesUplaoded = true;
  }
  close(){
    this.uploader.isFilesUploading.emit(false)
  }
  ngOnDestroy(): void {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}

