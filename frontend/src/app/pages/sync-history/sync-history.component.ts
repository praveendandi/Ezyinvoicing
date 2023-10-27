import { HttpClient } from '@angular/common/http';
import { Component, OnInit, EventEmitter } from '@angular/core';
import { NgbModalConfig, NgbModal , ModalDismissReasons} from '@ng-bootstrap/ng-bootstrap';
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
import {ExcelService} from 'src/app/shared/services/excel.service';
import { ToastrService } from 'ngx-toastr';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

class SyncFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;

  searchFilter = {
    status:'all',
    sync_date:'',
    document_type:'all',
    sync_type:'all'
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
  years= [];
  filter_date: string;
  today = moment(new Date()).format('YYYY-12');
  seletedMonth=moment(new Date()).format('MMM')
  selectedyear = 2022;
  syncConfig: any;
  syncError: any = {}
  syncPartial: any = {};
  posChecksDate;
  date_type = ''
  containerId = "dwtcontrolContainer";
  selectedFiles = [];
  message;
  progressInfos =[];
  allFilesUplaoded;
  posCheckList = [];
  showList = false;
  countDataList = [];
  totalSyncProgress:any={}
  filteredString : string = '';
  searchText;

  // data: any = [{
  //   case_worked: "abc",
  //   note: "Test",
  //   id: "1234"
  // },
  // {
  //   case_worked: "def",
  //   note: "test 1",
  //   id: "1234"
  // },
  // {
  //   case_worked: "def",
  //   note: "Test 2",
  //   id: "3456"
  // }];
  syncStartDate = '2021/02/11'
  monthList: any;
  constructor(
    config: NgbModalConfig,
    public modal: NgbModal,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private scannerService : FiScannerService,
    public dateTimeAdapter: DateTimeAdapter<any>,
    public datepipe: DatePipe,
    public fileuploadProgressbarService : FileuploadProgressbarService,
    private socketService: SocketService,
    private excelService:ExcelService,
    private toastr: ToastrService,
    public yearService : MonthYearService
  ) {
    config.backdrop = 'static';
    config.keyboard = false;
  }


  ngOnInit(): void {
    this.socketService.connectMe()
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    // this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.syncList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });

    this.getSyncLogs();
    // this.getYear()
    // this.onDateFilterMonthChange(null,null);
    // this.getTotalCount();
    merge(this.socketService.sync_invoices.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
      if(data){
        this.totalSyncProgress["sync_status"] = true
        this.totalSyncProgress["sync_invoices"] = data
        if(this.totalSyncProgress?.sync_invoices?.invoice_count == this.totalSyncProgress?.sync_invoices?.count){
          this.getSyncLogs()
        }
      }
    })
    merge(this.socketService.sync_sac_hsn_codes.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
      if(data){
        this.totalSyncProgress["sync_status"] = true
        this.totalSyncProgress["sync_sac_hsn_codes"] = data
        if(this.totalSyncProgress?.sync_sac_hsn_codes?.item_count == this.totalSyncProgress?.sync_sac_hsn_codes?.count){
          this.getSyncLogs()
        }
      }
    })
    merge(this.socketService.sync_taxpayers.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
      if(data){
        this.totalSyncProgress["sync_status"] = true
        this.totalSyncProgress["sync_taxpayers"] = data
        if(this.totalSyncProgress?.sync_taxpayers?.taxpayer_count == this.totalSyncProgress?.sync_taxpayers?.count){
          this.getSyncLogs()
        }
      }
    })
    merge(this.socketService.sync_completed.pipe(takeUntil(this.destroyEvents))).pipe(debounceTime(300)).subscribe((data:any) =>{
      if(data){
        this.totalSyncProgress = {}
        // this.totalSyncProgress["sync_status"] = false
        this.getSyncLogs()
      }
    })
    this.yearService.months.pipe(takeUntil(this.destroyEvents))
    .subscribe((data) => {
      data.forEach((res:any)=>{
        res['disable']=false
      })
      this.monthList = data
    });
  }

  goBack() {
    this.showList = false;
  }
  viewListItems(item, type) {
    // this.filters.search.filterDate = item.bill_generation_date;
    this.getSyncLogs();
    this.showList = true;
  }

  getYear(){
    var currentYear = new Date().getFullYear()
    var startYear = 2021;
    for(var i=startYear; i<= currentYear; i++){
      this.years.push(startYear++);
    }
    return this.years;
 }

//  onDateFilterMonthChange(selectedDate,selectedYear) {
//   try {

//     let current_date = new Date();
//     let select_date  = selectedDate ? new Date(selectedDate) : new Date()
//     this.filter_date =  moment(select_date).format('YYYY-MM');
//     // current_date.setDate(current_date.getDate());
//     if (select_date.getMonth()+1 <= 9) {
//       this.seletedMonth = selectedDate ? `${0}${select_date.getMonth() + 1}`:`${0}${current_date.getMonth() + 1}`;
//     } else {
//       this.seletedMonth = selectedDate ? `${select_date.getMonth() + 1}`:`${current_date.getMonth()+1}`;
//     }
//     // let year_value = select_date.getFullYear();
//     let year_value = selectedYear ? JSON.parse(selectedYear):current_date.getFullYear()
//      this.selectedyear =year_value
//     this.http.post(ApiUrls.syncLogs, { data: { month: this.seletedMonth, year: JSON.stringify(year_value) } }).subscribe((res: any) => {
//       if (res?.message?.success) {
//         if (res?.message?.data) {
//           this.countDataList = res?.message?.data;
//         } else {
//           this.countDataList = [];
//         }

