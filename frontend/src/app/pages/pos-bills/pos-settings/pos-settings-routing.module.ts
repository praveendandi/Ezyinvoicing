import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PosSettingsComponent } from './pos-settings.component';

const routes: Routes = [{path:'',component:PosSettingsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PosSettingsRoutingModule { }
