import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';
import * as Moment from 'moment';
import moment from 'moment';
import { environment } from 'src/environments/environment';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { SocketService } from 'src/app/shared/services/socket.service';

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
  search = {
    name: '',
    display_name: '',
    sortBy: 'modified',
    filterBy: 'Yesterday',
    filterDate: '',
    found: 'No',
    folio_type: '',
    filterType: 'bill_generation_date'
  };
}

@Component({
  selector: 'app-invoice-reconcilation',
  templateUrl: './invoice-reconcilation.component.html',
  styleUrls: ['./invoice-reconcilation.component.scss']
})
export class InvoiceReconcilationComponent implements OnInit, OnDestroy {
  filters = new InvoicesFilter();
  onSearch = new EventEmitter();
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  invoiceList = [];
  current_date = new Date();
  seletedMonth;
  selectedyear = 2021
  countDataList = [];
  showList = false;
  selectedFile = [];
  uploadedFile = false;
  filter_date: string;
  today = Moment(new Date()).format('YYYY-12');

  // Min moment: February 12 2018, 10:30
  // min = new Date(2018, 1, 12, 10, 30);

  // Max moment: April 21 2018, 20:30

  fromMaxDate = new Date()
  toMaxDate = new Date()
  toMinDate = new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1)
  fromDate = [new Date(this.toMaxDate.getFullYear(), this.toMaxDate.getMonth(), 1), null];
  toDate = [null, this.toMaxDate]
  years = []
  apiDomain = environment.apiDomain;
  companyDetails;
  searchObj: any = {}
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
  upload_bulk_invoices_disable = false;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private modal: NgbModal,
    public dateTimeAdapter: DateTimeAdapter<any>,
    private toastr: ToastrService,
    private socketService : SocketService
  ) {
    dateTimeAdapter.setLocale('en-IN');
  }

  ngOnInit(): void {
    this.getYear()
    this.onDateFilterMonthChange(null, null);
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.invoiceList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {
        const dateBy = JSON.parse(res.search)
        this.filters.search.name = dateBy.name;
        // if (dateBy.filterDate) {
        //   this.filters.search.filterDate = [new Date(dateBy.filterDate[0]), new Date(dateBy.filterDate[1])] as any;
        // }
        // if (dateBy.fromDate) {
        //   this.filters.search.fromDate = [new Date(dateBy.fromDate[0]), new Date(dateBy.fromDate[1])] as any;
        // }
        // if (dateBy.toDate) {
        //   this.filters.search.toDate = [new Date(dateBy.toDate[0]), new Date(dateBy.toDate[1])] as any;
        // }
      }
    })
    this.getList();

    this.socketService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      console.log(" ==== res === ", res)
      if (res?.message?.type == "simple_reconciliation_file_uploading") {
        this.uploadProgress.status = 'STARTED'
        this.excelUploadData.totalCount = res?.message?.total_invoice_count
        // this.upload_bulk_invoices_disable = true
        this.excelUploadData.createdCount = res?.message?.invoice_count // this.excelUploadData.createdCount + 1

        this.uploadProgress.progress = (this.excelUploadData.createdCount * 100) / this.excelUploadData.totalCount
        this.uploadProgress.data = res.message.data
        this.uploadProgress.color = 'success';
        this.uploadProgress.label = 'Processing Files Successful';
        // setTimeout(() => {
        //   this.uploadProgress.status = 'SUCCESS';
          
        // }, 1000);

        
      }
      if (res?.message?.message === 'Simple reconciliation file uploaded') {
        this.upload_bulk_invoices_disable = false;
        this.getList()
      }
      if (res?.message?.type === 'simple_reconciliations_exception') {
        // this.execeptionError = true
        // this.execptionData = res?.message
      }
    })
  }
  fromDateSelected(dt) {
    var today = new Date();
    let month = dt.getMonth() + 1;
    let year = dt.getFullYear();
    let daysInMonth = new Date(year, month, 0).getDate();
    this.toMinDate = dt
    if (dt.getMonth() + 1 == today.getMonth() + 1) {
      console.log('same month')
      this.toMaxDate = today
    } else {
      console.log('not same month')
      this.toMaxDate = new Date(year, month - 1, daysInMonth)
    }

    if (this.fromDate && this.toDate) {
      if (this.fromDate[0].getDate() > this.toDate[1].getDate() || this.fromDate[0].getMonth() != this.toDate[1].getMonth()) {
        this.toDate = [null, null];
      }
    }

  }

  getYear() {
    var currentYear = new Date().getFullYear()
    var startYear = 2021;
    for (var i = startYear; i <= currentYear; i++) {
      this.years.push(startYear++);
    }
    return this.years;
  }
  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/invoice-reconciliation'], {
      queryParams: temp,
    });
  }

  goBack() {
    this.showList = false;
  }
  viewListItems(item, type) {
    this.filters.search.filterDate = item.bill_generation_date;
    this.getList();
    this.showList = true;
  }
  getList(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: InvoicesFilter) => {
      this.filters.active = parseInt(params.active as any) || 2;
      const queryParams: any = { filters: [] };
      if (this.filters.search.filterDate) {
        queryParams.filters.push(['bill_generation_date', 'like', this.filters.search.filterDate])
      }
      if (this.filters.search.name) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search.name}%`]);
      }
      if (this.filters.search.display_name) {
        queryParams.filters.push(['display_name', 'like', `%${this.filters.search.display_name}%`]);
      }
      if (this.filters.search.folio_type) {
        queryParams.filters.push(['folio_type', 'like', `%${this.filters.search.folio_type}%`]);
      }
      if (this.filters.search.found) {
        queryParams.filters.push(['invoice_found', '=', `${this.filters.search.found}`]);
      }


      // if (this.filters.search.filterBy) {

      //   if (this.filters.search.filterBy === 'Custom') {
      //     if (this.filters.search.filterDate) {
      //       const filter = new DateToFilter('Invoice Reconciliations', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
      //       if (filter) {
      //         queryParams.filters.push(filter);
      //       }
      //     }
      //   } else if (this.filters.search.filterBy !== 'All') {
      //     const filter = new DateToFilter('Invoice Reconciliations', this.filters.search.filterBy, null, this.filters.search.filterType as any).filter;
      //     if (filter) {
      //       queryParams.filters.push(filter);
      //     }
      //   }

      // }
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = this.filters.start;
      queryParams.order_by = "`tabInvoice Reconciliations`.`modified` desc"
      queryParams.fields = JSON.stringify(["*"]);
      queryParams.filters = JSON.stringify(queryParams.filters);

      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.invoiceReconciliation}`, {
        params: {
          fields: JSON.stringify(["count( `tabInvoice Reconciliations`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.invoiceReconciliation}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.invoiceList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.invoiceList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.invoiceList = this.invoiceList.concat(data.data)
          this.invoiceList = this.invoiceList.sort((a, b) => parseFloat(a.name) - parseFloat(b.name));
        } else {
          this.invoiceList = data.data;
          this.invoiceList = this.invoiceList.sort((a, b) => parseFloat(a.name) - parseFloat(b.name));
        }

      }
    });
  }



  onDateFilterChange() {
    this.filters.currentPage = 1;
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
  onDateFilterMonthChange(selectedDate, selectedYear) {
    try {

      let current_date = new Date();
      let select_date = selectedDate ? new Date(selectedDate) : new Date()
      this.filter_date = moment(select_date).format('YYYY-MM');
      // current_date.setDate(current_date.getDate());
      if (select_date.getMonth() + 1 <= 9) {
        this.seletedMonth = selectedDate ? `${0}${select_date.getMonth() + 1}` : `${0}${current_date.getMonth() + 1}`;
      } else {
        this.seletedMonth = selectedDate ? `${select_date.getMonth() + 1}` : `${current_date.getMonth() + 1}`;
      }
      // let year_value = select_date.getFullYear();
      let year_value = selectedYear ? JSON.parse(selectedYear) : current_date.getFullYear()
      this.selectedyear = year_value
      this.http.post(ApiUrls.reconcilationCount, { data: { month: this.seletedMonth, year: JSON.stringify(year_value) } }).subscribe((res: any) => {
        if (res?.message?.success) {
          if (res?.message?.data) {
            this.countDataList = res?.message?.data;
          } else {
            this.countDataList = [];
          }

        }
      })

    } catch (err) {
      console.log(err)
    }

  }

  chosenYearHandler(e) {

  }
  chosenMonthHandler(e, type) {

  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }


  /**openModelXml  */
  openModelXml(xmlUpload) {
    this.uploadedFile = false;
    this.selectedFile = [];
    let moadl = this.modal.open(xmlUpload, { centered: true, size: 'md', backdrop: 'static' })

    moadl.result.then((response: any) => {
      console.log("=========res ", response)
      if (response) {
        setTimeout((res: any) => {
          this.getList()
          this.onDateFilterMonthChange(this.seletedMonth, this.selectedyear)
        }, 1000)
      }
    })
  }

  selectFiles(files) {
    this.uploadedFile = false;
    Array.from(files).forEach(file => {

      this.selectedFile.push({ progress: 0, file });
      // console.log("file=====",this.selectedFile)
    });
  }
  removeFromList(file, i) {
    this.selectedFile.splice(i, 1)
  }
  uploadFiles() {
    const formData = new FormData();
    formData.append('file', this.selectedFile[0].file);
    formData.append('is_private', '1');
    formData.append('folder', 'Home');
    // formData.append('doctype', Doctypes.invoiceReconciliation);
    // formData.append('fieldname', 'invoice');
    this.http.post(ApiUrls.uploadFile, formData,).subscribe((response: any) => {
      if (response.message) {

        this.http.post(ApiUrls.reconcilation, { file_list: response?.message?.file_url }).subscribe((res: any) => {
          if (!res?.message?.success) {
            this.toastr.error(res?.message?.message)
          } else {
            this.uploadedFile = true;
          }
        })

      }
    })
  }
  export(content: any) {
    this.modal.open(content, { centered: true, size: 'md', backdrop: 'static' })


  }
  download() {
    if (!(this.fromDate[0] && this.toDate[1])) {
      this.toastr.warning('Select Dates')
      return
    }
    let fromDate = this.fromDate[0]
    let toData = this.toDate[1];
    this.http.post(ApiUrls.reconciliation, {
      start_date: Moment(new Date(fromDate)).format('YYYY-MM-DD'),
      end_date: Moment(new Date(toData)).format('YYYY-MM-DD'),
      // month:JSON.stringify(fromDate.getMonth()+1),//this.seletedMonth,
      // year :JSON.stringify(fromDate.getFullYear())//JSON.stringify(this.selectedyear)
    }).subscribe((res: any) => {
      if (res.message.success) {
        const link = document.createElement('a');
        link.setAttribute('target', '_blank');
        link.setAttribute('href', this.apiDomain + res.message.file_url);
        link.setAttribute('download', res.message.file_name);
        link.click();
        link.remove();
      }
    })
  }
  ngOnDestroy(): void {
    this.destroyEvents.emit(true);
  }
}
