import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AiService, AnalysisResult } from './ai.service';
import { JsonPipe } from '@angular/common';

@Component({
  imports: [RouterModule, FormsModule, JsonPipe],
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected title = 'web-angular';
  invoiceId = 123;
  result: AnalysisResult | null = null;
  loading = false;

  // eslint-disable-next-line @angular-eslint/prefer-inject
  constructor(private aiService: AiService) {}

  analyze() {
    this.loading = true;

    this.aiService.analyze({ invoice: this.invoiceId }).subscribe({
      next: (res: AnalysisResult) => {
        this.result = res;
        this.loading = false;
      },
      error: (err: unknown) => {
        console.error('Error:', err);
        this.loading = false;
      }
    });
  }
}
