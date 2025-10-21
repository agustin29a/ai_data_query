import React from 'react';
import { ConfigProvider } from 'antd';
import { appTheme } from './theme/antd-theme.config';
import Chat from './components/Chat/Chat';

const App: React.FC = () => {
  return (

    <ConfigProvider theme={appTheme}>
      <Chat />
    </ConfigProvider>

  );
};

export default App;