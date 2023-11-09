import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PosBillsComponent } from './pos-bills.component';

describe('PosBillsComponent', () => {
  let component: PosBillsComponent;
  let fixture: ComponentFixture<PosBillsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PosBillsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PosBillsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
