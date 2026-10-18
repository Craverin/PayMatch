import { Component } from '@angular/core'
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router'
import { Icon } from './shared/icon'

@Component({
  imports: [RouterLink, RouterLinkActive, RouterOutlet, Icon],
  selector: 'app-root',
  styleUrl: './app.scss',
  templateUrl: './app.html'
})
export class App {}
