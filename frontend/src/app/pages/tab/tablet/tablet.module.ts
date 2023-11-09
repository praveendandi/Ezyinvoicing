import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TabletRoutingModule } from './tablet-routing.module';
import { TabletComponent } from './tablet.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [TabletComponent],
  imports: [
    CommonModule,
    TabletRoutingModule,
    FormsModule
  ]
})
export class TabletModule { }
