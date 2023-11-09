import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RetPeriodComponent } from './ret-period.component';

describe('RetPeriodComponent', () => {
  let component: RetPeriodComponent;
  let fixture: ComponentFixture<RetPeriodComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RetPeriodComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RetPeriodComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
