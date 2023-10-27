import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { AmendInvoicesComponent } from './amend-invoices.component';

const routes: Routes = [{ path: '', component: AmendInvoicesComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AmendInvoicesRoutingModule { }
