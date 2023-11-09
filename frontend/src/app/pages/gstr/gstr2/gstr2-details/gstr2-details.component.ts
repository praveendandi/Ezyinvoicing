import { Location } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Event, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { LocalStorageService, Storekeys } from 'src/app/shared/services/local-storage.service';

class SearchFilter {
  itemsPerPage = 50;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  from='';
  to = '';
  legal_name = 'All';
  invoice_number=''
}
@Component({
  selector: 'app-gstr2-details',
  templateUrl: './gstr2-details.component.html',
  styleUrls: ['./gstr2-details.component.scss']
})
export class Gstr2DetailsComponent implements OnInit {
  filters = new SearchFilter();
  onSearch = new EventEmitter();
  filename: any
  fileToUpload: any

  loginDetails: any = {}
  companyDetails: any;
  secondUpdate = false

  dupThValues: any = []
  tableArrs: any = {
    thValues: [],
    gstr2XcelTableHeadings: [],
    gstr2XcelList: [],
    mappedArr: []
  }
  xcelModal = {
    uploadedFileData: false,
    mappedBtn: false,
    uploadedFilepath: '',
    showMappedBtnTh: false
  }
  gstr2AList: any = [];
  allSuppliersList: any = []
  b2bInvoicesData:any;
  constructor(
    private router: Router,
    private http: HttpClient,
    private location: Location,
    private modal: NgbModal,
    private activatedRoute: ActivatedRoute,
    private storageService : LocalStorageService
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    this.loginDetails =JSON.parse(this.storageService.getRawValue(Storekeys.LOGIN) || '')
    let queryParams = this.activatedRoute.snapshot.queryParams
    console.log(queryParams)
    this.filters.from = queryParams.from;
    this.filters.to = queryParams.to;
    this.getCompanyDetails();
    this.getGSTR2AListData();
    this.getSuplliersList();
    this.getb2bTotalData();
  }
  updateRouterParams(): void {
    // const temp = JSON.parse(JSON.stringify(this.filters));
    // temp.search = JSON.parse(JSON.stringify(temp.search));
    // console.log("temp ====",temp)
    this.router.navigate(['gstr/gstr2-details'], {
      queryParams: this.filters
    });
  }
  getSuplliersList() {
    const queryParams: any = {};
    queryParams.limit_page_length = this.filters.totalCount;
    queryParams.limit_start = this.filters.start
    queryParams.order_by = "`tabGSTR 2A`.`modified` desc"
    queryParams.fields = JSON.stringify(["name", "legal_name", "gstin"]);
    this.http.get(`${ApiUrls.resource}${Doctypes.gstr2a}`, { params: queryParams }).subscribe((res: any) => {
      if (res.data) {
        this.allSuppliersList = res.data.filter((v: any, i: any, a: any) => a.findIndex((t: any) => (t.legal_name === v.legal_name)) === i)
      }
    })
  }
  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
  getGSTR2AListData() {
    this.activatedRoute.queryParams.pipe(switchMap((params: any = SearchFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      // this.filters.search = params.search || this.filters.search;
      // console.log("search ===",this.filters.search)
      const queryParams: any = { filters: [] };
      if(this.filters.from && this.filters.to){
        queryParams.filters.push([`invoice_date`, 'Between', [this.filters.from, this.filters.to]])
      }
      if (this.filters.legal_name !== "All") {
        queryParams.filters.push(['legal_name', 'like', `%${this.filters.legal_name}%`]);
      }
      if (this.filters.invoice_number) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.invoice_number}%`]);
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabGSTR 2A`.`modified` desc"
      queryParams.fields = JSON.stringify(["name", "creation", "modified", "modified_by", "idx", "gstin", "legal_name", "invoice_number", "invoice_type", "invoice_date", "invoice_value", "place_of_supply", "supply_attract_reverse_charge", "tax_rate", "taxable_value", "igst", "cgst", "sgst", "cess", "amendment_made", "company"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}${Doctypes.gstr2a}`, {
        params: {
          fields: JSON.stringify(["count( `tabGSTR 2A`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}${Doctypes.gstr2a}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.gstr2AList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index: any) => {
        if (each) {
          each.index = this.gstr2AList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.gstr2AList = this.gstr2AList.concat(data.data)
        } else {
          this.gstr2AList = data.data;
        }

      }
    });
  }
  getCompanyDetails() {
    this.http.get(`${ApiUrls.resource}${Doctypes.company}/${this.loginDetails.company}`).subscribe((res: any) => {
      if (res.data) {
        this.companyDetails = res.data;
        this.getGstr2ATheads();
      }
    })
  }
  getGstr2ATheads() {
    this.http.get(`${ApiUrls.gstr2ATheads}`).subscribe((res: any) => {
      if (res?.message?.fields) {
        this.tableArrs.thValues = res?.message?.fields;
        this.tableArrs.thValues.map((each: any) => {
          if (each) {
            each['selected'] = false;
          }
        })
      }
    })
  }
  gotoBack() {
    // this.location.back()
    this.router.navigate(['gstr/gstr2'])
  }
  addEditInvoice(type: any) {
    this.router.navigate(['home/invoice-details'])
  }

  uploadExcelFile(uploadFile: any): void {
    this.filename = '';
    this.fileToUpload = '';
    this.xcelModal = {
      uploadedFileData: false,
      mappedBtn: false,
      uploadedFilepath: '',
      showMappedBtnTh: false
    }

    let modal = this.modal.open(uploadFile, { size: 'xl', centered: true, windowClass: 'custom-modal', backdrop: 'static' })
  }

  handleFileInput(e: any) {
    this.filename = e.target.files[0].name;
    this.fileToUpload = e.target.files[0];
    // var reader = new FileReader();
    // reader.readAsDataURL(e.target.files[0]);
    // reader.onload = (_event) => {
    //   let imgURL = reader.result;
    //   console.log(imgURL)
    // }

  }

  uploadService() {
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      formData.append('doctype', Doctypes.gstr2a);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message?.file_url) {
          this.xcelModal.uploadedFilepath = res.message?.file_url;
          this.xcelModal.uploadedFileData = true
          this.http.post(`${ApiUrls.gstr2Excel}`, {
            data: {
              file_path: res.message?.file_url,
              company: this.loginDetails.company
            }
          }).subscribe((resXcel: any) => {
            if (resXcel.message.success) {
              this.xcelModal.mappedBtn = true;
              this.tableArrs.gstr2XcelList = resXcel.message.data;
              let headings = Object.keys(resXcel.message.data[0])
              headings.map((each: any, index: any) => {
                if (each) {
                  this.tableArrs.gstr2XcelTableHeadings.push({ "value": each, "id": index, "selected": false, mappedHead: '' });
                }
              })

              if (this.companyDetails?.mapping_fields !== "" && this.tableArrs.gstr2XcelTableHeadings.length > 0) {
                this.xcelModal.showMappedBtnTh = true
                let companyheadingList: any = JSON.parse(this.companyDetails?.mapping_fields)
                this.tableArrs.gstr2XcelTableHeadings.forEach((item: any) => {
                  companyheadingList.forEach((each: any) => {
                    if (item.value == Object.values(each)[0]) {
                      item.mappedHead = Object.values(each)[1]
                    }
                  })
                  return item;
                })

                this.tableArrs.thValues.forEach((item: any) => {
                  companyheadingList.forEach((each: any) => {
                    if (item.label == Object.values(each)[1]) {
                      item.selected = true
                    }
                  })
                  return item;
                })
                this.tableArrs.thValues = this.tableArrs.thValues.filter((res: any) => !res.selected)

                //   this.secondUpdate =true
                //   this.tableArrs.thValues=[]
                //   // headings.map((each: any, index: any) => {
                //   //   if (each) {
                //   //     this.tableArrs.gstr2XcelTableHeadings.push({ "value": each, "id": index, "selected": false });
                //   //   }
                //   // })
                //   let headingFromCompany = JSON.parse(this.companyDetails?.mapping_fields)

                //   // let templist: any = []
                //   // headingFromCompany.map((i:any) => {
                //   //   templist.push({ "value": "each", "id": "index", "selected": false,mappedHead: ''})
                //   // })
                //   headings.map((each: any, index: any) => {
                //     let i = headingFromCompany.findIndex((x: any) => x[Object.keys(x)[1]] === each);
                //     // console.log(i)
                //     this.tableArrs.gstr2XcelTableHeadings.push({ "value": each, "id": index, "selected": false });

                //     if (i != -1) {
                //       // console.log(each)
                //       this.tableArrs.thValues.push({ "value": each, "id": i, "selected": true, mappedHead: each })
                //     } else {
                //       this.tableArrs.thValues.push({ "value": each, "id": i, "selected": false, mappedHead: '' })
                //     }
                //     // console.log(each)

                //     // console.log(each[Object.keys(each)[0]])
                //     // let keyindex = headings.indexOf(each[Object.keys(each)[0]])
                //     // // console.log(keyindex)
                //     // templist.splice(keyindex, 1, { "value": each[Object.keys(each)[0]], "id": keyindex, "selected": true,mappedHead: Object.keys(each)[1]})
                //   })
                //   // this.tableArrs.thValues = []
                //   // templist.map((each: any) => {
                //   //   console.log(each)
                //   //   // if (each.value != "each") {
                //   //     this.tableArrs.thValues.push(each)
                //   //   // }
                //   // })
                //   console.log(this.tableArrs.thValues)

              }
            }
          })
        } else {
          console.log(res)
        }
      })
    }
  }

  selectedITem(each: any, staticTh: any, id: any) {
    console.log(each, id, staticTh)
    each.selected = !each.selected;

    if (staticTh.mappedHead != '') {
      this.tableArrs.thValues.map((item: any) => {
        if (item.label == staticTh.mappedHead) {
          item.selected = false;
        }
        return item;
      })
      this.tableArrs.mappedArr.splice(this.tableArrs.mappedArr.findIndex((res: any) => res.mappedTh == staticTh.mappedHead), 1);
    }
    //  this.tableArrs.thValues = this.tableArrs.thValues.filter((res: any) => !res.selected)
    console.log("====== th  ", this.tableArrs.thValues)
    this.tableArrs.gstr2XcelTableHeadings = this.tableArrs.gstr2XcelTableHeadings.map((heading: any) => {
      if (heading.id === id) {
        heading.mappedHead = each.label
      }
      return heading
    })
    let obj: any = {}
    obj[each.fieldname] = staticTh.value;
    obj['mappedTh'] = each.label;
    this.tableArrs.mappedArr.push(obj)
    console.log("......mappedArr=====", this.tableArrs.mappedArr)
  }

  submitMappedData() {
    this.http.post(`${ApiUrls.gstr2AMapped}`, {
      data: { file_path: this.xcelModal.uploadedFilepath, company: this.loginDetails.company, mapping_fields: this.tableArrs.mappedArr }
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.tableArrs = {
          gstr2XcelTableHeadings: [],
          gstr2XcelList: [],
          mappedArr: []
        }
        this.getCompanyDetails();
        this.modal.dismissAll();
      }
    })
  }

  resetbtn() {
    this.xcelModal.showMappedBtnTh = false;
    this.tableArrs.gstr2XcelTableHeadings.map((res: any) => res.mappedHead = "")
    this.tableArrs.thValues = this.tableArrs.thValues.map((res: any) => res.selected = false)
  }

  modalCancel(type: any) {
    this.tableArrs.gstr2XcelTableHeadings = []; this.tableArrs.gstr2XcelList = []; this.tableArrs.mappedArr = [];
    if (this.tableArrs.thValues.length > 0) {
      this.tableArrs.thValues.map((res: any) => {
        if (res?.selected) {
          res.selected = false
        }
      })
    }

    this.modal.dismissAll()

  }

  getb2bTotalData(){
    this.http.post(ApiUrls.gstr2Ab2bData,{data:{from:this.filters.from,to:this.filters.to}}).subscribe((res:any)=>{
      if(res.message.data){
        this.b2bInvoicesData = res.message.data;
      }
    })
  }
}
