import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ReconciliationComponent } from './reconciliation.component';

const routes: Routes = [{ path: '', component: ReconciliationComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ReconciliationRoutingModule { }
