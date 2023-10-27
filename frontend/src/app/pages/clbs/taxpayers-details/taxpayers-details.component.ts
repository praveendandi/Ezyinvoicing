import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { Location } from '@angular/common';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';
import { LocationModalComponent } from '../location-modal/location-modal.component';

class ContactsFilter {
   /**
   * Limit start of company filter
   * i.e Items per page
   */
    itemsPerPage = 20;
    currentPage = 1;
    totalCount = 0;
    start= 0;
    /**
     * Limit page length of company filter
     * page length
     */
    search = '';
    name='';

}
class LocationsFilter{
    itemsPerPage = 20;
    currentPage = 1;
    totalCount = 0;
    start= 0;
    search = '';
    name='';

}
@Component({
  selector: 'app-taxpayers-details',
  templateUrl: './taxpayers-details.component.html',
  styleUrls: ['./taxpayers-details.component.scss']
})
export class TaxpayersDetailsComponent implements OnInit {
  filters = new ContactsFilter()
  filters2 = new LocationsFilter()
  conatctsOnSearch = new EventEmitter()
  locationsOnSearch = new EventEmitter()
  paramsData: any={};
  active = 1;
  taxPayerDetails:any ={}
  selectedOption ='companies'
  contactsList: any =[];
  locationsList: any =[];
  cities: any[];
  newLocationform: any={};
  invalidPincode: string;
  zip_code_valid: boolean;
  formDisable: string;
  locationType: any;
  constructor(public location : Location,public modal : NgbModal,public router : Router,public activatedRoute:ActivatedRoute,public http: HttpClient,public toaster : ToastrService) {
    this.paramsData = this.activatedRoute.snapshot.queryParams;
    this.formDisable = 'View'
    // console.log(this.paramsData)
    // console.log(this.paramsData)
    // this.header = this.paramsData.id ? `${this.paramsData.type}` : "Create"
  }

  ngOnInit(): void {
    // this.active = localStorage.getItem('taxpayerTab')
    // console.log(this.paramsData)
    this.getCompanyInfo()
    this.getLocationsBtn()
    // this.contactsFilter()
    // this.locationsFilter()
    // this.checkTheSelectedTab()
  }

  checkTheSelectedTab(){
    // this.active=='1'? this.selectedOption='companies':this.active=='2'?this.selectedOption='contacts':this.active=='3'?this.selectedOption='locations':'';

  }
  contactsFilter(){
    this.conatctsOnSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
   this.activatedRoute.queryParams.pipe(switchMap((params: ContactsFilter) => {
        this.filters.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters.itemsPerPage;
        this.filters.currentPage = parseInt(params.currentPage as any, 0) || this.filters.currentPage;
        this.filters.search = params.search || this.filters.search;
        const queryParams: any = { filters: [] };
        queryParams.limit_start = this.filters.itemsPerPage;
        queryParams.limit_page_length = this.filters.currentPage - 1;
        queryParams.filters.push(['taxpayer','=',this.paramsData.name])
        if (this.filters.search) {
          queryParams.filters.push(['contact_name', 'like', `%${this.filters.search}%`]);
        }
        queryParams.fields = JSON.stringify(['*']);
        queryParams.filters = JSON.stringify(queryParams.filters);
        return this.http.get(ApiUrls.contacts, { params: queryParams });

    })).subscribe((res: any) => {
      if (res.data) {
        this.contactsList = res.data;
        // console.log(this.contactsList)
      }
    });

  }
  locationsFilter(){
    this.locationsOnSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
      this.activatedRoute.queryParams.pipe(switchMap((params: LocationsFilter) => {
        this.filters2.itemsPerPage = parseInt(params.itemsPerPage as any, 0) || this.filters2.itemsPerPage;
        this.filters2.currentPage = parseInt(params.currentPage as any, 0) || this.filters2.currentPage;
        this.filters2.search = params.search || this.filters2.search;
        const queryParams: any = { filters: [] };
        queryParams.limit_start = this.filters2.itemsPerPage;
        queryParams.limit_page_length = this.filters2.currentPage - 1;
        queryParams.filters.push(['taxpayer_details','=',this.paramsData.name])
        if (this.filters2.search) {
          queryParams.filters.push(['location', 'like', `%${this.filters2.search}%`]);
        }
        queryParams.fields = JSON.stringify(['*']);
        queryParams.filters = JSON.stringify(queryParams.filters);
        return this.http.get(ApiUrls.taxpayerlocation, { params: queryParams });
    })).subscribe((res: any) => {
      if (res?.data) {
        this.locationsList = res.data;
        // console.log(this.locationsList)
      }
    });
  }
  checkPagination(): void {
      this.filters.currentPage = 1;
      this.updateRouterParams()
  }
  getCompanyInfo(){

    let filters = [['gst_number','=',this.paramsData.name]]

    this.http.get(ApiUrls.taxPayerDefault,{
      params:{
        fields: JSON.stringify(['*']),
        filters : JSON.stringify(filters)
      }
    }).subscribe((res:any)=>{
      // console.log(res)
      if(res){
        this.taxPayerDetails = res.data[0];
        // console.log(this.taxPayerDetails)
      }

      // this.reservationsfilters = res.data

    })
  }
  updateRouterParams(): void {
    let data ;
    if(this.selectedOption=='contacts'){
      data = this.filters
    }else{
      data = this.filters2
    }
    data.name =  this.paramsData.name
    console.log(data)

    this.router.navigate(['clbs/taxpayer-details'], {
      queryParams: data
    });
  }
  goBack(){
    this.location.back()
    this.router.navigate(['clbs/taxpayers'])
  }

