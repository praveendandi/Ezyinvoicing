import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

class RoleFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 100;
  search = '';
}
@Component({
  selector: 'app-roles',
  templateUrl: './roles.component.html',
  styleUrls: ['./roles.component.scss']
})
export class RolesComponent implements OnInit {
  @ViewChild('showUsers') showUsers: ElementRef;
  filters = new RoleFilter();
  onSearch = new EventEmitter();
  roleList = [];
  usersList = [];
  selectedRole;
  rolesObj:any;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private modal: NgbModal,
    private toaster : ToastrService
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());

    this.getRolesData();
  }
  updateRouterParams(): void {
    this.router.navigate(['home/roles'], {
      queryParams: this.filters
    });
  }

  getRolesCount(): void {
    this.http.get(`${ApiUrls.roles}`, {
      params: {
        fields: JSON.stringify(["count( `tabRole`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getRolesData();
    });
  }

  getRolesData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: RoleFilter) => {
      // this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };

      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
      }
      queryParams.limit_page_length = 'None';
      queryParams.order_by = "`tabRole`.`creation` desc"
      queryParams.fields = JSON.stringify(["*"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      
      const resultApi = this.http.get(`${ApiUrls.roles}`, { params: queryParams });
      return  resultApi;
    })).subscribe((res: any) => {
      if (res?.data?.length) {
        this.roleList = res.data.filter((each: any) => each?.name.includes('ezy')).map((each:any)=> {
          if(each){
            each.status = each?.disabled == 0 ? 1 : 0
          }
          return each
        })
      }
    });
  }

  ShowUsers(item, i): void {
    this.usersList = []
    this.selectedRole = item
    this.modal.open(this.showUsers, {
      size: 'md',
      centered: true
    })

    const formData = new FormData();
    formData.append('doctype', Doctypes.user);
    formData.append('fields', JSON.stringify(["`tabUser`.`full_name`", "`tabUser`.`name`", "`tabUser`.`email`"]));
    formData.append('filters', JSON.stringify([["Has Role", "role", "=", `${item.name}`]]))
    this.http.post(ApiUrls.roleByUser, formData).subscribe((res: any) => {
      if(res?.message?.values.length){
        res?.message?.values?.map((each: any) => {
          this.usersList.push(each[0])
        })
      }
    })
  }

  addRoles(modalObj) {
    this.rolesObj = {}
    let modal = this.modal.open(modalObj, { centered: true, size: 'md',backdrop:'static' });
    modal.result.then((res: any) => {
      if (res) {
        // this.getRolesList()
      }
    })
  }

  addRolesForm(form: NgForm, modal: any) {
    if (form.valid) {      
        let data_obj = {
          role_name: 'ezy-'+form.value.role_name,
        }
        this.http.post(ApiUrls.roles, { data: data_obj }).subscribe((res: any) => {
          if (res.data) {
            this.getRolesCount()
            modal.close(res.data);
            this.toaster.success('Created')
          }
        })      
    } else {
     form.form.markAllAsTouched()
    }

  }
  switchStatus(item){
    let obj = item;
    obj['disabled'] = item?.status ?  0 : 1
    this.http.put(`${ApiUrls.roles}/${item?.name}`,{data:obj}).subscribe((res:any)=>{
      if(res?.data){
        this.getRolesData()
        this.toaster.success("Updated")
      }else{
        this.toaster.error("Failed to Update")
      }
    })
  }
}
