import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkstationsComponent } from './workstations.component';

describe('WorkstationsComponent', () => {
  let component: WorkstationsComponent;
  let fixture: ComponentFixture<WorkstationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WorkstationsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WorkstationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
