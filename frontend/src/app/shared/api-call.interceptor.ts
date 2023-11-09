import { ApiUrls } from './api-urls';
import { LoaderService } from './loader.component';
import { HostListener, Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpResponse
} from '@angular/common/http';
import { Observable, of, Subject, throwError } from 'rxjs';
import { finalize, map, catchError, takeUntil, tap } from 'rxjs/operators';
import { ActivatedRoute, ActivationEnd, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { LocationStrategy } from '@angular/common';

@Injectable()
export class ApiCallInterceptor implements HttpInterceptor {
  private pendingHTTPRequests$ = new Subject<void>();
  apiCount = 0;
  nonLoadingApis = [
    ApiUrls.networkStatus,
    ApiUrls.xlBulkInvoice,
    ApiUrls.sendEmail,
    ApiUrls.invoices,
    ApiUrls.taxPayerDefault,
    ApiUrls.taxpayerlocation,
    // ApiUrls.summary_activity_log
    ApiUrls.posChecks,
    ApiUrls.summary_amendment,
    ApiUrls.reconcilation
  ]

  private cache = new Map<string, any>();
  constructor(
    private loader: LoaderService,
    private router: Router,
    private toastr: ToastrService,
    private activatedRoute : ActivatedRoute,
    private location : LocationStrategy,
    
    
  ) {
    location.onPopState((res) => {
      this.router.events.subscribe(event => {
        if (event instanceof ActivationEnd) {
          this.cancelPendingRequests();
        }
      })
      
    });
  }

  public cancelPendingRequests() {
    this.pendingHTTPRequests$.next();
  }

  public onCancelPendingRequests() {
    return this.pendingHTTPRequests$.asObservable();
  }

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    this.apiCount++;
    const body = request.body;
    let withCredentials = true;
    if (body instanceof FormData) {
      if (body.get('cmd') == 'login') {
        withCredentials = false;
      }
    }
    // console.log('withCredentials: ', withCredentials);

    if (this.nonLoadingApis.indexOf(request.url) == -1) {
      this.loader.showLoader();
    }

    if (request.url.includes('method/version2_app.version2_app.doctype.company.company.bench_migrate')) {
      this.loader.hideLoader();
    }
    if (request.url.includes('method/version2_app.version2_app.doctype.company.company.updateUiProd')) {
      this.loader.hideLoader();
    }
    if (request.url.includes('method/version2_app.clbs.doctype.summaries.summaries.summary_activity_log?')) {
      this.loader.hideLoader();
    }
    if (request.url.includes('method/version2_app.version2_app.doctype.xml_parse.extract_xml')) {
      this.loader.hideLoader();
    }
    if (this.router.url.split("?")[0] == '/home/pos-bills' && request.url.includes('method/upload_file')) {
      this.loader.hideLoader();
    }
    if (window.location.href.includes('home/dashboard')) {
      this.loader.hideLoader();
    }

    if (window.location.href.includes('/clbs/')) {
      let company = JSON.parse(localStorage.getItem('company'));
      if (!company?.name) {
        window.location.reload();
      }
      if(company?.clbs == 0){
        this.toastr.info('CLBS module is disabled.')
        this.router.navigate([''])
      }
    }
    // let url = request.url.replace('+','%2B')
    // url = request.url.replace('#','%23')
    let temp = request.clone({
      url: request.url.replace(/%/, '%25').replace('#','%23'),
      // withCredentials: withCredentials,
      setHeaders: {
        // 'Access-Control-Allow-Origin':"*"
        'cache-control': "no-cache"
      }
    });
    // if (this.storage.getRawValue('CUSTOMER')) {
    //   temp = request.clone({
    //     setHeaders: {
    //       authorization: `Bearer ${this.storage.getRawValue('CUSTOMER')}`
    //     }
    //   });
    // }

  

    return next.handle(temp).pipe(map(event => {
      return event;
    }), finalize(() => {
      if (this.nonLoadingApis.indexOf('api/api/' + request.url) == -1) {
        this.apiCount--;
        if (this.apiCount <= 0) {
          this.loader.hideLoader();
        }
      }
    }),catchError(err => {

      if (err.status === 401 || err.error.exc_type == "CSRFTokenError") {
        //  this.toastr.show("Session Expired")
        localStorage.clear()
        sessionStorage.removeItem("SelItem");
        // this.toastr.show("Session Expired")
        this.router.navigate(['']);
      }
      if (err.status === 500) {
        this.toastr.error("Internal Error 500");
      }
      if (err.status === 403) {
        // this.toastr.error("Forbidden Error 403")
      }
      if (err.status === 409) {
        this.toastr.error("Already Exists");
      }
      if (err.status === 400) {
        this.toastr.error("Bad Request");
      }
      return throwError(err);
    })
    ).pipe(takeUntil(this.onCancelPendingRequests()));
  }


 
}
