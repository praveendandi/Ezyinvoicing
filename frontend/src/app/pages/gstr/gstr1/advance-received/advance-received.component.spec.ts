import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvanceReceivedComponent } from './advance-received.component';

describe('AdvanceReceivedComponent', () => {
  let component: AdvanceReceivedComponent;
  let fixture: ComponentFixture<AdvanceReceivedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdvanceReceivedComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdvanceReceivedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
