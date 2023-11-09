import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { TabletConfComponent } from './tablet-conf.component';

const routes: Routes = [{ path: '', component: TabletConfComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TabletConfRoutingModule { }