//       }
//     })

//   } catch (err) {
//     console.log(err)
//   }

// }

  getSyncCount(): void {
    this.http.get(`${ApiUrls.syncLogs}`, {
      params: {
        fields: JSON.stringify(["count( `tabSync Logs`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
    })
  }

  updateRouterParams(): void {
    // this.filters.itemsPerPage=40
    console.log(this.filters.itemsPerPage)
    console.log(this.filters)
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
        this.filters.searchFilter.sync_date = dateBy.sync_date;
        this.filters.searchFilter.document_type = dateBy.document_type;
        this.filters.searchFilter.status = dateBy.status;
        this.filters.searchFilter.sync_type = dateBy.sync_type;
      }
      // this.filters.searchFilter.document_type = JSON.parse(JSON.stringify(params.searchFilter)) || this.filters.searchFilter;
      console.log(this.filters.searchFilter)
      const queryParams: any = { filters: [] };
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabSync Logs`.`modified` desc"
      // ["name", "transactioncode", "owner", "creation", "modified", "modified_by", "idx", "description", "sgst", "cgst", "type", "status", "igst", "taxble", "code", "company", "net", "service_charge", "vat_rate", "state_cess_rate", "central_cess_rate", "accommodation_slab", "service_charge_net","ignore","sac_index","exempted","ignore_non_taxable_items"]
      queryParams.fields = JSON.stringify(['*']);
      if (this.filters.searchFilter.sync_date && this.filters.searchFilter.sync_date !=null) {
        queryParams.filters.push(['sync_started_on', '=', `${moment(this.filters.searchFilter.sync_date).format('yyyy-MM-DD')}`]);
      }
      if (this.filters.searchFilter.document_type && this.filters.searchFilter.document_type !='all') {
        queryParams.filters.push(['document', '=', `${this.filters.searchFilter.document_type}`]);
      }
      if (this.filters.searchFilter.status && this.filters.searchFilter.status !='all') {
        queryParams.filters.push(['status', '=', `${this.filters.searchFilter.status}`]);
      }
      if (this.filters.searchFilter.sync_type && this.filters.searchFilter.sync_type !='all') {
        queryParams.filters.push(['sync_type', '=', `${this.filters.searchFilter.sync_type}`]);
      }
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
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.syncList.length + index+1;
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




  errorLogs(data) {
    console.log(data)
    this.http.get(`${ApiUrls.getSync}?doctype=${Doctypes.syncLogs}&name=${data.name}`).subscribe((res: any) => {
      if(res.docs){

        this.syncError = res.docs[0];
         console.log('========', this.syncError);
      }else{

      }

    })
  }




  selectFiles(files) {
    Array.from(files).forEach(file => {
      this.selectedFiles.push({ progress: 0, file });
    });
  }



  checkPagination(){
    // console.log(this.syncList.length)
    this.filters.currentPage = 1
    this.updateRouterParams()
  }


  open(content) {
    this.modal.open(content, {size:'md', centered: true,});
    this.getYear()
  }

  openmodel(submodel,data) {
    this.modal.open(submodel, {size:'lg', centered: true,}).result.then((result) => {
      this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    });
    this.errorLogs(data);

  }
  syncFunc(){
    this.modal.dismissAll()
    console.log(this.seletedMonth,this.selectedyear)
    this.http.post(ApiUrls.sync_data_from_web,{
      month:this.seletedMonth,
      year:this.selectedyear
    }).subscribe((res:any)=>{
      if (res.message.success) {
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

  exportAsXLSX():void {
    console.log(this.syncError.error)
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
  yearChange(event:any){
    console.log(this.selectedyear,moment().month(this.seletedMonth).format("M"))
    let date = moment(this.syncStartDate).format("YYYY/MM")
    let selectedDate = moment(`${this.selectedyear}/${moment().month(this.seletedMonth).format("M")}`).format("YYYY/MM")
    console.log('sync Date',date)
    console.log('selected Date',selectedDate)
    if(moment(selectedDate).format('YYYY') == moment(date).format('YYYY')){
      this.monthList.forEach((res:any)=>{
        console.log(moment(date).format('MM'),'--------------',moment().month(res.short).format("MM"))
        res['disable']=false
      })
    }else if(moment(selectedDate).format('YYYY') > moment(date).format('YYYY')){
      this.monthList.forEach((res:any)=>{
        res['disable']=false
      })
    }else{
      this.monthList.forEach((res:any)=>{
        res['disable']=true
      })
    }
    // let data = new Date(moment(this.syncStartDate))
    // console.log(data)
    this.seletedMonth =''

  }
}
