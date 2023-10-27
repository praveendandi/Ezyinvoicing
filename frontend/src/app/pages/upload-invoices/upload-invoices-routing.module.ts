import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { UploadInvoicesComponent } from './upload-invoices.component';

const routes: Routes = [{path:'',component:UploadInvoicesComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class UploadInvoicesRoutingModule { }
