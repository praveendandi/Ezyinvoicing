import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DasboardUiComponent } from './dasboard-ui.component';

describe('DasboardUiComponent', () => {
  let component: DasboardUiComponent;
  let fixture: ComponentFixture<DasboardUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DasboardUiComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DasboardUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
