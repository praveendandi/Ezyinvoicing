import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-gsp-apis',
  templateUrl: './gsp-apis.component.html',
  styleUrls: ['./gsp-apis.component.scss']
})
export class GspApisComponent implements OnInit {
  gspApiData;
  p = 1;
  constructor(private router: Router, private http : HttpClient) { }

  ngOnInit(): void {
    this.http.get(ApiUrls.resource + `/GSP APIS`).subscribe((res:any) => {
      if(res){
        console.log(res);
        this.gspApiData = res.data
      }
    })
  }

  /**
   * Navigates gsp apis component
   * @params data
   * @params type
   */
  navigate(data: any, type: string): void {
    console.log(data.name);
    this.router.navigate(['/home/gsp-apis-details'], { queryParams: { id: data.name } });
  }

}
