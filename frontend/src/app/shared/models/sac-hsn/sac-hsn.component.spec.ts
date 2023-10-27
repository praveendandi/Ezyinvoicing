import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SacHsnComponent } from './sac-hsn.component';

describe('SacHsnComponent', () => {
  let component: SacHsnComponent;
  let fixture: ComponentFixture<SacHsnComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SacHsnComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SacHsnComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
