import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, EventEmitter } from '@angular/core';
import { NgForm, NgModel } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import * as moment from 'moment';
import { ActivatedRoute, Router } from '@angular/router';
import { debounceTime, switchMap } from 'rxjs/operators';
import { forkJoin } from 'rxjs';


class UserFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  search = '';
}

@Component({
  selector: 'app-ip-printers',
  templateUrl: './ip-printers.component.html',
  styleUrls: ['./ip-printers.component.scss']
})
export class IpPrintersComponent implements OnInit {


  filters = new UserFilter();
  onSearch = new EventEmitter();
  formData: any = {};
  posPrinters = [];
  editItem;
  viewType;
  ipPrinterCheck;
  printerValid = false;
  ipValid = false;
  date = moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
  status;
  @ViewChild('printerModal') printerModal: ElementRef;

  constructor(private modal: NgbModal, private http: HttpClient, private toaster: ToastrService, private activatedRoute: ActivatedRoute, private router: Router) { }

  ngOnInit(): void {
    this.formData.status = 'Enable';
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.getPosPrinters();
  }


  updateRouterParams(): void {
    this.router.navigate(['home/ip-printer'], {
      queryParams: this.filters
    });
  }

  addPrinter(type, item) {
    this.printerValid = false;
    this.ipValid = false;
    if (type == 'edit') {
      this.formData = { ...item };
      this.viewType = 'edit';
    } else {
      this.formData = {};
      this.viewType = 'add';
      this.formData.status = 'Enable'
    }
    this.modal.open(this.printerModal, {
      size: 'md',
      centered: true
    });
  }



  contentChange(e) {
    console.log(e);
    this.status = e;
    // if(e === "Disable"){
    //   this.formData.last_used = this.date;
    // }
  }


  onSubmit(form: NgForm) {
    form.form.markAllAsTouched();
    if (form.valid && this.viewType === 'add') {
      if (this.status === 'Disable') {
        this.formData.last_used = this.date;
      }
      this.formData.doctype = Doctypes.posPrinters;
      const formData = new FormData();
      formData.append('doc', JSON.stringify(this.formData));
      formData.append('action', 'Save');
      this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
        if (res) {
          console.log(res);
          this.getPosPrinters();
          this.toaster.success("successfully added");
          this.modal.dismissAll();

        }
      })
    } else {
      if (this.status === 'Disable') {
        this.formData.last_used = this.date;
      }
      this.formData.doctype = Doctypes.posPrinters;

      this.http.put(`${ApiUrls.resource}/${Doctypes.posPrinters}/${this.formData.name}`, this.formData).subscribe((res: any) => {
        if (res) {
          console.log(res);
          this.getPosPrinters();
          this.toaster.success("successfully Updated");
          this.modal.dismissAll();
        }
      })
    }
  }

  getPosPrinters() {
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
      }

      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabPOS Printers`.`modified` desc"
      queryParams.fields = JSON.stringify(["last_used", "printer_ip","port","printer_name", "status", "name"]);
      queryParams.filters = JSON.stringify(queryParams.filters);

      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posPrinters}`, {
        params: {
          fields: JSON.stringify(["count( `tabPOS Printers`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posPrinters}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.posPrinters = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.posPrinters = this.posPrinters.concat(data.data)
        } else {
          this.posPrinters = data.data;
        }

      }
    });
  }

  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }


  getPrinter(e, ref: NgModel) {
    this.ipPrinterCheck = e.target?.value
    this.ValidateIPaddress(this.ipPrinterCheck);
    // if (this.ipPrinterCheck) {
    //   this.http.get(`${ApiUrls.resource}/${Doctypes.posPrinters}`, {
    //     params: {
    //       limit_page_length: "None",
    //       fields: JSON.stringify(["last_used", "printer_ip", "status", "name"]),
    //       filters: JSON.stringify([["printer_ip", "=", `${this.ipPrinterCheck}`]]),
    //     }
    //   }).subscribe((res: any) => {
    //     if (res?.data[0]?.name) {
    //       this.formData.printer_ip = this.ipPrinterCheck;
    //       this.printerValid = true;
    //     } else {
    //       this.formData.printer_ip = this.ipPrinterCheck;
    //       this.printerValid = false;
    //     }
    //   })
    // }

  }


  ValidateIPaddress(ipAddress) {
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipAddress)) {
      this.ipValid = false;
      return (true)
    } else {
      // alert("You have entered an invalid IP address!")
      this.ipValid = true;
      return (false)
    }
  }


}
