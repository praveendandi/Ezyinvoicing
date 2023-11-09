import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { stateCode } from 'src/app/shared/state-codes'

@Component({
  selector: 'app-invoice-details',
  templateUrl: './invoice-details.component.html',
  styleUrls: ['./invoice-details.component.scss']
})
export class InvoiceDetailsComponent implements OnInit {

  invoicesData:any={}
  constructor(
    private http:HttpClient,
    private activatedRoute: ActivatedRoute
  ) { }

  ngOnInit(): void {
    this.activatedRoute.params.subscribe((res:any)=>{
      if(res.id){
        this.getInvoiceDetails(res.id)
      }
    })
  }


  getInvoiceDetails(id:any){
    this.http.get(`${ApiUrls.resource}/${Doctypes.invoices}/${id}`).subscribe((res:any)=>{
      if(res.data){
        this.invoicesData = res.data;
        this.invoicesData['pos'] = stateCode.find((each:any)=>{
          if(each.tin == res.data?.place_of_supply){return each;}
        }) 
      }
    })
  }
}
