import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BenchLogDetailsComponent } from './bench-log-details.component';

describe('BenchLogDetailsComponent', () => {
  let component: BenchLogDetailsComponent;
  let fixture: ComponentFixture<BenchLogDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BenchLogDetailsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BenchLogDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
