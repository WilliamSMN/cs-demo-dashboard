import { Component, inject } from '@angular/core';
import { PlayerReport } from '../../components/player-report/player-report';
import { RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';

interface Step {
  title: string;
  text: string;
}

@Component({
  imports: [PlayerReport, RouterLink],
  selector: 'app-home-page',
  styleUrl: './home-page.scss',
  templateUrl: './home-page.html',
})
export class HomePage {
  protected readonly auth = inject(Auth);

  protected readonly steps: Step[] = [
    { title: 'Get your demo', text: 'Find the folder with Your Matches, and download the replay of the match you want to analyze (a .dem file).' },
    { title: 'Sign in and upload', text: 'Sign in with Steam, then upload the .dem file from the matches page. The analysis runs in the background.' },
    { title: 'Read your report', text: 'Scoreboard, utility, trades, clutches, and a full player report with charts and maps.' },
  ];

  protected scrollToDemo() {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.getElementById('demo')?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  }
}
