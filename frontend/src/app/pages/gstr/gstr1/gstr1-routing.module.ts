import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Gstr1Component } from './gstr1.component';

const routes: Routes = [
  { path: '', component: Gstr1Component },
  {
    path: 'invoice', loadChildren: () => import('./invoice/invoice.module').then((m) => m.InvoiceModule)
  },
  {
    path:'invoice-details/:id',loadChildren:() => import('./invoice-details/invoice-details.module').then((m)=>m.InvoiceDetailsModule)
  },
  {
    path:'ill-rated',loadChildren:()=> import('./nill-rated/nill-rated.module').then((m)=>m.NillRatedModule)
  },
  { path: 'reconciliation', loadChildren: () => import('./reconciliation/reconciliation.module').then(m => m.ReconciliationModule) },
  {
    path:'sac-hsn-outward', loadChildren:() => import('./sac-hsn-outward/sac-hsn-outward.module').then(m=>m.SacHsnOutwardModule)
  },
  {
    path:'save-gstin',loadChildren:()=> import('./save-gstin/save-gstin.module').then(m=>m.SaveGstinModule)
  },
  { path: 'gstr1-summary', loadChildren: () => import('./gstr1-summary/gstr1-summary.module').then(m => m.Gstr1SummaryModule) },
  { path: 'advance-received', loadChildren: () => import('./advance-received/advance-received.module').then(m => m.AdvanceReceivedModule) },
  { path: 'adjustment-of-advances', loadChildren: () => import('./adjustment-of-advances/adjustment-of-advances.module').then(m => m.AdjustmentOfAdvancesModule) },


];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class Gstr1RoutingModule { }
