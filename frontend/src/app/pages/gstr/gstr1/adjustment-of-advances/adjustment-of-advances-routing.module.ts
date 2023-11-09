import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdjustmentOfAdvancesComponent } from './adjustment-of-advances.component';

const routes: Routes = [{ path: '', component: AdjustmentOfAdvancesComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdjustmentOfAdvancesRoutingModule { }
