import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { BenchLogDetailsComponent } from './bench-log-details.component';

const routes: Routes = [{path:'',component:BenchLogDetailsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class BenchLogDetailsRoutingModule { }
