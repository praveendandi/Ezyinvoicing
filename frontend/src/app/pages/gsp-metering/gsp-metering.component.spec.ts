import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GspMeteringComponent } from './gsp-metering.component';

describe('GspMeteringComponent', () => {
  let component: GspMeteringComponent;
  let fixture: ComponentFixture<GspMeteringComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GspMeteringComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GspMeteringComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
