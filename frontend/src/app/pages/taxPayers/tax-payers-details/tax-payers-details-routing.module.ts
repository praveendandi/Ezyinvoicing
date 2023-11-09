import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { TaxPayersDetailsComponent } from './tax-payers-details.component';



const routes: Routes = [
  { path: '', component: TaxPayersDetailsComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TaxPayersDetailsRoutingModule { }
