import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy, EventEmitter } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';
class UserFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  search = '';
}
@Component({
  selector: 'app-email-logs',
  templateUrl: './email-logs.component.html',
  styleUrls: ['./email-logs.component.scss']
})
export class EmailLogsComponent implements OnInit {
  filters = new UserFilter();
  onSearch = new EventEmitter();

  emailLogList:any = []
  apiDomain = environment.apiDomain
  companyDetails;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private modal: NgbModal,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.getTotalCount();
  }

  updateRouterParams(): void {
    this.router.navigate(['home/email-logs'], {
      queryParams: this.filters
    });
  }

  getTotalCount(): void {
    this.http.get(`${ApiUrls.resource}/${Doctypes.emailLogs}`, {
      params: {
        fields: JSON.stringify(["count( `tabEmail Queue`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getEmailLogList();
    })
  }

  getEmailLogList(){
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
      }
      
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabEmail Queue`.`modified` desc"
      queryParams.fields = JSON.stringify(["name", "creation", "modified", "modified_by", "sender","message","reference_doctype","reference_name","status"]);
      queryParams.filters = JSON.stringify(queryParams.filters);

      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.emailLogs}`, {
        params: {
          fields: JSON.stringify(["count( `tabEmail Queue`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.emailLogs}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {

      // if (res.data) {
      //     this.emailLogList = res?.data.map((each:any)=>{
      //       if(each){
      //         each.to = each?.message.match(/(To: [a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi)[0].split('To: ')[1];
      //       }
      //       return each;
      //     })  
               
      // }

      if (this.filters.currentPage == 1) {
        this.emailLogList = [];
      }
      const [count, data] = res;
      data.data = data.data.map((each:any,index)=>{
        if(each){
          each.to = each?.message.match(/(To: [a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi)[0].split('To: ')[1];
        each.index = this.emailLogList.length + index+1;
        }
        return each;
      })
      this.filters.totalCount = count.data[0].total_count;
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.emailLogList = this.emailLogList.concat(data.data)
        } else {
          this.emailLogList = data.data;
        }
        
      }
    });
  }

  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
}
