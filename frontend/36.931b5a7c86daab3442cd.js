(window.webpackJsonp=window.webpackJsonp||[]).push([[36],{AnDN:function(e,t,n){"use strict";n.r(t),n.d(t,"PaymentTypeDetailsModule",(function(){return b}));var a=n("ofXK"),s=n("tyNb"),i=n("t0ZU"),c=n("fXoL"),o=n("RINa"),r=n("tk/3"),p=n("kmKP"),l=n("3Pt+"),m=n("HgEw"),d=n("MgRC");function h(e,t){1&e&&(c.hc(0,"small",25),c.cd(1,"Already Exists"),c.gc())}const u=function(){return["/home/payment-type"]};function y(e,t){1&e&&(c.hc(0,"div",26),c.hc(1,"button",27),c.cd(2,"Cancel"),c.gc(),c.hc(3,"button",28),c.cd(4,"Save"),c.gc(),c.gc()),2&e&&(c.Nb(1),c.Ec("routerLink",c.Hc(1,u)))}const g=[{path:"",component:(()=>{class e{constructor(e,t,n,a,s){this.paymentService=e,this.activatedRoute=t,this.http=n,this.router=a,this.userService=s,this.checkName=!1,this.companyList=[],this.paymentDetails={}}ngOnInit(){var e;this.company=JSON.parse(localStorage.getItem("company")),this.paramDetails=this.activatedRoute.snapshot.queryParams,this.header=this.paramDetails.type?"view"===this.paramDetails.type?"View":"Edit":"Create",(null===(e=this.paramDetails)||void 0===e?void 0:e.id)&&(this.getPaymentDetails(),this.getPermissions()),this.changeCompany()}getPermissions(){var e;const t={};t.doctype=i.b.paymentTypes,t.name=null===(e=this.paramDetails)||void 0===e?void 0:e.id,this.http.get(i.a.permissions,{params:t}).subscribe(e=>{this.userService.setUser(e)})}getPaymentDetails(){var e;this.http.get(`${i.a.paymentTypes}/${null===(e=this.paramDetails)||void 0===e?void 0:e.id}`).subscribe(e=>{this.paymentDetails=e.data})}changePayment(e){this.http.get(`${i.a.getClient}?doctype=${i.b.paymentTypes}&fieldname=name&filters=${e}`).subscribe(e=>{var t;this.checkName=!!(null===(t=e.message)||void 0===t?void 0:t.name)})}changeCompany(){this.http.get(""+i.a.company).subscribe(e=>{e.data&&(this.paymentDetails.company=e.data[0].name)})}onSubmit(e){if(e.valid)if("edit"===this.paramDetails.type)this.http.put(`${i.a.paymentTypes}/${this.paramDetails.id}`,e.value).subscribe(e=>{console.log("edited",e),this.router.navigate(["/home/payment-type"])});else{e.value.doctype=i.b.paymentTypes,e.value.company=this.company.name;const t=new FormData;t.append("doc",JSON.stringify(e.value)),t.append("action","Save"),this.http.post(""+i.a.fileSave,t).subscribe(e=>{console.log("Added",e),this.router.navigate(["/home/payment-type"])})}else e.form.markAllAsTouched()}}return e.\u0275fac=function(t){return new(t||e)(c.bc(o.a),c.bc(s.a),c.bc(r.b),c.bc(s.e),c.bc(p.a))},e.\u0275cmp=c.Vb({type:e,selectors:[["app-payment-type-details"]],decls:38,vars:11,consts:[[1,"card"],[1,"card-body"],[1,"font-weight-bold"],[1,"text-muted"],[1,"text-primary","cursor-pointer",3,"routerLink","queryParamsHandling","replaceUrl"],[3,"ngSubmit"],["form","ngForm"],[1,"row"],[1,"col-lg-10","col-md-10"],[1,"col-lg-6","col-md-6"],[1,"form-group"],["type","text","appMatInput","","id","payment_type","name","payment_type","required","",1,"form-control",3,"ngModel","readOnly","ngModelChange"],["payment_type","ngModel"],["for","payment_type",1,"mat-label"],["class","text-danger",4,"ngIf"],[1,"col-lg-6","col-md-6","d-none"],["type","text","appMatInput","","id","company","name","company","readonly","","required","",1,"form-control",3,"ngModel","ngModelChange"],["company","ngModel"],["for","company",1,"mat-label"],["appMatInput","","name","status","id","status","required","",1,"custom-select",3,"ngModel","ngModelChange"],["status","ngModel"],["value","Active"],["value","In-Active"],["for","status",1,"mat-label"],["class","text-right",4,"ngIf"],[1,"text-danger"],[1,"text-right"],["type","button",1,"btn","btn-outline-primary","mb-0","text-uppercase",3,"routerLink"],["appPermissionButton","","accessType","write","type","submit",1,"btn","btn-primary","mb-0","text-uppercase","ml-3"]],template:function(e,t){if(1&e){const e=c.ic();c.hc(0,"section"),c.hc(1,"div",0),c.hc(2,"div",1),c.hc(3,"h4",2),c.cd(4,"Payment Type"),c.gc(),c.hc(5,"p",3),c.hc(6,"a",4),c.cd(7,"Payment Type "),c.gc(),c.cd(8),c.gc(),c.hc(9,"form",5,6),c.sc("ngSubmit",(function(){c.Qc(e);const n=c.Oc(10);return t.onSubmit(n)})),c.hc(11,"div",7),c.hc(12,"div",8),c.hc(13,"div",7),c.hc(14,"div",9),c.hc(15,"div",10),c.hc(16,"input",11,12),c.sc("ngModelChange",(function(e){return t.paymentDetails.payment_type=e}))("ngModelChange",(function(e){return t.changePayment(e)})),c.gc(),c.hc(18,"label",13),c.cd(19,"Payment Type"),c.gc(),c.ad(20,h,2,0,"small",14),c.gc(),c.gc(),c.hc(21,"div",15),c.hc(22,"div",10),c.hc(23,"input",16,17),c.sc("ngModelChange",(function(e){return t.paymentDetails.company=e})),c.gc(),c.hc(25,"label",18),c.cd(26,"Company"),c.gc(),c.gc(),c.gc(),c.hc(27,"div",9),c.hc(28,"div",10),c.hc(29,"select",19,20),c.sc("ngModelChange",(function(e){return t.paymentDetails.status=e})),c.hc(31,"option",21),c.cd(32,"Active"),c.gc(),c.hc(33,"option",22),c.cd(34,"In-Active"),c.gc(),c.gc(),c.hc(35,"label",23),c.cd(36,"Status"),c.gc(),c.gc(),c.gc(),c.gc(),c.ad(37,y,5,2,"div",24),c.gc(),c.gc(),c.gc(),c.gc(),c.gc(),c.gc()}2&e&&(c.Nb(6),c.Ec("routerLink",c.Hc(10,u))("queryParamsHandling","preserve")("replaceUrl",!0),c.Nb(2),c.ed("/ ",t.header," Payment Type "),c.Nb(8),c.Ec("ngModel",t.paymentDetails.payment_type)("readOnly","view"===t.paramDetails.type),c.Nb(4),c.Ec("ngIf",t.checkName),c.Nb(3),c.Ec("ngModel",t.paymentDetails.company),c.Nb(6),c.Ec("ngModel",t.paymentDetails.status),c.Nb(8),c.Ec("ngIf","view"!==(null==t.paramDetails?null:t.paramDetails.type)))},directives:[s.h,l.u,l.j,l.k,l.b,m.a,l.q,l.i,l.l,a.p,l.r,l.m,l.t,s.f,d.a],styles:[""]}),e})()}];let v=(()=>{class e{}return e.\u0275mod=c.Zb({type:e}),e.\u0275inj=c.Yb({factory:function(t){return new(t||e)},imports:[[s.i.forChild(g)],s.i]}),e})(),b=(()=>{class e{}return e.\u0275mod=c.Zb({type:e}),e.\u0275inj=c.Yb({factory:function(t){return new(t||e)},imports:[[a.c,v,l.d,m.b,d.b]]}),e})()},MgRC:function(e,t,n){"use strict";n.d(t,"a",(function(){return i})),n.d(t,"b",(function(){return c}));var a=n("fXoL"),s=n("kmKP");let i=(()=>{class e{constructor(e,t){this.elementRef=e,this.userService=t,this.permissions={}}ngOnInit(){this.checkDocLevelAccess()}checkAccess(){this.userService.currentUser.subscribe(e=>{var t,n;if(null===(t=null==e?void 0:e.docinfo)||void 0===t?void 0:t.permissions){let t=null===(n=null==e?void 0:e.docinfo)||void 0===n?void 0:n.permissions;t.hasOwnProperty(this.accessType)&&(this.elementRef.nativeElement.disabled=!(t[this.accessType]>0))}})}checkDocLevelAccess(){var e;this.permissions=JSON.parse(localStorage.getItem("checkPermissions")),(null===(e=this.permissions)||void 0===e?void 0:e.hasOwnProperty(this.accessType))&&(this.elementRef.nativeElement.style["pointer-events"]=this.permissions[this.accessType]>0?"auto":"none",this.elementRef.nativeElement.style.cursor=this.permissions[this.accessType]>0?"pointer":"not-allowed",this.elementRef.nativeElement.disabled=!(this.permissions[this.accessType]>0))}}return e.\u0275fac=function(t){return new(t||e)(a.bc(a.o),a.bc(s.a))},e.\u0275dir=a.Wb({type:e,selectors:[["","appPermissionButton",""]],inputs:{moduleType:"moduleType",accessType:"accessType"}}),e})(),c=(()=>{class e{}return e.\u0275mod=a.Zb({type:e}),e.\u0275inj=a.Yb({factory:function(t){return new(t||e)}}),e})()}}]);