import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UtilityCard } from './utility-card';

describe('UtilityCard', () => {
  let component: UtilityCard;
  let fixture: ComponentFixture<UtilityCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UtilityCard],
    }).compileComponents();

    fixture = TestBed.createComponent(UtilityCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
