import { CUSTOM_ELEMENTS_SCHEMA, NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoiceReconcilationListRoutingModule } from './invoice-reconcilation-list-routing.module';
import { InvoiceReconcilationListComponent } from './invoice-reconcilation-list.component';
import { NoDataSignPipeModule } from 'src/app/shared/pipes/no-data-sign.pipe';
import { GoogleChartsModule } from 'angular-google-charts';
import { FormsModule } from '@angular/forms';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SharedModule } from 'src/app/shared/shared.module';
import { InvoiceReconcilationComponent } from '../invoice-reconcilation/invoice-reconcilation.component';
import { NgCircleProgressModule } from 'ng-circle-progress';
import { FileuploadProgressbarModule } from 'src/app/resuable/fileupload-progressbar/fileupload-progressbar.module';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [
    InvoiceReconcilationListComponent,
    InvoiceReconcilationComponent
  ],
  imports: [
    CommonModule,
    NoDataSignPipeModule,
    GoogleChartsModule,
    FormsModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbModule,
    SharedModule,
    FileuploadProgressbarModule,
    InvoiceReconcilationListRoutingModule,
    PermissionButtonDirectiveModule,
  ],
  schemas: [
    CUSTOM_ELEMENTS_SCHEMA,
    NO_ERRORS_SCHEMA
  ]
})
export class InvoiceReconcilationListModule { }
