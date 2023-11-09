import { TestBed } from '@angular/core/testing';

import { SearchByInputService } from './search-by-input.service';

describe('SearchByInputService', () => {
  let service: SearchByInputService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SearchByInputService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
