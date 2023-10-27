import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy, EventEmitter } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from '../../api-urls';
import { SocketService } from '../../services/socket.service';

@Component({
  selector: 'app-file-uploader',
  templateUrl: './file-uploader.component.html',
  styleUrls: ['./file-uploader.component.scss'],
  // changeDetection: ChangeDetectionStrategy.OnPush
})
export class FileUploaderComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  selectedFiles = [];
  progressInfos = [];
  message = '';
  allFilesUplaoded = false;
  companyDetails;
  
  constructor(
    private http: HttpClient,
    private activeModal: NgbActiveModal
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    
  }

  selectFiles(files) {
    Array.from(files).forEach(file => {
      this.selectedFiles.push({ progress: 0, file });
    });
  }
  removeFromList(file, i) {
    this.selectedFiles.splice(i, 1)
  }

  async uploadFiles() {
    this.message = '';
    const apiCalls = this.selectedFiles.map((info,idx) => {
      return new Promise((resolve, reject) => {
        this.progressInfos[idx] = { uploadProgress: 0, parserProgress: 0, color: 'info', fileName: info.file.name};
        const formData = new FormData();
        formData.append('file', info.file);
        formData.append('is_private', '1');
        formData.append('folder', 'Home');
        // formData.append('doctype', Doctypes.invoices);
        // formData.append('fieldname', 'invoice');
        // formData.append('attached_to_name','1');
        this.http.post(ApiUrls.uploadFile, formData, {
          reportProgress: true, observe: "events",
        }).subscribe((event) => {
          if (event.type === HttpEventType.UploadProgress) {
            this.progressInfos[idx].uploadProgress = Math.round((100 * (event.loaded / event.total)) / 2);
          }
          if (event.type === HttpEventType.Response) {
            this.progressInfos[idx].color = 'warning';
            let response:any = event.body;
            let dataObj = {
              filepath: response?.message?.file_url
            }
            let api = this.companyDetails?.new_parsers == 0 ? `${ApiUrls.reinitiate}` : `${ApiUrls.new_reinitiate}`
            this.http.post(`${api}${this.companyDetails?.name}.${'invoice_parser.file_parsing'}`, dataObj, {
              reportProgress: true, observe: "events",
            }).subscribe((event) => {
             if (event.type === HttpEventType.DownloadProgress) {
                this.progressInfos[idx].parserProgress = Math.round((100 * (event.loaded / event.total) / 2));
              }
              if (event.type === HttpEventType.Response) {
                let responseParser:any = event.body
                this.allFilesUplaoded = true;
                if(responseParser?.message?.success){
                  this.progressInfos[idx].color = 'success';
                  
                  resolve(idx);
                }
                
              }
            });
          }

        }, err => {
          this.progressInfos[idx].value = 0;
          this.message = 'Could not upload the file:' + info.file.name;
        })
      })
    });
    await Promise.all(apiCalls);
    this.allFilesUplaoded = true;
    // console.log('All calls resoved',this.allFilesUplaoded );

  }



  closeModal() {
    this.allFilesUplaoded = false;
    this.activeModal.close()
  }

  closeModalRefrsh(){
    this.allFilesUplaoded = false;
    this.activeModal.close('refresh')
  }
}
