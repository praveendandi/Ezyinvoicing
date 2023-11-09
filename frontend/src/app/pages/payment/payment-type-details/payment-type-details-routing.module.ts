import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PaymentTypeDetailsComponent } from './payment-type-details.component';

const routes: Routes = [{ path: '', component: PaymentTypeDetailsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PaymentTypeDetailsRoutingModule { }
