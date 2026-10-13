import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatchStats } from './match-stats';

describe('MatchStats', () => {
  let component: MatchStats;
  let fixture: ComponentFixture<MatchStats>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatchStats],
    }).compileComponents();

    fixture = TestBed.createComponent(MatchStats);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
