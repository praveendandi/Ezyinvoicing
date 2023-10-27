import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TabletConfComponent } from './tablet-conf.component';

describe('TabletConfComponent', () => {
  let component: TabletConfComponent;
  let fixture: ComponentFixture<TabletConfComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TabletConfComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TabletConfComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
