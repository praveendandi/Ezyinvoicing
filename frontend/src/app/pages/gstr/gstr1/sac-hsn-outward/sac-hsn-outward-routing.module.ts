import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SacHsnOutwardComponent } from './sac-hsn-outward.component';

const routes: Routes = [{ path: '', component: SacHsnOutwardComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SacHsnOutwardRoutingModule { }
