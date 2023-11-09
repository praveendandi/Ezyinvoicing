import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { DasboardUiComponent } from './dasboard-ui.component';

const routes: Routes = [{ path: '', component: DasboardUiComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DasboardUiRoutingModule { }
