import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InformationInvoiceRoutingModule } from './information-invoice-routing.module';
import { SafePipeModule } from 'src/app/shared/pipes/safe.pipe';
import { InformationInvoiceComponent } from './information-invoice.component';
import { FormsModule } from '@angular/forms';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';

@NgModule({
  declarations: [InformationInvoiceComponent],
  imports: [
    CommonModule,
    InformationInvoiceRoutingModule,
    SafePipeModule,
    NgbTooltipModule,
    FormsModule,
    VirtualScrollerModule
  ]
})
export class InformationInvoiceModule { }
