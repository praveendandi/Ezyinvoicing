import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { EventEmitter } from 'events';
import { forkJoin, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

import { HeaderComponent } from 'src/app/shared/header/header.component';

class BenchLogFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  /**
   * Limit page length of company filter
   * page length
   */
  // search = '';

  config: any;

}
@Component({
  selector: 'app-bench-logs',
  templateUrl: './bench-logs.component.html',
  styleUrls: ['./bench-logs.component.scss']
})
export class BenchLogsComponent implements OnInit,OnDestroy {
  @ViewChild('maintenence') maintenence: ElementRef

  filters = new BenchLogFilter();
  onSearch = new EventEmitter();
  logsList = [];
  showUpdateBtn = false;
  clearInterval;
  loginUser;
  loginUSerRole;
  companyDetails;
  constructor(
    private http: HttpClient,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.getTotalCountofLogs()
    let update = localStorage.getItem('update');
    let updateUI = localStorage.getItem('updateUI')
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each:any)=> (each == 'ezy-IT'))
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page 
    this.showUpdateBtn = (update == "true" || updateUI == "true") ? true : false;
  }

  getTotalCountofLogs() {

    this.http.get(`${ApiUrls.resource}/${Doctypes.updateLogs}`, {
      params: {
        fields: JSON.stringify(["count( `tabUpdate Logs`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getBenchLogs();
    })
  }

  getBenchLogs() {
    this.activatedRoute.queryParams.pipe(switchMap((params: BenchLogFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = this.filters.start;
      queryParams.limit_page_length = this.filters.totalCount;
      queryParams.order_by = "`tabUpdate Logs`.`creation` desc";
      queryParams.fields = JSON.stringify(["name", "creation", "modified", "modified_by", "Status", "Command"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.updateLogs}`, {
        params: {
          fields: JSON.stringify(["count( `tabUpdate Logs`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.updateLogs}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {

      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      this.logsList = data.data;

    })
  }


  // update() {
   
  //   /**Proxy to set */
  //   if(this.companyDetails?.proxy == 1){
  //     this.http.post(ApiUrls.checkProxy, { data: { company: this.companyDetails?.name, type: 'set' } }).subscribe((proxy: any) => {
  //       if (proxy.message.success) {
  //         this.http.post(`${ApiUrls.benchUpdate_new}`,{data:{company:this.companyDetails?.name,username:this.loginUser?.username}}).subscribe((res: any) => {
  //           if (res) {
  
  //           }
  //         })
  //       }
  //     })
  //   }else{
  //     this.http.post(`${ApiUrls.benchUpdate_new}`,{data:{company:this.companyDetails?.name,username:this.loginUser?.username}}).subscribe((res: any) => {
  //       if (res) {

  //       }
  //     })
  //   }
  //   // this.http.post(ApiUrls.checkProxy, { data: { company: this.companyDetails?.name, type: 'set' } }).subscribe((proxy: any) => {
  //   //   if (proxy.message.success) {
  //   //     this.http.get(`${ApiUrls.benchUpdate}`).subscribe((res: any) => {
  //   //       if (res) {
  //           // const date = new Date();
  //           // const formData = new FormData();
  //           // formData.append('key',JSON.stringify(date));
  //           // formData.append('caller','bench_update');
  //           // formData.append('docs',JSON.stringify(res?.docs[0]))
  //           // formData.append('method',"console_command")
  //           // formData.append('args',JSON.stringify({'key':date,'caller':'bench_update'}))

  //           // this.http.get(ApiUrls.generateIrn).subscribe((res: any) => {
  //           //   console.log(res)
  //           //   if (res) {
  //           //     //  this.clearInterval = setInterval(()=>{
  //           //     //    this.checkMaintenceMode()

  //           //     //   },10000)
  //           //   }
  //           // })


  //           // setTimeout(()=>{
  //           //   this.http.get(ApiUrls.migrateBench).subscribe((res:any)=>{
  //           //     if(res){
  //           //       console.log(res)
  //           //       this.modal.dismissAll()
  //           //       localStorage.clear();
  //           //       this.router.navigate([''])
  //           //     }
  //           //   })
  //           // },30000)

  //   //       }
  //   //     })
  //   //   }
  //   // })

  // }

  // checkMaintenceMode():void{
  //   this.http.get(`${ApiUrls.resource}/${Doctypes.benchMangerCmd}`,{observe:'response'}).subscribe((response:any)=>{
  //     console.log("======================",response)
  //     if(response){

  //     }
  //   }),catchError(err =>{
  //     debugger
  //     console.log(err)
  //     if(err.status === 503){
  //       console.log("503 ====")
  //       this.openModal();
  //     }
  //     if(err.status === 504){
  //       localStorage.clear();
  //     }
  //     if(err.status === 200){
  //       this.clearInterval(this.clearInterval);
  //     }
  //     return throwError(err);
  //   })
  // }
  // openModal(){
  //   console.log("open modal ")
  //   let modal = this.modal.open(this.maintenence,{centered:true,size:'sm'})
  // }
  navigate(item, type) {
    this.router.navigate(['./home/bench-logs-info'], { queryParams: { id: item.name, type }, queryParamsHandling: 'merge' })
  }
  ngOnDestroy(): void {
    this.modal.dismissAll();
  }
}
