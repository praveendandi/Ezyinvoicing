import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TabletConfRoutingModule } from './tablet-conf-routing.module';
import { TabletConfComponent } from './tablet-conf.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [TabletConfComponent],
  imports: [
    CommonModule,
    TabletConfRoutingModule,
    FormsModule
  ]
})
export class TabletConfModule { }
