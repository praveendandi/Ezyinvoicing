import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { EmailLogsRoutingModule } from './email-logs-routing.module';
import { EmailLogsComponent } from './email-logs.component';
import { FormsModule } from '@angular/forms';
import { VirtualScrollerModule } from 'ngx-virtual-scroller';


@NgModule({
  declarations: [EmailLogsComponent],
  imports: [
    CommonModule,
    EmailLogsRoutingModule,
    FormsModule,
    VirtualScrollerModule
    
  ]
})
export class EmailLogsModule { }
