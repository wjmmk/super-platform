import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { NxWelcome } from './nx-welcome';
import { AiService } from './ai.service';
import { JsonPipe } from '@angular/common';

@Component({
  imports: [NxWelcome, RouterModule, FormsModule, JsonPipe],
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected title = 'web-angular';
  invoiceId = 123;
  result: any = null;
  loading = false;

  // eslint-disable-next-line @angular-eslint/prefer-inject
  constructor(private aiService: AiService) {}

  analyze() {
    this.loading = true;

    this.aiService.analyze({ invoice: this.invoiceId }).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error:', err);
        this.loading = false;
      }
    });
  }
}
