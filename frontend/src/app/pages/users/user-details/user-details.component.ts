import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.component.html',
  styleUrls: ['./user-details.component.scss']
})
export class UserDetailsComponent implements OnInit {
  header;
  paramsData;
  userDetails: any = {};
  roleList: [];
  rolesDup: [];
  loginUser: any;
  checkDuplicateEmail;
  checkName = false;
  pageType;
  constructor(
    private http: HttpClient,
    private router: Router,
    private activateRoute: ActivatedRoute,
    private toaster : ToastrService
  ) { }

  ngOnInit(): void {
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.paramsData = this.activateRoute.snapshot.queryParams;
    // this.pageType = this.activateRoute.snapshot.queryParams?.type
    this.getRoles();
    if (this.paramsData?.id && this.paramsData?.type) {
      this.getUserDetails()
    }
  }

  getUserDetails() {
    this.http.get(`${ApiUrls.users}/${this.paramsData.id}`).subscribe((res: any) => {
      this.userDetails = res?.data
      this.userDetails.roles = this.userDetails.roles.map((each: any) => each.role);
      this.userDetails.roles = this.userDetails.roles.filter((each:any)=> each.includes('ezy-'));
      this.userDetails.roles = this.userDetails.roles[0]
    })
  }
  // getTotalRolesCount(): void {
  //   this.http.get(`${ApiUrls.roles}`, {
  //     params: {
  //       fields: JSON.stringify(["count( `tabRole`.`name`) AS total_count"])
  //     }
  //   }).subscribe((res: any) => {
  //     this.getRoles(res.data[0].total_count)
  //   })
  // }
  getRoles(): void {
    this.http.get(ApiUrls.roles, {
      params: {limit_page_length: 'None', fields: JSON.stringify(['name', 'role_name']), filters:JSON.stringify([["role_name",'like', '%ezy-%'],["role_name","!=","ezy-Admin"],["disabled","!=","1"]]) }
    }).subscribe((res: any) => {
      this.roleList = res.data?.map((each:any)=> each.role_name);
    })
  }
  onSubmit(form: NgForm) {
    
    let defaultRoles = ['EzyInvoicing'] ;
    defaultRoles = defaultRoles.concat(form.value.roles)
    if (form.valid) {
      let roleObj = {
        docstatus: 0,
        doctype: "Has Role",
        modified_by: this.loginUser.full_name,
        owner: this.loginUser.full_name,
        parent: form.value.username? form.value.username + '@ezyinvoicing.local' : this.userDetails.email,
        parentfield: "roles",
        parenttype: "User",
        role: defaultRoles
      }
      let dataObj = {
        email: form.value.username ? form.value.username + '@ezyinvoicing.local' : this.userDetails.email,
        first_name: form.value.first_name,
        enabled: 1,
        user_type: "System User",
        username: form.value.username ? form.value.username : this.userDetails.username
      }
      if (this.paramsData?.id) {
        // this.http.put(`${ApiUrls.users}/${dataObj.email}`, dataObj).subscribe((res: any) => {
        //   if(res.data){
        //   this.router.navigate(['/home/users'])
        //   }
        // })
        if (form.value.roles) {
          this.http.put(`${ApiUrls.addUserRoles}`, roleObj).subscribe((res: any) => {
            if(res.message?.success){
              this.toaster.success("Updated")
            this.router.navigate(['/home/users'])
            }else{
              this.toaster.error("Error")
            }
          })
        }

      } else {
        this.http.post(ApiUrls.users, dataObj).subscribe((res: any) => {
          console.log(res)
          if (form.value.new_password) {
            this.http.put(`${ApiUrls.users}/${dataObj.email}`, { new_password: form.value.new_password }).subscribe((res: any) => {
              if (res.data) {
                setTimeout(() => {
                  this.http.post(`${ApiUrls.addUserRoles}`, roleObj).subscribe((res: any) => {
                    this.router.navigate(['/home/users'])
                  })
                }, 1000)
              }
            })
          }

        },(err:any) => {
          if(err.status == 409){
            this.toaster.info("User Email is exists.")
            // if (!window.confirm(`Are you want sure to continue with same email ?`)) {
            //   return null;
            // }else{
            //   let val:any = Math.floor(1000 + Math.random() * 9000);
            //   val = 'Noshow' + val+dataObj.email
            //   const formData = new FormData()
            //   formData.append('old',dataObj.email);
            //   formData.append('new',val);
            //   formData.append('merge','0')
            //   formData.append('doctype','User')
            //   this.http.post(`${ApiUrls.user_name_rename_doc}`,formData).subscribe((res:any)=>{
            //     if(res?.message){
            //       this.http.put(`${ApiUrls.users}/${res?.message}`,{
            //         enabled: 0,
            //         user_type: "System User"
            //       }).toPromise();
            //       this.onSubmit(form);
            //       console.log(res);
            //     }
            //   })
            // }
          }
        })
      }
    } else {
      form.form.markAllAsTouched();
    }
  }


  checkUserName(e:any , type:string){
    let filtersObj = type == 'Email' ? ['email', '=', e] : ['username', '=', e]
    this.http.get(`${ApiUrls.users}`,{
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([filtersObj])
      }
    }).subscribe((res:any)=>{
      if(res?.data?.length == 0){
        // type == 'Email' ? this.checkDuplicateEmail =  false : null
        if(type == 'userName') this.checkName =  false           
      }else{
        // type == 'Email' ? this.checkDuplicateEmail =  true : null
        if(type == 'userName') this.checkName =  true 

      }
    })
  }
}
