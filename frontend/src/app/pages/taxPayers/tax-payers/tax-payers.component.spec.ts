import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TaxPayersComponent } from './tax-payers.component';

describe('TaxPayersComponent', () => {
  let component: TaxPayersComponent;
  let fixture: ComponentFixture<TaxPayersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TaxPayersComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TaxPayersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
