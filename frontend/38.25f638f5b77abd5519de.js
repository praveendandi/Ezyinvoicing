(window.webpackJsonp=window.webpackJsonp||[]).push([[38],{MgRC:function(e,t,s){"use strict";s.d(t,"a",(function(){return n})),s.d(t,"b",(function(){return r}));var c=s("fXoL"),i=s("kmKP");let n=(()=>{class e{constructor(e,t){this.elementRef=e,this.userService=t,this.permissions={}}ngOnInit(){this.checkDocLevelAccess()}checkAccess(){this.userService.currentUser.subscribe(e=>{var t,s;if(null===(t=null==e?void 0:e.docinfo)||void 0===t?void 0:t.permissions){let t=null===(s=null==e?void 0:e.docinfo)||void 0===s?void 0:s.permissions;t.hasOwnProperty(this.accessType)&&(this.elementRef.nativeElement.disabled=!(t[this.accessType]>0))}})}checkDocLevelAccess(){var e;this.permissions=JSON.parse(localStorage.getItem("checkPermissions")),(null===(e=this.permissions)||void 0===e?void 0:e.hasOwnProperty(this.accessType))&&(this.elementRef.nativeElement.disabled=!(this.permissions[this.accessType]>0))}}return e.\u0275fac=function(t){return new(t||e)(c.bc(c.o),c.bc(i.a))},e.\u0275dir=c.Wb({type:e,selectors:[["","appPermissionButton",""]],inputs:{moduleType:"moduleType",accessType:"accessType"}}),e})(),r=(()=>{class e{}return e.\u0275mod=c.Zb({type:e}),e.\u0275inj=c.Yb({factory:function(t){return new(t||e)}}),e})()},eDec:function(e,t,s){"use strict";s.r(t),s.d(t,"RolesModule",(function(){return C}));var c=s("ofXK"),i=s("tyNb"),n=s("fXoL"),r=s("Kj3r"),o=s("eIep"),a=s("t0ZU"),l=s("tk/3"),h=s("1kSV"),d=s("3Pt+");const u=["showUsers"],p=function(){return["MMM d, y, h:mm a"]};function f(e,t){if(1&e){const e=n.ic();n.hc(0,"tr"),n.hc(1,"td"),n.cd(2),n.gc(),n.hc(3,"td"),n.cd(4),n.gc(),n.hc(5,"td"),n.cd(6),n.xc(7,"date"),n.gc(),n.hc(8,"td"),n.hc(9,"a",17),n.sc("click",(function(){n.Pc(e);const s=t.$implicit,c=t.index;return n.wc().ShowUsers(s,c)})),n.cd(10,"Show Users"),n.gc(),n.gc(),n.gc()}if(2&e){const e=t.$implicit,s=t.index,c=n.wc();n.Nb(2),n.dd(c.filters.itemsPerPage*(c.filters.currentPage-1)+(s+1)),n.Nb(2),n.dd(null==e?null:e.name),n.Nb(2),n.ed(" ",n.zc(7,3,null==e?null:e.modified,n.Gc(6,p)),"")}}function g(e,t){1&e&&(n.hc(0,"div",18),n.hc(1,"h5"),n.cd(2,"No Data Found"),n.gc(),n.gc())}function m(e,t){if(1&e&&(n.hc(0,"li"),n.cd(1),n.xc(2,"titlecase"),n.gc()),2&e){const e=t.$implicit;n.Nb(1),n.ed(" ",n.yc(2,1,e)," ")}}function b(e,t){if(1&e&&(n.hc(0,"div",19),n.hc(1,"h6"),n.hc(2,"strong"),n.cd(3),n.gc(),n.gc(),n.hc(4,"button",20),n.sc("click",(function(){return t.$implicit.dismiss("Cross click")})),n.hc(5,"span",21),n.cd(6,"\xd7"),n.gc(),n.gc(),n.gc(),n.hc(7,"div",22),n.hc(8,"div",23),n.hc(9,"ul",24),n.ad(10,m,3,3,"li",14),n.gc(),n.gc(),n.gc()),2&e){const e=n.wc();n.Nb(3),n.ed("",null==e.selectedRole?null:e.selectedRole.name," "),n.Nb(7),n.Dc("ngForOf",e.usersList)}}class y{constructor(){this.itemsPerPage=20,this.currentPage=1,this.totalCount=100,this.search=""}}const v=[{path:"",component:(()=>{class e{constructor(e,t,s,c){this.http=e,this.activatedRoute=t,this.router=s,this.modal=c,this.filters=new y,this.onSearch=new n.q,this.roleList=[],this.usersList=[]}ngOnInit(){this.onSearch.pipe(Object(r.a)(500)).subscribe(e=>this.updateRouterParams()),this.getRolesCount()}updateRouterParams(){this.router.navigate(["home/roles"],{queryParams:this.filters})}getRolesCount(){this.http.get(""+a.a.roles,{params:{fields:JSON.stringify(["count( `tabRole`.`name`) AS total_count"])}}).subscribe(e=>{this.filters.totalCount=e.data[0].total_count,this.getRolesData()})}getRolesData(){this.activatedRoute.queryParams.pipe(Object(o.a)(e=>{this.filters.totalCount=parseInt(e.totalCount,0)||this.filters.totalCount,this.filters.search=e.search||this.filters.search;const t={filters:[]};return this.filters.search&&t.filters.push(["name","like",`%${this.filters.search}%`]),t.limit_page_length=this.filters.totalCount,t.order_by="`tabRole`.`creation` desc",t.fields=JSON.stringify(["name","role_name","modified_by","modified","creation"]),t.filters=JSON.stringify(t.filters),this.http.get(""+a.a.roles,{params:t})})).subscribe(e=>{e.data&&(this.roleList=e.data,this.roleList=this.roleList.filter(e=>null==e?void 0:e.name.includes("ezy")))})}ShowUsers(e,t){this.usersList=[],this.selectedRole=e,this.modal.open(this.showUsers,{size:"md",centered:!0});const s=new FormData;s.append("doctype",a.b.user),s.append("fields",JSON.stringify(["`tabUser`.`full_name`","`tabUser`.`name`","`tabUser`.`email`"])),s.append("filters",JSON.stringify([["Has Role","role","=",""+e.name]])),this.http.post(a.a.roleByUser,s).subscribe(e=>{e.message.values.map(e=>{this.usersList.push(e[0])})})}}return e.\u0275fac=function(t){return new(t||e)(n.bc(l.b),n.bc(i.a),n.bc(i.e),n.bc(h.k))},e.\u0275cmp=n.Vb({type:e,selectors:[["app-roles"]],viewQuery:function(e,t){var s;1&e&&n.jd(u,!0),2&e&&n.Mc(s=n.tc())&&(t.showUsers=s.first)},decls:30,vars:3,consts:[[1,"row","mb-3"],[1,"col-md-9","col-lg-9"],[1,"d-flex"],[1,"font-weight-bold","text-white"],[1,"col-lg-3","col-md-3"],[1,"position-relative","mt-2","mt-lg-0","mt-md-0"],["type","search","placeholder","Search",1,"form-control","pl-5",3,"ngModel","ngModelChange","keyup","search"],["search",""],[1,"search"],[1,"ri-search-line"],[1,"card"],[1,"table-responsive"],[1,"table"],[1,"thead"],[4,"ngFor","ngForOf"],["class","text-center py-3",4,"ngIf"],["showUsers",""],[3,"click"],[1,"text-center","py-3"],[1,"modal-header"],["type","button","aria-label","Close",1,"close",3,"click"],["aria-hidden","true"],[1,"modal-body"],[1,"a-logs"],[1,"list-unstyled","px-3"]],template:function(e,t){if(1&e){const e=n.ic();n.hc(0,"section"),n.hc(1,"div",0),n.hc(2,"div",1),n.hc(3,"div",2),n.hc(4,"h4",3),n.cd(5,"Roles"),n.gc(),n.gc(),n.gc(),n.hc(6,"div",4),n.hc(7,"div",5),n.hc(8,"input",6,7),n.sc("ngModelChange",(function(e){return t.filters.search=e}))("keyup",(function(){n.Pc(e);const s=n.Nc(9);return t.filters.search=s.value,t.onSearch.emit(t.filters)}))("search",(function(){return t.onSearch.emit(t.filters)})),n.gc(),n.hc(10,"span",8),n.cc(11,"i",9),n.gc(),n.gc(),n.gc(),n.gc(),n.hc(12,"div",10),n.hc(13,"div",11),n.hc(14,"table",12),n.hc(15,"thead",13),n.hc(16,"tr"),n.hc(17,"th"),n.cd(18,"#"),n.gc(),n.hc(19,"th"),n.cd(20,"Name"),n.gc(),n.hc(21,"th"),n.cd(22,"Last Modified "),n.gc(),n.hc(23,"th"),n.cd(24,"Users"),n.gc(),n.gc(),n.gc(),n.hc(25,"tbody"),n.ad(26,f,11,7,"tr",14),n.gc(),n.gc(),n.ad(27,g,3,0,"div",15),n.gc(),n.gc(),n.gc(),n.ad(28,b,11,2,"ng-template",null,16,n.bd)}2&e&&(n.Nb(8),n.Dc("ngModel",t.filters.search),n.Nb(18),n.Dc("ngForOf",t.roleList),n.Nb(1),n.Dc("ngIf",!t.roleList.length))},directives:[d.b,d.i,d.l,c.o,c.p],pipes:[c.f,c.x],styles:["table[_ngcontent-%COMP%]   thead[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{border-bottom:0;border-top:0;font-size:12px;padding:9px 10px}.table[_ngcontent-%COMP%]   td[_ngcontent-%COMP%], .table[_ngcontent-%COMP%]   th[_ngcontent-%COMP%]{padding:9px 10px;font-size:14px;border:1px solid rgba(221,218,218,.3)}"]}),e})()}];let w=(()=>{class e{}return e.\u0275mod=n.Zb({type:e}),e.\u0275inj=n.Yb({factory:function(t){return new(t||e)},imports:[[i.i.forChild(v)],i.i]}),e})();var P=s("oOf3"),O=s("MgRC");let C=(()=>{class e{}return e.\u0275mod=n.Zb({type:e}),e.\u0275inj=n.Yb({factory:function(t){return new(t||e)},imports:[[c.c,w,d.d,P.a,O.b]]}),e})()}}]);