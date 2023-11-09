import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr2ReconFullTableComponent } from './gstr2-recon-full-table.component';

const routes: Routes = [{ path: '', component: Gstr2ReconFullTableComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr2ReconFullTableRoutingModule { }
