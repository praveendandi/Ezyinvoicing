import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Gstr2ReconciliationComponent } from './gstr2-reconciliation.component';

describe('Gstr2ReconciliationComponent', () => {
  let component: Gstr2ReconciliationComponent;
  let fixture: ComponentFixture<Gstr2ReconciliationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Gstr2ReconciliationComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Gstr2ReconciliationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
