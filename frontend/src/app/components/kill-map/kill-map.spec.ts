import { ComponentFixture, TestBed } from '@angular/core/testing';
import { KillMap } from './kill-map';

describe('KillMap', () => {
  let component: KillMap;
  let fixture: ComponentFixture<KillMap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [KillMap],
    }).compileComponents();

    fixture = TestBed.createComponent(KillMap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
