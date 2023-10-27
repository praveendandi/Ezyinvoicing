import { Component, OnInit, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-multi-split-item',
  templateUrl: './multi-split-item.component.html',
  styleUrls: ['./multi-split-item.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MultiSplitItemComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

}
