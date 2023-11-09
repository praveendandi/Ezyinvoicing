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
      params:{limit_start:'0',limit_page_length:JSON.stringify(count)}
    }).subscribe((res:any)=>{
      this.rolesList = res.data.filter((each)=>each.name.includes('ezy'))
    })
  }

  selectRole(e){
    const formData = new FormData();
    formData.append('role',e.target.value)
    this.http.post(ApiUrls.rolePermissions,formData).subscribe((res:any)=>{
      this.permissionsList = res.message
    })
  }
}
