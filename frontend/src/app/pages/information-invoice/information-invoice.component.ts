import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { SocketService } from 'src/app/shared/services/socket.service';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from '../../shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter'
import { HttpClient, HttpEventType } from '@angular/common/http';
import { forkJoin } from 'rxjs';
import { StorageService } from 'src/app/shared/services/storage.service';
import { ToastrService } from 'ngx-toastr';
import { environment } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { degrees, PDFDocument } from 'pdf-lib';
import print from 'print-js'
class InvoicesFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  active = 2;
  /**
   * Limit page length of company filter
   * page length
   */
  search = {
    name: '',
    invoice: '',
    gstNumber: '',
    confirmation: '',
    roomNo: '',
    invoiceType: '',
    uploadType: 'All',
    irn: '',
    sortBy: 'modified',
    filterBy: 'Today',
    filterDate: '',
    orderBy: '',
    has_credit_items: '',
    filterType: 'creation'
  };
}
@Component({
  selector: 'app-information-invoice',
  templateUrl: './information-invoice.component.html',
  styleUrls: ['./information-invoice.component.scss']
})
export class InformationInvoiceComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  invoicesList = [];
  sortingList = [];
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  selectAll = false;
  dupinvoicesList = [];
  companyInfo: any = {};
  loggedInUser;
  bulkFileType = {
    type: '.xml',
    gst: '.csv',
    typeMsg: '',
    gstMsg: '',
    fileType: '/assets/sample-formats-files/invoice-sample.xlsx',
    fileGst: '/assets/sample-formats-files/GSTR-1-4A.CSV'
  }
  active = 1;
  errInvoiceList = [];
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
  modalRef: any;
  apiDomain = environment.apiDomain;
  companyDetails: any;
  previewFile: any;
  constructor(private router: Router,
    private activatedRoute: ActivatedRoute,
    private socketService: SocketService,
    private http: HttpClient,
    private modalService: NgbModal,
    private storage: StorageService,
    private toastr: ToastrService,) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.http.get('/assets/jsons/sortlist.json').subscribe((res: any[]) => this.sortingList = res);
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoicesList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    if (this.activatedRoute.snapshot.queryParams.value && this.activatedRoute.snapshot.queryParams.prop === 'invoice') {
      this.filters.search.gstNumber = this.activatedRoute.snapshot.queryParams.value;
      this.filters.search.filterBy = 'All';
    }
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {

        const dateBy = JSON.parse(res.search);

        this.filters.search.filterBy = dateBy.filterBy;
        this.filters.search.filterType = dateBy.filterType;
        this.filters.search.irn = dateBy.irn;
        this.filters.search.confirmation = dateBy.confirmation;
        this.filters.search.gstNumber = dateBy.gstNumber;
        this.filters.search.roomNo = dateBy.roomNo;
        this.filters.search.name = dateBy.name;
        this.filters.search.invoice = dateBy.invoice;
        this.filters.search.invoiceType = dateBy.invoiceType;
        this.filters.search.uploadType = dateBy.uploadType;
        this.filters.search.has_credit_items = dateBy.has_credit_items;
        if (dateBy.filterDate) {
          this.filters.search.filterDate = [new Date(dateBy.filterDate[0]), new Date(dateBy.filterDate[1])] as any;
        }
      }
    })

    this.getInvoiceList();
  }
  getInvoiceList(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      this.filters.active = parseInt(params.active as any) || 2;
      // const queryParams: any = { filters: [['creation', 'like', '2021-10-01%']] };
      const queryParams: any = { filters: [] };


      if (this.filters.search.confirmation) {
        queryParams.filters.push(['confirmation_no', 'like', `%${this.filters.search.confirmation}%`]);
      }
      if (this.filters.search.name) {
        queryParams.filters.push(['guest_name', 'like', `%${this.filters.search.name}%`]);
      }
      if (this.filters.search.roomNo) {
        queryParams.filters.push(['room_no', 'like', `%${this.filters.search.roomNo}%`]);
      }

      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.fields = JSON.stringify(['*']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.order_by = "`tabInformation Invoices`.`creation` desc";
      const countApi = this.http.get(ApiUrls.information_invoice, {
        params: {
          fields: JSON.stringify(["count( `tabInformation Invoices`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(ApiUrls.information_invoice, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.invoicesList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      this.selectAll = false;
      this.dupinvoicesList = []
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.invoicesList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        data.data['checked'] = false;
        if (this.filters.currentPage !== 1) {
          this.invoicesList = this.invoicesList.concat(data.data)

        } else {
          this.invoicesList = data.data;

        }

      }
    });
  }
  sortBy(type, sort): void {
    this.filters.search.sortBy = `${type}`;
    this.filters.search.orderBy = `${sort}`
    this.updateRouterParams();
  }
  viewModal(content: any, file) {
    this.modalRef = this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic-title',
      // size: 'lg',
      windowClass: 'informationInvoicePdfViewModal',
      centered: true,
    });
    this.fileType(file)
    this.modalRef.result.then((res: any) => {
      // console.log(res)
    })
  }

 async printPDF(file, type) {
   await this.fileType(file)
    setTimeout((res) => {
      if (this.previewFile) {
        print({
          printable: this.previewFile.split(',')[1],
          type: 'pdf',
          base64: true,
        })
      } else {
        alert("Error to Print")
      }
    }, 1000)
  }
  async fileType(originalFileUrl, returnFile = false) {

    let xyz = this.apiDomain + originalFileUrl;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    pdfDoc.setTitle('Information invoice');

    const pages = pdfDoc.getPages();
    const firstPage = this.companyDetails?.pms_payment_qr == 'Last' ? pages[pages.length - 1] : pages[0];
    let sampleImg = this.companyDetails?.pms_payment_qr ? this.apiDomain + this.companyDetails?.pms_payment_qr : null;
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      let pngImage
      await pdfDoc.embedPng(imgBytes).then((res) => {
        pngImage = res
      }).catch(async (err) => {
        await pdfDoc.embedJpg(imgBytes).then((res1) => {
          pngImage = res1
        })

      })

      const pngDims = pngImage.scale(0.6);
      firstPage.drawImage(pngImage, {
        x: parseInt(this.companyDetails.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.companyDetails.qr_rect_y0) - parseInt(this.companyDetails.qr_rect_y1),
        width: parseInt(this.companyDetails.qr_rect_x1),
        height: parseInt(this.companyDetails.qr_rect_y1)
      });
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;

      //  window.open(this.previewFile )

      if (returnFile) {
        return await pdfDoc.save();
      }
      // console.log("Preview File",this.previewFile)
    } else {
      console.log('QR img not found');

    }
  }

  updateRouterParams(): void {

    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/Information_invoice'], {
      queryParams: temp
    });
  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
}
