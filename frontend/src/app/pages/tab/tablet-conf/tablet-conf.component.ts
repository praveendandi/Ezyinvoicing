import { HttpClient } from '@angular/common/http';
import { Component,EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { SocketService } from 'src/app/shared/services/socket.service';

class tabletConfigFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  config: any;
  search=''
}
@Component({
  selector: 'app-tablet-conf',
  templateUrl: './tablet-conf.component.html',
  styleUrls: ['./tablet-conf.component.scss']
})
export class TabletConfComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  filters = new tabletConfigFilter();
  onSearch = new EventEmitter();
  tableConfigList = [];
  constructor(
    private modal: NgbModal,
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toaster: ToastrService,
    private sockect: SocketService
  ) { }

  ngOnInit(): void {
    this.getWorkStationData();
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.tableConfigList=[];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    
    this.sockect.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      console.log(res,"ppppppppp")
      if (res?.message?.message === 'Tablet Configuration') {
        console.log(res,"ifff")
        this.getWorkStationData();
      }
    })
  }

  getWorkStationData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: tabletConfigFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      
      if (this.filters.search) {
        queryParams.filters.push(['work_station', 'like', `%${this.filters.search}%`]);
      }
     
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabTablet Config`.`creation` desc"
      queryParams.fields = JSON.stringify(["name","creation", "modified", "modified_by", "idx","work_station","tablet","username","tablet_ip_address","work_station_ip_address","mode"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.tabletConfig}`, {
        params: {
          fields: JSON.stringify(["count( `tabTablet Config`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.tabletConfig}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.tableConfigList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.tableConfigList.length + index+1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.tableConfigList = this.tableConfigList.concat(data.data)
        } else {
          this.tableConfigList = data.data;
        }
      }
    });
  }
  updateRouterParams(): void {
    this.router.navigate(['home/tablet-conf'], {
      queryParams: this.filters
    });
  }
  resetTablet(item){
    this.http.post(ApiUrls.tabletReset,{data:item}).subscribe((res:any)=>{
      console.log(res)
      if(res){
        this.getWorkStationData();
      }
    })
  }
}
