import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { PaymentReconcilationComponent } from './payment-reconcilation.component';

const routes: Routes = [{ path: '', component: PaymentReconcilationComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PaymentReconcilationRoutingModule { }
