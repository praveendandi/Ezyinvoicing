import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ErrLogsComponent } from './err-logs.component';

describe('ErrLogsComponent', () => {
  let component: ErrLogsComponent;
  let fixture: ComponentFixture<ErrLogsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ErrLogsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ErrLogsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
