(window.webpackJsonp=window.webpackJsonp||[]).push([[70],{hEQw:function(t,e,a){"use strict";a.r(e),a.d(e,"ReportsModule",(function(){return C}));var o=a("ofXK"),i=a("tyNb"),r=a("F2Ga"),s=a.n(r),n=a("t0ZU"),c=a("AytR"),l=a("wd/R"),d=a("eIep"),u=a("LRne"),p=a("fXoL"),h=a("tk/3"),m=a("3Pt+"),f=a("1kSV"),g=a("MgRC"),D=a("z17N");function b(t,e){if(1&t&&(p.hc(0,"option",18),p.cd(1),p.gc()),2&t){const t=e.$implicit;p.Ec("value",null==t?null:t.name),p.Nb(1),p.dd(null==t?null:t.name)}}function w(t,e){if(1&t){const t=p.ic();p.hc(0,"select",5),p.sc("ngModelChange",(function(e){return p.Qc(t),p.wc().filterDate.default_Date=e}))("ngModelChange",(function(){return p.Qc(t),p.wc().onDateFilterChange()})),p.hc(1,"option",19),p.cd(2,"Today"),p.gc(),p.hc(3,"option",20),p.cd(4,"Yesterday"),p.gc(),p.hc(5,"option",21),p.cd(6,"This Week"),p.gc(),p.hc(7,"option",22),p.cd(8,"Last Week"),p.gc(),p.hc(9,"option",23),p.cd(10,"This Month"),p.gc(),p.hc(11,"option",24),p.cd(12,"Last Month"),p.gc(),p.hc(13,"option",25),p.cd(14,"This Year"),p.gc(),p.hc(15,"option",26),p.cd(16,"Custom"),p.gc(),p.gc()}if(2&t){const t=p.wc();p.Ec("ngModel",t.filterDate.default_Date)}}function v(t,e){if(1&t){const t=p.ic();p.hc(0,"div",27),p.hc(1,"input",28),p.sc("ngModelChange",(function(e){return p.Qc(t),p.wc().filterDate.custom=e}))("dateTimeChange",(function(){return p.Qc(t),p.wc().updateRouterParams()})),p.gc(),p.hc(2,"span",29),p.cc(3,"i",30),p.gc(),p.cc(4,"owl-date-time",31,32),p.gc()}if(2&t){const t=p.Oc(5),e=p.wc();p.Nb(1),p.Ec("ngModel",e.filterDate.custom)("owlDateTime",t)("selectMode","range")("owlDateTimeTrigger",t),p.Nb(1),p.Ec("owlDateTimeTrigger",t),p.Nb(2),p.Ec("pickerType","calendar")}}class Y{constructor(){this.default_Date="This Week",this.from_date="",this.to_date="",this.custom="",this.reportType=""}}let y=(()=>{class t{constructor(t,e,a){this.http=t,this.activatedRoute=e,this.router=a,this.filterDate=new Y,this.colList=[],this.valueList=[],this.apiDomain=c.a.apiDomain,this.reportTypeList=[],this.colListXL=[]}ngOnInit(){this.activatedRoute.queryParams.subscribe(t=>{t&&(this.filterDate.reportType=null==t?void 0:t.reportType)}),this.company=JSON.parse(localStorage.getItem("company")),this.getTotalCountReports()}updateRouterParams(){this.router.navigate(["home/reports"],{queryParams:this.filterDate})}exportData(t){var e;let a={data:{company:null===(e=this.company)||void 0===e?void 0:e.name,columns:this.colListXL,values:this.valueList,report_name:this.filterDate.reportType,file_type:t}};this.http.post(n.a.reportMethod,a).subscribe(t=>{(null==t?void 0:t.message)&&window.open(`${this.apiDomain}${t.message}`,"_blank")})}remove(t){var e;let a={data:{company:null===(e=this.company)||void 0===e?void 0:e.name,filepath:t}};this.http.post(n.a.deleteReportFile,a).subscribe(t=>console.log("deleteeee",t))}getTotalCountReports(){this.http.get(n.a.reportList,{params:{fields:JSON.stringify(["count( `tabReport`.`name`) AS total_count"])}}).subscribe(t=>{this.getReportsTypes(null==t?void 0:t.data[0].total_count)})}getReportsTypes(t){const e={filters:JSON.stringify([["Report","ref_doctype","in",[n.b.invoices,n.b.deleteDocument]],["Report","disabled","=",0],["Report","name","!=","Amendment SAC HSN Summary"],["Report","name","!=","Amendment"]])};e.page_length=t,e.order_by="`tabReport`.`creation` asc",this.http.get(n.a.reportList,{params:e}).subscribe(t=>{this.reportTypeList=null==t?void 0:t.data,this.filterDate.reportType=this.reportTypeList[0].name,this.getActivatedParamsData()})}onreportTypeChange(t){this.updateRouterParams()}onDateFilterChange(){this.filterDate.custom="",this.filterDate.from_date="",this.filterDate.to_date="",this.updateRouterParams()}getActivatedParamsData(){let t=document.querySelector("#datatable");this.activatedRoute.queryParams.pipe(Object(d.a)(t=>{let e;if(this.filterDate.default_Date=t.default_Date||this.filterDate.default_Date,this.filterDate.reportType=t.reportType||this.filterDate.reportType,"Custom"===this.filterDate.default_Date&&t.custom&&2==t.custom.length)this.filterDate.custom=[new Date(t.custom[0]),new Date(t.custom[1])],e=new M("Reports",this.filterDate.default_Date,this.filterDate.custom).filter;else{if("Custom"===this.filterDate.default_Date)return Object(u.a)(null);e=new M("Reports",this.filterDate.default_Date).filter}return console.log(e),this.http.get(n.a.reports,{params:{filters:JSON.stringify({from_date:e[0],to_date:e[1]}),report_name:this.filterDate.reportType}})})).subscribe(e=>{var a,o,i;if(e){this.colListXL=null===(a=null==e?void 0:e.message)||void 0===a?void 0:a.columns.map(t=>t.label),this.valueList=null===(o=null==e?void 0:e.message)||void 0===o?void 0:o.result.map(t=>Object.values(t)),this.colList=null===(i=null==e?void 0:e.message)||void 0===i?void 0:i.columns.map(t=>{let e={};return e.name=null==t?void 0:t.label,e.width=170,e});let r={columns:this.colList,data:this.valueList,dropdownButton:"\u25bc",headerDropdown:[{label:"Custom Action",action:function(t){}}],sortIndicator:{asc:"\u2191",desc:"\u2193",none:""},serialNoColumn:!0,noDataMessage:"No Data",inlineFilters:!0};console.log("Options ====",r),new s.a(t,r)}else console.log("===============")})}}return t.\u0275fac=function(e){return new(e||t)(p.bc(h.b),p.bc(i.a),p.bc(i.e))},t.\u0275cmp=p.Vb({type:t,selectors:[["app-reports"]],decls:24,vars:4,consts:[[1,"row","mb-3"],[1,"col-md-9","col-lg-9"],[1,"d-flex"],[1,"text-white"],[1,"form-group","ml-3","w-c-50"],["id","my-select","name","",1,"custom-select",3,"ngModel","ngModelChange"],[3,"value",4,"ngFor","ngForOf"],[1,"form-group","w-c-50","ml-1"],["id","my-select","class","custom-select","name","",3,"ngModel","ngModelChange",4,"ngIf"],["class","form-group calendar w-c-50 position-relative ml-1",4,"ngIf"],[1,"col-md-3","col-lg-3","text-right"],["ngbDropdown","",1,"d-inline-block"],["id","dropdownBasic1","appPermissionButton","","accessType","export","ngbDropdownToggle","",1,"btn","btn-primary"],["ngbDropdownMenu","","aria-labelledby","dropdownBasic1"],["ngbDropdownItem","",3,"click"],[1,"btn","btn-primary","mb-0","text-case","ml-3",3,"click"],[1,"card"],["id","datatable"],[3,"value"],["value","Today"],["value","Yesterday"],["value","This Week"],["value","Last Week"],["value","This Month"],["value","Last Month"],["value","This Year"],["value","Custom"],[1,"form-group","calendar","w-c-50","position-relative","ml-1"],["placeholder","Date Time",1,"form-control","h-auto",3,"ngModel","owlDateTime","selectMode","owlDateTimeTrigger","ngModelChange","dateTimeChange"],[1,"example-trigger",3,"owlDateTimeTrigger"],[1,"ri-calendar-2-line"],[3,"pickerType"],["dt1",""]],template:function(t,e){1&t&&(p.hc(0,"section"),p.hc(1,"div",0),p.hc(2,"div",1),p.hc(3,"div",2),p.hc(4,"h4",3),p.hc(5,"b"),p.cd(6,"Reports"),p.gc(),p.gc(),p.hc(7,"div",4),p.hc(8,"select",5),p.sc("ngModelChange",(function(t){return e.filterDate.reportType=t}))("ngModelChange",(function(t){return e.onreportTypeChange(t)})),p.ad(9,b,2,2,"option",6),p.gc(),p.gc(),p.hc(10,"div",7),p.ad(11,w,17,1,"select",8),p.gc(),p.ad(12,v,6,6,"div",9),p.gc(),p.gc(),p.hc(13,"div",10),p.hc(14,"div",11),p.hc(15,"button",12),p.cd(16,"Export"),p.gc(),p.hc(17,"div",13),p.hc(18,"button",14),p.sc("click",(function(){return e.exportData("Excel")})),p.cd(19,"Excel"),p.gc(),p.gc(),p.gc(),p.hc(20,"button",15),p.sc("click",(function(){return e.getActivatedParamsData()})),p.cd(21,"Refresh"),p.gc(),p.gc(),p.gc(),p.hc(22,"div",16),p.cc(23,"div",17),p.gc(),p.gc()),2&t&&(p.Nb(8),p.Ec("ngModel",e.filterDate.reportType),p.Nb(1),p.Ec("ngForOf",e.reportTypeList),p.Nb(2),p.Ec("ngIf","E-invoice missing report"!=e.filterDate.reportType),p.Nb(1),p.Ec("ngIf","Custom"==(null==e.filterDate?null:e.filterDate.default_Date)))},directives:[m.r,m.i,m.l,o.o,o.p,f.e,g.a,f.j,f.h,f.g,m.m,m.t,m.b,D.d,D.f,D.c],styles:[""]}),t})();class M{constructor(t,e,a){switch(e){case"Today":const t=l(new Date).format("YYYY-MM-DD");this.filter=[t,t];break;case"Yesterday":const e=l(new Date).subtract(1,"day").format("YYYY-MM-DD");this.filter=[e,e];break;case"This Week":const o=l(new Date).startOf("week").format("YYYY-MM-DD"),i=l(new Date).endOf("week").format("YYYY-MM-DD");this.filter=[o,i];break;case"Last Week":const r=l(new Date).subtract(1,"week").startOf("week").format("YYYY-MM-DD"),s=l(new Date).subtract(1,"week").endOf("week").format("YYYY-MM-DD");this.filter=[r,s];break;case"This Month":const n=l(new Date).startOf("month").format("YYYY-MM-DD"),c=l(new Date).endOf("month").format("YYYY-MM-DD");this.filter=[n,c];break;case"Last Month":const d=l(new Date).subtract(1,"month").startOf("month").format("YYYY-MM-DD"),u=l(new Date).subtract(1,"month").endOf("month").format("YYYY-MM-DD");this.filter=[d,u];break;case"This Year":const p=l(new Date).startOf("year").format("YYYY-MM-DD"),h=l(new Date).endOf("year").format("YYYY-MM-DD");this.filter=[p,h];break;case"Custom":const[m,f]=a,g=l(m).format("YYYY-MM-DD"),D=l(f).format("YYYY-MM-DD");this.filter=[g,D]}}}const T=[{path:"",component:y}];let k=(()=>{class t{}return t.\u0275mod=p.Zb({type:t}),t.\u0275inj=p.Yb({factory:function(e){return new(e||t)},imports:[[i.i.forChild(T)],i.i]}),t})(),C=(()=>{class t{}return t.\u0275mod=p.Zb({type:t}),t.\u0275inj=p.Yb({factory:function(e){return new(e||t)},imports:[[o.c,k,f.i,m.d,D.e,D.g,g.b]]}),t})()}}]);