import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { BenchLogsComponent } from './bench-logs.component';

const routes: Routes = [{path:'',component:BenchLogsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class BenchLogsRoutingModule { }
