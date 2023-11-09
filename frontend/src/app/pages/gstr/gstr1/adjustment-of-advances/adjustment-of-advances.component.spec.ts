import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdjustmentOfAdvancesComponent } from './adjustment-of-advances.component';

describe('AdjustmentOfAdvancesComponent', () => {
  let component: AdjustmentOfAdvancesComponent;
  let fixture: ComponentFixture<AdjustmentOfAdvancesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdjustmentOfAdvancesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdjustmentOfAdvancesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
