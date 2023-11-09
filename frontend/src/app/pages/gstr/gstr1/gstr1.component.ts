import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { merge } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { OtpComponent } from 'src/app/shared/models/otp/otp.component';
import { UploadExcelFileComponent } from 'src/app/shared/models/upload-excel-file/upload-excel-file.component';

import { LocalStorageService, Storekeys } from 'src/app/shared/services/local-storage.service';
import { MonthYearService } from 'src/app/shared/services/month-year.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-gstr1',
  templateUrl: './gstr1.component.html',
  styleUrls: ['./gstr1.component.scss']
})
export class Gstr1Component implements OnInit {

  gstr1InvoicesData: any = {};
  loginDetails: any = {};
  // yearsList: any = [];
  // monthList: any = [];
  month: any = '';
  year: any = '';
  property: any = [];
  propertyList: any = [];
  reconcileSummary: any = {}
  domain = environment.apiDomain;
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  gstr1DocumentSequence: any;

  constructor(
    private yearService: MonthYearService,
    private storageService: LocalStorageService,
    private http: HttpClient,
    private modal: NgbModal,
    private router: Router,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {

    this.yearService.getSelectedYear().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return; }
      this.year = res;
      if (this.month != '' && this.year != '') {
        this.getGSTR1Data();
        this.getGSTR1DocumentSeries()
      }

      // this.getReconcileSummary()
    })
    this.yearService.getSelectedMonth().pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (!res) { return; }
      this.month = res;
      if (this.month != '' && this.year != '') {
        this.getGSTR1Data();
        this.getGSTR1DocumentSeries()
      }
      // this.getGSTR1Data();
      // this.getReconcileSummary()
    })

    this.loginDetails = JSON.parse(this.storageService.getRawValue(Storekeys.LOGIN) || '')
    // if (this.loginDetails?.company) {
    //   this.getPropertyDetails()
    // }

  }


  returnSave() {
    let dataObj = {
      company_code: this.loginDetails?.company,
      month : JSON.stringify(this.month),
      year: JSON.stringify(this.year)
    }
    this.http.post(ApiUrls.retSave,dataObj).subscribe((res:any)=>{
      if(res){
        this.returnSaveOtp()
      }
    })


  }
  returnSaveOtp(){
    const modalRes =  this.modal.open(OtpComponent,{size:'md',centered:true})
     modalRes.result.then((res:any)=>{
      if(res){
        let dataObj = {
          company_code: this.loginDetails?.company,
          month : JSON.stringify(this.month),
          year: JSON.stringify(this.year),
          otp : res
        }
        this.http.post(ApiUrls.retSave,dataObj).subscribe((res:any)=>{
          if(res){
            this.router.navigate(['/gstr/save-gstin'])
          }
        })

      }
     })
  }

  SelectByData(e: any, type: string) {
    console.log(e);
    if (!e) { return }
    // if (type === 'month') {
    //   this.month = e;
    // }
    // if (type === 'year') {
    //   this.year = e;
    // }
    if (type === 'property') {
      this.property = e;
    }
    this.getGSTR1Data();
    this.getGSTR1DocumentSeries()
    // this.getReconcileSummary()
  }

  // getPropertyDetails() {
  //   this.http.get(`${ApiUrls.resource}${Doctypes.property}`, {
  //     params: {
  //       fields: JSON.stringify(['*'])
  //     }
  //   }).subscribe((res: any) => {
  //     if (res?.data) {
  //       this.propertyList = res?.data;
  //     }
  //   })
  // }



  getGSTR1Data() {
    // let filters: any = []
    // if (this.property.length) {
    //   filters.push(['property', 'in', this.property])
    // }
    let obj = {
      month: this.month,
      year: this.year,
      properties: JSON.stringify(this.property)
      // filters : JSON.stringify(filters)
    }

    this.http.get(`${ApiUrls.dashboardGSTR1}`, { params: obj }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.gstr1InvoicesData = res?.message?.data;
      } else {
        this.toastr.error("Error");
      }
    })
  }

  getGSTR1DocumentSeries() {

    let obj = {
      month: this.month,
      year: this.year,
      // properties: JSON.stringify(this.property)
    }

    this.http.get(`${ApiUrls.document_series}`, { params: obj }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.gstr1DocumentSequence = res?.message?.data;
      } else {
        this.toastr.error("Error");
      }
    })
  }

  /****** Download Workbook */
  export_workbook(){
    this.http.get(`${ApiUrls.export_workbook}`,{params:{month:this.month,year:this.year}}).subscribe((res:any)=>{
      console.log(res)
      if(res?.message?.success){
        window.open(`${this.domain}${res?.message?.file_url}`);
      }
    })
  }
  /*********** */

  /************ Upload Excel */
  uploadExcelFile(type:string){
    let modal = this.modal.open(UploadExcelFileComponent,{size: 'xl', centered: true, windowClass: 'custom-modal'})
  }
  /************ */
  ngOnDestroy() {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }
}
