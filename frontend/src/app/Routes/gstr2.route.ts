import { Routes } from '@angular/router';
import { PurchaseRegisterComponent } from '../pages/gstr/gstr2/purchase-register/purchase-register.component';

export const gstr2Routes: Routes = [
  { 
    path: '', pathMatch: 'full', redirectTo: 'gstr2' },

  {
    path: 'gstr2', loadChildren: () => import('../pages/gstr/gstr2/gstr2.module').then((m) => m.Gstr2Module)
  },
  {
    path: 'gstr2-details', loadChildren: () => import('../pages/gstr/gstr2/gstr2-details/gstr2-details.module').then((m) => m.Gstr2DetailsModule)
  },
  {
    path: 'invoice-details', loadChildren: () => import('../pages/gstr/gstr2/add-edit-gstr2/add-edit-gstr2.module').then((m) => m.AddEditGstr2Module)
  },
  {
    path: 'gstr-reconciliation', loadChildren: () => import('../pages/gstr/gstr2/gstr2-reconciliation/gstr2-reconciliation.module').then((m) => m.Gstr2ReconciliationModule)
  },
  {
    path: 'gstr2-data', loadChildren: () => import('../pages/gstr/gstr2/gstr2-recon-full-table/gstr2-recon-full-table.module').then((m) => m.Gstr2ReconFullTableModule)
  },
  {
    path: 'purchase-register', component: PurchaseRegisterComponent
  }
]