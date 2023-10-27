import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AddEditGstr2Component } from './add-edit-gstr2.component';

const routes: Routes = [{ path: '', component: AddEditGstr2Component }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AddEditGstr2RoutingModule { }
