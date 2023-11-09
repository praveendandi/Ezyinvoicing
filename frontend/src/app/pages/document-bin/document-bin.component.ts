import { HttpClient } from '@angular/common/http';
import { Component, OnInit, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap, takeUntil } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';
import * as Moment from 'moment';
import { ClipboardService } from 'ngx-clipboard'
import { SocketService } from 'src/app/shared/services/socket.service';
import { ToastrService } from 'ngx-toastr';
import moment from 'moment';

class DocBinFilter {
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
  config: any;
  searchFilter = {
    document_printed: '',
    invoice_number: '',
    document_type: '',
    creation: new Date()
  }
}
@Component({
  selector: 'app-document-bin',
  templateUrl: './document-bin.component.html',
  styleUrls: ['./document-bin.component.scss']
})
export class DocumentBinComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();
  @ViewChild('uploadModal') uploadModal: ElementRef;
  filters = new DocBinFilter();
  onSearch = new EventEmitter();

  docBinList = [];
  companyDetails;
  errorMessage;
  successMessage;
  filename;
  fileToUpload;
  imgURL;
  seletedITem;
  domain;
  copiedText = false;
  copiedIndex;
  parserFile;
  errDocument = [];
  checkErrDocument = [];
  reprocessDoc = false;
  reprocessButn = false;
  today = Moment(new Date()).endOf('day').toDate();
  lastSevenDays = Moment(new Date()).subtract(7, 'days').startOf('day').toDate();
  dateOfreprocess;
  constructor(
    private http: HttpClient,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private modal: NgbModal,
    private _clipboardService: ClipboardService,
    private sockectService: SocketService,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {
    this.domain = environment.apiDomain
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    console.log(this.companyDetails)
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.docBinList = [];
      this.filters.start = 0;
      this.filters.totalCount = 0;
      this.updateRouterParams()
    });

    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res.searchFilter) {
        const dateBy = JSON.parse(res.searchFilter)
        this.dateOfreprocess = dateBy
        this.filters.searchFilter.document_printed = dateBy.document_printed;
        this.filters.searchFilter.invoice_number = dateBy.invoice_number;
        this.filters.searchFilter.document_type = dateBy.document_type;
        this.filters.searchFilter.creation = dateBy.creation;
      }
    })

    this.sockectService.newInvoice.pipe(takeUntil(this.destroyEvents)).subscribe((res: any) => {
      if (res?.message?.type === 'document_bin_insert') {
        this.getBinList();
      }
      if (res?.message?.type === 'redo bin error') {
        // this.errDocument
      }
    })
    this.getBinList()
  }

  updateRouterParams(): void {
    const temp = JSON.parse(JSON.stringify(this.filters));
    temp.searchFilter = JSON.stringify(temp.searchFilter);
    this.router.navigate(['home/document-bin'], {
      queryParams: temp
    });
  }

  navigate(item) {
    const domain = environment.apiDomain;
    const fileUrl = `${domain}${item.invoice_file}`
    window.open(fileUrl, '_blank');
  }

  openModalReprocess(multiReprocess) {
    let list = { ...this.docBinList }
    this.errDocument = this.docBinList.filter((each: any) => each.document_printed == 'No');
    let modal = this.modal.open(multiReprocess, {
      centered: true, size: 'md'
    })
    modal.result.then((res: any) => {
      this.errDocument = []
      this.reprocessDoc = false;
      this.getBinList()
    })
  }
  async reprocessMulti() {
    if (!window.confirm(`Are you sure to Reprocess Error documents? `)) {
      return null;
    } else {
      let date = moment(this.filters.searchFilter.creation).format('YYYY-MM-DD')
      this.http.post(ApiUrls.reprocessDocmentBin, { docdate: date }).subscribe((res: any) => {
        if (res) {
          this.modal.dismissAll();
        }
      })
      // const apiCalls = this.errDocument.map((each: any, idx) => {

      //   return new Promise((resolve, reject) => {

      //     this.errDocument[idx] = { uploaded: '', invoice_number: each.invoice_number, name: each.name, invoice_file: each.invoice_file };

      //     let dataObj = {
      //       filepath: each?.invoice_file
      //     }
      //     let api = this.companyDetails?.new_parsers == 0 ? `${ApiUrls.reinitiate}` : `${ApiUrls.new_reinitiate}`
      //     this.http.post(`${api}${this.companyDetails?.name}.${'invoice_parser.file_parsing'}`, dataObj).subscribe((res: any) => {
      //       if (res?.message?.success) {
      //         this.errDocument[idx].uploaded = "success";
      //       } else {
      //         this.errDocument[idx].uploaded = "failed";
      //       }
      //     }, (err) => {
      //       resolve
      //       console.log('err: ', err);
      //     });
      //     resolve(idx)
      //   })

      // })
      // await Promise.all(apiCalls);
      // this.reprocessDoc = true;

    }
  }
  reprocess(item) {
    let dataObj = {
      filepath: item?.invoice_file
    }
    let api = this.companyDetails?.new_parsers == 0 ? `${ApiUrls.reinitiate}` : `${ApiUrls.new_reinitiate}`
    this.http.post(`${api}${this.companyDetails?.name}.${'invoice_parser.file_parsing'}`, dataObj).subscribe((res: any) => {
      if (res?.message?.success) {
        this.modal.dismissAll();
        this.getBinList()
      }
    })
  }

  getCodesCount(): void {
    this.http.get(`${ApiUrls.resource}/${Doctypes.documentBin}`, {
      params: {
        fields: JSON.stringify(["count( `tabDocument Bin`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getBinList()
    })
  }
  refreshParams(): void {
    this.filters.itemsPerPage = 20;
    this.filters.currentPage = 1;
    this.filters.start = 0;
    this.filters.totalCount = 0;
    this.filters.searchFilter.document_printed = '';
    this.filters.searchFilter.creation = new Date();
    this.filters.searchFilter.document_type = ''
    this.filters.searchFilter.invoice_number = '';
    this.getBinList();
  }
  getBinList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: DocBinFilter) => {
      const queryParams: any = { filters: [] };
      if (this.filters.searchFilter.document_printed) {
        queryParams.filters.push(['document_printed', 'like', `%${this.filters.searchFilter.document_printed}%`]);
      }
      if (this.filters.searchFilter.invoice_number) {
        queryParams.filters.push(['invoice_number', 'like', `%${this.filters.searchFilter.invoice_number}%`]);
      }
      if (this.filters.searchFilter.document_type) {
        queryParams.filters.push(['document_type', 'like', `%${this.filters.searchFilter.document_type}%`]);
      }
      if (this.filters.searchFilter.creation) {
        const from = Moment(this.filters.searchFilter.creation).format('YYYY-MM-DD');
        const to = Moment(this.filters.searchFilter.creation).format('YYYY-MM-DD');
        queryParams.filters.push(['creation', 'Between', [from, to]])
      }
      queryParams.limit_start = this.filters.start
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.order_by = "`tabDocument Bin`.`creation` desc"
      queryParams.fields = JSON.stringify(["name", "invoice_file", "invoice_number", "document_printed", "print_by", "document_type", "error_log", "creation", "modified", "system_name"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentBin}`, {
        params: {
          fields: JSON.stringify(["count( `tabDocument Bin`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentBin}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.docBinList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.docBinList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.start !== 0) {
          this.docBinList = this.docBinList.concat(data.data)
        } else {
          this.docBinList = data.data;
        }
        this.reprocessButn = this.docBinList.find((each: any) => each.document_printed == 'No')
      }
    });

  }

  /** Re-upload  */
  reInitiateInvoice(item) {
    this.seletedITem = item;
    this.errorMessage = null;
    this.successMessage = ''
    this.filename = '';
    const modalRef = this.modal.open(this.uploadModal, {
      size: 'md',
      centered: true
    });
  }

  handleFileInput(files: File[]) {
    this.filename = files[0].name;
    this.fileToUpload = files[0];
    var reader = new FileReader();
    reader.readAsDataURL(this.fileToUpload);
    reader.onload = (_event) => {
      this.imgURL = reader.result;
    }
  }

  uploadService() {
    if (this.fileToUpload) {
      const params = this.activatedRoute.snapshot.params;
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      formData.append('doctype', Doctypes.invoices);
      formData.append('docname', params.id);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message?.file_url) {
          this.http.put(`${ApiUrls.resource}/${Doctypes.documentBin}/${this.seletedITem.name}`, { invoice_file: res.message?.file_url }).subscribe((res: any) => {
            this.reprocess(res.data)
          })
        } else {
          console.log(res)
        }
      })
    }
  }

  /**Copy File path */
  // copyInputMessage(item){
  //   const fileUrl = `${environment.apiDomain}${item.invoice_file}`
  //   console.log(item)
  //   let selecText = document.createRange()

  //   document.execCommand("copy")
  // }
  copy(text: string) {
    this._clipboardService.copy(text)
  }

  copyText(item, index) {
    this.copiedIndex = index;
  }

  copyInputMessage(inputElement) {
    inputElement.select();
    document.execCommand('copy');
    inputElement.setSelectionRange(0, 0);
  }



  openParserModal(parserModal) {
    this.http.post(`${ApiUrls.parserFile}`, { "company": this.companyDetails?.name }).subscribe((res: any) => {
      if (res?.message?.success) {
        this.parserFile = res.message.data;
        let modal = this.modal.open(parserModal, {
          size: 'lg', centered: true
        })
      }
    })

  }
  openParser(file, type) {
    // const domain = environment.apiDomain;
    const fileUrl = `${environment.apiDomain}${file}`
    const fileLocal = "/home/caratred/Downloads/invoice_parser.py"
    window.open(fileLocal, '_blank');
  }

  updateParsers() {


    if (this.companyDetails?.proxy == 1) {
      this.http.post(ApiUrls.checkProxy, { data: { company: this.companyDetails?.name, type: 'set' } }).subscribe((proxy: any) => {
        if (proxy.message.success) {
          this.http.get(ApiUrls.updateParsers).subscribe((res: any) => {
            if (res) {
              this.http.post(ApiUrls.checkProxy, { data: { company: this.companyDetails?.name, type: 'unset' } }).subscribe((unset: any) => {

              })
              this.toastr.success(res?.message?.message)
            }
          })
        }
      })
    } else {
      this.http.get(ApiUrls.updateParsers).subscribe((res: any) => {
        if (res) {
          this.toastr.success(res?.message?.message)
        }
      })
    }
  }

  checkPagination(): void {
    this.filters.currentPage = 1
    this.updateRouterParams()
  }
  /**diagnostic  */
  diagnostic() {
    this.http.post(ApiUrls.diagnostic, { data: { company_code: this.companyDetails?.company_code } }).subscribe((res: any) => {
      if (res?.message) {
        console.log(this.domain + res?.message)
        window.open(this.domain + res?.message, '_blank')
      }
    })
  }


  /************** */
  downloadExe() {
    let link = document.createElement('a');
    link.setAttribute('type', 'hidden');
    link.href = 'https://ezyinvoicing-disk.s3.ap-south-1.amazonaws.com/EzyUtility.exe';
    link.download = 'EzyUtility.exe';
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  reprocess_B2C_pending_invoices() {
    this.http.get(ApiUrls.reprocess_B2C_pending_invoices).subscribe((res: any) => {
      if (res?.message?.success) {
        this.getBinList()
      } else {
        this.toastr.error(res?.message?.message)
      }
    })
  }
  redo_error() {
    let date = moment(this.filters.searchFilter.creation).format('YYYY-MM-DD')
    this.http.post(ApiUrls.redo_error, { docdate: date }).subscribe((res: any) => {
      console.log(res)
    })
  }
}
