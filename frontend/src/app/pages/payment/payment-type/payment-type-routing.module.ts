import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PaymentTypeComponent } from './payment-type.component';

const routes: Routes = [{ path: '', component: PaymentTypeComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PaymentTypeRoutingModule { }
