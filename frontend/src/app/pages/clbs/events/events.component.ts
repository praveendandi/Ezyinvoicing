import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';


class EventsFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  search = '';
 
}

@Component({
  selector: 'app-events',
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.scss']
})
export class EventsComponent implements OnInit {

  filters = new EventsFilter()
  onSearch = new EventEmitter()
  eventsList = [];
  eventInfo:any = {}
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toastr: ToastrService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      if (res) {
        this.filters.start = 0;
        this.filters.totalCount = 0;
        this.updateRouterParams()
      }
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        this.filters.search = res.search;
      }
    })
    this.getEventsList();
  }


  updateRouterParams(): void {
    this.router.navigate(['clbs/events'], {
      queryParams: this.filters
    });
  }

  getEventsList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: EventsFilter) => {
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.itemsPerPage;
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters?.search}%`]);
      }
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      queryParams.order_by = "`tabEvents`.`creation` desc";
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.events}`, {
        params: {
          fields: JSON.stringify(["count( `tabEvents`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.events}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.eventsList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.eventsList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.eventsList = this.eventsList.concat(data.data)
        } else {
          this.eventsList = data.data;
        }

      }
    });
  }

  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  eventModalFunc(event, each){
    this.eventInfo = {...each};
    let modal = this.modal.open(event,{size:'md',centered:true})
  }

  eventFormAdd(form:NgForm,modal){
    this.http.post(`${ApiUrls.resource}/${Doctypes.events}`,{data:form.value}).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getEventsList()
      }
    })
  }

  eventFormEdit(form:NgForm,modal){
    this.http.put(`${ApiUrls.resource}/${Doctypes.events}/${this.eventInfo.name}`,form.value).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getEventsList()
      }
    })
  }

}
