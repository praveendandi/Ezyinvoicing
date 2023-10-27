import { HttpClient } from '@angular/common/http';
import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';
import { Component, ElementRef, EventEmitter, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
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
  totalCount = 100;
  search = '';
}
@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.scss']
})
export class UsersComponent implements OnInit {
  @ViewChild('addUser') addUser: ElementRef;
  filters = new UserFilter();
  onSearch = new EventEmitter();
  companyDetails: any = {};
  userList = [];
  roles;
  index;
  roleList = [];
  userDetails: any = {};
  new_password;
  selectedUser: any = {}
  loginUser:any={}
  loginUSerRole ;
  signature_img: any = {}
  signature_pfx: any = {}
  pfx_password;
  domain = environment.apiDomain
  filename;
  fileToUpload;
  active = 1;
  UserSignature: any = {};
  userName;
  showPassword: boolean = false;

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
    this.signature_img = JSON.parse(localStorage.getItem('signature_img'));
    this.signature_pfx = JSON.parse(localStorage.getItem('signature_pfx'));
    this.pfx_password = JSON.parse(localStorage.getItem('pfx_password'))

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.getTotalCount();
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each:any)=>(each == 'ezy-IT' || each =='ezy-Finance'))
    console.log(this.loginUSerRole)
  }

  showHidePassword() {
    this.showPassword = !this.showPassword;
  }

  addSignature(contentSign, userName) {
    this.userName = userName
    this.modal.open(contentSign, {
      centered: true
    });
    this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
      params:{
        filters:JSON.stringify([['name','=',this.userName]]),
        fields:JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        console.log('=======', this.UserSignature)
        this.signature_img = res.data[0]?.signature_image;
        this.signature_pfx = res.data[0]?.signature_pfx
        this.pfx_password = res.data[0]?.pfx_password;
      }
    })
  }


  saveSignature(modal) {
    let data={};
    this.signature_pfx ? data['signature_pfx'] = this.signature_pfx:''
    this.pfx_password? data['pfx_password'] = this.pfx_password:''
    this.signature_img? data['signature_image'] = this.signature_img:''
    data['users'] = this.userName
    this.http.get(`${ApiUrls.resource}/${Doctypes.userSignature}`, {
      params:{
        filters:JSON.stringify([['name','=',this.userName]]),
        fields:JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if (res?.data) {
       if(res.data[0]?.signature_image || res.data[0]?.signature_pfx){
        this.http.put(`${ApiUrls.resource}/${Doctypes.userSignature}/${res.data[0]?.name}`, data).subscribe((res: any) => {
          this.toastr.success("uploaded");
          this.UserSignature = res.data;
          this.modal.dismissAll()
        })
       }else{
        this.http.post(`${ApiUrls.resource}/${Doctypes.userSignature}`, data).subscribe((res: any) => {
          console.log(res?.data)
          this.toastr.success("Uploaded");
          this.modal.dismissAll()
        })
       }
      }
    })
  }



  handlePfxFileInput(files: File[], field_name) {

    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', this.companyDetails?.doctype);
      // formData.append('fieldname', field_name);
      formData.append('docname', this.companyDetails?.company_code);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
           this.signature_pfx = res.message.file_url

          // if (field_name === 'signature') {
          //   this.companyDetails['signature'] = res.message.file_url
          //   const formData = new FormData();
          //   formData.append('doc', JSON.stringify(this.companyDetails));
          //   formData.append('action', 'Save')
          //   this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
          //     this.ngOnInit()
          //     this.toaster.success('Document Saved')
          //   });
          // }

        }
      })
    }
  }


  handleFileInput(files: File[], field_name) {

    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      // formData.append('doctype', this.companyDetails?.doctype);
      // formData.append('fieldname', field_name);
      formData.append('docname', this.companyDetails?.company_code);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
           this.signature_img = res.message.file_url

          // if (field_name === 'signature') {
          //   this.companyDetails['signature'] = res.message.file_url
          //   const formData = new FormData();
          //   formData.append('doc', JSON.stringify(this.companyDetails));
          //   formData.append('action', 'Save')
          //   this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {
          //     this.ngOnInit()
          //     this.toaster.success('Document Saved')
          //   });
          // }

        }
      })
    }
  }


  updateRouterParams(): void {
    this.router.navigate(['home/users'], {
      queryParams: this.filters
    });
  }
  // checkPagination(): void {
  //   if (this.filters.totalCount < (this.filters.itemsPerPage * this.filters.currentPage)) {
  //     this.filters.currentPage = 1
  //     this.updateRouterParams()
  //   }
  //   else {
  //     this.updateRouterParams()
  //   }
  // }

  getTotalCount(): void {
    this.http.get(`${ApiUrls.users}`, {
      params: {
        fields: JSON.stringify(["count( `tabUser`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getUSerList();
    })
  }
  getUSerList(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['first_name', 'like', `%${this.filters.search}%`]);
      }
      queryParams.limit_page_length = this.filters.totalCount;
      queryParams.order_by = "`tabUser`.`modified` desc"
      queryParams.fields = JSON.stringify(["*"]);
      queryParams.filters = JSON.stringify(queryParams.filters);

      const resultApi = this.http.get(`${ApiUrls.users}`, { params: queryParams });
      return resultApi;
    })).subscribe((res: any) => {

      if (res.data) {
        this.userList = res.data.filter((each: any) => each.username !== 'guest' && each.username !== "administrator");
      }
    });
  }
  // getUSerData(): void {
  //   this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
  //     this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
  //     this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
  //     this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
  //     this.filters.search = params.search || this.filters.search;
  //     const queryParams: any = { filters: [] };
  //     // queryParams.limit_start = this.filters.itemsPerPage;

  //     if (this.filters.search) {
  //       queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
  //       // queryParams.filters.push(['code', 'like', `%${this.filters.search}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     } else {
  //       queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //     }
  //     queryParams.order_by = "`tabUser`.`modified` asc"
  //     queryParams.fields = JSON.stringify(["name", "email","enabled","username"]);
  //     queryParams.filters = JSON.stringify(queryParams.filters);
  //     // queryParams.with_comment_count = true;
  //     const countApi = this.http.get(`${ApiUrls.users}`, {
  //       params: {
  //         fields: JSON.stringify(["count( `tabUser`.`name`) AS total_count"]),
  //         filters: queryParams.filters
  //       }
  //     });
  //     const resultApi = this.http.get(`${ApiUrls.users}`, { params: queryParams });
  //     return forkJoin([countApi, resultApi]);
  //   })).subscribe((res: any) => {
  //     console.log(res);
  //     const [count, data] = res;
  //     this.filters.totalCount = count.data[0].total_count;
  //     if (data.data) {
  //       this.userList = data.data;
  //       this.userList = this.userList.reverse();
  //     }
  //   });
  // }

  navigateRoles(each, index): void {
    this.index = index
    this.roles = []
    this.http.get(`${ApiUrls.users}/${each.name}`).subscribe((res: any) => {
      if (res.data.roles) {
        let roles = res.data.roles.map((each) => each.role);
        this.roles = roles.filter(each => each.includes('ezy'))
        this.roles = this.roles.join(", ")
        console.log(this.roles)
        if (this.roles.length == 0) {
          this.toastr.error("Not defined")
        }
      }
    })
  }
  editUSer(item, type) {
    this.router.navigate(['home/users-details'], { queryParams: { id: item.name, type }, queryParamsHandling: 'merge' })
  }

  changePassword(content, user) {
    this.selectedUser = user;
    this.modal.open(content, {
      centered: true
    });
  }

  onSubmit() {
    if (this.new_password) {
      this.http.put(`${ApiUrls.users}/${this.selectedUser?.email}`, { new_password: this.new_password }).subscribe((res: any) => {
        if (res.data) {
          this.toastr.success("Password Changed");
          this.modal.dismissAll();
        } else {
          this.toastr.error("Failed")
        }
      })
    }
  }

  /**deleteUser */
  deleteUser(content,item){
    if (!window.confirm(`Are you sure to delete ${item?.first_name}? `)) {
      return null;
    } else {
      this.http.delete(`${ApiUrls.users}/${item.name}`).subscribe((res:any)=>{
        if(res?.message == "ok"){
          this.toastr.success("Successfully deleted")
          this.getUSerList()
        }else{
          this.toastr.error("Error")
        }
      })
    }

  }
}
