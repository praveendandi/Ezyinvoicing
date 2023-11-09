import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PaymentTypeRoutingModule } from './payment-type-routing.module';
import { PaymentTypeComponent } from './payment-type.component';
import { NgxPaginationModule } from 'ngx-pagination';
import { FormsModule } from '@angular/forms';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';


@NgModule({
  declarations: [PaymentTypeComponent],
  imports: [
    CommonModule,
    PaymentTypeRoutingModule,
    NgxPaginationModule,
    FormsModule,
    PermissionButtonDirectiveModule,
    VirtualScrollerModule
  ]
})
export class PaymentTypeModule { }
