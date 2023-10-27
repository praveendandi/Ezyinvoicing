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
  constructor(
    private http: HttpClient,
    private router: Router,
    private activateRoute: ActivatedRoute,
    private toaster : ToastrService
  ) { }

  ngOnInit(): void {
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.paramsData = this.activateRoute.snapshot.queryParams;
    this.getTotalRolesCount();
    if (this.paramsData.id) {
      this.getUserDetails()
    }
  }

  getUserDetails() {
    this.http.get(`${ApiUrls.users}/${this.paramsData.id}`).subscribe((res: any) => {
      this.userDetails = res?.data
      this.userDetails.roles = this.userDetails.roles.map((each: any) => each.role);
      this.userDetails.roles = this.userDetails.roles.filter((each:any)=> each.includes('ezy-'));
    })
  }
  getTotalRolesCount(): void {
    this.http.get(`${ApiUrls.roles}`, {
      params: {
        fields: JSON.stringify(["count( `tabRole`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.getRoles(res.data[0].total_count)
    })
  }
  getRoles(count): void {
    this.http.get(ApiUrls.roles, {
      params: { limit_start: '0', limit_page_length: JSON.stringify(count), fields: JSON.stringify(['name', 'role_name']) }
    }).subscribe((res: any) => {
      this.roleList = res.data.filter((each: any) => each.name.includes('ezy'));
    })
  }
  onSubmit(form: NgForm) {
    
    let defaultRoles = ['Maintenance Manager','System Manager'] ;
    console.log(form.value.roles)
    defaultRoles = defaultRoles.concat(form.value.roles)
    if (form.valid) {
      let roleObj = {
        docstatus: 0,
        doctype: "Has Role",
        modified_by: this.loginUser.full_name,
        owner: this.loginUser.full_name,
        parent: form.value.email,
        parentfield: "roles",
        parenttype: "User",
        role: defaultRoles
      }
      let dataObj = {
        email: form.value.email,
        first_name: form.value.first_name,
        enabled: form.value.enabled ? form.value.enabled : 1,
        user_type: "System User",
        username: form.value.username
      }
      if (this.paramsData.id) {
        this.http.put(`${ApiUrls.users}/${dataObj.email}`, dataObj).subscribe((res: any) => {
          if(res.data){
          this.router.navigate(['/home/users'])
          }
        })
        if (form.value.roles) {
          this.http.put(`${ApiUrls.addUserRoles}`, roleObj).subscribe((res: any) => {
            if(res.data){
            this.router.navigate(['/home/users'])
            }
          })
        }

      } else {
        this.http.post(ApiUrls.users, dataObj).subscribe((res: any) => {
          console.log(res)
          if (form.value.new_password) {
            this.http.put(`${ApiUrls.users}/${form.value.email}`, { new_password: form.value.new_password }).subscribe((res: any) => {
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
            if (!window.confirm(`Are you want sure to continue with same email ?`)) {
              return null;
            }else{
              let val:any = Math.floor(1000 + Math.random() * 9000);
              val = 'Noshow' + val+form.value.email
              const formData = new FormData()
              formData.append('old',form.value.email);
              formData.append('new',val);
              formData.append('merge','0')
              formData.append('doctype','User')
              this.http.post(`${ApiUrls.user_name_rename_doc}`,formData).subscribe((res:any)=>{
                if(res?.message){
                  this.http.put(`${ApiUrls.users}/${res?.message}`,{
                    enabled: 0,
                    user_type: "System User"
                  }).toPromise();
                  this.onSubmit(form);
                  console.log(res);
                }
              })
            }
          }
        })
      }
    } else {
      form.form.markAllAsTouched();
    }
  }
}
