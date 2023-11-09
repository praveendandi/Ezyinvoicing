import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from 'src/environments/environment';
import DataTable from "frappe-datatable";
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { debounceTime, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';
import * as Moment from 'moment';
class ReportsFilter {
  default_Date = 'This Year';
  from_date = '';
  to_date = '';
  custom = '';
  reportType = '';
  taxpayer = '';
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  /**
   * Limit page length of company filter
   * page length
   */
  search = '';
}

@Component({
  templateUrl: './clbs-reports.component.html',
  styleUrls: ['./clbs-reports.component.scss']
})
export class ClbsReportsComponent implements OnInit {
  filterDate = new ReportsFilter();
  onSearch = new EventEmitter()

  colList = [];
  valueList = [];
  apiDomain = environment.apiDomain;
  reportTypeList = [];
  company
  colListXL = [];
  taxpayerList: any = []
  taxpayertrade_name: string;
  unableExport = false;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router
  ) { }

  ngOnInit(): void {

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      if (res) {
        if (res?.taxpayer !== '') {
          this.getTaxPayerBySearch(res?.taxpayer);

          this.getActivatedParamsData()
        } else {
          this.getTaxPayerList();
          this.getActivatedParamsData()
        }

        this.filterDate.start = 0;
        this.filterDate.totalCount = 0;
      }
    });
    this.company = JSON.parse(localStorage.getItem("company"));
    this.getReportsTypes();
    this.getTaxPayerList();
  }
  updateRouterParams(): void {
    this.router.navigate(['clbs/clbs-reports'], {
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
    this.http.post(ApiUrls.deleteReportFile, dataObj).subscribe((res) => { })
  }



  getReportsTypes(): void {
    const params: any = { filters: JSON.stringify([["Report", "ref_doctype", "in", ["Summaries", "Invoices"]], ["Report", 'name', 'in', ['Invoices In Summary', 'Invoices Not In Summary', 'Summary Report']], ["Report", "disabled", "=", 0]]) };
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
      this.filterDate.default_Date = params.default_Date || this.filterDate.default_Date;
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
          filters: JSON.stringify({ from_date: filter[0], to_date: filter[1], tax_payer_details: this.filterDate.taxpayer }),
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
          if(item?.label=='Emails'){
            obj['width'] = 300
          }else{
            obj['width'] = 170
          }
          return obj;
        })
        if (this.colList.length || this.valueList) {
          this.unableExport = true;
        } else {
          this.unableExport = false;
        }
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
          // cellHeight: 20,
          inlineFilters: true,
          // treeView: false,
          // checkedRowStatus: true,
          // dynamicRowHeight: false,
          // pasteFromClipboard: false
        };
        console.log("Options ====", options)
        const datatable = new DataTable(tableId, options);
      } else {
        console.log("===============")
      }
    })
  }

  // getActivatedParamsData(): void {
  //   let tableId = document.querySelector('#datatable');
  //   this.activatedRoute.queryParams.pipe(switchMap((params: ReportsFilter) => {
  //     this.filterDate.default_Date = params.default_Date || this.filterDate.default_Date;
  //     this.filterDate.reportType = params.reportType || this.filterDate.reportType;
  //     this.filterDate.default_Date = params.default_Date || this.filterDate.default_Date;
  //     let date;
  //     let filter: string[];
  //     if (this.filterDate.default_Date === 'Custom' && params.custom && params.custom.length == 2) {
  //       this.filterDate.custom = [new Date(params.custom[0]), new Date(params.custom[1])] as any;
  //       filter = new DateToFilter('Reports', this.filterDate.default_Date, this.filterDate.custom as any).filter;
  //     } else if (this.filterDate.default_Date === 'Custom') {
  //       return of(null);
  //     } else {
  //       filter = new DateToFilter('Reports', this.filterDate.default_Date).filter;
  //     }
  //     let reportFilter =  {from_date: filter[0], to_date: filter[1]}
  //     if(this.filterDate.taxpayer){
  //       reportFilter['tax_payer_details']= this.filterDate.taxpayer
  //     }
  //     const resultApi = this.http.get(ApiUrls.reports, {
  //       params: {
  //         filters: JSON.stringify(reportFilter),
  //         report_name: this.filterDate.reportType,
  //       }
  //     });
  //     return resultApi;
  //   })).subscribe((res: any) => {
  //     if (res) {
  //       console.log(res)
  //       this.colListXL = res?.message?.columns.map(item => item.label)
  //       this.valueList = res?.message?.result.map(item => Object.values(item))
  //       console.log("========values list ======", this.valueList)
  //       this.colList = res?.message?.columns.map(item => {
  //         let obj = {};
  //         obj['name'] = item?.label
  //         obj['width'] = 170
  //         return obj;
  //       })
  //       if(this.colList.length || this.valueList ){
  //         this.unableExport = true;
  //       }else{
  //         this.unableExport = false;
  //       }
  //       let options = {
  //         columns: this.colList,
  //         data: this.valueList,
  //         dropdownButton: '▼',
  //         headerDropdown: [
  //           {
  //             label: 'Custom Action',
  //             action: function (column) {
  //             }
  //           }
  //         ],
  //         sortIndicator: {
  //           asc: '↑',
  //           desc: '↓',
  //           none: ''
  //         },
  //         serialNoColumn: true,
  //         noDataMessage: 'No Data',
  //         inlinefilterDate: true
  //       };
  //       const datatable = new DataTable(tableId, options);
  //     } else {
  //     }
  //   })
  // }


  inputfocus() {
    const element: any = document.getElementsByClassName('paragraphClass');
    element[0].style.display = "block";
  }
  inputblur() {
    const element: any = document.getElementsByClassName('paragraphClass');
    setTimeout(() => {
      element[0].style.display = "none";
    }, 200);
  }
  getTaxPayerList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.taxPayers}`, {
      params: {
        fields: JSON.stringify(['*']),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res.data) {
        this.taxpayerList = res?.data;
      }

    })
  }
  getTaxPayerBySearch(res) {
    let filterData
    if (parseInt(res.slice(0, 2))) {
      filterData = [['gst_number', 'like', `%${res}%`]]
    } else {
      filterData = [['legal_name', 'like', `%${res}%`]]
    }
    this.http.get(ApiUrls.taxPayerDefault, {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify(filterData)
      }
    }).subscribe((res: any) => {
      this.taxpayerList = res.data;
      // this.reservationsfilterDate = res.data

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
