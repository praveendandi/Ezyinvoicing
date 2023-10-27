import { Routes } from '@angular/router';
import { PermissionResolver } from '../permission.resolver';
import { Doctypes } from '../shared/api-urls';
import { ExpiredInvoicesComponent } from '../pages/invoices/expired-invoices/expired-invoices.component';

export const mainRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'company',
    loadChildren: () =>
      import('../pages/company/company/company.module').then(
        (m) => m.CompanyModule
      ),
  },
  {
    path: 'company-details/:id',
    data: {
      name: 'Company',
    },
    loadChildren: () =>
      import('../pages/company/company-details/company-details.module').then(
        (m) => m.CompanyDetailsModule
      ),
  },
  {
    path: 'company-details',
    data: {
      name: 'Company',
    },
    loadChildren: () =>
      import('../pages/company/company-details/company-details.module').then(
        (m) => m.CompanyDetailsModule
      ),
  },
  {
    path: 'sac-hsn-codes',
    data: {
      name: 'SAC/HSN Codes',
      docType: Doctypes.sacCodes,
    },
    loadChildren: () =>
      import('../pages/sacHsnCodes/sac-hsn-codes/sac-hsn-codes.module').then(
        (m) => m.SacHsnCodesModule
      ),
    // resolve:{reslv: PermissionResolver}
  },
  {
    path: 'sac-hsn-codes-details',
    data: {
      name: 'SAC/HSN Codes',
    },
    loadChildren: () =>
      import(
        '../pages/sacHsnCodes/sac-hsn-codes-details/sac-hsn-codes-details.module'
      ).then((m) => m.SacHsnCodesDetailsModule),
  },
  {
    path: 'payment-type',
    data: {
      name: 'Payment Types',
      docType: Doctypes.paymentTypes,
    },
    loadChildren: () =>
      import('../pages/payment/payment-type/payment-type.module').then(
        (m) => m.PaymentTypeModule
      ),
  },
  {
    path: 'payment-type-details',
    data: {
      name: 'Payment Types',
      docType: Doctypes.sacCodes,
    },
    loadChildren: () =>
      import(
        '../pages/payment/payment-type-details/payment-type-details.module'
      ).then((m) => m.PaymentTypeDetailsModule),
  },
  {
    path: 'gsp-apis',
    data: {
      name: 'GSP API',
      docType: Doctypes.gspApis,
    },
    loadChildren: () =>
      import('../pages/gspApis/gsp-apis/gsp-apis.module').then(
        (m) => m.GspApisModule
      ),
  },
  {
    path: 'gsp-apis-details',
    data: {
      name: 'GSP API',
    },
    loadChildren: () =>
      import('../pages/gspApis/gsp-apis-details/gsp-apis-details.module').then(
        (m) => m.GspApisDetailsModule
      ),
  },
  {
    path: 'invoices',
    data: {
      name: 'Invoices',
      docType: Doctypes.invoices,
    },
    loadChildren: () =>
      import('../pages/invoices/invoices/invoices.module').then(
        (m) => m.InvoicesModule
      ),
  },
  {
    path: 'Information_invoice',
    data: {
      name: 'Information Invoice',
      docType: Doctypes.information_invoice,
    },
    loadChildren: () =>
      import('../pages/information-invoice/information-invoice.module').then(
        (m) => m.InformationInvoiceModule
      ),
  },
  {
    path: 'invoice-details/:id',
    data: {
      name: 'Invoices',
    },
    loadChildren: () =>
      import('../pages/invoices/invoice-details/invoice-details.module').then(
        (m) => m.InvoiceDetailsModule
      ),
  },
  // {
  //   path: 'dashboard',
  //   data: {
  //     name: 'Dashboard',
  //   },
  //   loadChildren: () =>
  //     import('../pages/dashboard/dashboard.module').then(
  //       (m) => m.DashboardModule
  //     ),
  // },
  {
    path: 'credit-invoices',
    data: {
      name: 'SYS. Credit Notes',
      docType: Doctypes.invoices,
    },
    loadChildren: () =>
      import('../pages/credits/credit-invoices/credit-invoices.module').then(
        (m) => m.CreditInvoicesModule
      ),
  },
  {
    path: 'tax-payers',
    data: {
      name: 'Tax Payers Details',
      docType: Doctypes.taxPayers,
    },
    loadChildren: () =>
      import('../pages/taxPayers/tax-payers/tax-payers.module').then(
        (m) => m.TaxPayersModule
      ),
  },
  {
    path: 'tax-payers-details',
    data: {
      name: 'Tax Payers Details',
    },
    loadChildren: () =>
      import(
        '../pages/taxPayers/tax-payers-details/tax-payers-details.module'
      ).then((m) => m.TaxPayersDetailsModule),
  },
  {
    path: 'users',
    data: {
      name: 'User Management',
      docType: Doctypes.user,
    },
    loadChildren: () =>
      import('../pages/users/users.module').then((m) => m.UsersModule),
  },
  {
    path: 'users-details',
    data: {
      name: 'User Management',
    },
    loadChildren: () =>
      import('../pages/users/user-details/user-details.module').then(
        (m) => m.UserDetailsModule
      ),
  },
  {
    path: 'roles',
    data: {
      name: 'Role Management',
      docType: Doctypes.role,
    },
    loadChildren: () =>
      import('../pages/roles/roles.module').then((m) => m.RolesModule),
  },
  {
    path: 'permissions',
    data: {
      name: 'Permissions',
      docType: Doctypes.sacCodes,
    },
    loadChildren: () =>
      import('../pages/permissions/permissions.module').then(
        (m) => m.PermissionsModule
      ),
  },
  {
    path: 'reports',
    data: {
      name: 'Reports',
      docType: Doctypes.report,
    },
    loadChildren: () =>
      import('../pages/reports/reports.module').then((m) => m.ReportsModule),
  },

  {
    path: 'manual-credit-notes',
    data: {
      name: 'Manual Credit Notes',
    },
    loadChildren: () =>
      import('../pages/manual-credit-notes/manual-credit-notes.module').then(
        (m) => m.ManualCreditNotesModule
      ),
  },
  {
    path: 'manual-credit-details/:id',
    data: {
      name: 'Manual Credit Notes',
    },
    loadChildren: () => import('../pages/manual-credit-details/manual-credit-details.module').then(m => m.ManualCreditDetailsModule)
  },
{
  path: 'bench-logs',
  data:{
    name: 'Update Logs'
  },
  loadChildren:()=>import('../pages/bench-logs/bench-logs.module').then(m=>m.BenchLogsModule)
},
{
  path: 'bench-logs-info',
  data:{
    name: 'Update Logs'
  },
  loadChildren:()=>import('../pages/bench-logs/bench-log-details/bench-log-details.module').then(m=>m.BenchLogDetailsModule)
},
{
  path: 'document-bin',
  data:{
    name: 'Document Bin'
  },
  loadChildren:()=>import('../pages/document-bin/document-bin.module').then(m=>m.DocumentBinModule)
},{
  path:'upload-invoice',
  data:{
    name: 'Upload Invoices'
  },
  loadChildren:() => import('../pages/upload-invoices/upload-invoices.module').then(m=>m.UploadInvoicesModule)
},
{
  path:'deleted-documents',
  data:{
    name:'Deleted Documents'
  },
  loadChildren:() => import('../pages/deleted-documents/deleted-documents.module').then(m=>m.DeletedDocumentsModule)
},
{
  path:'email-logs',
  data:{
    name:'Email Logs'
  },
  loadChildren:() => import('../pages/email-logs/email-logs.module').then(m=>m.EmailLogsModule)
},
{
  path:'email-smtp',
  data:{
    name:'Email Settings'
  },
  loadChildren:() => import('../pages/email-settings/email-settings.module').then(m=>m.EmailSettingsModule)
},{
  path:'invoice-reconciliation',
  data:{
    name:'Simple Reconciliation'
  },
  loadChildren:() => import('../pages/invoice-reconcilation/invoice-reconcilation.module').then(m=>m.InvoiceReconcilationModule)
},{
  path:'gsp-metering',
  data:{
    name:'GSP Metering'
  },
  loadChildren:() => import('../pages/gsp-metering/gsp-metering.module').then(m=>m.GspMeteringModule)
},
{
  path: 'dashboard',
  data:{
    name:'Dashboard'
  },
  loadChildren: () =>
    import('../pages/dasboard-ui/dasboard-ui.module').then(
      (m) => m.DasboardUiModule
    ),
},
{
  path:'error-logs',
  data:{
    name:'Error Logs'
  },
  loadChildren:() => import('../pages/err-logs/err-logs.module').then(m=>m.ErrLogsModule)
},
{
  path:'pos-bills',
  data:{
    name:'POS Checks'
  },
  loadChildren:() => import('../pages/pos-bills/pos-bills/pos-bills.module').then(m=>m.PosBillsModule)
},
{
  path:'pos-bills-settings',
  data:{
    name:'Print Settings'
  },
  loadChildren:() => import('../pages/pos-bills/pos-settings/pos-settings.module').then(m=>m.PosSettingsModule)
},
{
  path:'outlets',
  data:{
    name:'Outlets'
  },
  loadChildren:() => import('../pages/pos-bills/outlets/outlets.module').then(m=>m.OutletsModule)
},
{
  path:'ip-printer',
  data:{
    name:'POS Printers'
  },
  loadChildren:() => import('../pages/pos-bills/ip-printers/ip-printers.module').then(m=>m.IpPrintersModule)
},
{
  path:'tablet',
  data:{
    name:'Tablets'
  },
  loadChildren:() => import('../pages/tab/tablet/tablet.module').then(m=>m.TabletModule)
},
{
  path:'work-stations',
  data:{name:'Work Stations'},
  loadChildren:() => import('../pages/tab/workstations/workstations.module').then(m=>m.WorkstationsModule)
},{
  path:'tablet-conf',
  data:{name:'Tablet Configurations'},
  loadChildren:() => import('../pages/tab/tablet-conf/tablet-conf.module').then(m=>m.TabletConfModule)
},
{
  path:'payment-reconciliation',
  data: { name:'Payment Reconciliation'},
  loadChildren:() => import('../pages/invoice-reconcilation/invoice-reconcilation.module').then(m => m.InvoiceReconcilationModule)
},
{
  path:'sync-history',
  data: { name:'Sync History'},
  loadChildren:() => import('../pages/sync-history/sync-history.module').then(m => m.SyncHistoryModule)
},{
  path:'invoice-recon',
  data: { name : 'Advanced Reconcilation'},
  loadChildren:() => import('../pages/invoice-recon/invoice-reconcilation-list/invoice-reconcilation-list.module').then(m=>m.InvoiceReconcilationListModule)
},
{
  path:'amend-invoices',
  data: { name : 'Amended Invoices'},
  loadChildren:() => import('../pages/amend-invoices/amend-invoices.module').then(m=>m.AmendInvoicesModule)
},

{
  path:'expired-invoices',
  data: { name : 'Invoices'},component: ExpiredInvoicesComponent
}

];
