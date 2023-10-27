import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { NgForm, NgModel } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, switchMap } from 'rxjs/operators';
import { Location } from '@angular/common';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { LocationModalComponent } from '../location-modal/location-modal.component';
import { environment } from 'src/environments/environment';
import { SummaryDetailsComponent } from '../summary-details/summary-details.component';
import { SocketService } from 'src/app/shared/services/socket.service';

@Component({
  selector: 'app-create-contact',
  templateUrl: './create-contact.component.html',
  styleUrls: ['./create-contact.component.scss']
})
export class CreateContactComponent implements OnInit,OnDestroy {
  onConfirmationSearch: any = new EventEmitter()
  texpayerlist: any = [];
  enteredConfNumber: string;
  taxpayerLocationsList: any = [];
  pageType: any;
  name: any;
  contactDetails: any = {};
  newLocationform: any = {}
  taxpayertrade_name = ''
  selectedLocationDetails: any
  zip_code_valid: boolean;
  cities: any = [];
  invalidPincode: any;
  mobNumberPattern = "^((\\+91-?)|0)?[0-9]{13}$";
  landlineNumberPattern = "^((\\+91-?)|0)?[0-9]{13}$";
  company: any = {}
  domain = environment.apiDomain
  routingFromPage: any;
  paramsID: any;
  constructor(
    public location: Location,
    private router: Router,
    public http: HttpClient,
    public socketService : SocketService,
    public activatedRoute: ActivatedRoute,
    public modal: NgbModal,
    public toaster: ToastrService
  ) { }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
    this.activatedRoute.queryParams.subscribe((res: any) => {
      console.log(res)
      this.routingFromPage = res.prop
      if(res.paramsID){
        this.paramsID =res.paramsID
      }
      if(res.prop){
        if(res.prop == 'CreateWithGST'){
          this.pageType = 'Create'
        }else if(res.prop == 'Create'){
          this.pageType ='Create'
        }else if(res.prop == 'Edit'){
          this.pageType ='Edit'
        }else if(res.prop == 'summary_contact'){
          this.pageType ='Create'
        }
      }
      // this.pageType = res.prop
      this.name = res.name ? res?.name : ''
      if (res.taxpayer) {
        this.contactDetails.taxpayer = res.taxpayer
        if(res.location){
          this.contactDetails.location  = res.location
        }
        this.taxpayertrade_name = res.companyName
        this.gettaxPayerById(this.contactDetails.taxpayer)
      } else {
      }
      console.log
      if (this.name) {
        this.getcontactById()
      }
    })
    this.getTaxPayerList();
    this.onConfirmationSearch.pipe(debounceTime(500)).subscribe((res: any) => {
      console.log(res)
      this.getTaxPayerBySearch(this.contactDetails.taxpayer)

    })
  }
  getTaxPayerList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.taxPayers}`, {
      params: {
        fields: JSON.stringify(['*']),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res.data) {
        this.texpayerlist = res?.data;
      }

    })
  }
  getTaxPayerBySearch(res) {
    this.gettaxpayerTradeName(res)
    console.log(parseInt(res.slice(0, 2)))
    let filters
    if (parseInt(res.slice(0, 2))) {
      filters = [['gst_number', 'like', `%${res}%`]]
    } else {
      filters = [['legal_name', 'like', `%${res}%`]]
    }
    this.http.get(ApiUrls.taxPayerDefault, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify(filters)
      }
    }).subscribe((res: any) => {
      console.log(res)
      this.texpayerlist = res.data;
    })
  }
  gettaxpayerTradeName(res) {
    let filters
    if (parseInt(res.slice(0, 2))) {
      filters = [['gst_number', '=', res]]
    } else {
      filters = [['legal_name', '=', res]]
    }
    this.http.get(ApiUrls.taxPayerDefault, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify(filters)
      }
    }).subscribe((res: any) => {
      console.log(res)
      if (res.data) {
        this.taxpayertrade_name = res.data[0]?.trade_name;
      } else {
        this.taxpayertrade_name = ''
      }
    })
  }
  selectedLocation(value) {
    console.log(value)
  }
  itemSelection(item1) {
    this.contactDetails.taxpayer = item1.name;
    this.taxpayertrade_name = item1.trade_name;
    this.inputfocus();
    this.gettaxPayerById(item1.name);
    this.contactDetails.location = null
  }
  getcontactById() {
    this.http.get(ApiUrls.contacts + '/' + this.name).subscribe((res: any) => {
      console.log(res)
      this.contactDetails = res.data;
      if (this.contactDetails.taxpayer) {
        this.getTaxPayerBySearch(this.contactDetails.taxpayer)
        this.gettaxPayerById(this.contactDetails.taxpayer)
      }
    })
  }
  companySearch(taxpayer) {
    this.taxpayertrade_name = '';
    this.contactDetails.location = null
    this.onConfirmationSearch.emit(taxpayer.value);
    this.gettaxPayerById(this.contactDetails.taxpayer);

  }
  gettaxPayerById(name) {
    // form.location =''
    // this.contactDetails.location =null
    this.selectedLocationDetails = ''
    this.http.get(ApiUrls.taxpayerlocation, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify([['taxpayer_details', '=', name], ['company', '=', this.company.name]])
      }
    }).subscribe((res: any) => {
      console.log(res)
      if (res.data) {
        this.taxpayerLocationsList = res.data
        this.taxpayerLocationsList.forEach(element => {
          if (this.contactDetails.location == element.name) {
            this.selectedLocationDetails = element
            console.log(this.selectedLocationDetails)
          }
        });
      }
    })
  }
  search(term: string): void {
    this.newLocationform.state = ""
    this.newLocationform.city = ""
    this.cities = []
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
  openLocationModel() {
    let modal = this.modal.open(LocationModalComponent, { size: 'md', centered: true, backdrop: 'static' })
    //  modal.componentInstance.newLocationform = item;
    modal.componentInstance.gstNumber = this.contactDetails.taxpayer;
    modal.componentInstance.locationType = "create"
    modal.result.then((data) => {
      // on close
    }, (reason) => {
      console.log("dismissed", modal.componentInstance.location)
      this.contactDetails.location = modal.componentInstance.location
      this.newLocationform = {}
      this.gettaxPayerById(this.contactDetails.taxpayer)
      // on dismiss
    });
  }
  addLocation(addForm) {
    addForm.form.markAllAsTouched();
    console.log(addForm.form.invalid)
    if (addForm.form.invalid) {
      return
    }
    let data = {
      ...addForm.form.value, 'taxpayer_details': this.contactDetails.taxpayer ,'company': this.company.name 
    }
    console.log(data)
    this.http.post(ApiUrls.taxpayerlocation, data).subscribe((res: any) => {
      console.log(res)
      this.contactDetails.location = res.data.name
      this.newLocationform = {}
      console.log(this.contactDetails.location)
      this.gettaxPayerById(this.contactDetails.taxpayer)
      this.modal.dismissAll()
    })
  }
  goBack() {
    console.log(this.location)
    this.location.back()
    // this.router.navigate(['./clbs/contacts'])
  }
  saveContact(form: NgForm) {

    // console.log(" ==== ", this.selectedLocationDetails.name, "====== ",this.selectedLocationDetails.location)
    form.form.markAllAsTouched();
    if (form.form.invalid) {
      return
    }
    let company = {
      'company': this.company.name,
      'contact_status': 1
    }
    let payload = {
      ...company,
      ...form.form.value,
      location_name : this.selectedLocationDetails.location
    }
    console.log(payload)

    if (form.valid) {
      this.http.get(`${ApiUrls.contacts}`, {
        params: {
          fields: JSON.stringify(['*']),
          filters: JSON.stringify([['location', '=', payload?.location], ['contact_status', '=', 1], ['email_id', '=', payload?.email_id]]),
          limit_page_length: 'None'
        }
      }).subscribe((res: any) => {
        if (res?.data) {
          // console.log(res)
          if (res?.data?.length) {
            this.toaster.error("Duplicate Contact");
          } else {
            this.http.post(ApiUrls.contacts, payload).subscribe((res: any) => {
              console.log(res)

              this.toaster.success('Created')
              this.updateContactStatus(res.data.name)
              this.location.back();
              // this.router.navigate(['clbs/contacts'])
            })
          }

        }
      })



    }


  }
  updateContactStatus(name:any){
    this.http.get(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`).subscribe((res: any) => {
      if (res) {
        console.log(res.data)
        if(res.data){
          let contacts = JSON.parse(res.data.contacts)
          contacts.push(name)
          this.http.put(`${ApiUrls.resource}/${Doctypes.summaries}/${this.paramsID}`, { contacts: JSON.stringify(contacts) }).subscribe((res: any) => {
            console.log(res)
            this.socketService.isContactAdded.next('refresh')
          })
        }
      }
    })
  }

  updateContact(form) {
    form.form.markAllAsTouched();
    if (form.form.invalid) {
      return
    }
    
    let payload = {      
      ...form.form.value, 'company' : this.company.name
    }
    this.http.put(ApiUrls.contacts + '/' + this.name, payload).subscribe((res: any) => {
      console.log(res)

      this.toaster.success('Updated')
      this.location.back()
      // this.router.navigate(['clbs/contacts'])
    })
  }

  getTaxpayer() {
    let queryParams: any = { filters: [] }
    queryParams.limit_page_length = 'none'
    queryParams.fields = JSON.stringify(['*'])
    this.http.get(ApiUrls.taxpayerdetails, { params: queryParams }).subscribe((res: any) => {
      console.log(res)
      this.texpayerlist = res.data
    })
  }
  inputfocus() {
    this.enteredConfNumber = 'valid'
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    element2[0].style.display = "none";

  }
  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    const element2: any = document.getElementsByClassName('companyInputErrorMsg');
    setTimeout(() => {
      element[0].style.display = "none";
      element2[0].style.display = "block";
    }, 200);

  }
  ngOnDestroy(): void {
    this.modal.dismissAll();
  }
}
