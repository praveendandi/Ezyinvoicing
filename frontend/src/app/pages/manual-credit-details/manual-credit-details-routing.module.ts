import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ManualCreditDetailsComponent } from './manual-credit-details.component';

const routes: Routes = [{ path: '', component: ManualCreditDetailsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ManualCreditDetailsRoutingModule { }
