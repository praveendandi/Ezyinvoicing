import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { SacHsnComponent } from 'src/app/shared/models/sac-hsn/sac-hsn.component';
import { environment } from 'src/environments/environment';
class SacHsnFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  synced_to_erp = '';

  /**
   * Limit page length of company filter
   * page length
   */
  // search = '';

  config: any;
  searchFilter = {
    name: '',
    code: '',
    sacCode: ''
  }

}


@Component({
  selector: 'app-sac-hsn-codes',
  templateUrl: './sac-hsn-codes.component.html',
  styleUrls: ['./sac-hsn-codes.component.scss']
})
export class SacHsnCodesComponent implements OnInit, OnDestroy {

  filters = new SacHsnFilter();
  onSearch = new EventEmitter();
  codesDetails = [];
  p = 1;
  apiDomain = environment.apiDomain;
  sacCodeDetails: any = {};
  sacid;
  viewType;
  company;
  loginUser: any = {};
  loginUSerRole;
  status = false;
  companyDetails;
  @ViewChild('content', { static: true }) content: ElementRef;
  invoiceInfo: any;
  invoice_number;
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private toaster: ToastrService
  ) {



  }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.codesDetails = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.searchFilter) {
        const dateBy = JSON.parse(res.searchFilter)
        this.filters.searchFilter.name = dateBy.name;
        this.filters.searchFilter.code = dateBy.code;
        this.filters.searchFilter.sacCode = dateBy.sacCode;
      }
    })
    this.getCodesData()
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.loginUSerRole = this.loginUser.rolesFilter.some((each: any) => (each == 'ezy-IT' || each == 'ezy-Finance'))
  }



  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.searchFilter = JSON.stringify(temp.searchFilter);
    this.router.navigate(['home/sac-hsn-codes'], {
      queryParams: temp
    });
  }

  // checkPagination(): void {
  //   if (this.filters.totalCount < (this.filters.itemsPerPage * this.filters.currentPage)) {
  //     this.filters.currentPage = 1
  //     this.updateRouterParams()
  //   } else {
  //     this.updateRouterParams()
  //   }
  // }

  /**
   * Navigates sac hsn codes component
   * @params data
   * @params type
   */
  navigate(data: any, type: string): void {
    this.router.navigate(['/home/sac-hsn-codes-details'], { queryParams: { id: data.name, type }, queryParamsHandling: 'merge' });
  }

  // getSacData(): void {
  //   this.activatedRoute.queryParams.pipe(switchMap((params: SacHsnFilter) => {
  //     this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
  //     this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
  //     this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
  //     this.filters.search = params.search || this.filters.search;
  //     this.filters.totalCount = this.filters.totalCount;
  //     const queryParams: any = { filters: [] };

  //     if (this.filters.search) {
  //       queryParams.filters.push(['description', 'like', `%${this.filters.search}%`]);
  //       queryParams.limit_start = 0;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //       this.filters.currentPage = 1
  //     } else {
  //       queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
  //       queryParams.limit_page_length = this.filters.itemsPerPage;
  //     }
  //     queryParams.order_by = "`tabSAC HSN CODES`.`modified` desc"
  //     queryParams.fields = JSON.stringify(["name", "transactioncode", "owner", "creation", "modified", "modified_by", "idx", "description", "sgst", "cgst", "type", "status", "igst", "taxble", "code", "company"]);
  //     queryParams.filters = JSON.stringify(queryParams.filters);
  //     const countApi = this.http.get(`${ApiUrls.sacHsn}`, {
  //       params: {
  //         fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"]),
  //         filters: queryParams.filters
  //       }
  //     });
  //     const resultApi = this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams });
  //     return forkJoin([countApi, resultApi]);
  //   })).subscribe((res: any) => {
  //     const [count, data] = res;
  //     this.filters.totalCount = count.data[0].total_count;
  //     if (data.data) {
  //       this.codesDetails = data.data;
  //     }
  //   });
  // }

  getInactive() {
    this.status = !this.status
    console.log("Status ===", this.status)
    this.getCodesData();
  }
  getCodesCount(): void {
    this.http.get(`${ApiUrls.sacHsn}`, {
      params: {
        fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getCodesData()
    })
  }
  getCodesData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: SacHsnFilter) => {
      // this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.status) {
        queryParams.filters.push(['status', 'like', `In-Active`]);
      } else {
        queryParams.filters.push(['status', 'like', `Active`]);
      }
      if (this.filters.synced_to_erp) {
        queryParams.filters.push(['synced_to_erp', 'like', `%${this.filters.synced_to_erp}%`]);
      }
      if (this.filters.searchFilter.name) {
        queryParams.filters.push(['description', 'like', `%${this.filters.searchFilter.name}%`]);
      }
      if (this.filters.searchFilter.code) {
        queryParams.filters.push(['transactioncode', 'like', `%${this.filters.searchFilter.code}%`]);
      }
      if (this.filters.searchFilter.sacCode) {
        queryParams.filters.push(['code', 'like', `%${this.filters.searchFilter.sacCode}%`]);
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabSAC HSN CODES`.`modified` desc"
      // ["name", "transactioncode", "owner", "creation", "modified", "modified_by", "idx", "description", "sgst", "cgst", "type", "status", "igst", "taxble", "code", "company", "net", "service_charge", "vat_rate", "state_cess_rate", "central_cess_rate", "accommodation_slab", "service_charge_net","ignore","sac_index","exempted","ignore_non_taxable_items"]
      queryParams.fields = JSON.stringify(['*']);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.sacHsn}`, {
        params: {
          fields: JSON.stringify(["count( `tabSAC HSN CODES`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.sacHsn}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.codesDetails = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.codesDetails.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.codesDetails = this.codesDetails.concat(data.data)
        } else {
          this.codesDetails = data.data;
        }

      }
    });
  }

  editHsn(item, sactype, type) {
    console.log("item ====", item)
    this.sacid = item.name;
    this.viewType = sactype;
    this.sacCodeDetails.one_sc_applies_to_all = item?.one_sc_applies_to_all == 0 ? false : true;
    this.sacCodeDetails.ignore = item?.ignore == 0 ? false : true;
    this.sacCodeDetails.synced_to_erp = item?.synced_to_erp == 0 ? false : true;
    // this.modal.open(this.content, {
    //   size: 'lg',
    //   centered: true,
    //   windowClass: 'modal-sac',
    //   animation: false
    // });
    const editSacCode = this.modal.open(SacHsnComponent, {
      size: 'lg',
      centered: true,
      windowClass: 'modal-sac',
      animation: false
    })
    editSacCode.componentInstance.editSacHsn = item;
    editSacCode.componentInstance.editType = type;
    editSacCode.result.then((res: any) => {
      if (res == 'close') {
        this.getCodesData();
      }

    }, (reason) => {
      console.log(reason);
    })
    this.getSac();
  }


  getSac(): void {
    this.http.get(`${ApiUrls.sacHsn}/${this.sacid}`).subscribe((res: any) => {
      try {
        if (res) {
          this.sacCodeDetails = res.data;
        }
      } catch (e) { console.log(e) }
    })
  }


  onSubmit(form: NgForm): void {
    console.log(form.value)
    form.value['one_sc_applies_to_all'] = form.value.one_sc_applies_to_all == true ? 1 : 0;
    form.value['ignore'] = form.value.ignore == true ? 1 : 0;
    form.value.service_charge_rate = form.value.one_sc_applies_to_all == true ? 0 : form.value.service_charge_rate
    if (this.viewType === 'edit' && form.valid) {
      this.http.put(`${ApiUrls.sacHsn}/${this.sacid}`, form.value).subscribe((res: any) => {
        try {
          if (res.data) {
            this.toaster.success('Saved');
            this.modal.dismissAll();
            this.getCodesData();
          }
        } catch (e) { console.log(e) }
      })
    } else {
      form.form.markAllAsTouched();
      if (form.valid) {
        form.value['doctype'] = Doctypes.sacCodes;
        form.value['company'] = this.company.name;

        const formData = new FormData();
        formData.append('doc', JSON.stringify(form.value));
        formData.append('action', 'Save');
        this.http.post(`${ApiUrls.fileSave}`, formData).subscribe((res: any) => {
          try {
            if (res) {
              this.toaster.success('Saved');
              this.modal.dismissAll()
              this.getCodesData();
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

  addHsn(value) {
    this.sacCodeDetails = {
      one_sc_applies_to_all: true,
      state_cess_rate: 0,
      central_cess_rate: 0,
      vat_rate: 0,
      igst: 0,
      cgst: 0,
      sgst: 0

    };
    this.viewType = 'add'

    // this.modal.open(this.content, {
    //   size: 'lg',
    //   centered: true,
    //   windowClass: 'modal-sac',
    //   animation: false
    // });

    const modalData = this.modal.open(SacHsnComponent, {
      size: 'lg',
      centered: true,
      windowClass: 'modal-sac',
      animation: false

    });

    modalData.result.then((res: any) => {
      this.getCodesData();

    })


  }

  ngOnDestroy() {
    this.modal.dismissAll();
  }

  checkPagination(): void {
    // console.log(this.codesDetails.length)
    // if(this.filters.itemsPerPage < this.codesDetails.length){
    this.filters.currentPage = 1
    this.updateRouterParams()
    // }else{
    //   this.updateRouterParams() 
    // }
  }

  howToAddSac(addSacHsn) {
    this.modal.open(addSacHsn, {
      size: 'xl',
      centered: true,
    })
  }

  // synctoGST(){
  //   let data = {
  //     sync_mode: 'Manual',
  //     doctype: Doctypes.items,
  //     now: true
  //   }
  //   this.http.post(ApiUrls.sync_data_to_erp, data).subscribe((res: any) => {
  //     if (res.message.success) {
  //       this.toaster.success(res.message.message);
  //     } else {
  //       this.toaster.error(res.message.message)
  //     }
  //   })
  // }


  sacHsnType() {
    this.http.get(ApiUrls.sac_code_details).subscribe((res: any) => {
      console.log(res)
      window.open(`${this.apiDomain}${res.message.file_path}`, "_blank");
    })
  }



}
