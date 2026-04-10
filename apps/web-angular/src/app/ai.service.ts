import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface AnalysisRequest {
  invoice: number;
}

export interface AnalysisResult {
  invoiceId: number;
  riskScore: number;
  status: string;
  timestamp: string;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class AiService {

  // eslint-disable-next-line @angular-eslint/prefer-inject
  constructor(private http: HttpClient) {}

  analyze(data: AnalysisRequest) {
    console.log('Enviando datos al backend:', data);
    return this.http.post<AnalysisResult>('http://localhost:3000/api/analyze', data);
  }
}