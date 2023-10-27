import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { OutletsComponent } from './outlets.component';

const routes: Routes = [{path:'',component:OutletsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OutletsRoutingModule { }
