import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DocumentBinComponent } from './document-bin.component';

const routes: Routes = [{path:'',component:DocumentBinComponent}];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DocumentBinRoutingModule { }
