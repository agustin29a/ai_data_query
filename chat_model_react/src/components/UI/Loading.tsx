import React from 'react';
import { Spin, Space } from 'antd';

const Loading: React.FC = () => {
  return (
    <div style={{ 
      position: 'fixed', 
      top: '50%', 
      left: '50%', 
      transform: 'translate(-50%, -50%)',
      zIndex: 1000 
    }}>
      <Space size="middle">
        <Spin size="large" />
      </Space>
    </div>
  );
};

export default Loading;