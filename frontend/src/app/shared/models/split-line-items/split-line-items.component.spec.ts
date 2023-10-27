import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SplitLineItemsComponent } from './split-line-items.component';

describe('SplitLineItemsComponent', () => {
  let component: SplitLineItemsComponent;
  let fixture: ComponentFixture<SplitLineItemsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SplitLineItemsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SplitLineItemsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
