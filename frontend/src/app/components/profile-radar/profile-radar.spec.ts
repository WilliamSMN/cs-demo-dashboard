import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProfileRadar } from './profile-radar';

describe('ProfileRadar', () => {
  let component: ProfileRadar;
  let fixture: ComponentFixture<ProfileRadar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfileRadar],
    }).compileComponents();

    fixture = TestBed.createComponent(ProfileRadar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
