import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';


class DocumentTypeFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  search = '';
 
}
@Component({
  selector: 'app-document-types',
  templateUrl: './document-types.component.html',
  styleUrls: ['./document-types.component.scss']
})
export class DocumentTypesComponent implements OnInit {

  filters = new DocumentTypeFilter()
  onSearch = new EventEmitter()
  documentTypeList = [];
  documentTypeInfo:any = {}
  constructor(
    private router: Router,
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private toastr: ToastrService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      if (res) {
        this.filters.start = 0;
        this.filters.totalCount = 0;
        this.updateRouterParams()
      }
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        this.filters.search = res.search;
      }
    })
    this.getDocumentList();
  }


  updateRouterParams(): void {
    this.router.navigate(['clbs/document-type'], {
      queryParams: this.filters
    });
  }

  getDocumentList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: DocumentTypeFilter) => {
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.itemsPerPage;
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters?.search}%`]);
      }
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      queryParams.order_by = "`tabDocument Types`.`creation` desc";
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, {
        params: {
          fields: JSON.stringify(["count( `tabDocument Types`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.documentTypeList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.documentTypeList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.documentTypeList = this.documentTypeList.concat(data.data)
        } else {
          this.documentTypeList = data.data;
        }

      }
    });
  }

  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  docTypeModalFunc(event, each){
    this.documentTypeInfo = {...each};
    let modal = this.modal.open(event,{size:'md',centered:true})
  }

  eventFormAdd(form:NgForm,modal){
    this.http.post(`${ApiUrls.resource}/${Doctypes.documentTypes}`,{data:form.value}).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getDocumentList()
      }
    })
  }

  eventFormEdit(form:NgForm,modal){
    this.http.put(`${ApiUrls.resource}/${Doctypes.documentTypes}/${this.documentTypeInfo.name}`,form.value).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getDocumentList()
      }
    })
  }
}
