import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr2DetailsComponent } from './gstr2-details.component';

const routes: Routes = [{ path: '', component: Gstr2DetailsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr2DetailsRoutingModule { }
