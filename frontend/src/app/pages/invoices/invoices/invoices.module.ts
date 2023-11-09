import { NgxPaginationModule } from 'ngx-pagination';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoicesRoutingModule } from './invoices-routing.module';
import { InvoicesComponent } from './invoices.component';
import { OwlDateTimeModule, OwlNativeDateTimeModule, OWL_DATE_TIME_LOCALE } from 'ng-pick-datetime';
import { NgbNavModule, NgbProgressbarModule, NgbTooltipModule, NgbDropdownModule } from '@ng-bootstrap/ng-bootstrap';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { ExpiredInvoicesComponent } from '../expired-invoices/expired-invoices.component';
import { ExpiredInvoicesPipeModule } from 'src/app/shared/pipes/expired-invoices.pipe';


@NgModule({
  declarations: [InvoicesComponent,ExpiredInvoicesComponent],
  imports: [
    CommonModule,
    FormsModule,
    InvoicesRoutingModule,
    NgxPaginationModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbTooltipModule,
    MatInputDirectiveModule,
    PermissionButtonDirectiveModule,
    NgbNavModule,
    SafePipeModule,
    NgbProgressbarModule,
    VirtualScrollerModule,
    NgbDropdownModule,
    ExpiredInvoicesPipeModule
  ],
  providers: [
    { provide: OWL_DATE_TIME_LOCALE, useValue: 'en-GB' }
  ]
})
export class InvoicesModule { }
