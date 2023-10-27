import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import DataTable from "frappe-datatable";
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';
import * as Moment from 'moment';
import { ActivatedRoute, Router } from '@angular/router';
import { switchMap } from 'rxjs/operators';
import { forkJoin, of } from 'rxjs';
class ReportsFilter {
  default_Date = 'This Week';
  from_date = '';
  to_date = '';
  custom = '';
  reportType = ''
}

@Component({
  selector: 'app-reports',
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  filterDate = new ReportsFilter();

  colList = [];
  valueList = [];
  apiDomain = environment.apiDomain;
  reportTypeList = [];
  company
  colListXL = []

  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) { }

  ngOnInit(): void {
    // const datatable = new DataTable('#datatable', {
    //   columns: ['Name', 'Position', 'Salary'],
    //   data: [
    //     ['Faris', 'Software Developer', '$1200'],
    //     ['Manas', 'Software Engineer', '$1400'],
    //   ]
    // });

    this.activatedRoute.queryParams.subscribe((res:any)=>{
      if(res){
        this.filterDate.reportType = res?.reportType;
      }
    })

    
    this.company = JSON.parse(localStorage.getItem("company"));
    this.getTotalCountReports();
  }

  updateRouterParams(): void {
    this.router.navigate(['home/reports'], {
      queryParams: this.filterDate
    });
  }
  exportData(type): void {
    let dataObj = {
      data: {
        company: this.company?.name,
        columns: this.colListXL,
        values: this.valueList,
        report_name: this.filterDate.reportType,
        file_type: type
      }
    }
    this.http.post(ApiUrls.reportMethod, dataObj).subscribe((res: any) => {
      if (res?.message) {
        // this.remove(res.message);
        window.open(`${this.apiDomain}${res.message}`, "_blank");
      }
    })
  }
  remove(file): void {
    let dataObj = {
      data: {
        company: this.company?.name, filepath: file
      }
    }
    this.http.post(ApiUrls.deleteReportFile, dataObj).subscribe((res) => console.log("deleteeee", res))
  }

  getTotalCountReports(): void {
    this.http.get(ApiUrls.reportList, {
      params: {
        fields: JSON.stringify(["count( `tabReport`.`name`) AS total_count"]),
      }
    }).subscribe((res: any) => {
      this.getReportsTypes(res?.data[0].total_count)
    })
  }

  getReportsTypes(count): void {
    const params: any = { 
      filters: JSON.stringify([["Report", "ref_doctype", "in", [Doctypes.invoices,Doctypes.deleteDocument]],["Report", "disabled", "=", 0],["Report","name","!=","Amendment SAC HSN Summary"],["Report","name","!=","Amendment"]]) };
    params["page_length"] = count;
    params["order_by"] = "`tabReport`.`creation` asc";
    this.http.get(ApiUrls.reportList, { params: params }).subscribe((res: any) => {
      this.reportTypeList = res?.data
      this.filterDate.reportType = this.reportTypeList[0].name
      this.getActivatedParamsData()
    })
  }

  onreportTypeChange(e) {
    this.updateRouterParams()
  }

  onDateFilterChange() {
    this.filterDate.custom = '';
    this.filterDate.from_date = '';
    this.filterDate.to_date = "";
    if (this.filterDate.default_Date === 'Custom' && this.filterDate.custom) {
      this.updateRouterParams();
    } else {
      this.updateRouterParams();
    }
  }

  getActivatedParamsData(): void {
    let tableId = document.querySelector('#datatable');
    this.activatedRoute.queryParams.pipe(switchMap((params: ReportsFilter) => {
      this.filterDate.default_Date = params.default_Date || this.filterDate.default_Date;
      this.filterDate.reportType = params.reportType || this.filterDate.reportType;
      let date;
      let filter: string[];
      if (this.filterDate.default_Date === 'Custom' && params.custom && params.custom.length == 2) {
        this.filterDate.custom = [new Date(params.custom[0]), new Date(params.custom[1])] as any;
        filter = new DateToFilter('Reports', this.filterDate.default_Date, this.filterDate.custom as any).filter;
      } else if (this.filterDate.default_Date === 'Custom') {
        return of(null);
      } else {
        filter = new DateToFilter('Reports', this.filterDate.default_Date).filter;
      }
      console.log(filter)
      const resultApi = this.http.get(ApiUrls.reports, {
        params: {
          filters: JSON.stringify({ from_date: filter[0], to_date: filter[1] }),
          report_name: this.filterDate.reportType,
        }
      });
      return resultApi;
    })).subscribe((res: any) => {
      if (res) {
        this.colListXL = res?.message?.columns.map(item => item.label)
        this.valueList = res?.message?.result.map(item => Object.values(item))
        this.colList = res?.message?.columns.map(item => {
          let obj = {};
          obj['name'] = item?.label
          obj['width'] = 170
          return obj;
        })
        let options = {
          columns: this.colList,
          data: this.valueList,
          dropdownButton: '▼',
          headerDropdown: [
            {
              label: 'Custom Action',
              action: function (column) {
                // custom action
              }
            }
          ],
          // events: {
          //     onRemoveColumn(column) {},
          //     onSwitchColumn(column1, column2) {},
          //     onSortColumn(column) {},
          //     onCheckRow(row) {}
          // },
          sortIndicator: {
            asc: '↑',
            desc: '↓',
            none: ''
          },
          // freezeMessage: '',
          // getEditor: null,
          serialNoColumn: true,
          // checkboxColumn: false,
          // logs: false,
          // layout: 'fluid', // fixed, fluid, ratio
          noDataMessage: 'No Data',
          // cellHeight: null,
          inlineFilters: true,
          // treeView: false,
          // checkedRowStatus: true,
          // dynamicRowHeight: false,
          // pasteFromClipboard: false
        };
        console.log("Options ====",options)
        const datatable = new DataTable(tableId, options);
      }else{
        console.log("===============")
      }
    })
  }
}

