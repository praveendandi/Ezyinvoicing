import { StorageService } from './../../../shared/services/storage.service';
import { ApiUrls, Doctypes } from './../../../shared/api-urls';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import * as Moment from 'moment';
import moment from 'moment';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin, merge } from 'rxjs';
import { environment } from 'src/environments/environment';
import { FileUploaderComponent } from 'src/app/shared/models/file-uploader/file-uploader.component';
import { DateToFilter } from 'src/app/shared/date-filter'
import { SocketService } from 'src/app/shared/services/socket.service';
import { degrees, PDFDocument } from 'pdf-lib';
import print from 'print-js'
import { Message } from '@angular/compiler/src/i18n/i18n_ast';
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
    filterType: 'creation',
    error_message: '',
    synced_to_erp: '',
    invoice_date: ''
  };
}
@Component({
  selector: 'app-invoices',
  templateUrl: './invoices.component.html',
  styleUrls: ['./invoices.component.scss']
})
export class InvoicesComponent implements OnInit, OnDestroy {
  @ViewChild('addModal') addModal: ElementRef;
  @ViewChild('excelUpload') excelUpload: ElementRef;
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  sortingList = [];
  invoicesList = [];
  dupinvoicesList = [];
  gstList = [];
  syncList: any = {}
  selectedMonth = moment(new Date()).format('MMM')
  selectedyear = 2022;
  p = 1;
  years = [];
  gst_number;
  syncError: any = {}
  invoice_number;
  synced_to_erp;
  active = 1;
  apiDomain = environment.apiDomain;
  selectedInvoice;
  gerenateIRNITems = false;
  selectAll = false;
  redoErrItems = false;
  errInvoiceList = [];
  companyInfo: any = {};
  uploadProgress = {
    status: 'NO',
    progress: 0,
    label: 'Uploading',
    color: "secondary",
    data: null
  }
  excelUploadData = {
    totalCount: 0,
    createdCount: 0,
    status: ''
  }
  loggedInUser;
  invoiceInfo;
  previewFile;
  execeptionError = false;
  execptionData;
  bulkFileType = {
    type: '.xml',
    gst: '.csv',
    typeMsg: '',
    gstMsg: '',
    fileType: '/assets/sample-formats-files/invoice-sample.xlsx',
    fileGst: '/assets/sample-formats-files/GSTR-1-4A.CSV'
  }

  singleFile = false;
  doubleFiles = false;
  upload_bulk_invoices_disable = false;


