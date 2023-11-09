import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CreditInvoicesComponent } from './credit-invoices.component';


const routes: Routes = [{ path: '', component: CreditInvoicesComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CreditInvoicesRoutingModule { }
