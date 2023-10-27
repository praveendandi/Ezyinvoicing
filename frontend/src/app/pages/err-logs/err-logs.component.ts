import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';
import { DateToFilter } from 'src/app/shared/date-filter';

class ErrorLogFilter {
  search = {
    name: '',
    filterBy: 'Today',
    filterDate: '',
    filterType: 'creation'
  };
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
}
@Component({
  selector: 'app-err-logs',
  templateUrl: './err-logs.component.html',
  styleUrls: ['./err-logs.component.scss']
})
export class ErrLogsComponent implements OnInit {
  ErrLogList = [];
  p = 1;
  filters = new ErrorLogFilter();
  onSearch = new EventEmitter();
  loginUser: any = {};
  loginUSerRole;
  companyDetails;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.search) {

        const dateBy = JSON.parse(res.search);

        this.filters.search.filterBy = dateBy.filterBy;
        this.filters.search.filterType = dateBy.filterType;
        
        if (dateBy.filterDate) {
          this.filters.search.filterDate = [new Date(dateBy.filterDate[0]), new Date(dateBy.filterDate[1])] as any;
        }
      }
    })
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.ErrLogList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.getPaymentData()
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each) => (each == 'ezy-IT' || each == 'ezy-Finance'))
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.search = JSON.stringify(temp.search);
    this.router.navigate(['home/error-logs'], {
      queryParams: temp
    });
  }
  
  getPaymentData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: ErrorLogFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.filters.push(["method", "like", `%Ezy-invoicing%`]);
      if (this.filters.search.name) {
        queryParams.filters.push(['method', 'like', `%${this.filters.search.name}%`]);
      }
      if (this.filters.search.filterBy) {

          if (this.filters.search.filterBy === 'Custom') {
            if (this.filters.search.filterDate) {
              const filter = new DateToFilter('Error Log', this.filters.search.filterBy, this.filters.search.filterDate as any, this.filters.search.filterType as any).filter;
              if (filter) {
                queryParams.filters.push(filter);
              }
            }
          } else if (this.filters.search.filterBy !== 'All') {
            const filter = new DateToFilter('Error Log', this.filters.search.filterBy, null, this.filters.search.filterType).filter;
            if (filter) {
              queryParams.filters.push(filter);
            }
          }
        
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabError Log`.`creation` desc";
      queryParams.fields = JSON.stringify(['name', 'owner', 'creation', 'modified', 'modified_by', 'method', 'error','seen','docstatus']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.errorLog}`, {
        params: {
          fields: JSON.stringify(["count( `tabError Log`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.errorLog}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.ErrLogList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.ErrLogList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        // this.ErrLogList = data.data;
        if (this.filters.start !== 0) {
          this.ErrLogList = this.ErrLogList.concat(data.data)
        } else {
          this.ErrLogList = data.data;
        }
      }
    });
  }

  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  onDateFilterChange() {
    this.filters.currentPage = 1;
    if (this.filters.search.filterBy == 'Custom') {
      this.filters.search.filterDate = '';
    } else {
      this.updateRouterParams();
    }
  }
}
