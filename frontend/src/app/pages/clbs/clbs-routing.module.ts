import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ClbsReportsComponent } from './clbs-reports/clbs-reports.component';

import { ClbsComponent } from './clbs.component';
import { ContactsComponent } from './contacts/contacts.component';
import { CreateContactComponent } from './create-contact/create-contact.component';
import { CreateSummaryComponent } from './create-summary/create-summary.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DocumentTypesComponent } from './document-types/document-types.component';
import { EventsComponent } from './events/events.component';
import { InvoicesComponent } from './invoices/invoices.component';
import { SettingsComponent } from './settings/settings.component';
import { SummariesComponent } from './summaries/summaries.component';
import { SummaryDetailsViewComponent } from './summary-details-view/summary-details-view.component';
import { SummaryDetailsComponent } from './summary-details/summary-details.component';
import { TaxpayersDetailsComponent } from './taxpayers-details/taxpayers-details.component';
import { TaxpayersComponent } from './taxpayers/taxpayers.component';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'summaries',
    pathMatch: 'full',
  },
  {
    path: '',
    component: ClbsComponent,
    children: [
      // {
      //   path: 'dashboard',
      //   component: DashboardComponent,
      // },
      {
        path: 'summaries',
        component: SummariesComponent,
      },
      {
        path: 'contacts',
        component: ContactsComponent,
      }, {
        path: 'taxpayers',
        component: TaxpayersComponent
      },
      {
        path: 'clbs-reports',
        component: ClbsReportsComponent,
      }, {
        path: 'events',
        component: EventsComponent
      },{
        path:'clbs-settings',
        component: SettingsComponent
      },
      {
        path:'document-type',
        component: DocumentTypesComponent
      }
    ]
  },
  {
    path: 'create-summary',
    component: CreateSummaryComponent,
  },
  {
    path: 'summary-details/:id',
    component: SummaryDetailsComponent,
  },
  {
    path: 'summary-details-view',
    component: SummaryDetailsViewComponent,
  },
  {
    path: 'create-contact',
    component: CreateContactComponent,
  },
  {
    path: 'invoices/:id',
    component: InvoicesComponent,
  }, {
    path: 'taxpayer-details',
    component: TaxpayersDetailsComponent,
  }

];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ClbsRoutingModule { }
