import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { OtpComponent } from 'src/app/shared/models/otp/otp.component';
import { LocalStorageService, Storekeys } from 'src/app/shared/services/local-storage.service';
import { MonthYearService } from 'src/app/shared/services/month-year.service';

@Component({
  selector: 'app-save-gstin',
  templateUrl: './save-gstin.component.html',
  styleUrls: ['./save-gstin.component.scss']
})
export class SaveGstinComponent implements OnInit {

  yearsList: any = [];
  monthList: any = [];
  month: any = '';
  year: any = '';
  loginDetails: any;
  retSavedList: any = [];
  submitSuccess = false;
  submitResp :any ={};
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  constructor(
    private http: HttpClient,
    private router: Router,
    private toastr: ToastrService,
    private yearService: MonthYearService,
    private storageService: LocalStorageService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {

    this.yearService.years.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.yearsList = data);

    this.yearService.months.pipe(takeUntil(this.destroyEvents))
      .subscribe((data) => this.monthList = data);
    const d = new Date();
    d.setMonth(d.getMonth() - 1);
    // this.month =  d.toLocaleString('default', { month: 'long' });
    this.month = JSON.stringify(d.getMonth() + 1);
    this.year = d.getFullYear();
    this.loginDetails = JSON.parse(this.storageService.getRawValue(Storekeys.LOGIN) || '')

    this.getRetSaveData();

  }


  returnSave() {
    let dataObj = {
      // company_code: this.loginDetails?.company,
      month: this.month,
      year: JSON.stringify(this.year)
    }
    this.http.post(ApiUrls.retSave, dataObj).subscribe((res: any) => {
      if (res.message === true) {
        this.getRetSaveData()
      }
    })
  }

  getRetSaveData() {
    this.http.get(`${ApiUrls.resource}${Doctypes.gstrSavedData}`, {
      params: {
        // filters: JSON.stringify(['period', '=', `${this.month}${this.year}`]),
        fields: JSON.stringify(['*']),
        order_by: "`tabGstr One Saved Details`.`creation` desc"
      }
    }).subscribe((res: any) => {
      if (res.data) {
        this.retSavedList = res.data;
        
        // this.returnSave();
        // if (this.retSavedList.length === 0) {
        //   this.returnSave();
        // }
      } else {
        this.returnSave();
      }
    })
  }

  retSubmitFun(each: any) {
    const modalRes = this.modal.open(OtpComponent, { size: 'md', centered: true })
    modalRes.result.then((resOtp: any) => {
      console.log(resOtp)
      if (resOtp) {
        this.http.post(ApiUrls.retSubmit, { gstr_one_save_name: each?.name, otp: resOtp }).subscribe((res: any) => {
          if(res?.message?.success){
            this.submitSuccess = true;
          }else{
            this.submitSuccess = false;
            this.toastr.error(res?.message?.message)
          }
        })
      }
    })
    // this.http.post(ApiUrls.retSubmit,{gstr_one_save_name})
  }
  ngOnDestroy() {
    this.destroyEvents.next();
    this.destroyEvents.unsubscribe();
  }

}
