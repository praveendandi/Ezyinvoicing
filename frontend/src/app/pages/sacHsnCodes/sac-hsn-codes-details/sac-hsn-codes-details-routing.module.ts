import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SacHsnCodesDetailsComponent } from './sac-hsn-codes-details.component';

const routes: Routes = [
  { path: '', component: SacHsnCodesDetailsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SacHsnCodesDetailsRoutingModule { }
