import { ApiCallInterceptor } from './shared/api-call.interceptor';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { HeaderComponent } from './shared/header/header.component';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { LoaderComponent } from './shared/loader.component';
import { TrimPipe } from './shared/pipes/trim.pipe';
import { NgbAccordionModule, NgbDropdownModule, NgbPaginationModule, NgbProgressbarModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { PermissionResolver } from './permission.resolver';
import { AuthGuardService } from './shared/auth/auth-guard.service';
import { ToastrModule } from 'ngx-toastr';
import { MatInputDirectiveModule } from './shared/directives/mat-input.directive';
import { FormsModule } from '@angular/forms';
import { ActivitylogComponent } from './pages/activitylog/activitylog.component';
import { UnderscoreToSpaceModule } from './shared/pipes/underscore-to-space.pipe';
import { FileUploaderComponent } from './shared/models/file-uploader/file-uploader.component';
import { CreateInvoiceManualComponent } from './shared/models/create-invoice-manual/create-invoice-manual.component';
import { NgSelectModule } from '@ng-select/ng-select';
import { SplitLineItemsComponent } from './shared/models/split-line-items/split-line-items.component';
import { NoWhiteSpaceInputDirectiveModule } from './shared/directives/no-whitespaces.directive';
import { MultiSplitItemComponent } from './shared/models/multi-split-item/multi-split-item.component';
import { NotificationsComponent } from './shared/models/notifications/notifications.component';
import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';
import { CustomToastrComponent } from './shared/custom/custom-toastr/custom-toastr.component';
import { ClipboardModule } from 'ngx-clipboard';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { LottieModule } from 'ngx-lottie';
import player from 'lottie-web';
import { QuillModule } from 'ngx-quill';
import { DatePipe } from '@angular/common';

import { PerfectScrollbarConfigInterface, PERFECT_SCROLLBAR_CONFIG, PerfectScrollbarModule } from 'ngx-perfect-scrollbar';
import { FileuploadProgressbarModule } from './resuable/fileupload-progressbar/fileupload-progressbar.module';
import { FileuploadProgressbarComponent } from './resuable/fileupload-progressbar/fileupload-progressbar.component';
import { FileuploadProgressbarService } from './resuable/fileupload-progressbar/fileupload-progressbar.service';
import { NgCircleProgressModule } from 'ng-circle-progress';
import { BulkUploadExcelProgressbarComponent } from './shared/models/bulk-upload-excel-progressbar/bulk-upload-excel-progressbar.component';
import { ExcelService } from './shared/services/excel.service';
import { Ng2SearchPipeModule } from 'ng2-search-filter';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';



const DEFAULT_PERFECT_SCROLLBAR_CONFIG: PerfectScrollbarConfigInterface = {
  suppressScrollX: true,
  wheelPropagation: false
};
const config: SocketIoConfig = { url: '', options: {} };
@NgModule({
  declarations: [
    AppComponent,
    MainLayoutComponent,
    HeaderComponent,
    LoaderComponent,
    ActivitylogComponent,
    FileUploaderComponent,
    CreateInvoiceManualComponent,
    SplitLineItemsComponent,
    MultiSplitItemComponent,
    NotificationsComponent,
    CustomToastrComponent,
    NotificationsComponent,
    FileuploadProgressbarComponent,
    BulkUploadExcelProgressbarComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    NgbDropdownModule,
    BrowserAnimationsModule,
    MatInputDirectiveModule,
    NgbTooltipModule,
    FormsModule,
    NgbAccordionModule,
    NgSelectModule,
    UnderscoreToSpaceModule,
    NgbProgressbarModule,
    FileuploadProgressbarModule,
    NgbPaginationModule,
    NoWhiteSpaceInputDirectiveModule,
    NgCircleProgressModule.forRoot({
      // set defaults here
      radius: 100,
      outerStrokeWidth: 16,
      innerStrokeWidth: 8,
      outerStrokeColor: "#78C000",
      innerStrokeColor: "#C7E596",
      animationDuration: 300,
    }),
    QuillModule.forRoot(),
    ToastrModule.forRoot({
      timeOut: 10000,
      positionClass: 'toast-bottom-right',
      // preventDuplicates: true,
      // toastComponent: CustomToastrComponent
    }),
    SocketIoModule.forRoot(config),
    ClipboardModule,
    LottieModule.forRoot({ player: playerFactory }),
    VirtualScrollerModule,
    Ng2SearchPipeModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule
  ],
  providers: [
    {
      useClass: ApiCallInterceptor,
      provide: HTTP_INTERCEPTORS,
      multi: true
    },
    PermissionResolver,
    AuthGuardService,
    { provide: PERFECT_SCROLLBAR_CONFIG, useValue: DEFAULT_PERFECT_SCROLLBAR_CONFIG },
    DatePipe,
    ExcelService,
  ],
  bootstrap: [AppComponent],
  exports: [FileUploaderComponent, CreateInvoiceManualComponent, SplitLineItemsComponent, NotificationsComponent, CustomToastrComponent, MultiSplitItemComponent]
})
export class AppModule { }
export function playerFactory() {
  return player;
}
