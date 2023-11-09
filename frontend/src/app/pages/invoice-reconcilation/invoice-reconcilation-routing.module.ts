import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { InvoiceReconcilationComponent } from './invoice-reconcilation.component';

const routes: Routes = [{path:'',component:InvoiceReconcilationComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class InvoiceReconcilationRoutingModule { }
