import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';

class ContactsFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 25;
  start= 0;
  /**
   * Limit page length of company filter
   * page length
   */
  search = '';
  searchGST=''
}
@Component({
  selector: 'app-contacts',
  templateUrl: './contacts.component.html',
  styleUrls: ['./contacts.component.scss']
})
export class ContactsComponent implements OnInit {
  filters = new ContactsFilter()
  onSearch = new EventEmitter()
  hideShow = false;
  data = new Array(10)
  contactsList: any=[];
  displayPagination: boolean;
  companyDetails;

  constructor(private http : HttpClient,public activatedRoute : ActivatedRoute,public router :Router) { }

  ngOnInit(): void {
    this.companyDetails = JSON.parse(localStorage.getItem('company'))
    this.filters.itemsPerPage = this.companyDetails?.items_per_page
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
        this.updateRouterParams()
    });
    this.getContacts()

  }
  updateRouterParams(): void {
    this.router.navigate(['clbs/contacts'], {
      queryParams: this.filters
    });
  }

  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  toggle(type:any){
    if(type === 'list'){
     this.hideShow = true
    }
    if(type === 'grid'){
     this.hideShow = false
    }
   }

   getContacts(){
    this.activatedRoute.queryParams.pipe(switchMap((params: ContactsFilter) => {
      this.filters.search = params.search || this.filters.search;
      this.filters.searchGST = params.searchGST || this.filters.searchGST;
      // this.filters.taxpayer = params.taxpayer || this.filters.taxpayer;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.itemsPerPage;
      if (this.filters.search) {
        queryParams.filters.push(['contact_name', 'like', `%${this.filters.search}%`]);
      }
      if (this.filters.searchGST) {
        queryParams.filters.push(['taxpayer', 'like', `%${this.filters.searchGST}%`]);
      }

      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      queryParams.order_by = "`tabContacts`.`creation` desc";
      const countApi = this.http.get(`${ApiUrls.contacts}`, {
        params: {
          fields: JSON.stringify(["count( `tabContacts`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.contacts}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.contactsList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.contactsList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.contactsList = this.contactsList.concat(data.data)
        } else {
          this.contactsList = data.data;
        }

      }
    });
   }

   changeContactStatus(item,value){
    console.log(item,value)
    this.http.put(ApiUrls.contacts+'/'+item.name,{...item}).subscribe((res:any)=>{
      console.log(res)
      if(res.data){
        this.getContacts()
      }
      // this.contactDetails = res.data;
      // if(this.contactDetails.taxpayer){
      //   // this.getTaxPayerBySearch(this.contactDetails.taxpayer)
      //   // this.gettaxPayerById(this.contactDetails.taxpayer)
      // }
    })
  }

}
