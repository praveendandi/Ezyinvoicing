import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy, EventEmitter } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';

class UserFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 100;
  search = '';
  start = 0
}
@Component({
  selector: 'app-deleted-documents',
  templateUrl: './deleted-documents.component.html',
  styleUrls: ['./deleted-documents.component.scss']
})
export class DeletedDocumentsComponent implements OnInit {
  filters = new UserFilter();
  onSearch = new EventEmitter();

  deletedList: any = []
  apiDomain = environment.apiDomain
  companyDetails;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private modal: NgbModal,
    private toastr: ToastrService
  ) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      this.updateRouterParams();
      this.filters.start = 0;
      this.filters.totalCount = 0;
    });
    this.getTotalCount();
    // this.loginUser = JSON.parse(localStorage.getItem('login'))
    // this.loginUSerRole = this.loginUser.rolesFilter.some((each:any)=>each == 'ezy-IT')
    // console.log(this.loginUSerRole)
  }

  updateRouterParams(): void {
    this.router.navigate(['home/deleted-documents'], {
      queryParams: this.filters
    });
  }

  getTotalCount(): void {
    this.http.get(`${ApiUrls.resource}/${Doctypes.deleteDocument}`, {
      params: {
        fields: JSON.stringify(["count( `tabDeleted Document`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getDocumentList();
    })
  }

  getDocumentList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: UserFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      if (this.filters.search) {
        queryParams.filters.push(['deleted_name', 'like', `%${this.filters.search}%`]);
      }
      queryParams.filters.push(['deleted_doctype', 'like', Doctypes.invoices])
      queryParams.limit_page_length = this.filters.itemsPerPage;
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.order_by = "`tabDeleted Document`.`modified` desc"
      queryParams.fields = JSON.stringify(["name", "creation", "modified", "modified_by", "deleted_name", "deleted_doctype", "restored", "data"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.deleteDocument}`, {
        params: {
          fields: JSON.stringify(["count( `tabDeleted Document`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.deleteDocument}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.deletedList = [];
      }
      const [count, data] = res;
      data.data = data.data.map((each:any,index)=>{
        if(each){
        each.invoice_file = JSON.parse(each.data).invoice_file;
        each.index = this.deletedList.length + index+1;
        }
        return each;
      })
      this.filters.totalCount = count.data[0].total_count;
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.deletedList = this.deletedList.concat(data.data)
        } else {
          this.deletedList = data.data;
        }
        
      }
    });
  }

  ViewFile(item) {
    window.open(`${this.apiDomain}${item.invoice_file}`)
  }
  restoreFile(item) {
    const formData = new FormData();
    formData.append('name', item.name)
    this.http.post(ApiUrls.restoreFile, formData).subscribe((res: any) => {
      if (res) {
        let xyz = JSON.stringify(res._server_messages)
        let checkFile = xyz.includes("already exists")
        let successFile = xyz.includes("Document Restored")
        if (checkFile) {
          this.toastr.error("Already Exists")
        }
        if (successFile) {
          this.toastr.success("Restored Successfully")
          this.getDocumentList()
        }
      }
    })
  }

  checkPagination(): void {
    console.log(this.deletedList.length)
    // if (this.filters.itemsPerPage < this.deletedList.length) {
      this.filters.currentPage = 1;
      this.updateRouterParams()
    // } else {
    //   this.updateRouterParams()
    // }
  }
}
