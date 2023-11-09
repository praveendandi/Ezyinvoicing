import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SummaryDetailsViewComponent } from './summary-details-view.component';

describe('SummaryDetailsViewComponent', () => {
  let component: SummaryDetailsViewComponent;
  let fixture: ComponentFixture<SummaryDetailsViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SummaryDetailsViewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SummaryDetailsViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
