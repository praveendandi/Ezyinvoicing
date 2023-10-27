import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { TabletComponent } from './tablet.component';

const routes: Routes = [{ path: '', component: TabletComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TabletRoutingModule { }
