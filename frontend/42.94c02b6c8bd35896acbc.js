(window.webpackJsonp=window.webpackJsonp||[]).push([[42],{MgRC:function(t,e,n){"use strict";n.d(e,"a",(function(){return r})),n.d(e,"b",(function(){return i}));var c=n("fXoL"),s=n("kmKP");let r=(()=>{class t{constructor(t,e){this.elementRef=t,this.userService=e,this.permissions={}}ngOnInit(){this.checkDocLevelAccess()}checkAccess(){this.userService.currentUser.subscribe(t=>{var e,n;if(null===(e=null==t?void 0:t.docinfo)||void 0===e?void 0:e.permissions){let e=null===(n=null==t?void 0:t.docinfo)||void 0===n?void 0:n.permissions;e.hasOwnProperty(this.accessType)&&(this.elementRef.nativeElement.disabled=!(e[this.accessType]>0))}})}checkDocLevelAccess(){var t;this.permissions=JSON.parse(localStorage.getItem("checkPermissions")),(null===(t=this.permissions)||void 0===t?void 0:t.hasOwnProperty(this.accessType))&&(this.elementRef.nativeElement.style["pointer-events"]=this.permissions[this.accessType]>0?"auto":"none",this.elementRef.nativeElement.style.cursor=this.permissions[this.accessType]>0?"pointer":"not-allowed",this.elementRef.nativeElement.disabled=!(this.permissions[this.accessType]>0))}}return t.\u0275fac=function(e){return new(e||t)(c.bc(c.o),c.bc(s.a))},t.\u0275dir=c.Wb({type:t,selectors:[["","appPermissionButton",""]],inputs:{moduleType:"moduleType",accessType:"accessType"}}),t})(),i=(()=>{class t{}return t.\u0275mod=c.Zb({type:t}),t.\u0275inj=c.Yb({factory:function(e){return new(e||t)}}),t})()},OXlc:function(t,e,n){"use strict";n.r(e),n.d(e,"TaxPayersModule",(function(){return B}));var c=n("ofXK"),s=n("tyNb"),r=n("fXoL"),i=n("Kj3r"),a=n("eIep"),o=n("t0ZU"),l=n("tk/3"),g=n("5eHb"),d=n("3Pt+"),h=n("MgRC"),u=n("oOf3");const p=function(){return["/home/tax-payers-details"]};function m(t,e){1&t&&(r.hc(0,"button",27),r.cc(1,"i",28),r.gc()),2&t&&r.Ec("routerLink",r.Hc(1,p))}function f(t,e){1&t&&(r.hc(0,"th"),r.cd(1,"Sync Status"),r.gc())}function y(t,e){1&t&&(r.hc(0,"th"),r.cd(1,"Sync Date"),r.gc())}function P(t,e){1&t&&r.cc(0,"td")}function b(t,e){1&t&&r.cc(0,"td")}const _=function(){return["../../invoices"]},M=function(t){return{value:t,prop:"invoice"}};function C(t,e){if(1&t&&(r.hc(0,"a",33),r.cd(1,"view"),r.gc()),2&t){const t=r.wc().$implicit;r.Ec("routerLink",r.Hc(2,_))("queryParams",r.Ic(3,M,t.gstNumber))}}const O=function(){return["../../credit-invoices"]},x=function(t){return{value:t,prop:"credit_count"}};function v(t,e){if(1&t&&(r.hc(0,"a",33),r.cd(1,"view"),r.gc()),2&t){const t=r.wc().$implicit;r.Ec("routerLink",r.Hc(2,O))("queryParams",r.Ic(3,x,t.gstNumber))}}function N(t,e){if(1&t&&(r.hc(0,"td"),r.cd(1),r.gc()),2&t){const t=r.wc().$implicit;r.Nb(1),r.dd(null!=t&&t.synced_to_erp?"Synced":"Not Synced")}}const w=function(){return["MMM d y"]};function T(t,e){if(1&t&&(r.hc(0,"td"),r.cd(1),r.xc(2,"date"),r.gc()),2&t){const t=r.wc().$implicit;r.Nb(1),r.dd(r.zc(2,1,null==t?null:t.synced_date,r.Hc(4,w)))}}function k(t,e){if(1&t){const t=r.ic();r.hc(0,"tr"),r.hc(1,"td"),r.cd(2),r.gc(),r.hc(3,"td"),r.cd(4),r.gc(),r.hc(5,"td"),r.cd(6),r.gc(),r.hc(7,"td"),r.cd(8),r.gc(),r.hc(9,"td"),r.cd(10),r.gc(),r.hc(11,"td"),r.cd(12),r.hc(13,"span"),r.ad(14,C,2,5,"a",29),r.gc(),r.gc(),r.hc(15,"td"),r.cd(16),r.hc(17,"span"),r.ad(18,v,2,5,"a",29),r.gc(),r.gc(),r.hc(19,"td"),r.cd(20),r.gc(),r.hc(21,"td"),r.cd(22),r.xc(23,"date"),r.gc(),r.ad(24,N,2,1,"td",10),r.ad(25,T,3,5,"td",10),r.hc(26,"td"),r.hc(27,"span"),r.hc(28,"a",30),r.sc("click",(function(){r.Qc(t);const n=e.$implicit;return r.wc().navigate(n,"View")})),r.cd(29,"view"),r.gc(),r.gc(),r.hc(30,"span",31),r.hc(31,"a",32),r.sc("click",(function(){r.Qc(t);const n=e.$implicit;return r.wc().navigate(n,"Edit")})),r.cd(32,"Edit"),r.gc(),r.gc(),r.gc(),r.gc()}if(2&t){const t=e.$implicit,n=e.index,c=r.wc();r.Nb(2),r.dd(c.filters.itemsPerPage*(c.filters.currentPage-1)+(n+1)),r.Nb(2),r.dd(null==t?null:t.trade_name),r.Nb(2),r.dd(null==t?null:t.legal_name),r.Nb(2),r.dd(null==t?null:t.gstNumber),r.Nb(2),r.dd(null==t?null:t.status),r.Nb(2),r.ed("",null==t?null:t.invoice_count," "),r.Nb(2),r.Ec("ngIf",0!==(null==t?null:t.invoice_count)),r.Nb(2),r.ed("",null==t?null:t.credit_count," "),r.Nb(2),r.Ec("ngIf",0!==(null==t?null:t.credit_count)),r.Nb(2),r.dd(null==t?null:t.invoice_count),r.Nb(2),r.dd(r.zc(23,13,null==t?null:t.creation,"MMM dd y h:mm:ss")),r.Nb(2),r.Ec("ngIf",1==(null==c.companyDetails?null:c.companyDetails.ezy_gst_module)),r.Nb(1),r.Ec("ngIf",1==(null==c.companyDetails?null:c.companyDetails.ezy_gst_module))}}function S(t,e){1&t&&(r.hc(0,"div",34),r.hc(1,"h4"),r.cd(2,"No Data Found"),r.gc(),r.gc())}function I(t,e){if(1&t){const t=r.ic();r.hc(0,"div"),r.hc(1,"p",35),r.sc("click",(function(){r.Qc(t);const e=r.wc();return e.filters.start=e.taxPayersList.length,e.filters.itemsPerPage=e.filters.itemsPerPage+20,e.updateRouterParams()})),r.cd(2," more "),r.gc(),r.gc()}}const E=function(t,e,n){return{itemsPerPage:t,currentPage:e,totalItems:n}};class L{constructor(){this.search={tradeName:"",gstNumber:"",legalName:""},this.itemsPerPage=20,this.currentPage=1,this.totalCount=0,this.sortBy="",this.status="",this.start=0}}const D=[{path:"",component:(()=>{class t{constructor(t,e,n,c){this.http=t,this.router=e,this.toastr=n,this.activatedParams=c,this.filters=new L,this.onSearch=new r.q,this.taxPayersList=[],this.searchType="",this.searchText="",this.sortBy="",this.status="All",this.loginUser={}}ngOnInit(){var t;this.companyDetails=JSON.parse(localStorage.getItem("company")),this.filters.itemsPerPage=null===(t=this.companyDetails)||void 0===t?void 0:t.items_per_page,this.onSearch.pipe(Object(i.a)(500)).subscribe(t=>{this.taxPayersList=[],this.filters.start=0,this.filters.totalCount=0,this.updateRouterParams()}),this.activatedParams.queryParams.subscribe(t=>{if(t.search){const e=JSON.parse(t.search);this.filters.search.tradeName=e.tradeName,this.filters.search.gstNumber=e.gstNumber,this.filters.search.legalName=e.legalName,this.filters.sortBy=t.sortBy,this.filters.status=t.status}}),this.getAllPayers(),this.loginUser=JSON.parse(localStorage.getItem("login")),this.loginUSerRole=this.loginUser.rolesFilter.some(t=>"ezy-IT"==t||"ezy-Finance"==t)}updateRouterParams(){const t=JSON.parse(JSON.stringify(this.filters));t.search=JSON.stringify(t.search),this.router.navigate(["home/tax-payers"],{queryParams:t})}checkPagination(){this.filters.totalCount<this.filters.itemsPerPage*this.filters.currentPage?(this.filters.currentPage=1,this.updateRouterParams()):this.updateRouterParams()}getAllPayers(){this.activatedParams.queryParams.pipe(Object(a.a)(t=>(this.filters.search.tradeName?(this.searchText=this.filters.search.tradeName,this.searchType="trade_name"):this.filters.search.legalName?(this.searchText=this.filters.search.legalName,this.searchType="legal_name"):this.filters.search.gstNumber?(this.searchText=this.filters.search.gstNumber,this.searchType="gst_number"):(this.searchText="",this.searchType=""),this.filters.sortBy&&(this.sortBy=this.filters.sortBy),this.filters.status&&(this.status=this.filters.status),this.http.post(o.a.taxPayers,{data:{start:this.filters.start,end:this.filters.itemsPerPage,value:this.searchText,key:this.searchType,sortKey:this.sortBy,type:this.searchText?"":"All",status:this.status}})))).subscribe(t=>{var e,n;try{(null==t?void 0:t.message)&&(this.taxPayersList=0!=this.filters.start?this.taxPayersList.concat(null===(e=t.message)||void 0===e?void 0:e.data):null===(n=t.message)||void 0===n?void 0:n.data,this.filters.totalCount=t.message.count.gstCount)}catch(c){console.log(c)}})}navigate(t,e){this.router.navigate(["home/tax-payers-details"],{queryParams:{id:t.gstNumber,type:e},queryParamsHandling:"merge"})}}return t.\u0275fac=function(e){return new(e||t)(r.bc(l.b),r.bc(s.e),r.bc(g.d),r.bc(s.a))},t.\u0275cmp=r.Vb({type:t,selectors:[["app-tax-payers"]],decls:84,vars:21,consts:[[1,"taxpayers","position-relative"],[1,"row","m-0","py-2"],[1,"col-md-12","col-lg-12"],[1,"d-flex"],[1,"font-weight-bold","text-white"],["class","create btn btn-primary","appPermissionButton","","accessType","create","moduleType","docType",3,"routerLink",4,"ngIf"],[1,"card"],[1,"table-responsive"],["id","s-table",1,"table"],[1,"thead"],[4,"ngIf"],[1,"input-group","input-group-sm"],[1,"input-group-prepend"],[1,"input-group-text"],[1,"ri-search-line"],["type","search",1,"form-control",3,"ngModel","ngModelChange","keyup","search","keyup.enter"],["tradeName",""],["legalName",""],["gstNumber",""],[1,"form-group"],["id","sortBy",1,"custom-select",3,"ngModel","ngModelChange","change"],["value","Active"],["value","In-Active"],["value","creation"],["value","modified"],[4,"ngFor","ngForOf"],["class","text-center py-3",4,"ngIf"],["appPermissionButton","","accessType","create","moduleType","docType",1,"create","btn","btn-primary",3,"routerLink"],[1,"ri-add-line"],["queryParamsHandling","merge",3,"routerLink","queryParams",4,"ngIf"],["appPermissionButton","","accessType","read","moduleType","docType",3,"click"],[1,"ml-3"],["appPermissionButton","","accessType","write","moduleType","docType",3,"click"],["queryParamsHandling","merge",3,"routerLink","queryParams"],[1,"text-center","py-3"],[1,"text-right","pr-5","more","text-primary",3,"click"]],template:function(t,e){1&t&&(r.hc(0,"section",0),r.hc(1,"div",1),r.hc(2,"div",2),r.hc(3,"div",3),r.hc(4,"h4",4),r.cd(5,"Tax Payers "),r.hc(6,"small"),r.cd(7),r.gc(),r.gc(),r.ad(8,m,2,2,"button",5),r.gc(),r.gc(),r.gc(),r.hc(9,"div",6),r.hc(10,"div",7),r.hc(11,"table",8),r.hc(12,"thead",9),r.hc(13,"tr"),r.hc(14,"th"),r.cd(15,"#"),r.gc(),r.hc(16,"th"),r.cd(17,"Trade Name"),r.gc(),r.hc(18,"th"),r.cd(19,"Legal Name"),r.gc(),r.hc(20,"th"),r.cd(21,"GST No."),r.gc(),r.hc(22,"th"),r.cd(23,"Status"),r.gc(),r.hc(24,"th"),r.cd(25,"Invoices"),r.gc(),r.hc(26,"th"),r.cd(27,"Credit"),r.gc(),r.hc(28,"th"),r.cd(29,"Debit"),r.gc(),r.hc(30,"th"),r.cd(31,"Sort by"),r.gc(),r.ad(32,f,2,0,"th",10),r.ad(33,y,2,0,"th",10),r.hc(34,"th"),r.cd(35,"Actions"),r.gc(),r.gc(),r.gc(),r.hc(36,"tbody"),r.hc(37,"tr"),r.cc(38,"td"),r.hc(39,"td"),r.hc(40,"div",11),r.hc(41,"div",12),r.hc(42,"span",13),r.cc(43,"i",14),r.gc(),r.gc(),r.hc(44,"input",15,16),r.sc("ngModelChange",(function(t){return e.filters.search.tradeName=t}))("keyup",(function(){return e.onSearch.emit(e.filters)}))("search",(function(){return e.onSearch.emit(e.filters)}))("keyup.enter",(function(){return e.updateRouterParams()})),r.gc(),r.gc(),r.gc(),r.hc(46,"td"),r.hc(47,"div",11),r.hc(48,"div",12),r.hc(49,"span",13),r.cc(50,"i",14),r.gc(),r.gc(),r.hc(51,"input",15,17),r.sc("ngModelChange",(function(t){return e.filters.search.legalName=t}))("keyup",(function(){return e.onSearch.emit(e.filters)}))("search",(function(){return e.onSearch.emit(e.filters)}))("keyup.enter",(function(){return e.updateRouterParams()})),r.gc(),r.gc(),r.gc(),r.hc(53,"td"),r.hc(54,"div",11),r.hc(55,"div",12),r.hc(56,"span",13),r.cc(57,"i",14),r.gc(),r.gc(),r.hc(58,"input",15,18),r.sc("ngModelChange",(function(t){return e.filters.search.gstNumber=t}))("keyup",(function(){return e.onSearch.emit(e.filters)}))("search",(function(){return e.onSearch.emit(e.filters)}))("keyup.enter",(function(){return e.updateRouterParams()})),r.gc(),r.gc(),r.gc(),r.hc(60,"td"),r.hc(61,"div",19),r.hc(62,"select",20),r.sc("ngModelChange",(function(t){return e.filters.status=t}))("change",(function(){return e.onSearch.emit(e.filters)})),r.hc(63,"option",21),r.cd(64,"Active"),r.gc(),r.hc(65,"option",22),r.cd(66,"In-Active"),r.gc(),r.gc(),r.gc(),r.gc(),r.cc(67,"td"),r.cc(68,"td"),r.cc(69,"td"),r.hc(70,"td"),r.hc(71,"div",19),r.hc(72,"select",20),r.sc("ngModelChange",(function(t){return e.filters.sortBy=t}))("change",(function(){return e.onSearch.emit(e.filters)})),r.hc(73,"option",23),r.cd(74,"Creation"),r.gc(),r.hc(75,"option",24),r.cd(76,"Modified"),r.gc(),r.gc(),r.gc(),r.gc(),r.ad(77,P,1,0,"td",10),r.ad(78,b,1,0,"td",10),r.cc(79,"td"),r.gc(),r.ad(80,k,33,16,"tr",25),r.xc(81,"paginate"),r.gc(),r.gc(),r.ad(82,S,3,0,"div",26),r.gc(),r.ad(83,I,3,0,"div",10),r.gc(),r.gc()),2&t&&(r.Nb(7),r.ed("(",e.filters.totalCount,")"),r.Nb(1),r.Ec("ngIf","Administrator"==(null==e.loginUser?null:e.loginUser.full_name)||e.loginUSerRole),r.Nb(24),r.Ec("ngIf",1==(null==e.companyDetails?null:e.companyDetails.ezy_gst_module)),r.Nb(1),r.Ec("ngIf",1==(null==e.companyDetails?null:e.companyDetails.ezy_gst_module)),r.Nb(11),r.Ec("ngModel",e.filters.search.tradeName),r.Nb(7),r.Ec("ngModel",e.filters.search.legalName),r.Nb(7),r.Ec("ngModel",e.filters.search.gstNumber),r.Nb(4),r.Ec("ngModel",e.filters.status),r.Nb(10),r.Ec("ngModel",e.filters.sortBy),r.Nb(5),r.Ec("ngIf",1==(null==e.companyDetails?null:e.companyDetails.ezy_gst_module)),r.Nb(1),r.Ec("ngIf",1==(null==e.companyDetails?null:e.companyDetails.ezy_gst_module)),r.Nb(2),r.Ec("ngForOf",r.zc(81,14,e.taxPayersList,r.Kc(17,E,e.filters.itemsPerPage,e.filters.currentPage,e.filters.totalCount))),r.Nb(2),r.Ec("ngIf",!e.taxPayersList.length),r.Nb(1),r.Ec("ngIf",e.taxPayersList.length<e.filters.totalCount))},directives:[c.p,d.b,d.i,d.l,d.r,d.m,d.t,c.o,h.a,s.f,s.h],pipes:[u.b,c.f],styles:[".taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   tr[_ngcontent-%COMP%]:nth-of-type(2n){background:#fff}.taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   tr[_ngcontent-%COMP%]:nth-of-type(odd){background:#f0f0f0}.taxpayers[_ngcontent-%COMP%]   .table-bordered[_ngcontent-%COMP%]{border:0}.taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]   .view[_ngcontent-%COMP%]{cursor:pointer;text-decoration:underline;color:#2164e8;font-weight:600}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   thead[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{border-bottom:0;border-top:0;font-size:12px;padding:9px 10px}.taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], .taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{font-size:14px;border:1px solid rgba(221,218,218,.3);white-space:nowrap;padding:9px 1rem}.taxpayers[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(2), .taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(3){max-width:300px!important}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(3)   div[_ngcontent-%COMP%], .taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(4)   div[_ngcontent-%COMP%]{max-width:140px!important}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(5)   div[_ngcontent-%COMP%]{max-width:180px!important}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(6)   div[_ngcontent-%COMP%]{max-width:120px!important;max-width:100px!important}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(7)   div[_ngcontent-%COMP%], .taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(8), .taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(9){max-width:100px!important}.taxpayers[_ngcontent-%COMP%]   table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:nth-child(3)   div[_ngcontent-%COMP%]{max-width:-webkit-fit-content!important;max-width:-moz-fit-content!important;max-width:fit-content!important}.taxpayers[_ngcontent-%COMP%]   .table[_ngcontent-%COMP%]   tbody[_ngcontent-%COMP%]   td[_ngcontent-%COMP%]:first-child{padding-left:8px!important}.taxpayers[_ngcontent-%COMP%]   .badge-success[_ngcontent-%COMP%]{padding:6px 20px;border-radius:30px;margin:0 auto;text-align:center;background:#0bd726;font-size:12px}.taxpayers[_ngcontent-%COMP%]   .badge-warning[_ngcontent-%COMP%]{background:#ffd00a}.taxpayers[_ngcontent-%COMP%]   .badge-danger[_ngcontent-%COMP%], .taxpayers[_ngcontent-%COMP%]   .badge-warning[_ngcontent-%COMP%]{padding:6px 20px;border-radius:30px;margin:0 auto;text-align:center;font-size:12px;color:#fff}.taxpayers[_ngcontent-%COMP%]   .badge-danger[_ngcontent-%COMP%]{background:#ff2f0a}.taxpayers[_ngcontent-%COMP%]   tr.pending[_ngcontent-%COMP%]{background:#fd8787!important}.taxpayers[_ngcontent-%COMP%]   .input-group[_ngcontent-%COMP%]{max-width:150px}.taxpayers[_ngcontent-%COMP%]   select.custom-select[_ngcontent-%COMP%]{height:auto}.taxpayers[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]{margin-bottom:0}.taxpayers[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]   select[_ngcontent-%COMP%]{font-size:13px}.taxpayers[_ngcontent-%COMP%]   .form-group[_ngcontent-%COMP%]   .form-control[_ngcontent-%COMP%]{padding:5px;border:0!important}.w-c-50[_ngcontent-%COMP%]{min-width:150px;margin-left:20px}.more[_ngcontent-%COMP%]{text-decoration:underline;cursor:pointer}.legalNameInp[_ngcontent-%COMP%]{width:20rem}.btn-right[_ngcontent-%COMP%]{position:absolute;top:0;right:0}"]}),t})()}];let z=(()=>{class t{}return t.\u0275mod=r.Zb({type:t}),t.\u0275inj=r.Yb({factory:function(e){return new(e||t)},imports:[[s.i.forChild(D)],s.i]}),t})(),R=(()=>{class t{}return t.\u0275mod=r.Zb({type:t}),t.\u0275inj=r.Yb({factory:function(e){return new(e||t)}}),t})(),B=(()=>{class t{}return t.\u0275mod=r.Zb({type:t}),t.\u0275inj=r.Yb({factory:function(e){return new(e||t)},imports:[[c.c,z,u.a,d.d,R,h.b]]}),t})()}}]);