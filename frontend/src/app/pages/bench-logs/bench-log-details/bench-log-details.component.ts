import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

@Component({
  selector: 'app-bench-log-details',
  templateUrl: './bench-log-details.component.html',
  styleUrls: ['./bench-log-details.component.scss']
})
export class BenchLogDetailsComponent implements OnInit {

  paramsData;
  updateInfo:any = {};
  constructor(
    private activatedRoute: ActivatedRoute,
    private http: HttpClient,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.paramsData = this.activatedRoute.snapshot.queryParams;

    if (this.paramsData.id) {
      this.getLogInfo();
    }
  }

  getLogInfo():void{
    this.http.get(`${ApiUrls.resource}/${Doctypes.benchMangerCmd}/${this.paramsData.id}`).subscribe((res:any)=>{
      if(res.data){
        res.data.console = res.data.console.replaceAll('↵','<br>');
        this.updateInfo = res.data;
      }
    })
  }
}
