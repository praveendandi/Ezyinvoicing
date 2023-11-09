import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { WorkstationsComponent } from './workstations.component';

const routes: Routes = [{ path: '', component: WorkstationsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class WorkstationsRoutingModule { }
