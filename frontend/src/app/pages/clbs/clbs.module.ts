import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ClbsRoutingModule } from './clbs-routing.module';
import { ClbsComponent } from './clbs.component';
import { SummariesComponent } from './summaries/summaries.component';
import { InvoicesComponent } from './invoices/invoices.component';
import { NgbDropdownModule, NgbNavModule, NgbProgressbarModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { CreateSummaryComponent } from './create-summary/create-summary.component';
import { SummaryDetailsComponent } from './summary-details/summary-details.component';
import { ContactsComponent } from './contacts/contacts.component';
import { CreateContactComponent } from './create-contact/create-contact.component';
import { QuillModule } from 'ngx-quill';
import { NgxPaginationModule } from 'ngx-pagination';
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';
import { TaxpayersComponent } from './taxpayers/taxpayers.component';
import { AttachmentsComponent } from './summary-details/attachments/attachments.component';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { TaxpayersDetailsComponent } from './taxpayers-details/taxpayers-details.component';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { NoWhiteSpaceInputDirectiveModule } from 'src/app/shared/directives/no-whitespaces.directive';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { LocationModalComponent } from './location-modal/location-modal.component';
import { AdditinalInfoComponent } from './summary-details/additinal-info/additinal-info.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { GoogleChartsModule } from 'angular-google-charts';
import { SummaryDetailsViewComponent } from './summary-details-view/summary-details-view.component';
import { ClbsReportsComponent } from './clbs-reports/clbs-reports.component';
import { EventsComponent } from './events/events.component';
import { SettingsComponent } from './settings/settings.component';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { DecimaNumberDirectiveModule } from 'src/app/shared/directives/decimal-number.directive';
import { DocumentTypesComponent } from './document-types/document-types.component';
import { DragDropModule } from "@angular/cdk/drag-drop";


@NgModule({
  declarations: [ClbsComponent,LocationModalComponent, SummariesComponent, InvoicesComponent, CreateSummaryComponent, SummaryDetailsComponent, ContactsComponent, CreateContactComponent, TaxpayersComponent, AttachmentsComponent, TaxpayersDetailsComponent, AdditinalInfoComponent, DashboardComponent, SummaryDetailsViewComponent, ClbsReportsComponent, EventsComponent, SettingsComponent, DocumentTypesComponent],
  imports: [
    CommonModule,
    ClbsRoutingModule,
    NgbDropdownModule,
    NgbNavModule,
    QuillModule,
    FormsModule,
    NgSelectModule,
    NgxPaginationModule,
    SafePipeModule,
    NumberInputDirectiveModule,
    VirtualScrollerModule,
    NoWhiteSpaceInputDirectiveModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    QuillModule,
    GoogleChartsModule,
    NgbTooltipModule,
    MatInputDirectiveModule,
    DecimaNumberDirectiveModule,
    NgbDropdownModule,
    NgbProgressbarModule,
    DragDropModule
  ]
})
export class ClbsModule { }
