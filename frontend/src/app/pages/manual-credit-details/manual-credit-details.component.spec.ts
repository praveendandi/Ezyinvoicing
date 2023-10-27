import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualCreditDetailsComponent } from './manual-credit-details.component';

describe('ManualCreditDetailsComponent', () => {
  let component: ManualCreditDetailsComponent;
  let fixture: ComponentFixture<ManualCreditDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ManualCreditDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManualCreditDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
