import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClbsReportsComponent } from './clbs-reports.component';

describe('ClbsReportsComponent', () => {
  let component: ClbsReportsComponent;
  let fixture: ComponentFixture<ClbsReportsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClbsReportsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClbsReportsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
