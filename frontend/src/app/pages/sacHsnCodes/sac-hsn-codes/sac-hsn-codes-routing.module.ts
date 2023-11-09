import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SacHsnCodesComponent } from './sac-hsn-codes.component';

const routes: Routes = [
  { path: '', component: SacHsnCodesComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SacHsnCodesRoutingModule { }
