import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { gstr1Routes } from './Routes/gstr1.route';
import { mainRoutes } from './Routes/main.routes';
import { AuthGuardService } from './shared/auth/auth-guard.service';

const routes: Routes = [
  {
    path: '',
    canActivate: [AuthGuardService],
    loadChildren: () => import('./authentication/login/login.module').then(m => m.LoginModule)
  },
  {
    path: 'home', component: MainLayoutComponent, children: mainRoutes, canActivate: [AuthGuardService],canActivateChild:[AuthGuardService]
  },
  { path: 'faqs', loadChildren: () => import('./pages/faqs/faqs.module').then(m => m.FaqsModule) },
  { path: 'payment-reconcilation', loadChildren: () => import('./pages/payment/payment-reconcilation/payment-reconcilation.module').then(m => m.PaymentReconcilationModule) },
  { path: 'clbs', loadChildren: () => import('./pages/clbs/clbs.module').then(m => m.ClbsModule) , canActivate:[AuthGuardService]},
  { path: 'gstr', loadChildren: () => import('./pages/gstr/gstr.module').then(m => m.GstrModule) , canActivate:[AuthGuardService]},
  { path: 'sync', loadChildren: () => import('./pages/sync-history/sync-history.module').then(m => m.SyncHistoryModule), canActivate:[AuthGuardService]}
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
