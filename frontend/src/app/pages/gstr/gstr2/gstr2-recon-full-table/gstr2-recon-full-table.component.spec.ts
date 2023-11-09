import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Gstr2ReconFullTableComponent } from './gstr2-recon-full-table.component';

describe('Gstr2ReconFullTableComponent', () => {
  let component: Gstr2ReconFullTableComponent;
  let fixture: ComponentFixture<Gstr2ReconFullTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Gstr2ReconFullTableComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(Gstr2ReconFullTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
