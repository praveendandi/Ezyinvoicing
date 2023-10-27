import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { InvoiceReconcilationComponent } from '../invoice-reconcilation/invoice-reconcilation.component';
import { InvoiceReconcilationListComponent } from './invoice-reconcilation-list.component';

const routes: Routes = [
  {
    path:'',component: InvoiceReconcilationListComponent
  },
  {
    path: 'invoice-recon', component:InvoiceReconcilationComponent
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class InvoiceReconcilationListRoutingModule { }
