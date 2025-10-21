import React from 'react';
import { Card } from 'antd';


interface ChartRendererProps {
  chartData: string;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData }) => {
  const renderChart = () => {
    
      return (
        <img 
          src={chartData} 
          alt="Chart" 
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      );

  };

  return (
    <Card size="small" title="Gráfico" style={{ marginTop: '8px' }}>
      {renderChart()}
    </Card>
  );
};

export default ChartRenderer;