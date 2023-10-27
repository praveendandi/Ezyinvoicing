import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgbActiveModal, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-location-modal',
  templateUrl: './location-modal.component.html',
  styleUrls: ['./location-modal.component.scss']
})
export class LocationModalComponent implements OnInit {
  newLocationform:any={}
  locationType:any
  gstNumber:any
  locationExist:boolean
  cities: any[];
  locations:any = [];
  invalidPincode: string;
  zip_code_valid: boolean;
  location: any;
  company: any
  constructor(public http :HttpClient,public modal : NgbModal,public toaster : ToastrService,public activeModal: NgbActiveModal) { }

  ngOnInit(): void {
    this.company = JSON.parse(localStorage.getItem('company'));
  }
  addLocation(addForm){
    addForm.form.markAllAsTouched();
    if(addForm.form.invalid || this.locationExist){
      return
    }
    let data ={
      ...addForm.form.value,...{'taxpayer_details':this.gstNumber},...{'company':this.company?.name}
    }
    if(this.locationType == 'edit'){
      this.http.put(ApiUrls.taxpayerlocation+'/'+this.newLocationform.name,data).subscribe((res:any)=>{
        this.toaster.success('Updated')
        // this.locationsFilter()
        // this.modal.dismissAll
        this.activeModal.dismiss(this.location)
     })
    }else{
      this.http.post(ApiUrls.taxpayerlocation,data).subscribe((res:any)=>{
        if(res?.data){
        this.location = res.data.name
        this.toaster.success('Success')
        this.activeModal.dismiss(this.location)
        // this.modal.dismissAll(this.location)
        }else{
          this.toaster.error("Error")
        }
     })
    }

    console.log(data)

  }
  search(term: string): void {
    this.newLocationform.state = ""
    this.newLocationform.city=""
    this.cities=[];this.locations=[];
    this.invalidPincode = "";
    if (term.length > 5) {
      let url = "https://api.postalpincode.in/pincode/"
      fetch(url + `${term}`)
        .then(response => response.json()) // or text() or blob() etc.
        .then(data => {
          if (data[0]?.Status == "Success") {
            this.zip_code_valid = false;
            this.newLocationform.state = data[0].PostOffice[0].State;
            this.newLocationform.location = data[0].PostOffice[0].Name;
            this.cities = data[0]?.PostOffice;
            this.locations = data[0]?.PostOffice;
            console.log(this.cities)
          } else {
            this.invalidPincode = data[0]?.Message
            this.newLocationform.guest_state = '';
            this.cities = [];
            this.locations = [];
            this.zip_code_valid = true;
          }
        })
    } else {
      this.invalidPincode = "Enter Valid Pincode";
    }
  }
  locationSearch(){
    console.log('location searcj')
    this.isLocationExist()
  }
  isLocationExist(){
    this.http.get(ApiUrls.taxpayerlocation,{
      params:{
        fields: JSON.stringify(['*']),
        filters : JSON.stringify([['location','=',this.newLocationform.location],['taxpayer_details','=',this.gstNumber],['company','=',this.company?.name]])
      }
    }).subscribe((res:any)=>{
      console.log(this.locationType)
      if(this.locationType == 'edit'){
        if(res.data.length >1){
          this.locationExist = true
        }else{
          this.locationExist =false
        }
      }else{
        if(res.data.length){
          this.locationExist = true
        }else{
          this.locationExist =false
        }
      }

       console.log(res)
    })
  }

  keyPressNumbers(event) {
    var charCode = (event.which) ? event.which : event.keyCode;
    // Only Numbers 0-9
    if ((charCode < 48 || charCode > 57)) {
      event.preventDefault();
      return false;
    } else {
      return true;
    }
  }
}
