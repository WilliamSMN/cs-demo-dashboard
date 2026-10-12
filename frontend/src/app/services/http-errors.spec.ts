import { TestBed } from '@angular/core/testing';
import { HttpErrors } from './http-errors';

describe('HttpErrors', () => {
  let service: HttpErrors;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(HttpErrors);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
