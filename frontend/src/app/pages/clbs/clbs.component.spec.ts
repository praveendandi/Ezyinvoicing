import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ClbsComponent } from './clbs.component';

describe('ClbsComponent', () => {
  let component: ClbsComponent;
  let fixture: ComponentFixture<ClbsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ClbsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ClbsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
