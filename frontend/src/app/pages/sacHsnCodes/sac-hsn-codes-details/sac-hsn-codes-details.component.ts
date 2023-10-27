import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { UserService } from 'src/app/shared/services/user.service';
import { SacHsnCodesService } from '../sac-hsn-codes.service';

@Component({
  selector: 'app-sac-hsn-codes-details',
  templateUrl: './sac-hsn-codes-details.component.html',
  styleUrls: ['./sac-hsn-codes-details.component.scss']
})
export class SacHsnCodesDetailsComponent implements OnInit {
  paramsData;
  header;
  sacCodeDetails: any = {};
  checkName = false;
  companyList = [];
  constructor(
    private codesService: SacHsnCodesService,
    private activatedRoute: ActivatedRoute,
    private http: HttpClient,
    private router: Router,
    private userService: UserService,
    private toaster: ToastrService
  ) {

  }

  ngOnInit(): void {
    this.paramsData = this.activatedRoute.snapshot.queryParams;
    this.header = this.paramsData.type ? this.paramsData.type === 'view' ? "View" : "Edit" : "Create"
    if (this.paramsData?.id) {
      this.getSacData();
      this.getPermissions()
    }
    this.changeCompany();
  }
  getPermissions(): void {
    const queryParams :any ={}
    queryParams["doctype"]=Doctypes.sacCodes;
    queryParams["name"]= this.paramsData?.id;
    this.http.get(ApiUrls.permissions,{params: queryParams}).subscribe((res:any)=>{
      this.userService.setUser(res)
    })
  }

  getSacData(): void {
    this.http.get(`${ApiUrls.sacHsn}/${this.paramsData.id}`).subscribe((res: any) => {
      try {
        if (res.data) {
          this.sacCodeDetails = res.data;
          console.log(this.sacCodeDetails)
        }
      } catch (e) { console.log(e) }
    })
  }
  changeDescription(e) {
    this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.sacCodes}&fieldname=name&filters=${e}`).subscribe((res: any) => {
      if (res.message?.name) {
        this.checkName = true;
      } else {
        this.checkName = false
      }
    })
  }
  changeCompany() {
    this.http.get(`${ApiUrls.company}`).subscribe((res: any) => {
      if (res.data) {
        this.sacCodeDetails.company = res.data[0].name;
      }
    })
  }
  onSubmit(form: NgForm): void {
    if (form) {
      if (this.paramsData.type === "edit") {
        this.http.put(`${ApiUrls.sacHsn}/${this.paramsData.id}`, form.value).subscribe((res: any) => {
          try {
            if (res.data) {
              this.router.navigate(['/home/sac-hsn-codes'])
            }
          } catch (e) { console.log(e) }
        })
      } else {
        this.http.post(`${ApiUrls.sacHsn}`, form.value).subscribe((res: any) => {
          try {
            if (res.data) {
              this.router.navigate(['/home/sac-hsn-codes'])
            } else {
              console.log("====", res._server_messages)

            }
          } catch (e) { console.log(e) }
        }, (err) => {
          form.form.setErrors({ error: err.error.message });
        })
      }
    } else {
      form.form.markAllAsTouched();
    }
  }

}
