import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import moment from 'moment';
import { DateTimeAdapter } from 'ng-pick-datetime';
import { ToastrService } from 'ngx-toastr';
import { forkJoin, merge } from 'rxjs';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { SocketService } from 'src/app/shared/services/socket.service';

class SummariFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  /**
   * Limit page length of company filter
   * page length
   */
  search = '';
  taxpayer = '';
  summaryId = '';
  status = '';
}
@Component({
  selector: 'app-summaries',
  templateUrl: './summaries.component.html',
  styleUrls: ['./summaries.component.scss']
})
export class SummariesComponent implements OnInit,OnDestroy {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  filters = new SummariFilter()
  onSearch = new EventEmitter()
  hideShow = false;
  summariList = [];
  taxpayerList = [];
  dispatchInfo: any = {}
  seletedSummary: any = {}
  minDispatchDate: any;
  emailLogs: any;
  companyDetails:any;
  summaryStatus:any = {}
  showProgress = false;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    public dateTimeAdapter: DateTimeAdapter<any>,
    private toastr: ToastrService,
    private modal: NgbModal,
    private socketService : SocketService
  ) {
    dateTimeAdapter.setLocale('en-IN');
   }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      if (res) {
        // console.log("=====",res?.taxpayer)
        if (res?.taxpayer !== '') {
          // console.log("===== ++++",res?.taxpayer)
          this.getTaxPayerBySearch(res?.taxpayer);
          this.summariList = [];
        } else {
          this.getTaxPayerList();
        }

        this.filters.start = 0;
        this.filters.totalCount = 0;
        this.updateRouterParams()
      }
    });
    this.socketService.summaryData?.pipe(takeUntil(this.destroyEvents)).pipe(debounceTime(300)).subscribe((data)=>{
      
      if(data?.message?.message == 'Summary Created'){
        this.summaryStatus = data.message;
        this.showProgress = true;
        this.getSummariesList();
      }
      if(data?.message?.message == 'Amendment Processing'){
        this.summaryStatus = data.message;
      }
      if(data?.message?.message == 'Amendment Completed'){
        this.summaryStatus = data.message;
        setTimeout(()=>{
          this.showProgress = false;
        },500)
        
      }
    })
     

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        this.filters.search = res.search;
        this.filters.taxpayer = res.taxpayer;
      }
    })
    this.getSummariesList()
    this.getTaxPayerList();
  }


  getSummariesList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: SummariFilter) => {
      this.filters.search = params.search || this.filters.search;
      this.filters.taxpayer = params.taxpayer || this.filters.taxpayer;
      const queryParams: any = { filters: [['status', '!=', 'Deleted']] };
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.itemsPerPage;
      if (this.filters.search) {
        queryParams.filters.push(['summary_title', 'like', `%${this.filters?.search}%`]);
      }
      if (this.filters?.taxpayer) {
        queryParams.filters.push(['tax_payer_details', 'like', `%${this.filters?.taxpayer}%`]);
      }
      if (this.filters?.summaryId) {
        queryParams.filters.push(['name', 'like', `%${this.filters?.summaryId}%`]);
      }
      if (this.filters?.status) {
        queryParams.filters.push(['status', 'like', `%${this.filters?.status}%`]);
      }
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      queryParams.order_by = "`tabSummaries`.`creation` desc";
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}`, {
        params: {
          fields: JSON.stringify(["count( `tabSummaries`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.summariList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.summariList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.summariList = this.summariList.concat(data.data)
        } else {
          this.summariList = data.data;
        }

      }
    });
  }

  gotoSummaryDetails(item) {
    this.router.navigate(['./clbs/summary-details/' + item.name])
  }
  updateRouterParams(): void {
    this.router.navigate(['clbs/summaries'], {
      queryParams: this.filters
    });
  }
  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
  inputfocus() {
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";
  }
  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    setTimeout(() => {
      element[0].style.display = "none";
    }, 200);
  }
  getTaxPayerList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.taxPayers}`, {
      params: {
        fields: JSON.stringify(['*']),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res.data) {
        this.taxpayerList = res?.data;
      }

    })
  }
  getTaxPayerBySearch(res) {
    const queryParams: any = { filters: [] };
    if (res) {
      queryParams.filters.push(['gst_number', 'like', `%${res}%`])
      queryParams.fields = JSON.stringify(['*'])
    }
    queryParams.filters = JSON.stringify(queryParams.filters)
    this.http.get(ApiUrls.taxPayerDefault, {
      params: queryParams
    }).subscribe((res: any) => {
      if (res?.data) {
        this.taxpayerList = res.data;
      }
    })
  }

  deleteSummary(item, type) {
    let typeItem = type === "Void" ? "void" : "delete"
    if (!window.confirm(`Are you sure to ${typeItem} summary ${item.name} ?`)) {
      return null;
    } else {
      this.http.get(`${ApiUrls.delete_summary}`, { params: { name: item.name, status: type } }).subscribe((res: any) => {
        if (res?.message?.success) {
          this.toastr.success(res?.message?.message);
          this.getSummariesList();
        }
      })
    }
  }

  dispatchTempFunc(temp, item) {
    this.seletedSummary = item;

    if (item?.name) {
      this.getDispatchDetails(item, temp)
    } else {
      this.dispatchInfo = {};
      let modal = this.modal.open(temp, { size: 'md', centered: true ,windowClass:'sideMenu30'})
    }
  }
  getDispatchDetails(item, temp) {
    console.log(item)
    let modified_date =  new Date(item.modified)
    this.minDispatchDate = new Date(modified_date.getFullYear(), modified_date.getMonth(),modified_date.getDate())

    const queryParams = {
      filters: JSON.stringify([['summaries', '=', item?.name]]),
      fields: JSON.stringify(['*'])
    }
    this.http.get(`${ApiUrls.resource}/${Doctypes.dispatchInfo}`, { params: queryParams }).subscribe((res: any) => {
      if (res?.data.length) {
        this.dispatchInfo = res?.data[0];
        let modal = this.modal.open(temp, { size: 'md', centered: true,windowClass:'sideMenu30' })
      } else {
        this.dispatchInfo = {};
        let modal = this.modal.open(temp, { size: 'md', centered: true ,windowClass:'sideMenu30'})
      }
    })
  }
  dispatchFormAdd(form, modal) {
    if (form.form.valid) {
      let formValue = form.value;
      formValue['dispatch_date'] = moment(form.value.dispatch_date).format("YYYY/MM/DD");
      let data = {
        ...formValue, summaries: this.seletedSummary?.name
      }
      this.http.post(`${ApiUrls.resource}/${Doctypes.dispatchInfo}`, { data: data }).subscribe((res: any) => {
        if (res) {
          this.toastr.success("Success")
          modal.close('success');
        }
      })
    }
  }
  dispatchFormEdit(form, modal) {
    if (form.form.valid) {
      let data = {
        ...form.value, summaries: this.seletedSummary?.name
      }
      this.http.put(`${ApiUrls.resource}/${Doctypes.dispatchInfo}/${this.dispatchInfo?.name}`, { data: data }).subscribe((res: any) => {
        if (res) {
          this.toastr.success("Success")
          modal.close('success');
        }
      })
    }
  }
  emailLogOpen(emailLog,name) {
    this.getEmailLogs(name)
    let modalVal = this.modal.open(emailLog, { size: 'md', centered: true, windowClass: 'sideMenu' })
  }
  getEmailLogs(name) {
    let params = {
      summary:name,
      // filters: JSON.stringify([['docname', '=', `${this.paramsID}`]]),
      // limit_page_length: "None",
      fields: JSON.stringify(['*'])
    }
    this.http.get(`${ApiUrls.email_tracking}`, { params: params }).subscribe((res: any) => {
      if (res?.data) {
        let items = res?.data.map((each: any) => {
          if (each.emails) {
            each.emails = JSON.parse(each.emails)
          }
          return each
        })
        this.emailLogs = items;
        console.log(this.emailLogs)

      }
    })

  }
  ngOnDestroy(): void {
    this.summaryStatus ={}
    this.showProgress = false;
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}
