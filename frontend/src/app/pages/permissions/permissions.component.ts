import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-permissions',
  templateUrl: './permissions.component.html',
  styleUrls: ['./permissions.component.scss']
})
export class PermissionsComponent implements OnInit {

  permissionsList=[];
  rolesList =[]
  selectedRole;
  permissionObj:any = {}
  constructor(
    private http: HttpClient
  ) { }

  ngOnInit(): void {
   this.getTotalRolesCount()
  }

  getTotalRolesCount(): void{
    this.http.get(`${ApiUrls.roles}`, {
      params: {
        fields: JSON.stringify(["count( `tabRole`.`name`) AS total_count"]),
      }
    }).subscribe((res:any)=>{
      this.getRoles(res.data[0].total_count)
    })
  }
  getRoles(count): void {
    this.http.get(ApiUrls.roles,{
      params:{
        // limit_page_length:'None',
      fields: JSON.stringify(['*']),
      filters: JSON.stringify ( [['name','like','%ezy-%'],["disabled","!=","1"],["role_name","!=","ezy-Admin"]])
    }
    }).subscribe((res:any)=>{
      this.rolesList = res.data
      this.selectedRole = this.rolesList[0].name
      this.getPermissionByRoles()
    })
  }

  getPermissionByRoles(){
    let loginUser = JSON.parse(localStorage.getItem('login'))
    this.http.get(`${ApiUrls.roles_permission}/${this.selectedRole}`, {
      params: {
        // filters:JSON.stringify([['role_name','like', '%ezy%' ]]),
        fields: JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if(res?.data){
        this.permissionsList = res.data?.permission_list
        if(loginUser.rolesFilter[0].toLowerCase() != 'ezy-Admin'){
          this.permissionsList = this.permissionsList.filter((each:any)=>{
            if(each?.select_route != 'User Management' && each?.select_route != 'User Management-Details' && each?.select_route != 'Role Management' && each?.select_route != 'Permissions'){
              return each;
            }
          })
        }
      }
     
    })
  }

  selectRole(e){
    this.selectedRole = e.target.value;
    this.getPermissionByRoles()
    // const formData = new FormData();
    // formData.append('role',e.target.value)
    // this.http.post(ApiUrls.rolePermissions,formData).subscribe((res:any)=>{
    //   this.permissionsList = res.message
    // })
  }

  switchRole() {
    this.permissionsList.forEach((obj:any) => {
      if(!obj.read){
         obj.write =0
         obj.export =0
         obj.create =0
         obj.delete_perm =0
      }
    });
    this.http.put(`${ApiUrls.roles_permission}/${this.selectedRole}`, {permission_list: this.permissionsList}).subscribe((res: any) => {
      if (res.data) {
        this.getPermissionByRoles()
      }
    })
  }
}
