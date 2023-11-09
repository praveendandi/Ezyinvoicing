import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, EventEmitter, OnInit, ViewChild, Output } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { FileuploadProgressbarService, FileQueueObject } from 'src/app/resuable/fileupload-progressbar/fileupload-progressbar.service';
import { takeUntil } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { SocketService } from 'src/app/shared/services/socket.service';

@Component({
  selector: 'app-bulk-upload-excel-progressbar',
  templateUrl: './bulk-upload-excel-progressbar.component.html',
  styleUrls: ['./bulk-upload-excel-progressbar.component.scss']
})
export class BulkUploadExcelProgressbarComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  @Output() item = new EventEmitter()

  excelUploadData = {
    totalCount: 0,
    createdCount: 0,
    status: ''
  }

  uploadProgress = {
    status: 'NO',
    progress: 0,
    label: 'Uploading',
    color: "secondary",
    data: null
  }
  execeptionError = false;
  execptionData;

  constructor(private socketService: SocketService) { }

  ngOnInit(): void {
     this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      console.log(res)
      this.uploadProgress.status = 'STARTED';
      this.uploadProgress.label = 'Uploading Files';
      // if (res?.message?.type === 'Bulk_upload_invoice_count') {
      //   this.excelUploadData.totalCount = res?.message?.count
      // }
      if (res?.message?.type === 'Bulk_file_invoice_created') {
        this.uploadProgress.color = 'secondary';
        this.excelUploadData.totalCount = res?.message?.count
        // this.excelUploadData.createdCount = this.excelUploadData.createdCount + 1;
        this.excelUploadData.createdCount = res?.message?.invoice_count;

        this.uploadProgress.progress = (this.excelUploadData.createdCount * 100) / this.excelUploadData.totalCount;

        console.log("this.uploadProgress.progress ===", this.excelUploadData.createdCount)

      }
      if (res?.message?.type === 'Bulk_upload_data') {
        this.uploadProgress.data = res.message.data
        this.uploadProgress.progress = 100;
        this.uploadProgress.color = 'success';
        this.uploadProgress.label = 'Processing Files Successful';
        setTimeout(() => {
          this.uploadProgress.status = 'SUCCESS';
          this.excelUploadData.createdCount = 0;
          this.excelUploadData.totalCount = 0;
        }, 1000);

      }
      if (res?.message?.message === 'Bulk Invoices Exception') {
        this.execeptionError = true
        this.execptionData = res?.message
      }
    })
  }


  uploadClose() {
    this.item.emit(false)
  }
  



}


