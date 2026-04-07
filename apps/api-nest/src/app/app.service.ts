import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { firstValueFrom } from 'rxjs';

@Injectable()
export class AppService {

  getData(): { message: string } {
    return { message: 'Hello API' };
  }

  async analyze(data: any) {
    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`Error en la petición: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new InternalServerErrorException('Error conectando con el servicio de IA');
    }
  }
}
