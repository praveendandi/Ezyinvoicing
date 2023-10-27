import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentTypeDetailsComponent } from './payment-type-details.component';

describe('PaymentTypeDetailsComponent', () => {
  let component: PaymentTypeDetailsComponent;
  let fixture: ComponentFixture<PaymentTypeDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentTypeDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PaymentTypeDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
