import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { GspMeteringComponent } from './gsp-metering.component';

const routes: Routes = [{path:'',component:GspMeteringComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GspMeteringRoutingModule { }
