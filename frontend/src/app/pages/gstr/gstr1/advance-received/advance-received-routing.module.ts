import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdvanceReceivedComponent } from './advance-received.component';

const routes: Routes = [{ path: '', component: AdvanceReceivedComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdvanceReceivedRoutingModule { }
