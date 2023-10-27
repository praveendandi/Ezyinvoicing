import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaxPayersDetailsComponent } from './tax-payers-details.component';

describe('TaxPayersDetailsComponent', () => {
  let component: TaxPayersDetailsComponent;
  let fixture: ComponentFixture<TaxPayersDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TaxPayersDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TaxPayersDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
