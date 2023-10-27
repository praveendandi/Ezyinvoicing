import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ManualCreditNotesComponent } from './manual-credit-notes.component';

const routes: Routes = [{ path: '', component: ManualCreditNotesComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ManualCreditNotesRoutingModule { }
