import * as _ from 'lodash';
import { HttpClient, HttpErrorResponse, HttpHeaders, HttpRequest, HttpResponse } from '@angular/common/http';
import { EventEmitter, Injectable, Output } from '@angular/core';

// import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { HttpEventType } from '@angular/common/http';
import { BehaviorSubject, Subscription } from 'rxjs';
import { environment } from 'src/environments/environment';
import { ApiUrls } from 'src/app/shared/api-urls';
import { debounceTime } from 'rxjs/operators';
import moment from 'moment';
// import { Subscription } from 'rxjs/Subscription';

export enum FileQueueStatus {
  Pending,
  Success,
  Error,
  Progress
}

export class FileQueueObject {
  public file: any;
  public status: FileQueueStatus = FileQueueStatus.Pending;
  public progress: number = 0;
  public request: Subscription = null;
  public response: HttpResponse<any> | HttpErrorResponse = null;
  public is_private:any = 0;
  public folder:any ='';
  public doctype:any=''
  public date:any=''
  public attached_to_doctype:any=''
  public attached_to_name:any=''
  constructor(file: any) {
    this.file = file;
  }

  // actions
  public upload = () => { /* set in service */ };
  public cancel = () => { /* set in service */ };
  public remove = () => { /* set in service */ };

  // statuses
  public isPending = () => this.status === FileQueueStatus.Pending;
  public isSuccess = () => this.status === FileQueueStatus.Success;
  public isError = () => this.status === FileQueueStatus.Error;
  public inProgress = () => this.status === FileQueueStatus.Progress;
  public isUploadable = () => this.status === FileQueueStatus.Pending || this.status === FileQueueStatus.Error;

}

@Injectable({
  providedIn: 'root'
})
export class FileuploadProgressbarService {
  public uploadedFiles:any=new EventEmitter()
  public isFilesUploading:any = new EventEmitter()
  // @Output() uploadedFiles: EventEmitter = new EventEmitter();
  public url: string = ApiUrls.uploadFile;

  private _queue: BehaviorSubject<FileQueueObject[]>;
  private _files: FileQueueObject[] = [];

  constructor(private http: HttpClient) {
    this._queue = <BehaviorSubject<FileQueueObject[]>>new BehaviorSubject(this._files);

  }

  // the queue
  public get queue() {
    return this._queue.asObservable();
  }

  // public events
  public onCompleteItem(queueObj: FileQueueObject, response: any): any {
    return { queueObj, response };
  }

  // public functions
  public addToQueue(data: any) {
    // add file to the queue
    console.log(data)
    this._addToQueue(data)
    // _.each(data, (file: any) => this._addToQueue(file));
    // _.each(data, (file: any) => {
    //   console.log(file)
    //   this._addToQueue(file)
    // });

  }

  public clearQueue() {
    // clear the queue
    this._files = [];
    this._queue.next(this._files);
  }

  public uploadAll() {
    // upload all except already successfull or in progress
    _.each(this._files, (queueObj: FileQueueObject) => {
      if (queueObj.isUploadable()) {
        this._upload(queueObj);
      }
    });
  }

  // private functions
  private _addToQueue(file: any) {
    const queueObj = new FileQueueObject(file.files);

    // set the individual object events
    queueObj.upload = () => this._upload(queueObj);
    queueObj.remove = () => this._removeFromQueue(queueObj);
    queueObj.cancel = () => this._cancel(queueObj);
    queueObj.is_private = file.is_private
    queueObj.folder = file.folder
    queueObj.doctype = file.doctype
    queueObj.date = file.date
    queueObj.attached_to_doctype = file.attached_to_doctype
    queueObj.attached_to_name = file.attached_to_name

    // push to the queue
    // console.log(queueObj)
    this._files.push(queueObj);
    this._queue.next(this._files);
  }

  private _removeFromQueue(queueObj: FileQueueObject) {
    _.remove(this._files, queueObj);
  }

  private _upload(queueObj: FileQueueObject) {
    // create form data for file
    console.log('queueObj',queueObj)
    const form = new FormData();

    // let newDate = new Date(queueObj.date).getFullYear()+''+new Date(queueObj.date).getMonth()+1+''+new Date(queueObj.date).getDate()+''+new Date().getHours()+''+new Date().getMinutes()+''+new Date().getSeconds()
    // console.log(newDate)
    let data = new Date(queueObj.date).toISOString().replace(/[\-\.\:ZT]/g,"");
    let dateFormat = moment(queueObj.date).format('YYYY-MM-DD')
    let fileName = "pos-@"+dateFormat+"@"+data+"dwt.pdf"
    if(queueObj.doctype = "POS Checks"){
      form.append('file', queueObj.file, fileName);
    }else{
      form.append('file', queueObj.file, queueObj.file.name);
    }

    form.append('is_private', queueObj.is_private);
    form.append('folder', queueObj.folder);
    // form.append('doctype', queueObj.doctype);
    // form.append('attached_to_doctype', queueObj.attached_to_doctype);
    // form.append('attached_to_name', queueObj.attached_to_name);
    // upload file and report progress
    const req = new HttpRequest('POST', this.url, form, {
      reportProgress: true,
    });

    // upload file and report progress
    queueObj.request = this.http.request(req).pipe(debounceTime(500)).subscribe(
      (event: any) => {
        if (event.type === HttpEventType.UploadProgress) {
          this._uploadProgress(queueObj, event);
        } else if (event instanceof HttpResponse) {
          this._uploadComplete(queueObj, event);
        }
      },
      (err: HttpErrorResponse) => {
        if (err.error instanceof Error) {
          // A client-side or network error occurred. Handle it accordingly.
          this._uploadFailed(queueObj, err);
        } else {
          // The backend returned an unsuccessful response code.
          this._uploadFailed(queueObj, err);
        }
      }
    );

    return queueObj;
  }

  private _cancel(queueObj: FileQueueObject) {
    // update the FileQueueObject as cancelled
    queueObj.request.unsubscribe();
    queueObj.progress = 0;
    queueObj.status = FileQueueStatus.Pending;
    this._queue.next(this._files);
  }

  private _uploadProgress(queueObj: FileQueueObject, event: any) {
    // update the FileQueueObject with the current progress
    const progress = Math.round(100 * event.loaded / event.total);
    queueObj.progress = progress;
    queueObj.status = FileQueueStatus.Progress;
    this._queue.next(this._files);
  }

  private _uploadComplete(queueObj: FileQueueObject, response: HttpResponse<any>) {
    // update the FileQueueObject as completed
    queueObj.progress = 100;
    queueObj.status = FileQueueStatus.Success;
    queueObj.response = response;
    this._queue.next(this._files);
    this.onCompleteItem(queueObj, response.body);
  }

  private _uploadFailed(queueObj: FileQueueObject, response: HttpErrorResponse) {
    // update the FileQueueObject as errored
    queueObj.progress = 0;
    queueObj.status = FileQueueStatus.Error;
    queueObj.response = response;
    this._queue.next(this._files);
  }

}
