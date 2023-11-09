import { HttpClient } from '@angular/common/http';
import { Component, OnInit, EventEmitter } from '@angular/core';
import { NgbModalConfig, NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter'
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin, merge } from 'rxjs';
import * as Moment from 'moment';
import moment from 'moment';
import { FiScannerService } from 'src/app/shared/services/fi-scanner.service';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { DatePipe } from '@angular/common';
import { FileuploadProgressbarService } from 'src/app/resuable/fileupload-progressbar/fileupload-progressbar.service';
import { SocketService } from 'src/app/shared/services/socket.service';
import { ExcelService } from 'src/app/shared/services/excel.service';
import { ToastrService } from 'ngx-toastr';
import { MonthYearService } from 'src/app/shared/services/month-year.service';
import { get } from 'lodash';
import { environment } from 'src/environments/environment';
class SyncFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  active = 1;
  searchFilter = {
    invoice: "",
    status: 'all',
    sync_date: '',
    document_type: 'all',
    sync_type: 'all',
    filterDate: '',
  }

}


@Component({
  selector: 'app-sync-history',
  templateUrl: './sync-history.component.html',
  styleUrls: ['./sync-history.component.scss'],
  providers: [NgbModalConfig, NgbModal]

})
export class SyncHistoryComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  filters = new SyncFilter();
  onSearch = new EventEmitter();
  closeResult = '';
  syncList = []
  syncLogCount: any;
  companyDetails;
  invoiceInfo: any = {};
  years = [];
  filter_date: string;
  curentMonth = moment(new Date()).format('12');
  today = moment(new Date()).format('YYYY-12');
  seletedMonth = moment(new Date()).format('MMM')
  selectedyear: any = 2022;
  seletedMonthsync = moment(new Date()).format('MMM')
  selectedyearsync: any = 2023;
  syncConfig: any;
  syncError: any = {}
  syncPartial: any = {};
  posChecksDate;
  date_type = ''
  containerId = "dwtcontrolContainer";
  selectedFiles = [];
  message;
  progressInfos = [];
  allFilesUplaoded;
  posCheckList = [];
  showList = false;
  countDataList = [];
  totalSyncProgress: any = {}
  filteredString: string = '';
  searchText;
  synceLists: any = {}
  invoice_recn_count: any = []
  invoice_recn_count_first: any = []
  invoice_recn_count_last: any = []
  active = 1
  tablists: any = {
    dashboard: 'Dashboard',
    errorLogs: 'ErrorLogs'
  }
  showdata_tabs = true
  sync_errorlogs = false
  sync_error_invoice = false
  apiDomain = environment.apiDomain;
  syncStartDate = '2021/02/11'
  monthList: any;
  monthsYearsList: any = [];
  seletedMonthyears: any
  syncTimeInterval: any;
  from_date: any;
  to_date: any
  selectedinvoicetype: any = 'all'
  company: any;


  constructor(
    config: NgbModalConfig,
    public modal: NgbModal,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private scannerService: FiScannerService,
    public dateTimeAdapter: DateTimeAdapter<any>,
    public datepipe: DatePipe,
    public fileuploadProgressbarService: FileuploadProgressbarService,
    private socketService: SocketService,
    private excelService: ExcelService,
    private toastr: ToastrService,
    public yearService: MonthYearService,
    private modalService: NgbModal
  ) {
    config.backdrop = 'static';
    config.keyboard = false;
  }


  ngOnInit(): void {
    var presenttMonth = '0' + (new Date().getMonth() + 1).toString().slice(-2)
    var presenttYear = new Date().getFullYear().toString()
    var years = presenttYear.toString()
    this.seletedMonth = presenttMonth;
    this.selectedyear = years
    this.ondatemonthyearsfilters()
    this.socketService.connectMe()
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.syncList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.getYear()
    merge(this.socketService.sync_invoices.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data: any) => {
      if (data) {
        this.totalSyncProgress["sync_status"] = true
        this.totalSyncProgress["sync_invoices"] = data
        if (!this.syncTimeInterval) {
          this.syncTimeInterval = setInterval(() => {
            this.getSyncLogs()
          }, 600000)
        }
        if (this.totalSyncProgress?.sync_invoices?.invoice_count == this.totalSyncProgress?.sync_invoices?.count) {
          this.totalSyncProgress['sync_status'] = false
          clearInterval(this.syncTimeInterval)
          this.getSyncLogs()
        }
      }
    })
    merge(this.socketService.d_sync.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data: any) => {
      if (data) {
        this.totalSyncProgress["sync_status"] = true
        this.totalSyncProgress["d_sync"] = data
        if (!this.syncTimeInterval) {
          this.syncTimeInterval = setInterval(() => {
            this.getSyncLogs()
          }, 600000)
        }

        if (this.totalSyncProgress?.d_sync?.invoice_count == this.totalSyncProgress?.d_sync?.count) {
          this.totalSyncProgress['d_sync'] = false
          clearInterval(this.syncTimeInterval)
          this.getSyncLogs()
        }
      }
    })

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => {
        data.forEach((res: any) => {
          res['disable'] = false
        })
        this.monthList = data
      });

  }
  goBack() {
    this.showList = false;
  }
  viewListItems(item, type) {
    this.getSyncLogs();

    this.showList = true;
  }

  getYear() {
    var currentYear = new Date().getFullYear()
    var startYear = 2021;
    for (var i = startYear; i <= currentYear; i++) {
      this.years.push(startYear++);
    }
    return this.years;

  }
  ondatemonthyearsfilters() {
    this.monthsYearsList = []
    let today = new Date()
   
     

    this.company = JSON.parse(localStorage.getItem('company'))
    console.log(this.company.multi_month_sync)
    if(this.company.multi_month_sync=='No'){
      for (let i = 0; i < 3; i++) {
        let date1 = new Date(today.getFullYear(), today.getMonth() - i, 1) // 1st Jan 2014
        let monthformat = date1.getMonth() + 1 < 10 ? `0${date1.getMonth() + 1}` : `${date1.getMonth() + 1}`
        let obj = {
          label: moment(date1).format('MMM YYYY'),
          value: `${monthformat}${date1.getFullYear()}`
        }
        this.monthsYearsList.push(obj)
      }
      this.seletedMonthyears = this.monthsYearsList[0].value
    }
    else{
       for (let i = 0; i < 12; i++) {
      let date1 = new Date(today.getFullYear(), today.getMonth() - i, 1) // 1st Jan 2014
      let monthformat = date1.getMonth() + 1 < 10 ? `0${date1.getMonth() + 1}` : `${date1.getMonth() + 1}`
      let obj = {
        label: moment(date1).format('MMM YYYY'),
        value: `${monthformat}${date1.getFullYear()}`
      }
      this.monthsYearsList.push(obj)
    }
    this.seletedMonthyears = this.monthsYearsList[0].value

    }

    
  
    this.getSyncLogsDashboard()
  }
  // getSyncCount(): void {
  //   this.http.get(`${ApiUrls.syncLogs}`, {
  //     params: {
  //       fields: JSON.stringify(["count( `tabSync Logs`.`name`) AS total_count"])
  //     }
  //   }).subscribe((res: any) => {
  //     this.filters.totalCount = res.data[0].total_count;

  //   })
  // }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.searchFilter = JSON.stringify(temp.searchFilter);
    this.router.navigate(['home/sync-history'], {
      queryParams: temp
    });


  }



  getSyncLogs(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: any) => {
      if (params.searchFilter) {
        const dateBy = JSON.parse(params?.searchFilter)
        this.filters.searchFilter.invoice = dateBy.invoice;
        this.filters.searchFilter.sync_date = dateBy.sync_date;
        this.filters.searchFilter.document_type = dateBy.document_type;
        this.filters.searchFilter.status = dateBy.status;
        this.filters.searchFilter.sync_type = dateBy.sync_type;
      }

      const queryParams: any = { filters: [] };
      let month = this.seletedMonthyears.slice(0, 2);
      let year = this.seletedMonthyears.slice(2)
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabSync Logs`.`modified` desc"
      queryParams.fields = JSON.stringify(['*']);
      let lastDay = moment(new Date(year, month - 1, 1)).endOf('month').format('DD');
      queryParams.filters.push(['invoice_date', 'between', [`${moment(new Date(year, month - 1, 1)).format('yyyy-MM-DD')}`, `${moment(new Date(year, month - 1, parseInt(lastDay))).format('yyyy-MM-DD')}`]]);

      // if (this.filters.searchFilter.sync_date && this.filters.searchFilter.sync_date != null) {
      //   queryParams.filters.push(['sync_started_on', '=', `${moment(this.filters.searchFilter.sync_date).format('yyyy-MM-DD')}`]);
      // }
      if (this.filters.searchFilter.invoice && this.filters.searchFilter.invoice != null) {
        // queryParams.filters.push(['invoice', '=', `${this.filters.searchFilter.invoice}`]);
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.searchFilter.invoice}%`]);
      }
      if (this.filters.searchFilter.status && this.filters.searchFilter.status != 'all') {
        queryParams.filters.push(['status', '=', `${this.filters.searchFilter.status}`]);
      }
      // if (this.filters.searchFilter.sync_type && this.filters.searchFilter.sync_type != 'all') {
      //   queryParams.filters.push(['sync_type', '=', `${this.filters.searchFilter.sync_type}`]);
      // }
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.syncLogs}`, {
        params: {
          fields: JSON.stringify(["count( `tabSync Logs`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.syncLogs}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.syncList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.syncList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.syncList = this.syncList.concat(data.data)
        } else {
          this.syncList = data.data;
        }

      }
    });
  }

  getSyncLogsDashboard(): void {
    let data = {

      month: this.seletedMonthyears.slice(0, 2),
      year: this.seletedMonthyears.slice(2)
    }
    this.http.post(ApiUrls.syncLogsDashboard, { data: data }).subscribe((res: any) => {
      if (res?.message?.success) {
        if (res?.message?.data) {
          this.synceLists = res?.message?.data.invoice_status;
          let tempcount = JSON.parse(res?.message?.data.invoice_reconciliations)
          this.invoice_recn_count = tempcount.map((each: any, index = 1) => {
            each['idx'] = index + 1
            return each;
          })
          this.invoice_recn_count_first = this.invoice_recn_count.filter((each: any) => {
            if (each?.idx <= 15) {
              return each
            }
          })
          this.invoice_recn_count_last = this.invoice_recn_count.filter((each: any) => {
            if (each?.idx > 15) {
              return each
            }
          })
        }
        else {
          this.synceLists = null;
          this.invoice_recn_count_first = null;
          this.invoice_recn_count_last = null
        }

      }

    })
  }




  errorLogs(data) {
    this.http.get(`${ApiUrls.getSync}?doctype=${Doctypes.syncLogs}&name=${data.name}`).subscribe((res: any) => {
      if (res.docs) {
        this.syncError = res.docs[0];

      }

    })
  }
  selectFiles(files) {
    Array.from(files).forEach(file => {
      this.selectedFiles.push({ progress: 0, file });
    });
  }
  checkPagination() {

    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  openmodel(submodel, data) {
    this.modal.open(submodel, { size: 'lg', centered: true, }).result.then((result) => {
      this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    });
    this.errorLogs(data);

  }

  syncfuncDashboard() {

    this.modal.dismissAll()

    let data = {

      month: this.seletedMonthyears.slice(0, 2),
      year: this.seletedMonthyears.slice(2)
    }

    this.http.post(ApiUrls.syncLogsDashboard, {
      data
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);
      } else {
        this.toastr.error(res.message.message)
      }
    })
  }

  syncFunc() {
    var presenttMonth = '0' + (new Date().getMonth() + 1).toString().slice(-2)
    var presenttYear = new Date().getFullYear().toString()
    var years = presenttYear.toString()
    this.seletedMonthsync = presenttMonth;
    this.selectedyearsync = years
    this.modal.dismissAll()
    let data = {
      month: this.seletedMonthyears.slice(0, 2),
      year: this.seletedMonthyears.slice(2)
    }
    this.http.post(ApiUrls.sync_data_from_web, {
      data
    }).subscribe((res: any) => {
      if (res?.message?.Success) {
        this.toastr.success(res.message.message);
      } else {
        this.toastr.error(res.message.message)
      }
    })
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }

  exportAsXLSX(): void {

    this.excelService.exportAsExcelFile(this.syncError.error, 'export-to-excel');
  }
  organise(arr) {
    var headers = [], // an Array to let us lookup indicies by group
      objs = [],    // the Object we want to create
      i, j;
    for (i = 0; i < arr.length; ++i) {
      j = headers.indexOf(arr[i].id); // lookup
      if (j === -1) { // this entry does not exist yet, init
        j = headers.length;
        headers[j] = arr[i].id;
        objs[j] = {};
        objs[j].id = arr[i].id;
        objs[j].data = [];
      }
      objs[j].data.push( // create clone
        {
          case_worked: arr[i].case_worked,
          note: arr[i].note, id: arr[i].id
        }
      );
    }
    return objs;
  }
  yearChange(event: any) {
    let date = moment(this.syncStartDate).format("YYYY/MM")
    let selectedDate = moment(`${this.selectedyear}/${moment().month(this.seletedMonth).format("M")}`).format("YYYY/MM")
    if (moment(selectedDate).format('YYYY') == moment(date).format('YYYY')) {
      this.monthList.forEach((res: any) => {
        res['disable'] = false
      })
    } else if (moment(selectedDate).format('YYYY') > moment(date).format('YYYY')) {
      this.monthList.forEach((res: any) => {
        res['disable'] = false
      })
    } else {
      this.monthList.forEach((res: any) => {
        res['disable'] = true
      })
    }
    this.seletedMonth = ''

  }

  navtabChange() {

    // this.active = e.nextId;
    if (this.filters.active == 1) {
      this.showdata_tabs = true
      this.sync_errorlogs = false
      this.sync_error_invoice = false

      this.getSyncLogsDashboard()
    }
    else {
      this.showdata_tabs = false
      this.sync_error_invoice = true
      let login_data = JSON.parse(localStorage.getItem('login'))
      console.log(login_data.rolesFilter, login_data)
      let dataezy_IT = login_data.rolesFilter.indexOf("ezy-IT")
      let dataezy_Finance = login_data.rolesFilter.indexOf("ezy-Finance")


      if (login_data.name == 'Administrator' || login_data.rolesFilter[dataezy_IT] == "ezy-IT" || login_data.rolesFilter[dataezy_Finance] == "ezy-Finance") {
        this.sync_errorlogs = true
        console.log(login_data.rolesFilter, 'testing...............')
      }

      else {
        this.sync_errorlogs = false
      }
      this.getSyncLogs()
    }
    // this.updateRouterParams();
  }

  reFresh() {
    if (this.filters.active == 1) {
      this.getSyncLogsDashboard()
    }
    else {
      this.getSyncLogs()
    }
  }




  d_sync_based_On_dates() {


    let data = {
      from_date: moment(this.from_date).format('YYYY-MM-DD'),
      to_date: moment(this.to_date).format('YYYY-MM-DD'),
      invoice_type: this.selectedinvoicetype
    }

    this.http.post(ApiUrls.reSync_based_on_from_to_dates, data).subscribe((res: any) => {

      if (res?.message?.success) {
        this.toastr.success(res?.message?.message);
      } else {
        this.toastr.error(res?.message?.message)
      }
    })
    this.modal.dismissAll()



  }

  deflagemodal(deflag) {
    this.from_date = null
    this.to_date = null
    this.modalService.open(deflag, { size: 'sm' });
  }

  exportexcel() {
    let data = {
      month: this.seletedMonthyears.slice(0, 2),
      year: this.seletedMonthyears.slice(2)
    }
    this.http.post(ApiUrls.export_as_excel_errorlogs, { data: data }).subscribe((res: any) => {
      if (res?.message) {
        const link = document.createElement('a');
        link.setAttribute('target', '_blank');
        link.setAttribute('href', this.apiDomain + res?.message?.file_url);
        link.click();
        link.remove();
      }
    })
  }
  reSynctoGST(e_number) {
    let data = {
      invoice_number: e_number,
      doctype: Doctypes.invoices
    }
    this.http.post(ApiUrls.sync_data_to_erp_single, data).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);

      } else {
        this.toastr.error(res.message.message)
      }
    });
  }
  errorDownloadJson(json_error) {
    console.log(json_error)
    // let sJson = JSON.stringify(json_error);
    // const link = document.createElement('a');
    // // link.setAttribute('target', '_blank');
    // // link.setAttribute('href', this.apiDomain + json_error);
    // link.setAttribute('href', "data:text/json;charset=UTF-8," + encodeURIComponent(sJson))
    // link.click();
    // link.remove();


    const sJson = JSON.stringify(json_error);
    const link = document.createElement('a');
    link.setAttribute('href', "data:text/json;charset=UTF-8," + encodeURIComponent(sJson));
    link.setAttribute('download', "Error Logs.json");
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click(); // simulate click
    document.body.removeChild(link);

  }


}
