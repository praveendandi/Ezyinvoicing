import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { GspApisDetailsComponent } from './gsp-apis-details.component';

const routes: Routes = [{ path: '', component: GspApisDetailsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GspApisDetailsRoutingModule { }
