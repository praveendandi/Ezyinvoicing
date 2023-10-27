import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CreditInvoicesComponent } from './credit-invoices.component';
import { FormsModule } from '@angular/forms';
import { CreditInvoicesRoutingModule } from './credit-invoices-routing.module';
import { NgxPaginationModule } from 'ngx-pagination';
import { OwlDateTimeModule, OwlNativeDateTimeModule, OWL_DATE_TIME_LOCALE } from 'ng-pick-datetime';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';



@NgModule({
  declarations: [CreditInvoicesComponent],
  imports: [
    CommonModule,
    FormsModule,
    CreditInvoicesRoutingModule,
    NgxPaginationModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    PermissionButtonDirectiveModule,
    VirtualScrollerModule
  ],
  providers:[
    { provide: OWL_DATE_TIME_LOCALE, useValue: 'en-GB' }
  ]
})
export class CreditInvoicesModule { }