  redoErrDateSelection
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private toastr: ToastrService,
    private socketService: SocketService,
    private storage: StorageService,
    // private activeModal : NgbActiveModal
  ) {

  }

  ngOnInit(): void {

    this.companyInfo = JSON.parse(localStorage.getItem('company'))
    console.log(this.companyInfo.company_code)
    this.filters.itemsPerPage = this.companyInfo?.items_per_page
    this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (res?.message?.message === 'Invoices Created') {
        this.getInvoiceList();
      }
      if (res?.message?.message === 'Invoice deleted') {
        setTimeout((res: any) => {
          this.getInvoiceList();
        }, 1000)
      }
      if (res?.message?.message === 'Duplicate Invoice') {
        // window.alert(`Duplicate Invoice ${res?.message?.invoice_number}`)
        this.toastr.error(res?.message?.invoice_number, 'Duplicate Invoice', { disableTimeOut: false })
      }
      if (res?.message?.type == 'redo error') {
        this.errInvoiceList = this.errInvoiceList.map((each: any) => {
          if (each.invoice_number == res.message.invoice_number) {
            each['status'] = res?.message?.status
          }
          return each;
        })
      }
      if (res?.message?.type === 'Bulk_upload_invoice_count') {
        this.excelUploadData.totalCount = res?.message?.count
      }
      if (res?.message?.type === 'Bulk_file_invoice_created') {
        // this.activeModal.dismiss();
        this.modal.dismissAll();
        this.upload_bulk_invoices_disable = true
        this.excelUploadData.createdCount = this.excelUploadData.createdCount + 1

        this.uploadProgress.progress = (this.excelUploadData.createdCount * 100) / this.excelUploadData.totalCount

        // console.log("this.uploadProgress.progress ===", this.uploadProgress.progress)
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
      if (res?.message?.message === 'Bulk Invoices Completed') {
        this.upload_bulk_invoices_disable = false;
        this.getInvoiceList()
      }
      if (res?.message?.message === 'Bulk Invoices Exception') {
        this.execeptionError = true
        this.execptionData = res?.message
      }
    })

    // setTimeout(() => {
    this.storage.select('company').subscribe((res) => this.companyInfo = res);
    // console.log(this.companyInfo)
    // }, 6000);

    this.storage.select('login').subscribe((res) => this.loggedInUser = res);
    this.http.get('/assets/jsons/sortlist.json').subscribe((res: any[]) => this.sortingList = res);
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoicesList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });

    // if (this.companyInfo?.bulk_excel_upload_type === 'Marriot') {
    //   this.bulkFileType = { type: '.xml', gst: '.csv', typeMsg: 'D110 with .xml', gstMsg: 'GSTR-1-4A with .csv ', fileType: '/assets/sample-formats-files/D110.xml', fileGst: '/assets/sample-formats-files/GSTR-1-4A.CSV' }
    // } else if (this.companyInfo?.bulk_excel_upload_type === 'HolidayIn') {
    //   this.bulkFileType = { type: '.xml', gst: '', typeMsg: ' .xml', gstMsg: 'GSTR-1-4A with .csv ', fileType: '/assets/sample-formats-files/D110.xml', fileGst: '' }
    // } else if (this.companyInfo?.bulk_excel_upload_type === 'Opera') {
    //   this.bulkFileType = { type: '.xlsx', gst: '.csv', typeMsg: ' .xlsx', gstMsg: 'GSTR-1-4A with .csv ', fileType: '/assets/sample-formats-files/opera.xlsx', fileGst: '' }
    // } else if (this.companyInfo?.bulk_excel_upload_type === 'Hyatt') {
    //   this.bulkFileType = { type: '.csv', gst: '.csv', typeMsg: ' .csv', gstMsg: 'GSTR-1-4A with .csv ', fileType: '/assets/sample-formats-files/hyatt.CSV', fileGst: '' }
    // }
    if (this.companyInfo?.bulkupload_inovice_file_type == 'csv') {
      this.bulkFileType.type = '.csv';
      this.bulkFileType.typeMsg = '.csv';
      this.bulkFileType.fileType = '/assets/sample-formats-files/hyatt.CSV';
    }
    if (this.companyInfo?.bulkupload_inovice_file_type == 'xml') {
      this.bulkFileType.type = '.xml';
      this.bulkFileType.typeMsg = 'D110 with .xml';
      this.bulkFileType.fileType = '/assets/sample-formats-files/folio_details6666795.xml';
    }
    if (this.companyInfo?.bulkupload_inovice_file_type == 'xlsx') {
      this.bulkFileType.type = '.xlsx';
      this.bulkFileType.typeMsg = '.xlsx';
      this.bulkFileType.fileType = '/assets/sample-formats-files/opera.xlsx';
    }
    if (this.companyInfo?.bulkupload_gst_file_type == 'csv') {
      this.bulkFileType.gst = '.csv';
      this.bulkFileType.gstMsg = 'GSTR-1-4A with .csv';
      this.bulkFileType.fileGst = '/assets/sample-formats-files/GSTR-1-4A.CSV';
    }
    if (this.companyInfo?.bulkupload_gst_file_type == 'xml') {
      this.bulkFileType.gst = '.xml';
      this.bulkFileType.gstMsg = '.xml';
      this.bulkFileType.fileGst = '/assets/sample-formats-files/folio_details6666795.xml';
    }
    if (this.companyInfo?.bulkupload_gst_file_type == 'xlsx') {
      this.bulkFileType.gst = '.xlsx';
      this.bulkFileType.gstMsg = '.xlsx';
      this.bulkFileType.fileGst = '/assets/sample-formats-files/opera.xlsx';
    }

    if (this.activatedRoute.snapshot.queryParams.filterType == "invoice_date") {
      this.filters.search.filterType = "invoice_date";
    }

    if (this.activatedRoute.snapshot.queryParams.invoice_date) {
      this.filters.search.invoice_date = this.activatedRoute.snapshot.queryParams.invoice_date;
      this.filters.search.filterBy = "All";
      this.filters.search.invoiceType = this.activatedRoute.snapshot.queryParams.invoiceType
      this.filters.active = 1;
    }
    if (this.activatedRoute.snapshot.queryParams.irn_generated) {
      this.filters.search.irn = this.activatedRoute.snapshot.queryParams.irn_generated;
    }
    if (this.activatedRoute.snapshot.queryParams.filterBy == "All") {
      this.filters.search.filterBy = "All";
    }
    if (this.activatedRoute.snapshot.queryParams.value && this.activatedRoute.snapshot.queryParams.prop === 'invoice') {
      this.filters.search.gstNumber = this.activatedRoute.snapshot.queryParams.value;
      this.filters.search.filterBy = 'All';
      this.active = 2;
    }

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {

        console.log(res)
        const dateBy = JSON.parse(res.search);
        console.log(dateBy)
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
        this.filters.search.error_message = dateBy.error_message;
        this.filters.search.synced_to_erp = dateBy.synced_to_erp;
        this.filters.search.invoice_date = dateBy.invoice_date;
        if (dateBy.filterDate) {
          this.filters.search.filterDate = [new Date(dateBy.filterDate[0]), new Date(dateBy.filterDate[1])] as any;
        }
        if (res.active == 2) {
          this.filters.search.invoice_date = ''
        }
      }
    })
    // this.activatedRoute.params.subscribe((res:any)=>{
    //   console.log("Activated params ====",typeof res.prev)
    //   if(res.prev){
    //   let xyz =  JSON.parse(res.prev)
    //   console.log(xyz)
    //   }
    // })
    this.getInvoiceList();
    this.getYear()
  }
  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    // if(this.activatedRoute.snapshot.queryParams.filterType == "invoice_date"){
    //   this.router.navigate(['home/invoices'], {
    //     queryParams: null
    //   });
    // }else{
    this.router.navigate(['home/invoices'], {
      queryParams: temp
    });
    // }


  }

  refreshParams(): void {
    // this.invoicesList = [];
    this.filters.itemsPerPage = 20;
    this.filters.currentPage = 1;
    this.filters.start = 0;
    this.filters.active = 2;
    this.filters.totalCount = 0;
    this.filters.search.name = '';
    this.filters.search.invoice = ''
    this.filters.search.gstNumber = ''
    this.filters.search.confirmation = '';
    this.filters.search.roomNo = '';
    this.filters.search.invoiceType = '';
    this.filters.search.uploadType = 'All';
    this.filters.search.irn = '';
    this.filters.search.sortBy = 'modified';
    this.filters.search.filterBy = 'Today';
    this.filters.search.filterType = 'creation'
    this.filters.search.filterDate = '';
    this.filters.search.orderBy = ''
    this.filters.search.has_credit_items = '';
    this.filters.search.invoice_date = ""
    this.selectAll = false;
    this.dupinvoicesList = [];
    // this.router.navigate(['home/invoices']);
    this.getInvoiceList();
    // this.updateRouterParams()
    this.dupinvoicesList = [];
  }

  getInvoicesCount(): void {
    this.http.get(ApiUrls.invoices, {
      params: {
        fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getInvoiceList()
    })
  }
  getInvoiceList(): void {
    console.log("empty hand")
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      this.filters.active = parseInt(params.active as any) || this.filters.active || 2;
      // const queryParams: any = { filters: [['invoice_category', '=', 'Tax Invoice']] };

      const queryParams: any = { filters: [] };

      if (this.filters.active === 1) {
        queryParams.filters.push(["Invoices", 'irn_generated', 'in', ["Pending", "Error"]], ['invoice_type', "like", "B2B"]);
      } else if (this.filters.active === 3) {
        queryParams.filters.push(['invoice_type', "like", "B2C"]);
      } else if (this.filters.active === 5) {
        queryParams.filters.push(['invoice_type', "like", "B2B"]);
      } else if (this.filters.active === 4) {
        queryParams.filters.push(['irn_generated', "like", "Error"]);
        queryParams.filters.push(['error_message', "like", `%${this.filters.search.error_message}%`]);
        // queryParams.filters.push(["Invoices", 'irn_generated', 'in', ["Error", "NA"]], ["Invoices", 'qr_generated', 'in', ["Error", "Pending"]]);

      } else if (this.filters.active === 6) {
        queryParams.filters.push(['converted_from_b2c', "like", "Yes"]);
      } else if (this.filters.active === 7) {
        queryParams.filters.push(['irn_generated', "like", "Zero Invoice"])
        // queryParams.filters.push(["Invoices", 'irn_generated', 'in', ["NA", "Zero Invoice"]], ["Invoices", 'qr_generated', 'in', ["Zero Invoice", "Pending"]]);
      } else {
        if (this.filters.search.irn) {
          queryParams.filters.push(['irn_generated', 'in', this.filters.search.irn]);
        }
      }
      if (this.filters.active === 8) {
        queryParams.filters.push(['pos_checks', "=", '1']);
      }
      if (this.filters.search.confirmation) {
        queryParams.filters.push(['confirmation_number', 'like', `%${this.filters.search.confirmation}%`]);
      }
      if (this.filters.search.invoice) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.search.invoice}%`]);
      }
      if (this.filters.search.gstNumber) {
        queryParams.filters.push(['gst_number', 'like', `%${this.filters.search.gstNumber}%`]);
      }
      if (this.filters.search.invoiceType) {
        queryParams.filters.push(['invoice_type', '=', this.filters.search.invoiceType]);
      }
      if (this.filters.search.synced_to_erp != '') {
        queryParams.filters.push(['synced_to_erp', 'like', `%${this.filters.search.synced_to_erp}%`]);
      }
      if (this.filters.search.uploadType === 'Web') {
        queryParams.filters.push(['invoice_from', '=', 'Web']);
      }
      if (this.filters.search.uploadType === 'Pms') {
        queryParams.filters.push(['invoice_from', '=', 'Pms']);
      }
      if (this.filters.search.uploadType === 'File') {
        queryParams.filters.push(['invoice_from', '=', 'File']);
      }
      if (!this.filters.search.uploadType || this.filters.search.uploadType == 'All') {
        queryParams.filters.push(['invoice_from', '!=', 'Web']);
      } else {
        queryParams.filters.push(['invoice_from', '=', this.filters.search.uploadType]);
      }

      // if (this.filters.search.irn) {
      //   queryParams.filters.push(['irn_generated', 'in', this.filters.search.irn]);
      // }
      if (this.filters.search.name) {
        queryParams.filters.push(['guest_name', 'like', `%${this.filters.search.name}%`]);
      }
      if (this.filters.search.roomNo) {
        queryParams.filters.push(['room_number', 'like', `%${this.filters.search.roomNo}%`]);
      }
      if (this.filters.search.has_credit_items) {
        queryParams.filters.push(['has_credit_items', 'like', `%${this.filters.search.has_credit_items}%`]);
      }
      if (this.filters.search.sortBy) {
        queryParams.order_by = '`tabInvoices`.`' + this.filters.search.sortBy + '` ' + this.filters.search.orderBy + '';
      }
      if (this.filters.search.invoice_date) {
        queryParams.filters.push(['invoice_date', '=', `${this.filters.search.invoice_date}`]);
      }

      if (this.filters.search.filterBy) {
        if (this.filters.active == 1 || this.filters.active == 4 || this.filters.active == 7) {

        } else {
          if (this.filters.search.filterBy === 'Custom') {
            if (this.filters.search.filterDate) {
              const filter = new DateToFilter('Invoices', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
              if (filter) {
                queryParams.filters.push(filter);
              }
            }
          } else if (this.filters.search.filterBy !== 'All') {
            const filter = new DateToFilter('Invoices', this.filters.search.filterBy, null, this.filters.search.filterType).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }
        }
      }


      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.fields = JSON.stringify(['*']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.order_by = "`tabInvoices`.`creation` desc";
      const countApi = this.http.get(ApiUrls.invoices, {
        params: {
          fields: JSON.stringify(["count( `tabInvoices`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(ApiUrls.invoices, { params: queryParams });
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

          // const oneDay = 24 * 60 * 60 * 1000;
          // let today_date:any = new Date()
          // let date_expiry:any = new Date(each.invoice_date);
          // date_expiry.setDate(date_expiry.getDate() + 7);
          // each['expiry_date'] = date_expiry.toLocaleDateString()
          // each['expiry_days'] = Math.round(Math.abs((date_expiry - today_date) / oneDay))

          let today_date: any = Moment(each?.invoice_date).format('YYYY-MM-DD')

          let date_expiry: any = this.companyInfo?.e_invoice_missing_start_date ? Moment(this.companyInfo?.e_invoice_missing_start_date).format('YYYY-MM-DD') : null
         
          if (this.companyInfo?.e_invoice_missing_date_feature && today_date >= date_expiry) {
            let today_date: any = Moment(new Date()).format('YYYY-MM-DD')
            // let date_expiry: any = Moment(Moment(each?.invoice_date).add(7, 'd').format('YYYY-MM-DD'))
            let date_expiry: any = Moment(Moment(each?.invoice_date).add(this.companyInfo.no_of_days_to_expiry, 'd').format('YYYY-MM-DD'))

            date_expiry = Moment(date_expiry).format('YYYY-MM-DD')
            each['expiry_date'] = Moment(date_expiry).format('YYYY-MM-DD')
           
            each['expiry_days'] = Moment(date_expiry).diff(Moment(today_date), 'days')

            console.log("each == ", each)
          }


        }
        return each;
      })
      console.log(data.data)
      if (data.data) {
        data.data['checked'] = false;
        if (this.filters.currentPage !== 1) {
          this.invoicesList = this.invoicesList.concat(data.data)
          // this.invoicesList = this.invoicesList.map((res:any)=>{
          //   if(res){
          //    res.error_message = res?.error_message.substring(1, res?.error_message.length-1)
          //   }
          //   return res;
          // })
        } else {
          this.invoicesList = data.data;

        }

      }
    });
  }

  /**
   * Navigates company component
   * @params data
   * @params type
   */
  navigate(data: any, type: string): void {
    this.router.navigate(['/home/company-details'], { queryParams: { id: data.sNo, type } });
  }
  onDateFilterChange() {
    this.filters.currentPage = 1;
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
  onDateFilterType() {
    this.updateRouterParams();
  }
  sortBy(type, sort): void {
    this.filters.search.sortBy = `${type}`;
    this.filters.search.orderBy = `${sort}`
    this.updateRouterParams();
  }

  addInvoice() {
    const modalRef = this.modal.open(this.addModal, {
      size: 'lg',
      centered: true
    });
  }

  // getSynctoGst() {
  //   this.http.get(ApiUrls.bulk_sync_ezygst).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.toastr.success(res.message.message);
  //       this.getInvoiceList()
  //     } else {
  //       this.toastr.error(res.message.message)
  //     }
  //   })
  // }


  getGstFilters(e): void {
    const params = {
      filters: JSON.stringify([['gst_number', 'like', `%${e.target.value}%`]])
    }
    this.http.get(ApiUrls.taxPayerDefault, { params: params }).subscribe((res: any) => {
      console.log(res)
      this.gstList = res.data
    })
  }

  SyncErrorLogs(submodel, invoice) {
    this.modal.open(submodel, { size: 'lg', centered: true, })
    this.syncList = invoice;
  }

  getYear() {
    var currentYear = new Date().getFullYear()
    var startYear = currentYear;
    for (var i = startYear; i <= currentYear; i++) {
      this.years.push(i++);
    }
    return this.years;
  }


  //  syncModel(content) {
  //     this.modal.open(content, {size:'md', centered: true,});
  //   }

  addInvoiceSubmit(): void {

  }

  onTabChange(e) {
    this.selectAll = false;
    this.dupinvoicesList = []
    this.active = e.nextId;
    this.filters.active = e.nextId;
    this.invoicesList = [];
    this.filters.start = 0;
    this.filters.totalCount = 0;
    this.filters.currentPage = 1;
    if (this.filters.active === 2) {
      this.filters.search.irn = '';
    }
    this.updateRouterParams();
  }


  printInvoice(invoice) {
    let printData = localStorage.getItem('printer');

    this.http.post(ApiUrls.print, { invoiceNumber: invoice?.invoice_number, printer: printData }).subscribe((res: any) => {
      console.log(res)
      if (res?.message?.success) {
        this.toastr.success(res?.message?.message)
      }
    })
  }

  async print(invoice) {
    this.selectedInvoice = invoice
    this.http.get(`${ApiUrls.invoices}/${invoice?.name}`).subscribe((res: any) => {
      console.log(res)
      if (res.data) {
        this.invoiceInfo = res?.data;
        if (invoice?.irn_generated == 'Success') {
          this.fileType('Tax Invoice');
        } else {
          this.fileType('Original Invoice');
        }
        if (this.previewFile.includes('/private/')) {
          print({
            printable: this.previewFile,
            type: 'pdf'
          })
        } else {
          print({
            printable: this.previewFile.split(',')[1],
            type: 'pdf',
            base64: true,
          });
        }


      }
    })
    //   const iframe = document.createElement('iframe');
    //   iframe.style.display = 'none';
    //   iframe.src = this.apiDomain + invoice?.invoice_file;
    //   document.body.appendChild(iframe);
    //   if (iframe.src) {
    //     setTimeout(() => { iframe.contentWindow.print() })
    //   }
  }

  async fileType(title: string, returnFile = false) {
    // this.pdfView = true;
    let qrPng;
    if (title == "Original Invoice") {
      qrPng = '';
      this.previewFile = this.apiDomain + this.invoiceInfo?.invoice_file;
      return;
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2B') {
      qrPng = this.invoiceInfo.qr_code_image;
    }
    if (title == "Tax Invoice with Credits") {
      qrPng = this.invoiceInfo.credit_qr_code_image;
    }
    if (title == "Tax Invoice" && this.invoiceInfo.invoice_type == 'B2C') {
      qrPng = this.invoiceInfo.b2c_qrimage;
    }
    // this.previewFile = type
    let xyz = this.apiDomain + this.invoiceInfo?.invoice_file;
    const existingPdfBytes = await fetch(xyz).then(res => res.arrayBuffer())
    const pdfDoc = await PDFDocument.load(existingPdfBytes, { ignoreEncryption: true });
    pdfDoc.setTitle(title);

    const pages = pdfDoc.getPages();
    const firstPage = pages[0];
    let sampleImg = qrPng ? this.apiDomain + qrPng : null;
    if (sampleImg) {
      const imgBytes = await this.http.get(sampleImg, { responseType: 'arraybuffer' }).toPromise();
      const pngImage = await pdfDoc.embedPng(imgBytes);
      const pngDims = pngImage.scale(0.6);
      firstPage.drawImage(pngImage, {
        x: parseInt(this.companyInfo.qr_rect_x0),
        y: firstPage.getHeight() - parseInt(this.companyInfo.qr_rect_y0) - parseInt(this.companyInfo.qr_rect_y1),
        width: parseInt(this.companyInfo.qr_rect_x1),
        height: parseInt(this.companyInfo.qr_rect_y1)
      });
      if (this.invoiceInfo?.invoice_type == 'B2B') {
        if (this.companyInfo.irn_text_alignment === "Horizontal") {
          const page = this.companyInfo.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo.irn_number}    ACK : ${this.invoiceInfo.ack_no}    Date : ${this.invoiceInfo.ack_date}`, {
            x: this.companyInfo?.irn_text_point1,
            y: page.getHeight() - parseInt(this.companyInfo.irn_text_point2),
            size: 8
          });
        } else {
          const page = this.companyInfo.irn_details_page === 'Last' ? pages[pages.length - 1] : pages[0];

          page.drawText(`IRN : ${this.invoiceInfo.irn_number}    ACK : ${this.invoiceInfo.ack_no}    Date : ${this.invoiceInfo.ack_date}  Buyer GST : ${this.invoiceInfo.gst_number}`, {
            x: 10, y: 25, rotate: degrees(90), size: 8
          });

        }

      }
      const pdfDataUri = await pdfDoc.saveAsBase64({ dataUri: true, addDefaultPage: true });
      this.previewFile = pdfDataUri;
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.src = this.previewFile;
      document.body.appendChild(iframe);
      if (iframe.src) {
        setTimeout(() => { iframe.contentWindow.print() })
      }
      if (returnFile) {
        return await pdfDoc.save();
      }
      console.log("Preview File", this.previewFile)
    } else {
      console.log('QR img not found');

    }
  }
  redoAllErrorInvoices() {
    let fromDate = moment(this.redoErrDateSelection[0]).format('YYYY-MM-DD')
    let toDate = moment(this.redoErrDateSelection[1]).format('YYYY-MM-DD')
    let data = {
      from_date: fromDate,
      to_date: toDate
    }
    this.http.get(ApiUrls.redo_err_invoices, {
      params: data
    }).subscribe((res: any) => {
      if (res?.message.success) {
        this.toastr.success("Re-process completed")
        this.redoErrItems = true;
        this.getInvoiceList()
      } else {
        this.toastr.error("Error")
      }
    })
  }

  uploadPdfFiles() {
    const modal = this.modal.open(FileUploaderComponent, {
      centered: true, size: 'lg'
    })
    modal.result.then((res: any) => {
      if (res == 'refresh') {
        this.getInvoiceList()
      }
    })
  }
  uploadExcelFile() {
    // if (this.companyInfo?.bulk_excel_upload_type == 'Hyatt Mumbai' || this.companyInfo?.bulk_excel_upload_type == 'Hyatt Hyderabad' || this.companyInfo?.bulk_excel_upload_type == 'Marriot') {
    //   this.doubleFiles = true;
    //   this.singleFile = false;
    // } else {
    //   if (this.companyInfo?.bulk_excel_upload_type != 'Hyatt Mumbai' || this.companyInfo?.bulk_excel_upload_type != 'Marriot') {
    //     this.singleFile = true;
    //     this.doubleFiles = false;
    //   }
    // }
    this.execeptionError = false;
    this.uploadProgress = {
      status: 'NO',
      // status: 'SUCCESS',
      progress: 0,
      label: 'Uploading',
      color: "secondary",
      data: null
      // data: [{ "date": "2020-12-20", "invoice_number": 203, "Pending": 26, "Error": 134, "Success": 43 }]
    }
    const modal = this.modal.open(this.excelUpload, {
      centered: true, size: 'lg', backdrop: 'static'
    })
    modal.result.then((res: any) => {
      if (res == 'refresh') {
        this.getInvoiceList()
      }
    })
  }
  async uploadExcels(invoiceInp: HTMLInputElement, gstInp: HTMLInputElement) {
    console.log(gstInp, "Input ===", invoiceInp)
    const validateFileType = (input: HTMLInputElement, name: string) => {
      // Allowing file type
      const allowedExtensions = /(\.xlsx|\.csv|\.xml|\.CSV)$/i;
      // console.log("============",allowedExtensions,input.value)
      if (!allowedExtensions.exec(input.value)) {
        alert(`Invalid "${name} Details Document" File`);
        input.value = '';
        return false;
      }
      return true;
    }
    const [con1, con2] = [validateFileType(invoiceInp, 'Invoice'), (!gstInp ? true : validateFileType(gstInp, 'GST'))];
    // returning if invalid files
    console.log(con1, con2)
    if (!(con1 && con2)) {
      return;
    }
    this.uploadProgress.status = 'STARTED';
    this.uploadProgress.label = 'Uploading Files';
    // this.modal.dismissAll();
    // const intervalRef = setInterval(() => {
    //   if (this.uploadProgress.progress < 90) {
    //     this.uploadProgress.progress++;
    //   }
    // }, 2000);

    // file uploading
    const upload = async (file: File) => {
      return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('is_private', '1');
        formData.append('folder', 'Home');
        formData.append('doctype', Doctypes.invoices);
        formData.append('docname', 'Manual-Upload-' + Moment(new Date()).format('YYYY/MM/DD'));
        let progress = 0;
        this.http.post(ApiUrls.uploadFile, formData).subscribe(
          (res: any) => {
            resolve(res.message?.file_url);
          }, (err) => {
            resolve(0);
          }, () => {
          });
      });
    }
    /** getting uploaded invoice urls */
    let invoiceUrl, gstUrl;
    if (invoiceInp.files[0]) {
      invoiceUrl = await upload(invoiceInp.files[0]);
    }
    if (gstInp?.files[0]) {
      console.log("gst Inp")
      gstUrl = await upload(gstInp.files[0]);
    }
    // const [invoiceUrl, gstUrl] = await Promise.all([upload(invoiceInp.files[0]), upload(gstInp.files[0])]);
    if (!invoiceUrl || gstInp ? !gstUrl : false) {
      // clearInterval(intervalRef);
      this.uploadProgress.label = 'Failed to upload invoices';
      this.uploadProgress.color = 'danger';
      this.uploadProgress.status == 'ERROR';
      return;
    }
    /** sending uploaded invoice urls  */
    const payload = {
      data: {
        invoice_file: invoiceUrl,
        gst_file: gstUrl,
        company: this.companyInfo.name,
        username: this.loggedInUser.username
      }
    };
    this.uploadProgress.label = 'Processing Files';
    this.http.post(ApiUrls.xlBulkInvoice, payload).toPromise();
    // this.http.post(ApiUrls.xlBulkInvoice, payload).subscribe((res: any) => {
    //   if (res?.message.success) {
    //     this.uploadProgress.progress = 100;
    //     this.uploadProgress.color = 'success';
    //     this.uploadProgress.label = 'Processing Files Successful';
    //     this.uploadProgress.data = res.message.data;
    //     setTimeout(() => {
    //       this.uploadProgress.status = 'SUCCESS';
    //     }, 1000);
    //   } else {
    //     // failure case
    //     console.log('its faileur', res);

    //     this.uploadProgress.color = 'danger';
    //     this.uploadProgress.status = 'ERROR';
    //     this.uploadProgress.label = 'Failed to Process Files';
    //   }
    //   // clearInterval(intervalRef);
    // }, (err) => {
    //   console.log(err);
    //   this.uploadProgress.color = 'danger';
    //   this.uploadProgress.status = 'ERROR';
    //   this.uploadProgress.label = 'File Processing Failed';
    //   // clearInterval(intervalRef);
    // })

  }

  /** Multiple Irn generation */
  checkedItemsAll(event) {
    if (this.selectAll) {
      this.dupinvoicesList = this.invoicesList.filter((each: any) => {
        if (each.irn_generated == "Pending") {
          each.checked = true
        }
        return each;
      })
    } else {
      this.dupinvoicesList = this.invoicesList.filter((each: any) => {
        if (each.irn_generated == "Pending") {
          each.checked = false
        }
        return each;
      })
    }
    this.dupinvoicesList = this.invoicesList.filter((each: any) => each.checked)
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
    console.log(this.dupinvoicesList)
  }

  checkedItems(event, item) {
    const temp = this.invoicesList.filter((each: any) => each.checked);
    this.selectAll = temp.length == this.invoicesList.length;
    this.dupinvoicesList = temp;
    this.dupinvoicesList = this.dupinvoicesList.map((each: any) => {
      if (each) {
        each['doctype'] = Doctypes.invoices
      }
      return each;
    })
    console.log(this.dupinvoicesList)
  }
  openModalIRN(multiGenerateIrn) {
    if (!window.confirm(`All rebates would be adjusted automatically before QR(IRN) generation. Do you wish to continue?`)) {
      return null;
    } else {
      let modalData = this.modal.open(multiGenerateIrn, { centered: true, size: 'md' })
      modalData.result.then((res: any) => {
        if (res == 'generated') {
          this.dupinvoicesList = []
          this.gerenateIRNITems = false;
          this.getInvoiceList()
        }

      })
    }
  }

  async generateIrn() {
    // if (!window.confirm(`Are you sure to generate IRN? `)) {
    //   return null;
    // } else {
    const apiCalls = this.dupinvoicesList.map((each: any, idx) => {

      return new Promise((resolve, reject) => {
        // this.dupinvoicesList[idx] = { uploadProgress: 0, parserProgress: 0, color: 'info', invoice_number: each.invoice_number,name: each.name };
        // const formData = new FormData();
        // formData.append('method', 'generateIrn');
        // formData.append('args', `{"invoice_number":"${each.name}"}`);
        // formData.append('docs', JSON.stringify(each));
        // this.http.post(ApiUrls.generateIrn, formData, {
        //   reportProgress: true, observe: "events",
        // }).subscribe(async (event: any) => {
        //   if (event.type === HttpEventType.UploadProgress) {
        //     this.dupinvoicesList[idx].uploadProgress = Math.round((100 * (event.loaded / event.total)));
        //   }
        //   if (event.type === HttpEventType.Response) {
        //     if (event.body.message.success) {
        //       this.dupinvoicesList[idx].color = 'success';
        //     } else {
        //       this.dupinvoicesList[idx].color = 'danger';
        //     }
        //   }

        this.dupinvoicesList[idx] = { uploaded: '', invoice_number: each.invoice_number, name: each.name, guest_name: each.guest_name };
        // const formData = new FormData();
        // formData.append('method', 'generateIrn');
        // formData.append('args', `{"invoice_number":"${each.name}"}`);
        // formData.append('docs', JSON.stringify(each));
        const dataObj = {
          invoice_number: each.name,
          generation_type: 'Manual',
          bulk_irn: true
        }
        this.http.post(ApiUrls.generateIrn_new, { data: dataObj }).subscribe(async (event: any) => {
          if (event.message.success) {
            this.dupinvoicesList[idx].uploaded = "success";

          } else {
            this.dupinvoicesList[idx].uploaded = "failed";
          }

        }, (err) => {
          resolve
          console.log('err: ', err);
        });
        resolve(idx)
      })

    })
    await Promise.all(apiCalls);
    this.gerenateIRNITems = true;

    // }
  }


  checkPagination(): void {
    console.log(this.invoicesList.length)
    this.filters.currentPage = 1
    this.updateRouterParams()

  }

  openDatesModelRedo(datesSelectionRedoErrors) {
    this.modal.open(datesSelectionRedoErrors, { centered: true, size: 'md' })
  }

  /**Redo Error functionality */
  // openModelRedo(multiRedoErrors) {
  //   // let modalData;
  //   this.http.get(ApiUrls.getErrInvoices).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.errInvoiceList = res.message.data;
  //       let modalData = this.modal.open(multiRedoErrors, { centered: true, size: 'md' })
  //       modalData?.result.then((res: any) => {
  //         console.log(res)
  //         if (res == 'Success') {
  //           this.redoErrItems = false;
  //           this.errInvoiceList = [];
  //           this.getInvoiceList()
  //         }
  //       })
  //     } else {
  //       this.toastr.error()
  //     }
  //   })



  // }
  openModelRedo(multiRedoErrors) {
    // let modalData;
    let today = new Date()
    this.redoErrDateSelection = [new Date(today.getFullYear(), today.getMonth(), 1), today];
    let modalData = this.modal.open(multiRedoErrors, { centered: true, size: 'md' })
    modalData?.result.then((res: any) => {
      console.log(res)
      if (res == 'Success') {
        this.redoErrItems = false;
        this.errInvoiceList = [];
        this.getInvoiceList()
      }
    })
    this.getRedoErrorsList()
  }
  redoErrorDateChange() {
    console.log(this.redoErrDateSelection)
    this.getRedoErrorsList()
  }
  getRedoErrorsList() {
    let fromDate = moment(this.redoErrDateSelection[0]).format('YYYY-MM-DD')
    let toDate = moment(this.redoErrDateSelection[1]).format('YYYY-MM-DD')
    let data = {
      from_date: fromDate,
      to_date: toDate
    }
    this.http.get(ApiUrls.getErrInvoices, {
      params: data
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.errInvoiceList = res.message.data;
        this.redoErrItems = false;
      } else {
        this.redoErrItems = true;
        this.toastr.error(res.message.message)
      }
    })
  }
  ngOnDestroy() {
    this.dupinvoicesList = [];
    this.errInvoiceList = [];
    this.gerenateIRNITems = false;
    this.redoErrItems = false;
    this.modal.dismissAll()
    this.destroyEvents.emit(true);
  }
  update_signature_on_pdf() {
    this.http.get(ApiUrls.update_signature_on_pdf).subscribe((res: any) => {

      console.log(res)
    })
  }
}

