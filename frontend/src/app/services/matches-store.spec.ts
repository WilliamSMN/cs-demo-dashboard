import { TestBed } from '@angular/core/testing';
import { MatchesStore } from './matches-store';

describe('MatchesStore', () => {
  let service: MatchesStore;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MatchesStore);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