  sidenavSelection(selectedNav){
    this.selectedOption = selectedNav
    if(this.selectedOption == 'contacts'){
      localStorage.setItem('taxpayerTab','2')
     this.contactsFilter()
    }else if(this.selectedOption == 'locations'){
      localStorage.setItem('taxpayerTab','3')
      this.locationsFilter()
    }else{
      localStorage.setItem('taxpayerTab','1')
    }
    this.filters = new ContactsFilter()
    this.filters2 =new LocationsFilter()
    this.updateRouterParams()
  }
  search(term: string): void {
    this.newLocationform.state = ""
    this.newLocationform.city=""
    this.cities=[]
    this.invalidPincode = "";
    if (term.length > 5) {
      let url = "https://api.postalpincode.in/pincode/"
      fetch(url + `${term}`)
        .then(response => response.json()) // or text() or blob() etc.
        .then(data => {
          if (data[0]?.Status == "Success") {
            this.zip_code_valid = false;
            this.newLocationform.state = data[0].PostOffice[0].State;
            this.cities = data[0]?.PostOffice;
            console.log(this.cities)
          } else {
            this.invalidPincode = data[0]?.Message
            this.newLocationform.guest_state = '';
            this.cities = []
            this.zip_code_valid = true;
          }
        })
    } else {
      this.invalidPincode = "Enter Valid Pincode";
    }
  }
  openLocationModel(item,locationType){
    this.locationType =locationType
    this.newLocationform =item
    console.log()
    let modal = this.modal.open(LocationModalComponent, { size: 'md', centered: true ,backdrop:'static'})
    modal.componentInstance.newLocationform = item;
    modal.componentInstance.gstNumber = this.paramsData.name;
    modal.componentInstance.locationType = locationType
    modal.result.then((data) => {
      // on close
    }, (reason) => {
      console.log("moda dismissed")
      this.locationsFilter()
      // on dismiss
    });

 }
 openNewLocationModel(){
  let modal = this.modal.open(LocationModalComponent, { size: 'md', centered: true ,backdrop:'static'})
  modal.componentInstance.gstNumber = this.paramsData.name;
  modal.componentInstance.locationType = 'create'
  modal.result.then((data) => {
    // on close
  }, (reason) => {
    console.log("moda dismissed")
    // this.locationsFilter()
    this.getLocationsBtn()
    // on dismiss
  });

}
 addLocation(addForm){
  addForm.form.markAllAsTouched();
  console.log(addForm.form.invalid)
  if(addForm.form.invalid){
    return
  }
  let data ={
    ...addForm.form.value,...{'taxpayer_details':this.paramsData.name},...{'company':JSON.parse(localStorage.getItem('company')).name}
  }
  if(this.locationType == 'edit'){
    this.http.put(ApiUrls.taxpayerlocation+'/'+this.newLocationform.name,data).subscribe((res:any)=>{
      console.log(res)
      // this.locationsFilter()
      this.modal.dismissAll()
   })
  }else{
    this.http.post(ApiUrls.taxpayerlocation,data).subscribe((res:any)=>{
      console.log(res)
      // this.locationsFilter()
      this.modal.dismissAll()
   })
  }

  console.log(data)

}
  // getcontactByGST(){
  //   this.http.get(ApiUrls.contacts,{
  //     params:{
  //       fields:JSON.stringify(['*']),
  //       filters:JSON.stringify([['taxpayer','=',this.taxPayerDetails.gst_number]])
  //     }
  //   }).subscribe((res:any)=>{
  //     console.log(res)
  //     this.contactsList = res.data;
  //     // if(this.contactDetails.taxpayer){
  //     //   this.gettaxPayerById(this.contactDetails.taxpayer)
  //     // }
  //   })
  // }
  onSubmit(form){
    console.log(form.form.value)

    let filters = [['gst_number','=',this.paramsData.name]]

    this.http.put(ApiUrls.taxPayerDefault+'/'+this.paramsData.name,form.form.value).subscribe((res:any)=>{
      console.log(res)
      this.taxPayerDetails = res.data;
      this.toaster.success('updated')
      // console.log(this.taxPayerDetails)
      // this.reservationsfilters = res.data

    })
  }

  getLocationsBtn(){
    const queryParams: any = { filters: [] };
    queryParams.filters.push(['taxpayer_details','=',this.paramsData.name])
    queryParams.fields = JSON.stringify(['*']);
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(ApiUrls.taxpayerlocation, { params: queryParams }).subscribe((res:any)=>{
      if (res?.data) {
        this.locationsList = res.data;
        // console.log(this.locationsList)
      }
    });
  }
  getContactsBtn(){
    const queryParams: any = { filters: [] };
    queryParams.filters.push(['taxpayer','=',this.paramsData.name])
    queryParams.fields = JSON.stringify(['*']);
    queryParams.filters = JSON.stringify(queryParams.filters);
    this.http.get(ApiUrls.contacts, { params: queryParams }).subscribe((res:any)=>{
      this.contactsList = res.data;
    })
  }
}
