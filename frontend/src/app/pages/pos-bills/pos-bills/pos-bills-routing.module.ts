import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PosBillsComponent } from './pos-bills.component';

const routes: Routes = [{path:'',component:PosBillsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PosBillsRoutingModule { }
