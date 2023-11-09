import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr1SummaryComponent } from './gstr1-summary.component';

const routes: Routes = [{ path: '', component: Gstr1SummaryComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr1SummaryRoutingModule { }
