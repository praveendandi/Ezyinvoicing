import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { NillRatedComponent } from './nill-rated.component';

const routes: Routes = [{ path: '', component: NillRatedComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class NillRatedRoutingModule { }
