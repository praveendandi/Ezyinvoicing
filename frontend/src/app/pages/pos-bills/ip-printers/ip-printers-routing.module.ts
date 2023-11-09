import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { IpPrintersComponent } from './ip-printers.component';

const routes: Routes = [{path:'',component:IpPrintersComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class IpPrintersRoutingModule { }
