import { Routes } from '@angular/router';

export const gstr1Routes: Routes = [
  { 
    path: '', pathMatch: 'full', redirectTo: 'gstr1' },

  {
    path: 'gstr1', loadChildren: () => import('../pages/gstr/gstr1/gstr1.module').then((m) => m.Gstr1Module)
  },
  {
    path:'invoice',loadChildren:() => import('../pages/gstr/gstr1/invoice/invoice.module').then((m)=>m.InvoiceModule)
  },
  {
    path:'invoice-details/:id',loadChildren:() => import('../pages/gstr/gstr1/invoice-details/invoice-details.module').then((m)=>m.InvoiceDetailsModule)
  },
  {
    path:'ill-rated',loadChildren:()=> import('../pages/gstr/gstr1/nill-rated/nill-rated.module').then((m)=>m.NillRatedModule)
  },
  { path: 'reconciliation', loadChildren: () => import('../pages/gstr/gstr1/reconciliation/reconciliation.module').then(m => m.ReconciliationModule) },
  {
    path:'sac-hsn-outward', loadChildren:() => import('../pages/gstr/gstr1/sac-hsn-outward/sac-hsn-outward.module').then(m=>m.SacHsnOutwardModule)
  },
  {
    path:'save-gstin',loadChildren:()=> import('../pages/gstr/gstr1/save-gstin/save-gstin.module').then(m=>m.SaveGstinModule)
  },
  { path: 'gstr1-summary', loadChildren: () => import('../pages/gstr/gstr1/gstr1-summary/gstr1-summary.module').then(m => m.Gstr1SummaryModule) },
  { path: 'advance-received', loadChildren: () => import('../pages/gstr/gstr1/advance-received/advance-received.module').then(m => m.AdvanceReceivedModule) },
  { path: 'adjustment-of-advances', loadChildren: () => import('../pages/gstr/gstr1/adjustment-of-advances/adjustment-of-advances.module').then(m => m.AdjustmentOfAdvancesModule) },





]