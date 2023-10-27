import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr2ReconciliationComponent } from './gstr2-reconciliation.component';

const routes: Routes = [{ path: '', component: Gstr2ReconciliationComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr2ReconciliationRoutingModule { }
