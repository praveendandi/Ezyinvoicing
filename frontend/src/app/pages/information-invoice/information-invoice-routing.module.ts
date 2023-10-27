import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { InformationInvoiceComponent } from './information-invoice.component';

const routes: Routes = [{ path: '', component: InformationInvoiceComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class InformationInvoiceRoutingModule { }
