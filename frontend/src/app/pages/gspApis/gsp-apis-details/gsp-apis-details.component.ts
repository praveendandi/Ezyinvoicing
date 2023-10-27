import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-gsp-apis-details',
  templateUrl: './gsp-apis-details.component.html',
  styleUrls: ['./gsp-apis-details.component.scss']
})
export class GspApisDetailsComponent implements OnInit {

  gspApiDetails: any = {};;
  constructor(private http: HttpClient, private activatedRoute: ActivatedRoute) { }

  ngOnInit(): void {
    const params = this.activatedRoute.snapshot.queryParams.id;
    this.http.get(ApiUrls.resource + `/GSP APIS/${params}`).subscribe((res: any) => {
      if (res) {
        this.gspApiDetails = res.data
      }
    })
  }

  /**
   * Determines whether submit on
   * @params form
   */
  onSubmit(form: NgForm): void {
    console.log(form.value)
    const params = this.activatedRoute.snapshot.queryParams.id;
    form.form.markAllAsTouched();
    this.http.put(ApiUrls.resource + `/GSP APIS/${params}`, this.gspApiDetails).subscribe((res:any) => {
      if(res){
        this.ngOnInit()
      }
    })
  }

}
