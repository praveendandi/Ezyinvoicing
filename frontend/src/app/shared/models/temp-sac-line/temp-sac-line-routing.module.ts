import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { TempSacLineComponent } from './temp-sac-line.component';

const routes: Routes = [{path:'',component:TempSacLineComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TempSacLineRoutingModule { }
