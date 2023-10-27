import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { EmailLogsComponent } from './email-logs.component';

const routes: Routes = [{path:'',component:EmailLogsComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class EmailLogsRoutingModule { }
