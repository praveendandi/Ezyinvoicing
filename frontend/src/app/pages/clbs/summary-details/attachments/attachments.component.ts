import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { PerfectScrollbarConfigInterface } from 'ngx-perfect-scrollbar';
import { ToastrService } from 'ngx-toastr';
import { PDFDocument } from 'pdf-lib';
import { takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { FiScannerService } from 'src/app/shared/services/fi-scanner.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-attachments',
  templateUrl: './attachments.component.html',
  styleUrls: ['./attachments.component.scss']
})
export class AttachmentsComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  active = 1;
  folios: any = []
  filteredFoliosByCategory: any = [];
  filePdf: any
  openedDoc: any = {}
  paramsID: any;
  company: any = {}
  fileTypes: any = []
  fileData: any = {}
  uploadDocType = ''
  apiDomain = environment.apiDomain;
  filename;
  fileToUpload;
  pdfView = true;
  previewFile: any;
  summaryData: any = {};
  fileImg: any;
  public config: PerfectScrollbarConfigInterface = {};
  activeCategoryIndex: any;
  activeCategory: any;
  containerId = "dwtcontrolContainer";
  doc_type;
  constructor(
    private http: HttpClient,
    private router: Router,
    public toaster : ToastrService,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private scannerService : FiScannerService
  ) { }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
    this.activatedRoute.params.subscribe((res: any) => this.paramsID = res?.id)
    if (this.paramsID) {

      this.getSummaryDetails();
      // this.getDocumentTypeList();
      // this.getDocumentsList()
    }
    // this.scannerService.dynamSoftOnload(false,this.containerId);
    this.scannerService.scannedFileUploadedRes.pipe(takeUntil(this.destroyEvents)).subscribe((res:any)=>{
      if(!res){return;}
      if(res.message){
        
      }
    })
  }
  getSummaryDetails() {
    this.active = this.activeCategoryIndex ? this.activeCategoryIndex : 1
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`).subscribe((res: any) => {
      if (res) {
        this.summaryData = res.data;

        this.getDocumentTypeList();

      }
    })
  }
  onChangeCategory(each: any,activeIndex :any) {
    this.activeCategoryIndex = activeIndex
    this.activeCategory = each

    this.openedDoc = {}
    this.filePdf = ""
    this.previewFile = ""
    this.filteredFoliosByCategory = [];
    if (each) {
      this.filteredFoliosByCategory = this.folios.filter((item: any) => {
        if (item?.document_type == each?.name) {
          item['document_name'] = item.document.substring(item?.document.indexOf('/files/') + 7);
          return item;
        }
      })
      if(activeIndex == 'pos_bills'){
        this.filteredFoliosByCategory = this.activeCategory.filter((item: any) => {
            item['document_name'] = item.document.substring(item?.document.indexOf('/files/') + 7);
            return item;
          
        })
      }
      if (this.filteredFoliosByCategory.length > 0) {
        this.openedDoc = this.filteredFoliosByCategory[0]
        setTimeout(() => {
          this.filePdf = `${this.apiDomain}/${this.openedDoc?.document}`
          let fileType = this.filePdf.split('.').reverse();
          fileType = fileType[0]
          if (fileType) {
            this.fileImg = (fileType == 'png' || fileType == 'jpeg' || fileType == 'jpg') ? true : false
            if (!this.fileImg) {
              this.fileType(null, true);
            }
          }
        }, 2000)
      }
    }
  }
  onPosbillsTab(activeIndex:any){
    this.activeCategoryIndex = activeIndex
    this.http.get(`${ApiUrls.getPosChecksData}`, {
      params: {
        summary:this.paramsID
      }
    }).subscribe((res:any)=>{
      if(res.message.success){
        this.onChangeCategory(res.message.checks,activeIndex)
      }else{
        this.previewFile = "";this.filePdf = "";this.openedDoc = {};
        this.filteredFoliosByCategory = []
        this.toaster.error(res.message.message)
      }
    })
  }
  onChangeTab(each: any) {
    this.filePdf = ""
    this.previewFile = ""
    this.openedDoc = {}
    if (each) {
      this.openedDoc = each;
      setTimeout(() => {
        this.filePdf = `${this.apiDomain}${this.openedDoc?.document}`
        let fileType = this.filePdf.split('.').reverse();
        fileType = fileType[0]
        if (fileType) {
          this.fileImg = (fileType == 'png' || fileType == 'jpeg' || fileType == 'jpg') ? true : false
          if (!this.fileImg) {
            this.fileType(null, true);
          }
        }
      }, 1500)
      // this.filePdf = `${this.apiDomain}${this.openedDoc?.document}`

    }
  }

  addDocuments(addDocument) {
    this.fileData = {}
    this.filename = "";

    let modal = this.modal.open(addDocument, { centered: true, size: 'md' })
  }
  getDocumentTypeList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, {
      params: {
        fields: JSON.stringify(['*']),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        this.fileTypes = res?.data;
        this.getDocumentsList()
      }
    })
  }

  getDocumentsList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaryDocuments}`, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['summary', '=', this.paramsID]]),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        this.folios = res?.data;
        this.filteredFoliosByCategory = res?.data.filter((item: any) => {
          let activeCat = this.activeCategory?.name ? this.activeCategory?.name : this.fileTypes[0]?.name
          if (item?.document && item?.document_type == activeCat) {
            item['document_name'] = item.document.substring(item?.document.indexOf('/files/') + 7);
            return item;
          }
        })
        if (this.filteredFoliosByCategory.length != 0) {
          this.openedDoc = this.filteredFoliosByCategory[0]
          setTimeout(() => {
            this.filePdf = `${this.apiDomain}/${this.openedDoc?.document}`
            let fileType = this.filePdf.split('.').reverse();
            fileType = fileType[0]
            if (fileType) {
              this.fileImg = (fileType == 'png' || fileType == 'jpeg' || fileType == 'jpg') ? true : false
              if (!this.fileImg) {
                this.fileType(null, true);
              }
            }
          }, 2000)

        }
      }
    })
  }

  handleFileInput(files: File[], field_name) {

    this.filename = files[0]?.name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
          this.fileData = res.message;
        }
      })
    }
  }
  saveDocumentFile(form: NgForm, modal) {
    if(form.invalid){
      form.form.markAllAsTouched()
      return
    }
    let obj = {
      doctype: Doctypes.summaryDocuments,
      company: this.company?.name,
      document_type: form.value.document_type,
      summary: this.paramsID,
      invoice_number: form.value.invoice_no || null,
      document: this.fileData?.file_url
    }
    const formData = new FormData();
    formData.append('doc', JSON.stringify(obj));
    formData.append('action', 'Save');

    this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
      if (res?.docs[0]?.name) {
        modal.close();
        this.openedDoc = ""; this.filePdf = ""; this.active = 1
        this.getSummaryDetails()
        // this.getDocumentsList()
      }
    })

  }

  /*****Attach QR to pdf */

  async fileType(title: any, returnFile = false) {
    this.pdfView = true;
    let qrPng;
    let invoiceTitle = 'Tax Invoice';
    qrPng = this.openedDoc.qr_code_image;
    let xyz = this.apiDomain + this.openedDoc?.document;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes,{ ignoreEncryption: true });
    pdfDoc.setTitle(invoiceTitle);

    const pages = pdfDoc.getPages();
    const firstPage = this.company?.qr_page == 'Last' ? pages[pages.length - 1] : pages[0];
    let sampleImg = qrPng ? this.apiDomain + qrPng : null;
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      const pngImage = await pdfDoc.embedPng(imgBytes);
      const pngDims = pngImage.scale(0.6);
      firstPage.drawImage(pngImage, {
        x: parseInt(this.company.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.company.qr_rect_y0) - parseInt(this.company.qr_rect_y1),
        width: parseInt(this.company.qr_rect_x1),
        height: parseInt(this.company.qr_rect_y1)
      });
      // if (this.invoiceInfo?.invoice_type == 'B2B') {
      //   if (this.company.irn_text_alignment === "Horizontal") {
      //     const page = this.company.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

      //     page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}`, {
      //       x: this.company?.irn_text_point1,
      //       y: page.getHeight() - parseInt(this.company.irn_text_point2),
      //       size: 8
      //     });
      //   } else {
      //     const page = this.company.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

      //     page.drawText(`IRN : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_irn_number : this.invoiceInfo?.irn_number}    ACK : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_no : this.invoiceInfo?.ack_no}    Date : ${this.invoiceInfo?.invoice_category == 'Credit Invoice' ? this.invoiceInfo?.credit_ack_date : this.invoiceInfo?.ack_date}    GSTIN : ${this.invoiceInfo?.gst_number}`, {
      //       x: 10, y: 25, rotate: degrees(90), size: 8
      //     });

      //   }

      // }
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;
      if (returnFile) {
        return await pdfDoc.save();
      }
    } else {
      console.log('QR img not found');

    }
  }
  deleteSupportingDoc(){
    if(this.openedDoc.document_type == "Invoices"){
      return;
    }
    if (!window.confirm(`Are you sure to delete file`)) {
      return null;
    } else{
      this.http.delete(`${ApiUrls.resource}/${Doctypes.summaryDocuments}/${this.openedDoc?.name}`).subscribe((res: any) => {
        if (res?.message == 'ok') {
          this.openedDoc = {}
          this.filePdf = ""
          this.previewFile = ""
          this.active = this.activeCategoryIndex ? this.activeCategoryIndex : 1
          this.toaster.success("This invoice is deleted")
          this.getSummaryDetails()
        }
      })
    }

  }
  scanToModal(scanToModal){
    let modal = this.modal.open(scanToModal,{
      size:'md',centered:true,backdrop:'static'
    })
  }
}
