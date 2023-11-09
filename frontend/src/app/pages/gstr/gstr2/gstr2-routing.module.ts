import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr2Component } from './gstr2.component';

const routes: Routes = [
  {path: '', component: Gstr2Component}
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr2RoutingModule { }
