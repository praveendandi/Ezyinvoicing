import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { UserService } from 'src/app/shared/services/user.service';

@Component({
  selector: 'app-tax-payers-details',
  templateUrl: './tax-payers-details.component.html',
  styleUrls: ['./tax-payers-details.component.scss']
})
export class TaxPayersDetailsComponent implements OnInit {

  paramsData;
  header;
  checkName = false;
  companyList: any = [];
  taxPayerDetails: any = {};
  checkApiMethod = false;
  apiMethod;
  companyDetails: any;
  constructor(
    private activatedRoute: ActivatedRoute,
    private http: HttpClient,
    private router: Router,
    private userService: UserService,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.paramsData = this.activatedRoute.snapshot.queryParams;
    this.header = this.paramsData.id ? `${this.paramsData.type}` : "Create"
    if (this.paramsData.id) {
      this.getTaxPayerDetails();
      this.checkApiMethod = true
      this.getPermissions();
    }
    this.changeCompany();
  }




  getPermissions(): void {
    const queryParams: any = {}
    queryParams["doctype"] = Doctypes.taxPayers;
    queryParams["name"] = this.paramsData?.id;
    this.http.get(ApiUrls.permissions, { params: queryParams }).subscribe((res: any) => {
      this.userService.setUser(res)
    })
  }
  getTaxPayerDetails(): void {
    this.http.get(`${ApiUrls.taxPayerDefault}/${this.paramsData.id}`).subscribe((res: any) => {
      try {
        if (res.data) {
          this.taxPayerDetails = res.data;
        }
      } catch (e) { console.log(e) }
    })
  }

  onSubmit(form: NgForm): void {
    console.log(form)
    if (form.valid) {
      if (!this.checkApiMethod) {
        const dataObj = { "data": { "code": form.value.company, "gstNumber": form.value.gst_number } }
        this.http.post(`${ApiUrls.taxPayersDetails}`, dataObj).subscribe((res: any) => {
          try {
            if (res.message.success) {
              this.checkApiMethod = true;
              this.apiMethod = res.message.update;
              this.taxPayerDetails = res.message.data
            } else {
              this.toastr.error(res.message.message);
            }
          } catch (e) { console.log(e) }
        })
      } else {

        const updateGstNum = this.http.put(`${ApiUrls.taxPayerDefault}/${this.taxPayerDetails.gst_number}`, form.value);
        const updateParam = this.http.put(`${ApiUrls.taxPayerDefault}/${this.paramsData.id}`, form.value);
        const postNew = this.http.post(`${ApiUrls.taxPayerDefault}`, form.value)
        const apiUrl = !this.apiMethod ? this.paramsData.type === "Edit" ? updateParam : postNew : updateGstNum;
        apiUrl.subscribe((res: any) => {
          try {
            if (res.data) {
              this.router.navigate(['/home/tax-payers'])
            }
          } catch (e) { console.log(e) }
        })


      }

    } else {
      form.form.markAllAsTouched();
    }

  }

  changeDescription(e): void {
    if(e.length > 13){
      this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.taxPayers}&fieldname=name&filters=${e}`).subscribe((res: any) => {
        if (res.message?.name) {
          this.checkName = true;
        } else {
          this.checkName = false
        }
      })
    }
    
  }

  changeCompany() {
    this.http.get(`${ApiUrls.company}`).subscribe((res: any) => {
      if (res.data) {
        this.taxPayerDetails.company = res.data[0].name;
      }
    })
  }

  TaxsynctoGST() {
    let data = {
      gst_number: this.taxPayerDetails.gst_number,
    }
    console.log(this.taxPayerDetails)
    this.http.post(ApiUrls.manual_sync_taxpayer_details, data).subscribe((res: any) => {
      if (res.message.success) {
        this.toastr.success(res.message.message);
        this.getTaxPayerDetails();
      }
    })
  }


}
