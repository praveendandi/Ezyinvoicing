import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformationInvoiceComponent } from './information-invoice.component';

describe('InformationInvoiceComponent', () => {
  let component: InformationInvoiceComponent;
  let fixture: ComponentFixture<InformationInvoiceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InformationInvoiceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InformationInvoiceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
