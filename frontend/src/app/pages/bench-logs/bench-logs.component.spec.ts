import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BenchLogsComponent } from './bench-logs.component';

describe('BenchLogsComponent', () => {
  let component: BenchLogsComponent;
  let fixture: ComponentFixture<BenchLogsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BenchLogsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BenchLogsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
