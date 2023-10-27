import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AmendInvoicesRoutingModule } from './amend-invoices-routing.module';
import { AmendInvoicesComponent } from './amend-invoices.component';

import { NgbNavModule, NgbTooltip, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { NumberInputDirectiveModule } from 'src/app/shared/directives/number-input.directive';
import { FormsModule } from '@angular/forms';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { MyFilterPipeModule } from 'src/app/shared/pipes/search-filter.pipe';


@NgModule({
  declarations: [AmendInvoicesComponent],
  imports: [
    CommonModule,
    AmendInvoicesRoutingModule,
    FormsModule,
    NumberInputDirectiveModule,
    MatInputDirectiveModule,
    NgbNavModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule,
    NgbTooltipModule,
    VirtualScrollerModule,
    MyFilterPipeModule
  ]
})
export class AmendInvoicesModule { }
