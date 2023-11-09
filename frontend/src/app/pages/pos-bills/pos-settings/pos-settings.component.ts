import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, OnInit, ViewChild, EventEmitter } from '@angular/core';
import { NgForm } from '@angular/forms';
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
  printer ='';
  start= 0
}

@Component({
  selector: 'app-pos-settings',
  templateUrl: './pos-settings.component.html',
  styleUrls: ['./pos-settings.component.scss']
})
export class PosSettingsComponent implements OnInit {

  filters = new UserFilter();
  onSearch = new EventEmitter();
  viewType;
  formData: any = {};
  posPrinters = [];
  printersList = [];
  outletList = [];
  editItem;
  date = moment(new Date()).format('YYYY-MM-DD HH:mm:ss');
  @ViewChild('settingsModal') settingsModal: ElementRef;

  constructor(private modal: NgbModal, private http: HttpClient, private toaster: ToastrService, private activatedRoute: ActivatedRoute, private router: Router) { }

  ngOnInit(): void {
    this.formData.status = 'Enable';
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    // this.getPrintSettings();
    this.getPOSPrinterSettings();

  }

  getPOSPrinterSettings(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter)=>{
      // if(this.filters.search){
      //   // this.searchText = this.filters.search.tradeName;
      //   // this.searchType = 'trade_name'
      // }else{
      //   this.searchText = '';
      //   this.searchType = ''
      // }
           
      const dataBody = {
        data: {
          start: this.filters.start,
          end: this.filters.itemsPerPage,
          value: this.filters.search,
          // key: this.searchType,
          // sortKey: this.sortBy,
          type: this.filters.search ? '': 'All'
        }
      }
      return this.http.post(ApiUrls.posPrinterSettings, dataBody)
    })).subscribe((res:any)=>{
      try {
            if (res?.message) {
              if(this.filters.start != 0){
                this.posPrinters = this.posPrinters.concat(res.message?.data)
              }else{
                this.posPrinters = res.message?.data;
              }
              this.filters.totalCount = res.message.count;
            } 
          } catch (e) { console.log(e) }
    })
  }
  
  updateRouterParams(): void {
    this.router.navigate(['home/pos-bills-settings'], {
      queryParams: this.filters
    });
  }

  addPrinterSettings(type, item) {
    this.getOutlets();
    this.getPrinter();
    if (type == 'edit') {
      this.formData = { ...item };
      this.editItem = {...item}
      this.viewType = 'edit';
      
    } else {
      this.formData = {};
      this.viewType = 'add'
      this.editItem = null;
    }
    setTimeout(()=>{
      this.modal.open(this.settingsModal, {
        size: 'md',
        centered: true
      });
    },1000)
    
  }




  onSubmit(form: NgForm) {
    form.form.markAllAsTouched();
    if (form.valid) {
      this.formData.mapped_on = this.date;
      this.formData.doctype = Doctypes.posPrintSettings;
      const formData = new FormData();
      formData.append('doc', JSON.stringify(this.formData));
      formData.append('action', 'Save');

      const url = this.editItem ? `${ApiUrls.resource}/${Doctypes.posPrintSettings}/${this.editItem.name}` : `${ApiUrls.fileSave}`;
      const method = this.editItem ? 'put' : 'post';
      const value = this.editItem ? this.formData : formData;
      this.http[method](url, value).subscribe((res: any) => {
        if (res) {
          console.log(res);
          this.getPOSPrinterSettings();
          this.toaster.success("successfully added");
          this.modal.dismissAll();
        } else {
          console.log(res);
          this.toaster.error(res._server_messages);
        }
      }, (err) => { this.toaster.error("This Outlet is already mapped to other printer.");})
    }
  }



  getPrintSettings() {
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['outlet', 'like', `%${this.filters.search}%`]);
      }

      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabPOS Print Settings`.`modified` desc"
      queryParams.fields = JSON.stringify(["outlet", "printer","printer_name", "mapped_on", "name"]);
      queryParams.filters = JSON.stringify(queryParams.filters);

      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posPrintSettings}`, {
        params: {
          fields: JSON.stringify(["count( `tabPOS Print Settings`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });

      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.posPrintSettings}`, { params: queryParams });
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


  getPrinter() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.posPrinters}`, {
      params: {
        limit_page_length: "None",
        fields: JSON.stringify(["last_used", "printer_ip","printer_name", "status", "name"]),
        // filters: JSON.stringify([["status","like","Enable"]])
      }
    }).subscribe((res: any) => {
      console.log(res);
      this.printersList = res.data;
      if(this.printersList.length && this.formData.printer){
        let printer = this.printersList.find((res:any)=>{
          return res.printer_ip == this.formData.printer
        })
        this.formData.printer = printer.name;
        console.log(this.formData.printer)
      }
    })

  }

  getOutlets() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.outlets}`, {
      params: {
        limit_page_length: "None",
        fields: JSON.stringify(["outlet_name", "name"]),
        // filters: JSON.stringify([["printer_mapped","like","0"]])
      }
    }).subscribe((res: any) => {
      console.log(res);
      this.outletList = res.data;
      if(this.outletList.length && this.formData.outlet){
        let outletName = this.outletList.find((res:any)=>{
          return res.outlet_name == this.formData.outlet
        })
        this.formData.outlet = outletName.name;
        console.log(this.formData.outlet)
      }
    })

  }

  modalClose() {
    this, this.modal.dismissAll();
    this.formData = {}
  }




}
