import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { InvoiceReconcilationComponent } from '../invoice-reconcilation/invoice-reconcilation.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { GstrComponent } from './gstr.component';
import { InvoiceReconcilationListComponent } from './invoice-reconcilation-list/invoice-reconcilation-list.component';

const routes: Routes = [
  {
    path : '',
    redirectTo : 'dashboard',
    pathMatch : 'full',
  },
  {
    path: '',
    component: GstrComponent,
    children: [
      {
        path: 'dashboard',
        component: DashboardComponent,
      },
      // {
      //   path: 'invoice-reconcilation-list',
      //   component: InvoiceReconcilationListComponent,
      // },
    ]
  },
  {
    path: 'gstr1', loadChildren: () => import('./gstr1/gstr1.module').then((m) => m.Gstr1Module)
  },
  {
    path: 'gstr2', loadChildren:() => import('./gstr2/gstr2.module').then((m)=> m.Gstr2Module)
  },
  {
    path: 'invoice-recon-list', loadChildren:()=> import('./invoice-reconcilation-list/invoice-reconcilation-list.module').then((m)=>m.InvoiceReconcilationListModule)
  }


];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GstrRoutingModule { }
