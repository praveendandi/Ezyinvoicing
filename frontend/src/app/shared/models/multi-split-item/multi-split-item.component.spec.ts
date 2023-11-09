import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MultiSplitItemComponent } from './multi-split-item.component';

describe('MultiSplitItemComponent', () => {
  let component: MultiSplitItemComponent;
  let fixture: ComponentFixture<MultiSplitItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MultiSplitItemComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MultiSplitItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
