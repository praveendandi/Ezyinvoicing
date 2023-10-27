import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { TaxPayersComponent } from './tax-payers.component';


const routes: Routes = [
  { path: '', component: TaxPayersComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TaxPayersRoutingModule { }
