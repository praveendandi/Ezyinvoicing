(window.webpackJsonp=window.webpackJsonp||[]).push([[35],{MgRC:function(t,e,c){"use strict";c.d(e,"a",(function(){return s})),c.d(e,"b",(function(){return a}));var n=c("fXoL"),i=c("kmKP");let s=(()=>{class t{constructor(t,e){this.elementRef=t,this.userService=e,this.permissions={}}ngOnInit(){this.checkDocLevelAccess()}checkAccess(){this.userService.currentUser.subscribe(t=>{var e,c;if(null===(e=null==t?void 0:t.docinfo)||void 0===e?void 0:e.permissions){let e=null===(c=null==t?void 0:t.docinfo)||void 0===c?void 0:c.permissions;e.hasOwnProperty(this.accessType)&&(this.elementRef.nativeElement.disabled=!(e[this.accessType]>0))}})}checkDocLevelAccess(){var t;this.permissions=JSON.parse(localStorage.getItem("checkPermissions")),(null===(t=this.permissions)||void 0===t?void 0:t.hasOwnProperty(this.accessType))&&(this.elementRef.nativeElement.disabled=!(this.permissions[this.accessType]>0))}}return t.\u0275fac=function(e){return new(e||t)(n.bc(n.o),n.bc(i.a))},t.\u0275dir=n.Wb({type:t,selectors:[["","appPermissionButton",""]],inputs:{moduleType:"moduleType",accessType:"accessType"}}),t})(),a=(()=>{class t{}return t.\u0275mod=n.Zb({type:t}),t.\u0275inj=n.Yb({factory:function(e){return new(e||t)}}),t})()},aRWC:function(t,e,c){"use strict";c.r(e),c.d(e,"PaymentTypeModule",(function(){return C}));var n=c("ofXK"),i=c("tyNb"),s=c("fXoL"),a=c("cp0P"),r=c("Kj3r"),o=c("eIep"),l=c("t0ZU"),p=c("AytR"),h=c("RINa"),d=c("tk/3"),u=c("3Pt+"),g=c("SYYg"),m=c("MgRC");const f=function(){return["/home/payment-type-details"]};function y(t,e){1&t&&(s.hc(0,"button",23),s.cc(1,"i",24),s.gc()),2&t&&s.Dc("routerLink",s.Gc(1,f))}function b(t,e){if(1&t){const t=s.ic();s.hc(0,"a",28),s.sc("click",(function(){s.Pc(t);const e=s.wc().$implicit;return s.wc().navigate(e,"edit")})),s.cd(1,"Edit"),s.gc()}}function P(t,e){if(1&t){const t=s.ic();s.hc(0,"tr"),s.hc(1,"td"),s.cd(2),s.gc(),s.hc(3,"td"),s.cd(4),s.gc(),s.hc(5,"td"),s.cd(6),s.gc(),s.hc(7,"td"),s.cd(8),s.gc(),s.hc(9,"td"),s.cd(10),s.xc(11,"date"),s.gc(),s.hc(12,"td"),s.hc(13,"span"),s.hc(14,"a",25),s.sc("click",(function(){s.Pc(t);const c=e.$implicit;return s.wc().navigate(c,"view")})),s.cd(15,"view"),s.gc(),s.gc(),s.hc(16,"span",26),s.ad(17,b,2,0,"a",27),s.gc(),s.gc(),s.gc()}if(2&t){const t=e.$implicit,c=s.wc();s.Nb(2),s.dd(null==t?null:t.index),s.Nb(2),s.dd(null==t?null:t.payment_type),s.Nb(2),s.dd(null==t?null:t.company),s.Nb(2),s.dd(null==t?null:t.status),s.Nb(2),s.dd(s.zc(11,6,null==t?null:t.creation,"MMM d, y")),s.Nb(7),s.Dc("ngIf","Administrator"==(null==c.loginUser?null:c.loginUser.full_name)||c.loginUSerRole)}}function v(t,e){1&t&&(s.hc(0,"div",29),s.hc(1,"h5"),s.cd(2,"No Data Found"),s.gc(),s.gc())}function D(t,e){if(1&t){const t=s.ic();s.hc(0,"div"),s.hc(1,"p",35),s.sc("click",(function(){s.Pc(t);const e=s.wc(2);return e.filters.start=e.paymentDetails.length,e.filters.currentPage=e.filters.currentPage+1,e.updateRouterParams()})),s.cd(2," more "),s.gc(),s.gc()}}function w(t,e){if(1&t){const t=s.ic();s.hc(0,"div",30),s.hc(1,"div",31),s.hc(2,"select",32),s.sc("ngModelChange",(function(e){return s.Pc(t),s.wc().filters.itemsPerPage=e}))("change",(function(){return s.Pc(t),s.wc().checkPagination()})),s.hc(3,"option",33),s.cd(4,"20"),s.gc(),s.hc(5,"option",33),s.cd(6,"50"),s.gc(),s.hc(7,"option",33),s.cd(8,"100"),s.gc(),s.hc(9,"option",33),s.cd(10,"150"),s.gc(),s.hc(11,"option",33),s.cd(12,"500"),s.gc(),s.gc(),s.gc(),s.ad(13,D,3,0,"div",34),s.gc()}if(2&t){const t=s.wc();s.Nb(2),s.Dc("ngModel",t.filters.itemsPerPage),s.Nb(1),s.Dc("value",20),s.Nb(2),s.Dc("value",50),s.Nb(2),s.Dc("value",100),s.Nb(2),s.Dc("value",150),s.Nb(2),s.Dc("value",500),s.Nb(2),s.Dc("ngIf",t.paymentDetails.length<t.filters.totalCount)}}class T{constructor(){this.search="",this.itemsPerPage=20,this.currentPage=1,this.totalCount=0,this.start=0}}const N=[{path:"",component:(()=>{class t{constructor(t,e,c,n){this.paymentService=t,this.router=e,this.http=c,this.activatedRoute=n,this.apiDomain=p.a.apiDomain,this.paymentDetails=[],this.p=1,this.filters=new T,this.onSearch=new s.q,this.loginUser={}}ngOnInit(){var t;this.companyDetails=JSON.parse(localStorage.getItem("company")),this.filters.itemsPerPage=null===(t=this.companyDetails)||void 0===t?void 0:t.items_per_page,this.onSearch.pipe(Object(r.a)(500)).subscribe(t=>{this.paymentDetails=[],this.filters.start=0,this.filters.totalCount=0,this.updateRouterParams()}),this.getTotalCountData(),this.loginUser=JSON.parse(localStorage.getItem("login")),this.loginUSerRole=this.loginUser.rolesFilter.some(t=>"ezy-IT"==t||"ezy-Finance"==t)}updateRouterParams(){this.router.navigate(["home/payment-type"],{queryParams:this.filters})}navigate(t,e){this.router.navigate(["/home/payment-type-details"],{queryParams:{id:t.name,type:e},queryParamsHandling:"merge"})}getTotalCountData(){this.http.get(""+l.a.paymentTypes,{params:{fields:JSON.stringify(["count( `tabPayment Types`.`name`) AS total_count"])}}).subscribe(t=>{this.filters.totalCount=t.data[0].total_count,this.getPaymentData()})}getPaymentData(){this.activatedRoute.queryParams.pipe(Object(o.a)(t=>{this.filters.search=t.search||this.filters.search;const e={filters:[]};this.filters.search&&e.filters.push(["name","like",`%${this.filters.search}%`]),e.limit_start=this.filters.start,e.limit_page_length=this.filters.itemsPerPage,e.order_by="`tabPayment Types`.`creation` desc",e.fields=JSON.stringify(["payment_type","status","company","creation","name"]),e.filters=JSON.stringify(e.filters);const c=this.http.get(""+l.a.paymentTypes,{params:{fields:JSON.stringify(["count( `tabPayment Types`.`name`) AS total_count"]),filters:e.filters}}),n=this.http.get(""+l.a.paymentTypes,{params:e});return Object(a.a)([c,n])})).subscribe(t=>{1==this.filters.currentPage&&(this.paymentDetails=[]);const[e,c]=t;this.filters.totalCount=e.data[0].total_count,c.data=c.data.map((t,e)=>(t&&(t.index=this.paymentDetails.length+e+1),t)),c.data&&(this.paymentDetails=0!==this.filters.start?this.paymentDetails.concat(c.data):c.data)})}checkPagination(){this.filters.currentPage=1,this.updateRouterParams()}paymentType_export(){this.http.get(l.a.payment_details).subscribe(t=>{console.log(t),window.open(`${this.apiDomain}${t.message.file_path}`,"_blank")})}}return t.\u0275fac=function(e){return new(e||t)(s.bc(h.a),s.bc(i.e),s.bc(d.b),s.bc(i.a))},t.\u0275cmp=s.Vb({type:t,selectors:[["app-payment-type"]],decls:43,vars:7,consts:[[1,"row","mb-3"],[1,"col-md-9","col-lg-9"],[1,"d-flex"],[1,"font-weight-bold","text-white","my-auto"],["class","create btn btn-primary","appPermissionButton","","accessType","create","moduleType","docType",3,"routerLink",4,"ngIf"],[1,"col-lg-3","col-md-3"],["type","button",1,"btn","btn-primary","btn-small","mr-2",3,"click"],[1,"position-relative","mt-2","mt-lg-0","mt-md-0"],["type","search","placeholder","Search",1,"form-control","pl-5",3,"ngModel","ngModelChange","keyup","search","keyup.enter"],["search",""],[1,"search"],[1,"ri-search-line"],[1,"card","pb-1"],[3,"items"],["scroll",""],[1,"table-responsive"],[1,"table"],[1,"thead"],["head",""],["container",""],[4,"ngFor","ngForOf"],["class","text-center py-3",4,"ngIf"],["class","d-flex justify-content-between",4,"ngIf"],["appPermissionButton","","accessType","create","moduleType","docType",1,"create","btn","btn-primary",3,"routerLink"],[1,"ri-add-line"],["appPermissionButton","","accessType","read","moduleType","docType",3,"click"],[1,"ml-3"],["appPermissionButton","","accessType","write","moduleType","docType",3,"click",4,"ngIf"],["appPermissionButton","","accessType","write","moduleType","docType",3,"click"],[1,"text-center","py-3"],[1,"d-flex","justify-content-between"],[1,"px-3"],["name","itemsPerPage","id","itemsPerPage",1,"custom-select",3,"ngModel","ngModelChange","change"],[3,"value"],[4,"ngIf"],[1,"text-right","pr-5","more","text-primary",3,"click"]],template:function(t,e){if(1&t){const t=s.ic();s.hc(0,"section"),s.hc(1,"div",0),s.hc(2,"div",1),s.hc(3,"div",2),s.hc(4,"h4",3),s.cd(5,"Payment Types "),s.hc(6,"small"),s.cd(7),s.gc(),s.gc(),s.ad(8,y,2,2,"button",4),s.gc(),s.gc(),s.hc(9,"div",5),s.hc(10,"div",2),s.hc(11,"button",6),s.sc("click",(function(){return e.paymentType_export()})),s.cd(12,"Export"),s.gc(),s.hc(13,"div",7),s.hc(14,"input",8,9),s.sc("ngModelChange",(function(t){return e.filters.search=t}))("keyup",(function(){s.Pc(t);const c=s.Nc(15);return e.filters.search=c.value,e.onSearch.emit(e.filters)}))("search",(function(){return e.onSearch.emit(e.filters)}))("keyup.enter",(function(){return e.updateRouterParams()})),s.gc(),s.hc(16,"span",10),s.cc(17,"i",11),s.gc(),s.gc(),s.gc(),s.gc(),s.gc(),s.hc(18,"div",12),s.hc(19,"virtual-scroller",13,14),s.hc(21,"div",15),s.hc(22,"table",16),s.hc(23,"thead",17,18),s.hc(25,"tr"),s.hc(26,"th"),s.cd(27,"#"),s.gc(),s.hc(28,"th"),s.cd(29,"Payment type"),s.gc(),s.hc(30,"th"),s.cd(31,"Company"),s.gc(),s.hc(32,"th"),s.cd(33,"Status"),s.gc(),s.hc(34,"th"),s.cd(35,"Created On"),s.gc(),s.hc(36,"th"),s.cd(37,"Actions"),s.gc(),s.gc(),s.gc(),s.hc(38,"tbody",null,19),s.ad(40,P,18,9,"tr",20),s.gc(),s.gc(),s.ad(41,v,3,0,"div",21),s.gc(),s.gc(),s.ad(42,w,14,7,"div",22),s.gc(),s.gc()}if(2&t){const t=s.Nc(20);s.Nb(7),s.ed("(",e.filters.totalCount,")"),s.Nb(1),s.Dc("ngIf","Administrator"==(null==e.loginUser?null:e.loginUser.full_name)||e.loginUSerRole),s.Nb(6),s.Dc("ngModel",e.filters.search),s.Nb(5),s.Dc("items",e.paymentDetails),s.Nb(21),s.Dc("ngForOf",t.viewPortItems),s.Nb(1),s.Dc("ngIf",!e.paymentDetails.length),s.Nb(1),s.Dc("ngIf",e.paymentDetails.length)}},directives:[n.p,u.b,u.i,u.l,g.a,n.o,m.a,i.f,u.r,u.m,u.t],pipes:[n.f],styles:[".more[_ngcontent-%COMP%]{text-decoration:underline;cursor:pointer}table[_ngcontent-%COMP%]   thead[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{border-bottom:0;border-top:0;font-size:12px;padding:9px 10px}.table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], .table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{padding:9px 10px;font-size:14px;border:1px solid rgba(221,218,218,.3)}virtual-scroller[_ngcontent-%COMP%]{width:100%;height:500px}.custom-select[_ngcontent-%COMP%]{font-size:14px;height:32px;border:0}"]}),t})()}];let _=(()=>{class t{}return t.\u0275mod=s.Zb({type:t}),t.\u0275inj=s.Yb({factory:function(e){return new(e||t)},imports:[[i.i.forChild(N)],i.i]}),t})();var k=c("oOf3");let C=(()=>{class t{}return t.\u0275mod=s.Zb({type:t}),t.\u0275inj=s.Yb({factory:function(e){return new(e||t)},imports:[[n.c,_,k.a,u.d,m.b,g.b]]}),t})()}}]);