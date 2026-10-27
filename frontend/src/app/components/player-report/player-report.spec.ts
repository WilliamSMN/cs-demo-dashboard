import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PlayerReport } from './player-report';

describe('PlayerReport', () => {
  let component: PlayerReport;
  let fixture: ComponentFixture<PlayerReport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlayerReport],
    }).compileComponents();

    fixture = TestBed.createComponent(PlayerReport);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
