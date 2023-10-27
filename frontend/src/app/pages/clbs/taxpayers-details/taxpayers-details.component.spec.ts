import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaxpayersDetailsComponent } from './taxpayers-details.component';

describe('TaxpayersDetailsComponent', () => {
  let component: TaxpayersDetailsComponent;
  let fixture: ComponentFixture<TaxpayersDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TaxpayersDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TaxpayersDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
