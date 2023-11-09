import { map, switchMap } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { ActivatedRoute } from '@angular/router';
import { forkJoin, pipe } from 'rxjs';

class BenchLogFilter {
  /**
   * Limit start of company filter
   * i.e Items per page
   */
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0
  /**
   * Limit page length of company filter
   * page length
   */
  // search = '';

  config: any;

}

@Component({
  selector: 'app-activitylog',
  templateUrl: './activitylog.component.html',
  styleUrls: ['./activitylog.component.scss']
})
export class ActivitylogComponent implements OnInit {
  activityLogs = [];
  activeLog;
  invoiceNumber;
  docInfo;
  docName = 'Invoices';
  filters = new BenchLogFilter();
  total_count: number;
  constructor(
    public activeModal: NgbActiveModal,
    private http: HttpClient,) { }

  ngOnInit(): void {
    this.getActivityLogs('0');

  }


  getActivityLogs(count) {
    this.http.get(ApiUrls.resource + `/DocType/` + this.docName).pipe(switchMap((res: any) => {
      const queryParams: any = { filters: [] };
      queryParams.limit_start = this.filters.start;
      queryParams.limit_page_length = this.total_count;
      let character1 = this.http.get(ApiUrls.resource + '/Version', {
        params: {
          filters: [JSON.stringify([['docname', '=', this.invoiceNumber]])],
          fields: JSON.stringify(['data', 'name', 'creation', 'modified_by']),
          order_by: `${'creation desc'}`,
          limit_start: count,
          limit_page_length: '7'
        }
      }).pipe(map((response: any) => {
        res.data.dataFields = res.data.fields.reduce((prev, nxt) => {
          prev[nxt.fieldname] = nxt.label;
          return prev;
        }, {});
        return (response.data as any[]).map((each) => {
          each.data = JSON.parse(each.data);
          each.data = Object.keys(each.data).reduce((prev, key) => {
            if (each.data[key] && Array.isArray(each.data[key]) && each.data[key].length) {
              prev[key] = each.data[key].map((cr: string[]) => {
                if (cr.length == 3) {
                  cr[0] = res.data.dataFields[cr[0]] || cr[0];
                }
                return cr;
              });
            } else {
              prev[key] = each.data[key];
            }
            return prev;
          }, {});
          return each;
        });
      }));
      let character2 = this.http.get(ApiUrls.resource + '/Version', {
        params: {
          filters: [JSON.stringify([['docname', '=', this.invoiceNumber]])],
          fields: JSON.stringify(["count( `tabVersion`.`name`) AS total_count"]),
        }
      })
      return forkJoin([character1, character2]);

    })).subscribe((res) => {
      const [data, count]: any = res;
      console.log(data)

      data.forEach((result: any) => {
        this.activityLogs.push(result)
      })
      this.total_count = count?.data[0].total_count
      console.log(this.activityLogs.length);
      console.log(this.total_count);
    });
  }


  onLogClick(item) {
    this.activeLog = item;
    (document.querySelector('.modal-dialog') as any).style.maxWidth = "100%";
    (document.querySelector('.modal-dialog') as any).style.width = "90%";
  }

  activityMore(incrementTotalCount) {
    this.getActivityLogs(incrementTotalCount);
    console.log(this.filters.totalCount)
  }




}
