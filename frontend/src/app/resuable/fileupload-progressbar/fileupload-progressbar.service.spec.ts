import { TestBed } from '@angular/core/testing';

import { FileuploadProgressbarService } from './fileupload-progressbar.service';

describe('FileuploadProgressbarService', () => {
  let service: FileuploadProgressbarService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FileuploadProgressbarService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