class DateToFilter {
  filter: string[];
  constructor(docType: string, filterBy: string, filterDate?: Date[]) {
    switch (filterBy) {
      case 'Today':
        const todayDate = Moment(new Date()).format('YYYY-MM-DD');
        this.filter = [todayDate, todayDate];
        break;
      case 'Yesterday':
        const yesterdayDate = Moment(new Date()).subtract(1, 'day').format('YYYY-MM-DD');
        this.filter = [yesterdayDate, yesterdayDate];
        break;
      case 'This Week':
        const weekStart = Moment(new Date()).startOf('week').format('YYYY-MM-DD');
        const weekEnd = Moment(new Date()).endOf('week').format('YYYY-MM-DD');
        this.filter = [weekStart, weekEnd];
        break;
      case 'Last Week':
        const lastWeekStart = Moment(new Date()).subtract(1, 'week').startOf('week').format('YYYY-MM-DD');
        const lastWeekEnd = Moment(new Date()).subtract(1, 'week').endOf('week').format('YYYY-MM-DD');
        this.filter = [lastWeekStart, lastWeekEnd];
        break;
      case 'This Month':
        const monthStart = Moment(new Date()).startOf('month').format('YYYY-MM-DD');
        const monthEnd = Moment(new Date()).endOf('month').format('YYYY-MM-DD');
        this.filter = [monthStart, monthEnd];
        break;
      case 'Last Month':
        const lastMonthStart = Moment(new Date()).subtract(1, 'month').startOf('month').format('YYYY-MM-DD');
        const lastMonthEnd = Moment(new Date()).subtract(1, 'month').endOf('month').format('YYYY-MM-DD');
        this.filter = [lastMonthStart, lastMonthEnd];
        break;
      case 'This Year':
        const yearStart = Moment(new Date()).startOf('year').format('YYYY-MM-DD');
        const yearEnd = Moment(new Date()).endOf('year').format('YYYY-MM-DD');
        this.filter = [yearStart, yearEnd];
        break;
      case 'Custom':
        const [startDate, endDate] = filterDate;
        const from = Moment(startDate).format('YYYY-MM-DD');
        const to = Moment(endDate).format('YYYY-MM-DD');
        this.filter = [from, to];
        break;
    }
  }
}
