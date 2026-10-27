import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DuelsCard } from './duels-card';

describe('DuelsCard', () => {
  let component: DuelsCard;
  let fixture: ComponentFixture<DuelsCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DuelsCard],
    }).compileComponents();

    fixture = TestBed.createComponent(DuelsCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
