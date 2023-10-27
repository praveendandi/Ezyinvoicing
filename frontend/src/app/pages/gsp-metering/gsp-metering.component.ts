import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { ApiUrls } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-gsp-metering',
  templateUrl: './gsp-metering.component.html',
  styleUrls: ['./gsp-metering.component.scss']
})
export class GspMeteringComponent implements OnInit {

  gspMeteringList = [];
  gspData;
  dateFilters = 'this week';
  constructor(
    private http: HttpClient,
  ) { }

  ngOnInit(): void {
    this.getGSPMeteringData()
  }

  getGSPMeteringData() {
    let dataObj = { data: { range: this.dateFilters } }
    this.http.post(ApiUrls.gspMetering, dataObj).subscribe((res: any) => {
      // console.log("===============", res)
      if (res?.message?.success) {
        this.gspData = res?.message?.data;
        this.gspMeteringList = res?.message?.data?.day_wise
        this.gspMeteringList = this.gspMeteringList.filter(value => Object.keys(value).length !== 0)
        // console.log()
      }
    })
  }

  onDateFilterChange() {
    // console.log("=======",this.dateFilters)
    this.getGSPMeteringData();
  }

}
