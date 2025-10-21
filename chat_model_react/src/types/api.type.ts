export interface ChartData {
  chart_code: string;
  chart_image: string;
  chart_type: string;
  needs_chart: boolean;
}

export interface ResultData {
  columns: string[];
  data: any[][];
}

export interface ApiResponse {
  chart?: ChartData;
  pregunta: string;
  resultados: ResultData;
  sql_generado: string;
  status: 'success' | 'error';
  _id: string
}



