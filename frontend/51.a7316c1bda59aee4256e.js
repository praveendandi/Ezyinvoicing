(window.webpackJsonp=window.webpackJsonp||[]).push([[51],{"6Fc4":function(c,t,e){"use strict";e.r(t),e.d(t,"GspMeteringModule",(function(){return p}));var n=e("ofXK"),g=e("tyNb"),l=e("t0ZU"),d=e("fXoL"),i=e("tk/3"),a=e("3Pt+");function h(c,t){if(1&c&&(d.hc(0,"tr"),d.hc(1,"td"),d.cd(2),d.xc(3,"date"),d.gc(),d.hc(4,"td"),d.cd(5),d.gc(),d.hc(6,"td"),d.cd(7),d.gc(),d.hc(8,"td"),d.cd(9),d.gc(),d.hc(10,"td"),d.cd(11),d.gc(),d.hc(12,"td"),d.cd(13),d.gc(),d.hc(14,"td"),d.cd(15),d.gc(),d.hc(16,"td"),d.cd(17),d.gc(),d.gc()),2&c){const c=t.$implicit;d.Nb(2),d.dd(d.yc(3,8,null==c?null:c.creation)),d.Nb(3),d.dd((null==c?null:c.login)||0),d.Nb(2),d.dd((null==c?null:c.generate_irn)||0),d.Nb(2),d.dd((null==c?null:c.cancel_irn)||0),d.Nb(2),d.dd((null==c?null:c.invoice_by_irn)||0),d.Nb(2),d.dd((null==c?null:c.tax_payer_details)||0),d.Nb(2),d.dd((null==c?null:c.sync_gst_details)||0),d.Nb(2),d.dd((null==c?null:c.get_irn_details_by_doc)||0)}}function s(c,t){1&c&&(d.hc(0,"div",24),d.hc(1,"h5"),d.hc(2,"b"),d.cd(3,"No Data Found"),d.gc(),d.gc(),d.gc())}const o=[{path:"",component:(()=>{class c{constructor(c){this.http=c,this.gspMeteringList=[],this.dateFilters="this week"}ngOnInit(){this.getGSPMeteringData()}getGSPMeteringData(){this.http.post(l.a.gspMetering,{data:{range:this.dateFilters}}).subscribe(c=>{var t,e,n,g;(null===(t=null==c?void 0:c.message)||void 0===t?void 0:t.success)&&(this.gspData=null===(e=null==c?void 0:c.message)||void 0===e?void 0:e.data,this.gspMeteringList=null===(g=null===(n=null==c?void 0:c.message)||void 0===n?void 0:n.data)||void 0===g?void 0:g.day_wise,this.gspMeteringList=this.gspMeteringList.filter(c=>0!==Object.keys(c).length))})}onDateFilterChange(){this.getGSPMeteringData()}}return c.\u0275fac=function(t){return new(t||c)(d.bc(i.b))},c.\u0275cmp=d.Vb({type:c,selectors:[["app-gsp-metering"]],decls:95,vars:10,consts:[[1,"row","mb-3"],[1,"col-md-12","col-lg-12","mb-3"],[1,"d-flex"],[1,"font-weight-bold","text-white","mr-3"],[1,"w-c-50"],[1,"form-group","mb-0"],["id","my-select",1,"custom-select",3,"ngModel","ngModelChange","change"],["value","last week"],["value","this week"],["value","this month"],["value","last month"],["value","this year"],[1,"col-12"],[1,""],[1,"d-grid","text-center","text-white"],[1,"text-left"],[1,"border-left"],[1,"border-left","text-right"],[1,"card"],[1,"table-responsive"],[1,"table"],[1,"thead"],[4,"ngFor","ngForOf"],["class","text-center py-3",4,"ngIf"],[1,"text-center","py-3"]],template:function(c,t){1&c&&(d.hc(0,"section"),d.hc(1,"div",0),d.hc(2,"div",1),d.hc(3,"div",2),d.hc(4,"h4",3),d.cd(5,"GSP Metering"),d.gc(),d.hc(6,"div",4),d.hc(7,"div",5),d.hc(8,"select",6),d.sc("ngModelChange",(function(c){return t.dateFilters=c}))("change",(function(){return t.onDateFilterChange()})),d.hc(9,"option",7),d.cd(10,"Last Week"),d.gc(),d.hc(11,"option",8),d.cd(12,"This Week"),d.gc(),d.hc(13,"option",9),d.cd(14,"This Month"),d.gc(),d.hc(15,"option",10),d.cd(16,"Last Month"),d.gc(),d.hc(17,"option",11),d.cd(18,"This Year"),d.gc(),d.gc(),d.gc(),d.gc(),d.gc(),d.gc(),d.hc(19,"div",12),d.hc(20,"div",13),d.hc(21,"div",14),d.hc(22,"div",15),d.hc(23,"h4"),d.hc(24,"b"),d.cd(25),d.gc(),d.gc(),d.hc(26,"small"),d.hc(27,"b"),d.cd(28,"Login"),d.gc(),d.gc(),d.gc(),d.hc(29,"div",16),d.hc(30,"h4"),d.hc(31,"b"),d.cd(32),d.gc(),d.gc(),d.hc(33,"small"),d.hc(34,"b"),d.cd(35,"Generate IRN"),d.gc(),d.gc(),d.gc(),d.hc(36,"div",16),d.hc(37,"h4"),d.hc(38,"b"),d.cd(39),d.gc(),d.gc(),d.hc(40,"small"),d.hc(41,"b"),d.cd(42,"Cancel IRN"),d.gc(),d.gc(),d.gc(),d.hc(43,"div",16),d.hc(44,"h4"),d.hc(45,"b"),d.cd(46),d.gc(),d.gc(),d.hc(47,"small"),d.hc(48,"b"),d.cd(49,"Invoice By IRN"),d.gc(),d.gc(),d.gc(),d.hc(50,"div",16),d.hc(51,"h4"),d.hc(52,"b"),d.cd(53),d.gc(),d.gc(),d.hc(54,"small"),d.hc(55,"b"),d.cd(56,"Get Taxpayer Details"),d.gc(),d.gc(),d.gc(),d.hc(57,"div",16),d.hc(58,"h4"),d.hc(59,"b"),d.cd(60),d.gc(),d.gc(),d.hc(61,"small"),d.hc(62,"b"),d.cd(63,"Sync GSTIN Details"),d.gc(),d.gc(),d.gc(),d.hc(64,"div",17),d.hc(65,"h4"),d.hc(66,"b"),d.cd(67),d.gc(),d.gc(),d.hc(68,"small"),d.hc(69,"b"),d.cd(70,"Get IRN Details By Doc."),d.gc(),d.gc(),d.gc(),d.gc(),d.gc(),d.gc(),d.gc(),d.hc(71,"div",18),d.hc(72,"div",19),d.hc(73,"table",20),d.hc(74,"thead",21),d.hc(75,"tr"),d.hc(76,"th"),d.cd(77,"Date"),d.gc(),d.hc(78,"th"),d.cd(79,"Login"),d.gc(),d.hc(80,"th"),d.cd(81,"Generate IRN"),d.gc(),d.hc(82,"th"),d.cd(83,"Cancel IRN"),d.gc(),d.hc(84,"th"),d.cd(85,"Invice By IRN"),d.gc(),d.hc(86,"th"),d.cd(87,"Get Taxpayer Details"),d.gc(),d.hc(88,"th"),d.cd(89,"Sync GSTIN Details"),d.gc(),d.hc(90,"th"),d.cd(91,"Get IRN Details by doc."),d.gc(),d.gc(),d.gc(),d.hc(92,"tbody"),d.ad(93,h,18,10,"tr",22),d.gc(),d.gc(),d.ad(94,s,4,0,"div",23),d.gc(),d.gc(),d.gc()),2&c&&(d.Nb(8),d.Dc("ngModel",t.dateFilters),d.Nb(17),d.dd((null==t.gspData?null:t.gspData.total_login)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_generate_irn)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_cancel_irn)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_invoice_by_irn)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_tax_payer_details)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_sync_gst_details)||0),d.Nb(7),d.dd((null==t.gspData?null:t.gspData.total_get_irn_details_by_doc)||0),d.Nb(26),d.Dc("ngForOf",t.gspMeteringList),d.Nb(1),d.Dc("ngIf",!t.gspMeteringList.length))},directives:[a.r,a.i,a.l,a.m,a.t,n.o,n.p],pipes:[n.f],styles:["table[_ngcontent-%COMP%]   thead[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{border-bottom:0;border-top:0;font-size:12px;padding:9px 10px}.table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], .table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{padding:9px 10px;font-size:14px;border:1px solid rgba(221,218,218,.3)}.w-c-50[_ngcontent-%COMP%]{min-width:100px;margin-left:10px}#my-select[_ngcontent-%COMP%]{height:32px}.d-grid[_ngcontent-%COMP%]{display:grid;grid-template-columns:repeat(7,1fr)}"]}),c})()}];let r=(()=>{class c{}return c.\u0275mod=d.Zb({type:c}),c.\u0275inj=d.Yb({factory:function(t){return new(t||c)},imports:[[g.i.forChild(o)],g.i]}),c})(),p=(()=>{class c{}return c.\u0275mod=d.Zb({type:c}),c.\u0275inj=d.Yb({factory:function(t){return new(t||c)},imports:[[n.c,r,a.d]]}),c})()}}]);