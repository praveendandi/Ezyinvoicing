(window.webpackJsonp=window.webpackJsonp||[]).push([[24],{GE6W:function(t,e,n){"use strict";n.r(e),n.d(e,"UploadInvoicesModule",(function(){return R}));var c=n("ofXK"),i=n("tyNb"),o=n("fXoL"),a=n("cp0P"),r=n("eIep"),s=n("t0ZU"),l=n("d+JV"),d=n("AytR"),g=n("tk/3"),h=n("3Pt+"),f=n("z17N");function p(t,e){if(1&t){const t=o.ic();o.hc(0,"div",14),o.hc(1,"select",15),o.sc("ngModelChange",(function(e){return o.Qc(t),o.wc().filters.search.filterType=e}))("ngModelChange",(function(){return o.Qc(t),o.wc().onDateFilterType()})),o.hc(2,"option",16),o.cd(3,"Uploaded Date"),o.gc(),o.hc(4,"option",17),o.cd(5,"Created Date"),o.gc(),o.gc(),o.gc()}if(2&t){const t=o.wc();o.Nb(1),o.Ec("ngModel",t.filters.search.filterType)}}function u(t,e){if(1&t){const t=o.ic();o.hc(0,"div",14),o.hc(1,"select",18),o.sc("ngModelChange",(function(e){return o.Qc(t),o.wc().filters.search.filterBy=e}))("ngModelChange",(function(){return o.Qc(t),o.wc().onDateFilterChange()})),o.hc(2,"option",19),o.cd(3,"All"),o.gc(),o.hc(4,"option",20),o.cd(5,"Today"),o.gc(),o.hc(6,"option",21),o.cd(7,"Yesterday"),o.gc(),o.hc(8,"option",22),o.cd(9,"This Week"),o.gc(),o.hc(10,"option",23),o.cd(11,"Last Week"),o.gc(),o.hc(12,"option",24),o.cd(13,"This Month"),o.gc(),o.hc(14,"option",25),o.cd(15,"Last Month"),o.gc(),o.hc(16,"option",26),o.cd(17,"This Year"),o.gc(),o.hc(18,"option",27),o.cd(19,"Custom"),o.gc(),o.gc(),o.gc()}if(2&t){const t=o.wc();o.Nb(1),o.Ec("ngModel",t.filters.search.filterBy)}}function v(t,e){if(1&t){const t=o.ic();o.hc(0,"div",28),o.hc(1,"input",29),o.sc("ngModelChange",(function(e){return o.Qc(t),o.wc().filters.search.filterDate=e}))("dateTimeChange",(function(){return o.Qc(t),o.wc().updateRouterParams()})),o.gc(),o.hc(2,"span",30),o.cc(3,"i",31),o.gc(),o.cc(4,"owl-date-time",32,33),o.gc()}if(2&t){const t=o.Oc(5),e=o.wc();o.Nb(1),o.Ec("ngModel",e.filters.search.filterDate)("owlDateTime",t)("selectMode","range")("owlDateTimeTrigger",t),o.Nb(1),o.Ec("owlDateTimeTrigger",t),o.Nb(2),o.Ec("pickerType","calendar")}}function m(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",null==t?null:t.date,"")}}function b(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",null==t?null:t.invoice_number,"")}}function P(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",null==t?null:t.Pending,"")}}function C(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",null==t?null:t.Success,"")}}function _(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",null==t?null:t.Error,"")}}function M(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",t.B2B,"")}}function O(t,e){if(1&t&&(o.hc(0,"div"),o.hc(1,"span"),o.cd(2),o.gc(),o.gc()),2&t){const t=e.$implicit;o.Nb(2),o.ed(" ",t.B2C,"")}}function y(t,e){if(1&t&&(o.hc(0,"tr"),o.hc(1,"td"),o.cd(2),o.gc(),o.hc(3,"td",34),o.cd(4),o.xc(5,"date"),o.gc(),o.hc(6,"td",34),o.cd(7),o.gc(),o.hc(8,"td"),o.ad(9,m,3,1,"div",11),o.gc(),o.hc(10,"td"),o.ad(11,b,3,1,"div",11),o.gc(),o.hc(12,"td"),o.ad(13,P,3,1,"div",11),o.gc(),o.hc(14,"td"),o.ad(15,C,3,1,"div",11),o.gc(),o.hc(16,"td"),o.ad(17,_,3,1,"div",11),o.gc(),o.hc(18,"td"),o.ad(19,M,3,1,"div",11),o.gc(),o.hc(20,"td"),o.ad(21,O,3,1,"div",11),o.gc(),o.hc(22,"td"),o.hc(23,"a",35),o.cd(24,"Download GST File"),o.gc(),o.cc(25,"br"),o.hc(26,"a",35),o.cd(27,"Download Ref. File"),o.gc(),o.gc(),o.gc()),2&t){const t=e.$implicit,n=e.index,c=o.wc();o.Nb(2),o.dd(n+1),o.Nb(2),o.dd(o.zc(5,12,null==t?null:t.creation,"MMM d")),o.Nb(3),o.dd((null==t?null:t.uploaded_by)||"NA"),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("ngForOf",t.invoice_details),o.Nb(2),o.Ec("href",c.apiDomain+t.gst_file,o.Tc),o.Nb(3),o.Ec("href",c.apiDomain+t.referrence_file,o.Tc)}}function w(t,e){1&t&&(o.hc(0,"div",36),o.hc(1,"h4"),o.cd(2,"No Data Found"),o.gc(),o.gc())}function x(t,e){if(1&t){const t=o.ic();o.hc(0,"div"),o.hc(1,"p",42),o.sc("click",(function(){o.Qc(t);const e=o.wc(2);return e.filters.start=e.invoicesStats.length,e.filters.currentPage=e.filters.currentPage+1,e.updateRouterParams()})),o.cd(2," more "),o.gc(),o.gc()}}function N(t,e){if(1&t){const t=o.ic();o.hc(0,"div",37),o.hc(1,"div",38),o.hc(2,"select",39),o.sc("ngModelChange",(function(e){return o.Qc(t),o.wc().filters.itemsPerPage=e}))("change",(function(){return o.Qc(t),o.wc().checkPagination()})),o.hc(3,"option",40),o.cd(4,"20"),o.gc(),o.hc(5,"option",40),o.cd(6,"50"),o.gc(),o.hc(7,"option",40),o.cd(8,"100"),o.gc(),o.hc(9,"option",40),o.cd(10,"150"),o.gc(),o.hc(11,"option",40),o.cd(12,"500"),o.gc(),o.gc(),o.gc(),o.ad(13,x,3,0,"div",41),o.gc()}if(2&t){const t=o.wc();o.Nb(2),o.Ec("ngModel",t.filters.itemsPerPage),o.Nb(1),o.Ec("value",20),o.Nb(2),o.Ec("value",50),o.Nb(2),o.Ec("value",100),o.Nb(2),o.Ec("value",150),o.Nb(2),o.Ec("value",500),o.Nb(2),o.Ec("ngIf",t.invoicesStats.length<t.filters.totalCount)}}class T{constructor(){this.itemsPerPage=20,this.currentPage=1,this.totalCount=0,this.start=0,this.active=2,this.search={filterBy:"Today",filterDate:"",filterType:"creation"}}}const k=[{path:"",component:(()=>{class t{constructor(t,e,n){this.http=t,this.router=e,this.activatedRoute=n,this.filters=new T,this.onSearch=new o.q,this.invoicesStats=[],this.apiDomain=d.a.apiDomain,this.active=1}ngOnInit(){var t;this.getInvoiceList(),this.companyDetails=JSON.parse(localStorage.getItem("company")),this.filters.itemsPerPage=null===(t=this.companyDetails)||void 0===t?void 0:t.items_per_page}getInvoicesCount(){this.http.get(s.a.excelUploadInvoices,{params:{fields:JSON.stringify(["count( `tab"+s.b.excelUploadInvoices+"`.`name`) AS total_count"])}}).subscribe(t=>{this.filters.totalCount=t.data[0].total_count,this.getInvoiceList()})}getInvoiceList(){this.activatedRoute.queryParams.pipe(Object(r.a)(t=>{const e={filters:[]};if(this.filters.search.filterBy)if("Custom"===this.filters.search.filterBy){if(this.filters.search.filterDate){const t=new l.a(s.b.excelUploadInvoices,this.filters.search.filterBy,this.filters.search.filterDate,this.filters.search.filterType).filter;t&&e.filters.push(t)}}else if("All"!==this.filters.search.filterBy){const t=new l.a(s.b.excelUploadInvoices,this.filters.search.filterBy,null,this.filters.search.filterType).filter;t&&e.filters.push(t)}e.limit_page_length=this.filters.itemsPerPage,e.limit_start=(this.filters.currentPage-1)*this.filters.itemsPerPage,e.fields=JSON.stringify(["name","process_time","uploaded_by","creation","invoice_details","referrence_file","gst_file"]),e.filters=JSON.stringify(e.filters),e.order_by="`tabExcel upload Stats`.`creation` desc";const n=this.http.get(s.a.excelUploadInvoices,{params:{fields:JSON.stringify(["count( `tabExcel upload Stats`.`name`) AS total_count"]),filters:e.filters||[]}}),c=this.http.get(s.a.excelUploadInvoices,{params:e});return Object(a.a)([n,c])})).subscribe(t=>{const[e,n]=t;this.filters.totalCount=e.data[0].total_count,n.data&&(n.data=n.data.map(t=>(t.invoice_details=JSON.parse(t.invoice_details).invoice_details,t)),n.data.checked=!1,this.invoicesStats=1!==this.filters.currentPage?this.invoicesStats.concat(n.data):n.data,console.log(this.invoicesStats))})}navigateInvoices(t){this.router.navigate(["home","invoices"],{queryParams:{search:JSON.stringify({uploadType:"File",filterType:"invoice_date",filterBy:"Custom",filterDate:[new Date(null==t?void 0:t.date),new Date(null==t?void 0:t.date)]})},queryParamsHandling:"merge"})}updateRouterParams(){const t=JSON.parse(JSON.stringify(this.filters));t.search=JSON.stringify(t.search),this.router.navigate(["home/upload-invoice"],{queryParams:t})}print(t){this.selectedInvoice=t;const e=document.createElement("iframe");e.style.display="none",e.src=this.apiDomain+(null==t?void 0:t.invoice_file),document.body.appendChild(e),e.src&&setTimeout(()=>{e.contentWindow.print()})}checkPagination(){this.filters.itemsPerPage<this.invoicesStats.length?(this.filters.currentPage=1,this.updateRouterParams()):this.updateRouterParams()}onDateFilterType(){this.updateRouterParams()}onDateFilterChange(){this.filters.currentPage=1,"Custom"==this.filters.search.filterBy?this.filters.search.filterDate="":this.updateRouterParams()}}return t.\u0275fac=function(e){return new(e||t)(o.bc(g.b),o.bc(i.e),o.bc(i.a))},t.\u0275cmp=o.Vb({type:t,selectors:[["app-upload-invoices"]],decls:44,vars:7,consts:[[1,"invoice","position-relative"],[1,"d-flex"],[1,"col-md-11"],[1,"d-flex","mb-3"],[1,"text-white"],["class","form-group w-c-50",4,"ngIf"],["class","form-group calendar w-c-50 position-relative",4,"ngIf"],[1,"card","border-0","shadow"],[1,"card-body","p-0"],[1,"table-responsive"],[1,"table","table-bordered","mb-0"],[4,"ngFor","ngForOf"],["class","text-center py-3",4,"ngIf"],["class","d-flex justify-content-between",4,"ngIf"],[1,"form-group","w-c-50"],["id","my-select2","name","",1,"custom-select","bg-white",3,"ngModel","ngModelChange"],["value","creation"],["value","invoice_date"],["id","my-select","name","",1,"custom-select","bg-white",3,"ngModel","ngModelChange"],["value","All"],["value","Today"],["value","Yesterday"],["value","This Week"],["value","Last Week"],["value","This Month"],["value","Last Month"],["value","This Year"],["value","Custom"],[1,"form-group","calendar","w-c-50","position-relative"],["placeholder","Date Time",1,"form-control","h-auto",3,"ngModel","owlDateTime","selectMode","owlDateTimeTrigger","ngModelChange","dateTimeChange"],[1,"example-trigger",3,"owlDateTimeTrigger"],[1,"ri-calendar-2-line"],[3,"pickerType"],["dt1",""],[1,"v-align-center"],["target","_blank","download","",3,"href"],[1,"text-center","py-3"],[1,"d-flex","justify-content-between"],[1,"px-3"],["name","itemsPerPage","id","itemsPerPage",1,"custom-select",3,"ngModel","ngModelChange","change"],[3,"value"],[4,"ngIf"],[1,"text-right","pr-5","more","text-primary",3,"click"]],template:function(t,e){1&t&&(o.hc(0,"section",0),o.hc(1,"div",1),o.hc(2,"div",2),o.hc(3,"div",3),o.hc(4,"h4",4),o.hc(5,"b"),o.cd(6," Upload Invoices "),o.hc(7,"small"),o.cd(8),o.gc(),o.gc(),o.gc(),o.ad(9,p,6,1,"div",5),o.ad(10,u,20,1,"div",5),o.ad(11,v,6,6,"div",6),o.gc(),o.gc(),o.gc(),o.hc(12,"div",7),o.hc(13,"div",8),o.hc(14,"div",9),o.hc(15,"table",10),o.hc(16,"thead"),o.hc(17,"tr"),o.hc(18,"th"),o.cd(19,"#"),o.gc(),o.hc(20,"th"),o.cd(21,"Uploaded At"),o.gc(),o.hc(22,"th"),o.cd(23,"Uploaded By"),o.gc(),o.hc(24,"th"),o.cd(25,"Invoice Date"),o.gc(),o.hc(26,"th"),o.cd(27,"Invoices Count"),o.gc(),o.hc(28,"th"),o.cd(29,"Pending"),o.gc(),o.hc(30,"th"),o.cd(31,"Success"),o.gc(),o.hc(32,"th"),o.cd(33,"Error"),o.gc(),o.hc(34,"th"),o.cd(35,"B2C"),o.gc(),o.hc(36,"th"),o.cd(37,"B2B"),o.gc(),o.hc(38,"th"),o.cd(39,"Attachments"),o.gc(),o.gc(),o.gc(),o.hc(40,"tbody"),o.ad(41,y,28,15,"tr",11),o.gc(),o.gc(),o.ad(42,w,3,0,"div",12),o.gc(),o.ad(43,N,14,7,"div",13),o.gc(),o.gc(),o.gc()),2&t&&(o.Nb(8),o.ed("(",e.filters.totalCount,")"),o.Nb(1),o.Ec("ngIf",2==e.filters.active||3==e.filters.active||5==e.filters.active),o.Nb(1),o.Ec("ngIf",2==e.filters.active||3==e.filters.active||5==e.filters.active),o.Nb(1),o.Ec("ngIf","Custom"==e.filters.search.filterBy),o.Nb(30),o.Ec("ngForOf",e.invoicesStats),o.Nb(1),o.Ec("ngIf",!e.invoicesStats.length),o.Nb(1),o.Ec("ngIf",e.invoicesStats.length))},directives:[c.p,c.o,h.r,h.i,h.l,h.m,h.t,h.b,f.d,f.f,f.c],pipes:[c.f],styles:['.invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]   .view[_ngcontent-%COMP%]{cursor:pointer;text-decoration:underline;color:#2164e8;font-weight:600}.invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   tr[_ngcontent-%COMP%]:nth-of-type(2n), .invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   tr[_ngcontent-%COMP%]:nth-of-type(odd){background:#fff}.invoice[_ngcontent-%COMP%]   .table-bordered[_ngcontent-%COMP%]{border:0}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   thead[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{border-bottom:0;border-top:0;font-size:12px;padding:9px 10px}.invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], .invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{padding:9px 10px;font-size:14px;border:1px solid rgba(221,218,218,.3)}.invoice[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:first-child{padding-left:8px!important}.invoice[_ngcontent-%COMP%]   .calendar[_ngcontent-%COMP%]{max-width:200px}.invoice[_ngcontent-%COMP%]   .calendar[_ngcontent-%COMP%]   i[_ngcontent-%COMP%]{position:absolute;top:5px;right:10px;cursor:pointer}.invoice[_ngcontent-%COMP%]   .input-group[_ngcontent-%COMP%]{max-width:150px}.invoice[_ngcontent-%COMP%]   select.custom-select[_ngcontent-%COMP%]{height:auto}.invoice[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]{margin-bottom:0}.invoice[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]   select[_ngcontent-%COMP%]{font-size:13px}.invoice[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]   .form-control[_ngcontent-%COMP%]{padding:5px;border:0!important}.invoice[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:first-child{max-width:50px!important;text-align:center}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(2){max-width:100px!important}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(4)   div[_ngcontent-%COMP%]{max-width:140px!important}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(5)   div[_ngcontent-%COMP%]{max-width:180px!important}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(6)   div[_ngcontent-%COMP%]{max-width:120px!important;max-width:100px!important}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(7)   div[_ngcontent-%COMP%], .invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(8), .invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(9){max-width:100px!important}.invoice[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(3)   div[_ngcontent-%COMP%]{max-width:-webkit-fit-content!important;max-width:-moz-fit-content!important;max-width:fit-content!important}.w-c-50[_ngcontent-%COMP%]{min-width:100px;margin-left:10px}.colorBg[_ngcontent-%COMP%]{color:#2164e8}.ri-refresh-line[_ngcontent-%COMP%]{font-size:large}.nav-tabs[_ngcontent-%COMP%]{border:0}.nav-tabs[_ngcontent-%COMP%]   .nav-item.show[_ngcontent-%COMP%]   .nav-link[_ngcontent-%COMP%], .nav-tabs[_ngcontent-%COMP%]   .nav-link.active[_ngcontent-%COMP%]{background:#f06135;border:1px solid #f06135;color:#fff;border-radius:5px}.bg-transparent[_ngcontent-%COMP%], .nav-tabs[_ngcontent-%COMP%]   .nav-link[_ngcontent-%COMP%]{background:transparent}.nav-tabs[_ngcontent-%COMP%]   .nav-link[_ngcontent-%COMP%]{border:1px solid #eee;color:#fff;border-radius:5px;margin-right:5px}.tab-content[_ngcontent-%COMP%]{padding:0}.c-py-1[_ngcontent-%COMP%]{padding:5px 8px}.more[_ngcontent-%COMP%]{text-decoration:underline;cursor:pointer}table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{background:#f5f5f5}table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{white-space:nowrap;padding-left:1.5rem;padding-right:1.5rem}td[_ngcontent-%COMP%]:first-child, th[_ngcontent-%COMP%]:first-child{position:sticky;left:0}td[_ngcontent-%COMP%]:last-child, th[_ngcontent-%COMP%]:last-child{position:sticky;right:0}td[_ngcontent-%COMP%]:first-child{background:#fff}th[_ngcontent-%COMP%]:last-child{background:#f5f5f5}td[_ngcontent-%COMP%]:last-child{background:#fff}.input-group-text[_ngcontent-%COMP%], table[_ngcontent-%COMP%]   .custom-select[_ngcontent-%COMP%]{background:#f6f6f6}.input-group.input-group-sm[_ngcontent-%COMP%]   .form-control[_ngcontent-%COMP%]{background:#f6f6f6!important}.mode-test[_ngcontent-%COMP%]{background:#f06135}.mode-prod[_ngcontent-%COMP%], .mode-test[_ngcontent-%COMP%]{position:absolute;content:"";bottom:14px;width:3px;height:3px;border-radius:50%}.mode-prod[_ngcontent-%COMP%]{background:#33f033}.c-pad-l[_ngcontent-%COMP%]{margin:0 12px 0 10px;width:2px;height:31px;background:#fff;display:inline-block}.c-total-v[_ngcontent-%COMP%]{position:absolute;background:#4858d4;padding:9px 5px;border-radius:3px}.v-align-center[_ngcontent-%COMP%]{vertical-align:inherit}']}),t})()}];let E=(()=>{class t{}return t.\u0275mod=o.Zb({type:t}),t.\u0275inj=o.Yb({factory:function(e){return new(e||t)},imports:[[i.i.forChild(k)],i.i]}),t})();var D=n("ITC6"),S=n("1kSV"),I=n("MgRC"),B=n("HgEw");let R=(()=>{class t{}return t.\u0275mod=o.Zb({type:t}),t.\u0275inj=o.Yb({factory:function(e){return new(e||t)},imports:[[c.c,h.d,E,f.e,f.g,S.B,B.b,I.b,S.t,D.b]]}),t})()},ITC6:function(t,e,n){"use strict";n.d(e,"a",(function(){return o})),n.d(e,"b",(function(){return a}));var c=n("fXoL"),i=n("jhN1");let o=(()=>{class t{constructor(t){this.sanitizer=t}transform(t){return this.sanitizer.bypassSecurityTrustResourceUrl(t)}}return t.\u0275fac=function(e){return new(e||t)(c.bc(i.b))},t.\u0275pipe=c.ac({name:"safe",type:t,pure:!0}),t})(),a=(()=>{class t{}return t.\u0275mod=c.Zb({type:t}),t.\u0275inj=c.Yb({factory:function(e){return new(e||t)}}),t})()},MgRC:function(t,e,n){"use strict";n.d(e,"a",(function(){return o})),n.d(e,"b",(function(){return a}));var c=n("fXoL"),i=n("kmKP");let o=(()=>{class t{constructor(t,e){this.elementRef=t,this.userService=e,this.permissions={}}ngOnInit(){this.checkDocLevelAccess()}checkAccess(){this.userService.currentUser.subscribe(t=>{var e,n;if(null===(e=null==t?void 0:t.docinfo)||void 0===e?void 0:e.permissions){let e=null===(n=null==t?void 0:t.docinfo)||void 0===n?void 0:n.permissions;e.hasOwnProperty(this.accessType)&&(this.elementRef.nativeElement.disabled=!(e[this.accessType]>0))}})}checkDocLevelAccess(){var t;this.permissions=JSON.parse(localStorage.getItem("checkPermissions")),(null===(t=this.permissions)||void 0===t?void 0:t.hasOwnProperty(this.accessType))&&(this.elementRef.nativeElement.style["pointer-events"]=this.permissions[this.accessType]>0?"auto":"none",this.elementRef.nativeElement.style.cursor=this.permissions[this.accessType]>0?"pointer":"not-allowed",this.elementRef.nativeElement.disabled=!(this.permissions[this.accessType]>0))}}return t.\u0275fac=function(e){return new(e||t)(c.bc(c.o),c.bc(i.a))},t.\u0275dir=c.Wb({type:t,selectors:[["","appPermissionButton",""]],inputs:{moduleType:"moduleType",accessType:"accessType"}}),t})(),a=(()=>{class t{}return t.\u0275mod=c.Zb({type:t}),t.\u0275inj=c.Yb({factory:function(e){return new(e||t)}}),t})()}}]);