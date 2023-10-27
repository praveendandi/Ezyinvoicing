import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { UserService } from 'src/app/shared/services/user.service';
import { PaymentTypeService } from '../payment-type.service';

@Component({
  selector: 'app-payment-type-details',
  templateUrl: './payment-type-details.component.html',
  styleUrls: ['./payment-type-details.component.scss']
})
export class PaymentTypeDetailsComponent implements OnInit {
  paramDetails;
  header;
  checkName = false;
  companyList = [];
  company;
  paymentDetails: any = {};
  constructor(
    private paymentService: PaymentTypeService,
    private activatedRoute: ActivatedRoute,
    private http: HttpClient,
    private router: Router,
    private userService: UserService
  ) { }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
    this.paramDetails = this.activatedRoute.snapshot.queryParams;
    this.header = this.paramDetails.type ? this.paramDetails.type === 'view' ? "View" : "Edit" : "Create"
    // this.paymentDetails = this.paymentService.getParticularPaymentDetails(this.paramDetails.id);
    if (this.paramDetails?.id) {
      this.getPaymentDetails();
      this.getPermissions();
    }
    this.changeCompany();
  }

  getPermissions(): void {
    const queryParams: any = {}
    queryParams["doctype"] = Doctypes.paymentTypes;
    queryParams["name"] = this.paramDetails?.id;
    this.http.get(ApiUrls.permissions, { params: queryParams }).subscribe((res: any) => {
      this.userService.setUser(res)
    })
  }

  getPaymentDetails() {
    this.http.get(`${ApiUrls.paymentTypes}/${this.paramDetails?.id}`).subscribe((res: any) => {
      this.paymentDetails = res.data;
    })
  }
  changePayment(e) {
    this.http.get(`${ApiUrls.getClient}?doctype=${Doctypes.paymentTypes}&fieldname=name&filters=${e}`).subscribe((res: any) => {
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
        this.paymentDetails.company = res.data[0].name;
      }
    })
  }
  /**
   * Determines whether submit on
   * @params form
   */
  onSubmit(form: NgForm): void {
    if (form.valid) {
      if (this.paramDetails.type === "edit") {
        this.http.put(`${ApiUrls.paymentTypes}/${this.paramDetails.id}`, form.value).subscribe((res: any) => {
          console.log("edited", res)
          this.router.navigate(["/home/payment-type"])
        })
      } else {
        form.value['doctype'] = Doctypes.paymentTypes;
        form.value['company'] = this.company.name;

        const formData = new FormData();
        formData.append('doc', JSON.stringify(form.value));
        formData.append('action', 'Save');
        this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
          console.log("Added", res)
          this.router.navigate(["/home/payment-type"])
        })

        // this.http.post(`${ApiUrls.paymentTypes}/`,form.value)
      }
    } else {
      form.form.markAllAsTouched()
    }
  }

}
