import type { ChartData } from '../types/api.type';

export class ChartService {
  static renderChart(chartData: ChartData): string {
    // Si tenemos una imagen base64, la retornamos directamente
    if (chartData.chart_image) {
      return chartData.chart_image;
    }

    return '';
  }

  static isValidChart(chartData: ChartData): boolean {
    return chartData.needs_chart && !!chartData.chart_image;
  }
}