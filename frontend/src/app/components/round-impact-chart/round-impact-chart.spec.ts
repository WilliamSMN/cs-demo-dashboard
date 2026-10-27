import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RoundImpactChart } from './round-impact-chart';

describe('RoundImpactChart', () => {
  let component: RoundImpactChart;
  let fixture: ComponentFixture<RoundImpactChart>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoundImpactChart],
    }).compileComponents();

    fixture = TestBed.createComponent(RoundImpactChart);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
