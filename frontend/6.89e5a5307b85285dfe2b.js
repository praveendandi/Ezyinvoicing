(window.webpackJsonp=window.webpackJsonp||[]).push([[6],{icpI:function(t,e,r){"use strict";r.d(e,"a",(function(){return L})),r.d(e,"b",(function(){return z}));var a=r("XNiG"),s=r("LRne"),i=r("HDdC"),o=r("jtHE"),n=r("itXk"),h=r("xgIS"),c=r("fXoL"),l=r("5+tZ"),p=r("lJxs"),d=r("eIep"),u=r("Kj3r");const g=["*"];var b=function(t){return t.AnnotationChart="AnnotationChart",t.AreaChart="AreaChart",t.Bar="Bar",t.BarChart="BarChart",t.BubbleChart="BubbleChart",t.Calendar="Calendar",t.CandlestickChart="CandlestickChart",t.ColumnChart="ColumnChart",t.ComboChart="ComboChart",t.PieChart="PieChart",t.Gantt="Gantt",t.Gauge="Gauge",t.GeoChart="GeoChart",t.Histogram="Histogram",t.Line="Line",t.LineChart="LineChart",t.Map="Map",t.OrgChart="OrgChart",t.Sankey="Sankey",t.Scatter="Scatter",t.ScatterChart="ScatterChart",t.SteppedAreaChart="SteppedAreaChart",t.Table="Table",t.Timeline="Timeline",t.TreeMap="TreeMap",t.WordTree="wordtree",t}({});const m={[b.AnnotationChart]:"annotationchart",[b.AreaChart]:"corechart",[b.Bar]:"bar",[b.BarChart]:"corechart",[b.BubbleChart]:"corechart",[b.Calendar]:"calendar",[b.CandlestickChart]:"corechart",[b.ColumnChart]:"corechart",[b.ComboChart]:"corechart",[b.PieChart]:"corechart",[b.Gantt]:"gantt",[b.Gauge]:"gauge",[b.GeoChart]:"geochart",[b.Histogram]:"corechart",[b.Line]:"line",[b.LineChart]:"corechart",[b.Map]:"map",[b.OrgChart]:"orgchart",[b.Sankey]:"sankey",[b.Scatter]:"scatter",[b.ScatterChart]:"corechart",[b.SteppedAreaChart]:"corechart",[b.Table]:"table",[b.Timeline]:"timeline",[b.TreeMap]:"treemap",[b.WordTree]:"wordtree"},C=new c.x("GOOGLE_CHARTS_CONFIG"),v=new c.x("GOOGLE_CHARTS_LAZY_CONFIG",{providedIn:"root",factory:()=>{const t=Object(c.hb)(C,c.v.Optional);return Object(s.a)(Object.assign(Object.assign({},{version:"current",safeMode:!1}),t||{}))}});let w=(()=>{class t{constructor(t,e,r){this.zone=t,this.localeId=e,this.config$=r,this.scriptSource="https://www.gstatic.com/charts/loader.js",this.scriptLoadSubject=new a.a}isGoogleChartsAvailable(){return"undefined"!=typeof google&&void 0!==google.charts}loadChartPackages(...t){return this.loadGoogleCharts().pipe(Object(l.a)(()=>this.config$),Object(p.a)(t=>Object.assign(Object.assign({},{version:"current",safeMode:!1}),t||{})),Object(d.a)(e=>new i.a(r=>{google.charts.load(e.version,{packages:t,language:this.localeId,mapsApiKey:e.mapsApiKey,safeMode:e.safeMode}),google.charts.setOnLoadCallback(()=>{this.zone.run(()=>{r.next(),r.complete()})})})))}loadGoogleCharts(){if(this.isGoogleChartsAvailable())return Object(s.a)(null);if(!this.isLoadingGoogleCharts()){const t=this.createGoogleChartsScript();t.onload=()=>{this.zone.run(()=>{this.scriptLoadSubject.next(),this.scriptLoadSubject.complete()})},t.onerror=()=>{this.zone.run(()=>{console.error("Failed to load the google charts script!"),this.scriptLoadSubject.error(new Error("Failed to load the google charts script!"))})}}return this.scriptLoadSubject.asObservable()}isLoadingGoogleCharts(){return null!=this.getGoogleChartsScript()}getGoogleChartsScript(){return Array.from(document.getElementsByTagName("script")).find(t=>t.src===this.scriptSource)}createGoogleChartsScript(){const t=document.createElement("script");return t.type="text/javascript",t.src=this.scriptSource,t.async=!0,document.getElementsByTagName("head")[0].appendChild(t),t}}return t.\u0275fac=function(e){return new(e||t)(c.pc(c.I),c.pc(c.C),c.pc(v))},t.\u0275prov=c.Xb({token:t,factory:t.\u0275fac}),t})(),y=(()=>{class t{create(t,e,r){if(null==t)return;let a=!0;null!=e&&(a=!1);const s=google.visualization.arrayToDataTable(this.getDataAsTable(t,e),a);return r&&this.applyFormatters(s,r),s}getDataAsTable(t,e){return e?[e,...t]:t}applyFormatters(t,e){for(const r of e)r.formatter.format(t,r.colIndex)}}return t.\u0275fac=function(e){return new(e||t)},t.\u0275prov=c.Xb({factory:function(){return new t},token:t,providedIn:"root"}),t})(),f=(()=>{class t{constructor(t){this.loaderService=t,this.error=new c.q,this.ready=new c.q,this.stateChange=new c.q,this.id="_"+Math.random().toString(36).substr(2,9),this.wrapperReadySubject=new o.a(1)}get wrapperReady$(){return this.wrapperReadySubject.asObservable()}get controlWrapper(){if(!this._controlWrapper)throw new Error("Cannot access the control wrapper before it being initialized.");return this._controlWrapper}ngOnInit(){this.loaderService.loadChartPackages("controls").subscribe(()=>{this.createControlWrapper()})}ngOnChanges(t){this._controlWrapper&&(t.type&&this._controlWrapper.setControlType(this.type),t.options&&this._controlWrapper.setOptions(this.options||{}),t.state&&this._controlWrapper.setState(this.state||{}))}createControlWrapper(){this._controlWrapper=new google.visualization.ControlWrapper({containerId:this.id,controlType:this.type,state:this.state,options:this.options}),this.addEventListeners(),this.wrapperReadySubject.next(this._controlWrapper)}addEventListeners(){google.visualization.events.removeAllListeners(this._controlWrapper),google.visualization.events.addListener(this._controlWrapper,"ready",t=>this.ready.emit(t)),google.visualization.events.addListener(this._controlWrapper,"error",t=>this.error.emit(t)),google.visualization.events.addListener(this._controlWrapper,"statechange",t=>this.stateChange.emit(t))}}return t.\u0275fac=function(e){return new(e||t)(c.bc(w))},t.\u0275cmp=c.Vb({type:t,selectors:[["control-wrapper"]],hostAttrs:[1,"control-wrapper"],hostVars:1,hostBindings:function(t,e){2&t&&c.kc("id",e.id)},inputs:{for:"for",type:"type",options:"options",state:"state"},outputs:{error:"error",ready:"ready",stateChange:"stateChange"},exportAs:["controlWrapper"],features:[c.Lb],decls:0,vars:0,template:function(t,e){},encapsulation:2,changeDetection:0}),t})(),S=(()=>{class t{constructor(t,e,r){this.element=t,this.loaderService=e,this.dataTableService=r,this.ready=new c.q,this.error=new c.q,this.initialized=!1}ngOnInit(){this.loaderService.loadChartPackages("controls").subscribe(()=>{this.dataTable=this.dataTableService.create(this.data,this.columns,this.formatters),this.createDashboard(),this.initialized=!0})}ngOnChanges(t){this.initialized&&(t.data||t.columns||t.formatters)&&(this.dataTable=this.dataTableService.create(this.data,this.columns,this.formatters),this.dashboard.draw(this.dataTable))}createDashboard(){const t=this.controlWrappers.map(t=>t.wrapperReady$),e=this.controlWrappers.map(t=>t.for).map(t=>Array.isArray(t)?Object(n.a)(t.map(t=>t.wrapperReady$)):t.wrapperReady$);Object(n.a)([...t,...e]).subscribe(()=>{this.dashboard=new google.visualization.Dashboard(this.element.nativeElement),this.initializeBindings(),this.registerEvents(),this.dashboard.draw(this.dataTable)})}registerEvents(){google.visualization.events.removeAllListeners(this.dashboard);const t=(t,e,r)=>{google.visualization.events.addListener(t,e,r)};t(this.dashboard,"ready",()=>this.ready.emit()),t(this.dashboard,"error",t=>this.error.emit(t))}initializeBindings(){this.controlWrappers.forEach(t=>{if(Array.isArray(t.for)){const e=t.for.map(t=>t.chartWrapper);this.dashboard.bind(t.controlWrapper,e)}else this.dashboard.bind(t.controlWrapper,t.for.chartWrapper)})}}return t.\u0275fac=function(e){return new(e||t)(c.bc(c.o),c.bc(w),c.bc(y))},t.\u0275cmp=c.Vb({type:t,selectors:[["dashboard"]],contentQueries:function(t,e,r){var a;1&t&&c.Ub(r,f,!1),2&t&&c.Mc(a=c.tc())&&(e.controlWrappers=a)},hostAttrs:[1,"dashboard"],inputs:{data:"data",columns:"columns",formatters:"formatters"},outputs:{ready:"ready",error:"error"},exportAs:["dashboard"],features:[c.Lb],ngContentSelectors:g,decls:1,vars:0,template:function(t,e){1&t&&(c.Cc(),c.Bc(0))},encapsulation:2,changeDetection:0}),t})(),L=(()=>{class t{constructor(t,e,r,a){this.element=t,this.scriptLoaderService=e,this.dataTableService=r,this.dashboard=a,this.options={},this.dynamicResize=!1,this.ready=new c.q,this.error=new c.q,this.select=new c.q,this.mouseover=new c.q,this.mouseleave=new c.q,this.wrapperReadySubject=new o.a(1),this.initialized=!1,this.eventListeners=new Map}get chart(){return this.chartWrapper.getChart()}get wrapperReady$(){return this.wrapperReadySubject.asObservable()}get chartWrapper(){if(!this.wrapper)throw new Error("Trying to access the chart wrapper before it was fully initialized");return this.wrapper}set chartWrapper(t){this.wrapper=t,this.drawChart()}ngOnInit(){var t;this.scriptLoaderService.loadChartPackages((t=this.type,m[t])).subscribe(()=>{this.dataTable=this.dataTableService.create(this.data,this.columns,this.formatters),this.wrapper=new google.visualization.ChartWrapper({container:this.element.nativeElement,chartType:this.type,dataTable:this.dataTable,options:this.mergeOptions()}),this.registerChartEvents(),this.wrapperReadySubject.next(this.wrapper),this.initialized=!0,this.drawChart()})}ngOnChanges(t){if(t.dynamicResize&&this.updateResizeListener(),this.initialized){let e=!1;(t.data||t.columns||t.formatters)&&(this.dataTable=this.dataTableService.create(this.data,this.columns,this.formatters),this.wrapper.setDataTable(this.dataTable),e=!0),t.type&&(this.wrapper.setChartType(this.type),e=!0),(t.options||t.width||t.height||t.title)&&(this.wrapper.setOptions(this.mergeOptions()),e=!0),e&&this.drawChart()}}ngOnDestroy(){this.unsubscribeToResizeIfSubscribed()}addEventListener(t,e){const r=this.registerChartEvent(this.chart,t,e);return this.eventListeners.set(r,{eventName:t,callback:e,handle:r}),r}removeEventListener(t){const e=this.eventListeners.get(t);e&&(google.visualization.events.removeListener(e.handle),this.eventListeners.delete(t))}updateResizeListener(){this.unsubscribeToResizeIfSubscribed(),this.dynamicResize&&(this.resizeSubscription=Object(h.a)(window,"resize",{passive:!0}).pipe(Object(u.a)(100)).subscribe(()=>{this.initialized&&this.drawChart()}))}unsubscribeToResizeIfSubscribed(){null!=this.resizeSubscription&&(this.resizeSubscription.unsubscribe(),this.resizeSubscription=void 0)}mergeOptions(){return Object.assign({title:this.title,width:this.width,height:this.height},this.options)}registerChartEvents(){google.visualization.events.removeAllListeners(this.wrapper),this.registerChartEvent(this.wrapper,"ready",()=>{google.visualization.events.removeAllListeners(this.chart),this.registerChartEvent(this.chart,"onmouseover",t=>this.mouseover.emit(t)),this.registerChartEvent(this.chart,"onmouseout",t=>this.mouseleave.emit(t)),this.registerChartEvent(this.chart,"select",()=>{const t=this.chart.getSelection();this.select.emit({selection:t})}),this.eventListeners.forEach(t=>t.handle=this.registerChartEvent(this.chart,t.eventName,t.callback)),this.ready.emit({chart:this.chart})}),this.registerChartEvent(this.wrapper,"error",t=>this.error.emit(t))}registerChartEvent(t,e,r){return google.visualization.events.addListener(t,e,r)}drawChart(){null==this.dashboard&&this.wrapper.draw()}}return t.\u0275fac=function(e){return new(e||t)(c.bc(c.o),c.bc(w),c.bc(y),c.bc(S,8))},t.\u0275cmp=c.Vb({type:t,selectors:[["google-chart"]],hostAttrs:[1,"google-chart"],inputs:{options:"options",dynamicResize:"dynamicResize",type:"type",data:"data",columns:"columns",title:"title",width:"width",height:"height",formatters:"formatters"},outputs:{ready:"ready",error:"error",select:"select",mouseover:"mouseover",mouseleave:"mouseleave"},exportAs:["googleChart"],features:[c.Lb],decls:0,vars:0,template:function(t,e){},styles:["[_nghost-%COMP%] { width: fit-content; display: block; }"],changeDetection:0}),t})(),z=(()=>{class t{static forRoot(e={}){return{ngModule:t,providers:[{provide:C,useValue:e}]}}}return t.\u0275mod=c.Zb({type:t}),t.\u0275inj=c.Yb({factory:function(e){return new(e||t)},providers:[w]}),t})()}}]);