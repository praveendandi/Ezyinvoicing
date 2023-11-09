import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';

class OutletFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  /**
   * Limit page length of company filter
   * page length
   */
  // search = '';

  config: any;
  search = ''

}
@Component({
  selector: 'app-outlets',
  templateUrl: './outlets.component.html',
  styleUrls: ['./outlets.component.scss']
})
export class OutletsComponent implements OnInit {
  filters = new OutletFilter();
  onSearch = new EventEmitter();
  outletList = [];
  outletDetails: any = {};
  viewType;
  qrImg;
  filename;
  fileToUpload;
  outletCheck;
  outletValid = false;
  files: any = {}
  loginData: any;
  companyDetails :any;
  btnType: any;
  constructor(
    private modal: NgbModal,
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toaster: ToastrService
  ) { }

  ngOnInit(): void {
    this.getOutletData();
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.outletList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.loginData = JSON.parse(localStorage.getItem('login'))
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
  }

  addOutlet(outletModal, type, item) {
    this.outletValid = false;
    this.btnType= type
    if (type == 'edit') {
      this.outletDetails = { ...item }
      console.log(this.outletDetails)
      this.viewType = 'Edit';
    } else {
      // this.outletDetails = ''
      this.viewType = 'Add'
    }
    this.modal.open(outletModal, {
      size: 'lg',
      centered: true
    });
  }
  getOutletData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: OutletFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };

      if (this.filters.search) {
        queryParams.filters.push(['outlet_name', 'like', `%${this.filters.search}%`]);
      }

      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabOutlets`.`creation` desc"
      queryParams.fields = JSON.stringify(["*"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}`, {
        params: {
          fields: JSON.stringify(["count( `tabOutlets`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.outletList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.outletList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.outletList = this.outletList.concat(data.data)
        } else {
          this.outletList = data.data;
        }

        if (this.outletList.length) {
          this.outletList = this.outletList.map((each: any) => {
            if (each) {
              each['payqr'] = each?.static_payment_qr_code.replace('/files/', '');
              each['logo'] = each?.outlet_logo.replace('/files/', '');
            }
            return each;
          })
        }
      }
    });
  }

  updateRouterParams(): void {
    this.router.navigate(['home/outlets'], {
      queryParams: this.filters
    });
  }
  onSubmit(form: NgForm): void {
    console.log(form.value)
    if (this.viewType === 'Edit' && form.valid) {
      form.value['outlet_logo'] = this.files?.outlet_logo || form.value.outlet_logo;
      form.value['static_payment_qr_code'] = this.files?.static_payment_qr_code || form.value.static_payment_qr_code;
      this.http.put(`${ApiUrls.resource}/${Doctypes.outlets}/${this.outletDetails.name}`, form.value).subscribe((res: any) => {
        try {
          if (res.data) {
            this.toaster.success('Saved');
            this.modal.dismissAll();
            this.outletDetails = {}
            this.getOutletData();
          }
        } catch (e) { console.log(e) }
      })
    } else {
      form.form.markAllAsTouched();
      if (form.valid) {
        form.value['doctype'] = Doctypes.outlets;
        form.value['outlet_logo'] = this.files?.outlet_logo;
        form.value['static_payment_qr_code'] = this.files?.static_payment_qr_code;
        const formData = new FormData();
        formData.append('doc', JSON.stringify(form.value));
        formData.append('action', 'Save');
        this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
          try {
            if (res) {
              this.toaster.success('Saved');
              this.modal.dismissAll();
              this.outletDetails = {};
              this.getOutletData();
            } else {
              this.toaster.error(res._server_messages);
            }
          } catch (e) { console.log(e) }
        }, (err) => {
          form.form.setErrors({ error: err.error.message });
        })
      } else {
        form.form.markAllAsTouched();
      }
    }
  }

  showQRImg(showQr, item) {
    if (item) {
      this.qrImg = environment.apiDomain + item;
      let modal = this.modal.open(showQr, { size: 'md', centered: true })
    } else {
      this.qrImg = "";
      this.toaster.error("Error")
    }

  }

  handleFileInput(ev:any, field_name) {
    let files: File[] = ev.target.files
    this.filename = files[0].name;
    console.log("============",this.filename , "=========",field_name)
    if (field_name === 'static_payment_qr_code') {
      this.outletDetails['static_payment_qr_code'] = files[0].name;
      this.checkFileValidate(files,409,403).then((res:any)=>{
        if(!res){
          this.outletDetails.static_payment_qr_code =null
          this.toaster.error('Size should be less than 409*403 pixels')
          return
        }
      })
    }
    if (field_name === 'outlet_logo') {
      this.outletDetails['outlet_logo'] = files[0].name;
      this.checkFileValidate(files,380,180).then((res:any)=>{
        if(!res){
          this.outletDetails.outlet_logo =null
          this.toaster.error('Size should be less than 380*180 pixels')
          return
        }
      })
    }
    // let fname = "the file name here.ext";
    var re = /(\.jpg|\.jpeg|\.bmp|\.gif|\.png)$/i;
    if (!re.exec(this.filename)) {
      alert("File extension not supported!");
      if (field_name === 'static_payment_qr_code') {
        this.outletDetails['static_payment_qr_code'] = "";
      }
      if (field_name === 'outlet_logo') {
        this.outletDetails['outlet_logo'] = "";
      }
    } else {
      this.fileToUpload = files[0];
      if (this.fileToUpload) {
        const formData = new FormData();
        formData.append('file', this.fileToUpload, this.fileToUpload.name);
        formData.append('is_private', '0');
        formData.append('folder', 'Home');
        formData.append('doctype', Doctypes.outlets);
        formData.append('fieldname', field_name);
        // formData.append('docname', this.companyDetails.company_code);
        this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
          if (res.message.file_url) {
            console.log(res);
            if (field_name === 'static_payment_qr_code') {
              this.files['static_payment_qr_code'] = res.message.file_url;
            }
            if (field_name === 'outlet_logo') {
              this.files['outlet_logo'] = res.message.file_url;
            }

          }
        })
      }
    }
  }
  checkFileValidate(files,validWidth,validHeight){
    return new Promise((resolve,reject)=>{
      var reader = new FileReader();
      //Read the contents of Image File.
      reader.readAsDataURL(files[0]);
      reader.onload = function (e) {
          //Initiate the JavaScript Image object.
          var image:any = new Image();

          //Set the Base64 string return from FileReader as source.
          image.src = e.target.result;

          //Validate the File Height and Width.
          image.onload = function () {
              var height = this.height;
              var width = this.width;
              if (height <= validHeight || width <= validWidth) {
                resolve(true);
              }else{
                resolve(false);
              }

          };

      }
    })

  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }



  getOutlets(e) {
    console.log(e.target?.value)
    this.outletCheck = e.target?.value
    if (this.outletCheck) {
      this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}`, {
        params: {
          limit_page_length: "None",
          fields: JSON.stringify(["outlet_name", "name"]),
          filters: JSON.stringify([["outlet_name", "=", `${this.outletCheck}`]]),
        }
      }).subscribe((res: any) => {
        if (res?.data[0]?.name) {
          this.outletDetails.outlet_name = this.outletCheck;
          this.outletValid = true;
        } else {
          this.outletDetails.outlet_name = this.outletCheck;
          this.outletValid = false;
        }
      })
    }

  }



}
