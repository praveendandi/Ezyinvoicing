import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { InvoiceDetailsRoutingModule } from './invoice-details-routing.module';
import { InvoiceDetailsComponent } from './invoice-details.component';
import { NgbNavModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [
    InvoiceDetailsComponent
  ],
  imports: [
    CommonModule,
    InvoiceDetailsRoutingModule,
    NgbNavModule
  ]
})
export class InvoiceDetailsModule { }
