import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualCreditNotesComponent } from './manual-credit-notes.component';

describe('ManualCreditNotesComponent', () => {
  let component: ManualCreditNotesComponent;
  let fixture: ComponentFixture<ManualCreditNotesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ManualCreditNotesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManualCreditNotesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
