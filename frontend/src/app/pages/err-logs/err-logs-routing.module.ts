import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ErrLogsComponent } from './err-logs.component';

const routes: Routes = [{ path: '', component: ErrLogsComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ErrLogsRoutingModule { }
