import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { GspApisComponent } from './gsp-apis.component';

const routes: Routes = [
  { path: '', component: GspApisComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GspApisRoutingModule { }
