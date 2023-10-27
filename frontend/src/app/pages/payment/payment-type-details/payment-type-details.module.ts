import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PaymentTypeDetailsRoutingModule } from './payment-type-details-routing.module';
import { PaymentTypeDetailsComponent } from './payment-type-details.component';
import { FormsModule } from '@angular/forms';
import { MatInputDirectiveModule } from 'src/app/shared/directives/mat-input.directive';
import { PermissionButtonDirectiveModule } from 'src/app/shared/directives/permission-button.directive';


@NgModule({
  declarations: [PaymentTypeDetailsComponent],
  imports: [
    CommonModule,
    PaymentTypeDetailsRoutingModule,
    FormsModule,
    MatInputDirectiveModule,
    PermissionButtonDirectiveModule
  ]
})
export class PaymentTypeDetailsModule { }
