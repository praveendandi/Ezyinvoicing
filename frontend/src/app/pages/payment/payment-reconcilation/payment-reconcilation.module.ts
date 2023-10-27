import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PaymentReconcilationRoutingModule } from './payment-reconcilation-routing.module';
import { PaymentReconcilationComponent } from './payment-reconcilation.component';
import { FormsModule } from '@angular/forms';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';
import { OwlDateTimeModule, OwlNativeDateTimeModule } from 'ng-pick-datetime';


@NgModule({
  declarations: [PaymentReconcilationComponent],
  imports: [
    CommonModule,
    PaymentReconcilationRoutingModule,
    FormsModule,
    VirtualScrollerModule,
    OwlDateTimeModule,
    OwlNativeDateTimeModule
  ]
})
export class PaymentReconcilationModule { }
