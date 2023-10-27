import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm, NgModel } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

class tabletFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  config: any;
  search=''
}
@Component({
  selector: 'app-tablet',
  templateUrl: './tablet.component.html',
  styleUrls: ['./tablet.component.scss']
})
export class TabletComponent implements OnInit {
  filters = new tabletFilter();
  onSearch = new EventEmitter();
  tabletList = [];
  tabletDetails:any = {}
  viewType;
  formData: any = {};
  ipValid;
  constructor(
    private modal: NgbModal,
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toaster: ToastrService
  ) { }

  ngOnInit(): void {
    this.getTabletData();
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.tabletList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
  }

  getTabletData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: tabletFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      
      if (this.filters.search) {
        queryParams.filters.push(['device_name', 'like', `%${this.filters.search}%`]);
      }
     
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabActive Tablets`.`creation` desc"
      queryParams.fields = JSON.stringify(["name","creation", "modified", "modified_by", "idx","tablet","ip_address","socket_id","uuid","device_name"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.tablet}`, {
        params: {
          fields: JSON.stringify(["count( `tabActive Tablets`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.tablet}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.tabletList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.index = this.tabletList.length + index+1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.tabletList = this.tabletList.concat(data.data)
        } else {
          this.tabletList = data.data;
        }
      }
    });
  }
  updateRouterParams(): void {
    this.router.navigate(['home/tablet'], {
      queryParams: this.filters
    });
  }
  addtablet(tabletModal,type,item){
    this.tabletDetails = {}
    this.viewType = type;    
    if(type === 'Edit'){
      this.tabletDetails = {...item};
    }
    this.modal.open(tabletModal, {
      size: 'md',
      centered: true
    });
  }
  onSubmit(form:NgForm){
    console.log("===",form.value)
    if (this.viewType === 'Edit' && form.valid) {
      this.http.put(`${ApiUrls.resource}/${Doctypes.tablet}/${this.tabletDetails?.name}`, form.value).subscribe((res: any) => {
        try {
          if (res.data) {
            this.toaster.success('Saved');
            this.modal.dismissAll();
            this.getTabletData();
          }
        } catch (e) { console.log(e) }
      })
    }else{
      if (form.valid) {
        form.value['doctype'] = Doctypes.tablet;
        const formData = new FormData();
        formData.append('doc', JSON.stringify(form.value));
        formData.append('action', 'Save');
        this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
          try {
            if (res) {
              this.toaster.success('Saved');
              this.modal.dismissAll();
              this.getTabletData()
            } else {
              this.toaster.error(res._server_messages);
            }
          } catch (e) { console.log(e) }
        }, (err) => {
          form.form.setErrors({ error: err.error.message });
        })
      } else {
        form.form.markAllAsTouched();
      }
    }
  }
  getPrinter(e, ref: NgModel) {
    this.ValidateIPaddress(e.target?.value);   
  }


  ValidateIPaddress(ipAddress) {
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipAddress)) {
      this.ipValid = false;
      return (true)
    } else {
      // alert("You have entered an invalid IP address!")
      this.ipValid = true;
      return (false)
    }
  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
}
