import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SacHsnComponent } from './sac-hsn.component';

const routes: Routes = [{path:'',component:SacHsnComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SacHsnRoutingModule { }
