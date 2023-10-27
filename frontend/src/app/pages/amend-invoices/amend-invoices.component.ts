
import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls } from 'src/app/shared/api-urls';

class AmendFilter{
  month = ''; year='';active=1;filling_period:any='';filling_date;get_before_month:any='';return_period=''
}
@Component({
  selector: 'app-amend-invoices',
  templateUrl: './amend-invoices.component.html',
  styleUrls: ['./amend-invoices.component.scss']
})
export class AmendInvoicesComponent implements OnInit {
  filters = new AmendFilter();
  onSearch = new EventEmitter();
  amendList:any = []
  years:any= []
  seletedMonth;
  selectedyear;
  active = 1
  totals = {
    itemValue : 0,igst: 0, cgst:0, sgst:0, cess : 0, totalValue:0
  }
  selectAll = false;
  dupamendList = []
  min_date; max_date;
  chooseFillingPeriod = false;
  searchText;
  // get_before_month = '';
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private toastr: ToastrService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());
    // this.generateArrayOfYears()

    this.activatedRoute.queryParams.subscribe((res: any) => {
      console.log(res)
      if(res){
        this.filters.active = res?.active;
        this.filters.month = res?.month;
        this.filters.year = res?.year;
        this.filters.filling_date = res?.filling_date
        this.filters.filling_period = res?.filling_period
        this.filters.get_before_month = res?.get_before_month;
        this.filters.return_period = res?.return_period;
        this.chooseFillingPeriod = res?.get_before_month ? true: false;
        if(res.get_before_month){
          this.generateArrayOfYears()
          this.getAmendInvoicesList()
        }
        console.log(this.filters.filling_period)
      }
    })
  }

  generateArrayOfYears() {
    var max = new Date().getFullYear()
    var min = max - 3
    this.filters.month = new Date().toLocaleString('default', { month: 'short' })
    this.seletedMonth = new Date().toLocaleString('default', { month: 'short' })
    let currMonth = new Date().toLocaleString('default', { month: 'short', day:'2-digit',year:'numeric' })


    for (var i = max; i >= min; i--) {
      this.years.push(i)
    }
    if (this.years.length) this.filters.year = this.years[0]; this.selectedyear = this.years[0]

    if(this.filters.filling_period){
      // let today = new Date(this.filters.filling_period);
      let getDate = moment(this.filters.filling_period).format('DD');
      this.filters.return_period = moment(this.filters.filling_period).format('MMM');
      this.filters.month = moment(this.filters.filling_period).format('MMM');
      this.filters.year = moment(this.filters.filling_period).format("YYYY");
      this.filters.filling_period = new Date(`${this.filters.month} ${getDate},${this.filters.year} `)
      this.min_date = moment(this.filters.filling_period).startOf('month').utc().format();
      this.max_date  = moment(this.filters.filling_period).endOf('month').utc().format();
      this.filters.filling_date  = moment(this.filters.filling_period).format('YYYY/MM/DD');
      this.filters.get_before_month = moment(this.filters.filling_period).subtract(1, "month").format('MMMM YYYY');

    }else{
      let today = new Date();
      this.min_date = new Date(today.getFullYear(), today.getMonth(), 1);
      this.max_date = new Date(today.getFullYear(), today.getMonth()+1, 0);
      this.filters.filling_period = new Date(`${this.filters.month} 11,${this.filters.year} `)
      this.filters.filling_date  = moment(this.filters.filling_period).format('YYYY/MM/DD')
      this.filters.get_before_month = moment(this.filters.filling_period).subtract(1, "month").format('MMMM YYYY');
    }


    return this.years
  }

  getAmendInvoicesList(){
    this.dupamendList = [];
    this.amendList = []
    this.activatedRoute.queryParams.pipe(switchMap((params: AmendFilter) => {
      // this.filters.month = params.month || this.seletedMonth
      // this.filters.year = params.year || this.selectedyear
      // this.filters.filling_date = params.filling_date || this.filters.filling_date
      this.filters.active = parseInt(params.active as any) || 1
      let apiUrl = (this.filters.active == 1) ? ApiUrls.get_amendments : ApiUrls?.get_data_amendment_sac_hsn_summary
      const resultApi = this.http.post(apiUrl, { filters: {month:this.filters.month,year:this.filters.year,"report":false,filing_date:this.filters.filling_date}});
      return  resultApi;
    })).subscribe((res:any)=>{
      if(res?.message?.success){
        this.amendList = res?.message?.data;

        if(this.filters.active == 2){
         this.totals.itemValue = this.amendList.reduce((sum, current)=> sum + current.item_value, 0);
         this.totals.igst = this.amendList.reduce((sum, current)=> sum + current.igst_amount, 0);
         this.totals.cgst = this.amendList.reduce((sum, current)=> sum + current.cgst_amount, 0);
         this.totals.sgst = this.amendList.reduce((sum, current)=> sum + current.sgst_amount, 0);
         this.totals.cess = this.amendList.reduce((sum, current)=> sum + current.cess, 0);
         this.totals.totalValue = this.amendList.reduce((sum, current)=> sum + current.total_value, 0);
        //  console.log(this.totals)
        }
      }else{
        this.toastr.error("Error")
      }
    })
  }

  updateRouterParams(): void {

      // let today = new Date(this.filters.filling_period);
      // let getDate =today.toLocaleDateString('en-US', {day:'2-digit'})
      // this.filters.filling_period = new Date(`${this.filters.month} ${getDate},${this.filters.year} `)
      // this.min_date = moment(this.filters.filling_period).startOf('month').format('YYYY-MM-DD hh:mm');
      // this.max_date  = moment(this.filters.filling_period).endOf('month').format('YYYY-MM-DD hh:mm');
      // this.filters.filling_date  = moment(this.filters.filling_period).format('YYYY/MM/DD')

    const temp = JSON.parse(JSON.stringify(this.filters));
    this.router.navigate(['home/amend-invoices'], {
      queryParams: temp
    });

  }
  onTabChange(e) {
    this.active = e.nextId;
    this.filters.active = e.nextId;
    this.amendList = [];
    this.dupamendList = [];
    this.selectAll = false;
    this.updateRouterParams();
  }
  refreshData(){
    this.filters.active = 1;
    this.filters.filling_date = '';
    this.filters.filling_period = '';
    this.filters.get_before_month = '';
    this.filters.month = '';
    this.filters.year = '';
    this.amendList = [];
    this.dupamendList = [];
    this.selectAll = false;
    this.generateArrayOfYears();
    this.chooseFillingPeriod = false;
  }

  checkedItems(event, item) {
    const temp = this.amendList.filter((each: any) => each?.checked);
    this.selectAll = temp.length == this.amendList.length;
    this.dupamendList = temp;
    console.log(this.dupamendList)
  }

  checkedItemsAll(event) {
    if (this.selectAll) {
      this.dupamendList = this.amendList.filter((each: any) => {
        if (each.is_amendment == "No") {
          each.checked = true
        }
        return each;
      })
    } else {
      this.dupamendList = this.amendList.filter((each: any) => {
        if (each.is_amendment == "No") {
          each.checked = false
        }
        return each;
      })
    }
    this.dupamendList = this.amendList.filter((each: any) => each?.checked)

    console.log(this.dupamendList)
  }

  accept_amendments(){
    if(this.dupamendList.length){
    let list = this.dupamendList.map((each:any)=>each.invoice_number)
    this.http.post(ApiUrls.accept_amendments,{data:{invoices:list,month:this.filters.month,year:this.filters.year}}).subscribe((res:any)=>{
      if(res?.message?.success){
        this.getAmendInvoicesList();
      }
    })
  }
  }
  openFilingModal(modal:NgbModal){
    this.generateArrayOfYears();
    let modalPop = this.modal.open(modal,{size:'md',backdrop:'static',centered: true,})
  }
  changeModalSelect(type){
    let today = new Date(this.filters.filling_period);
    let getDate =today.toLocaleDateString('en-US', {day:'2-digit'})
    this.filters.filling_period = new Date(`${this.filters.month} ${getDate},${this.filters.year} `)
    this.min_date = moment(this.filters.filling_period).startOf('month').utc().format();
    this.max_date  = moment(this.filters.filling_period).endOf('month').utc().format();
    this.filters.filling_date  = moment(this.filters.filling_period).format('YYYY/MM/DD')
    this.filters.get_before_month = moment(this.filters.filling_period).subtract(1, "month").format('MMMM YYYY');
    console.log(today, this.filters.get_before_month)
  }

  updateFilingPeriod(form:NgForm,modal){
    if(form.valid){
      this.filters.month = form.value.month;
      this.filters.year = form.value.year;
      this.filters.filling_date = this.filters.filling_date;
      this.filters.return_period = moment(this.filters.filling_period).format('MMM');
      modal.close();
      this.chooseFillingPeriod = true;
      this.updateRouterParams()
      this.getAmendInvoicesList()
    }
  }
}
