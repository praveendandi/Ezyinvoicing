import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SyncHistoryComponent } from './sync-history.component';

const routes: Routes = [
{
  path:'',
  component:SyncHistoryComponent
}

];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SyncHistoryRoutingModule { }
