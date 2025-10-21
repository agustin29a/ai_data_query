import React from 'react';
import { Layout } from 'antd';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import Loading from '../UI/Loading';
import Sidebar from '../Sidebar/Sidebar';
import './Chat.css';

const { Content } = Layout;

const Chat: React.FC = () => {
  const {
    messages,
    isLoading,
    sessions,
    currentSessionId,
    isSidebarCollapsed,
    sendMessage,
    deleteSession,
    selectSession,
    toggleSidebar,
    handleNewSession
  } = useChat();

  return (
    <Layout style={{ height: '100vh', overflow: 'hidden' }}> 
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        isCollapsed={isSidebarCollapsed}
        onToggle={toggleSidebar}
        onNewSession={handleNewSession}
        onSelectSession={selectSession}
        onDeleteSession={deleteSession}
      />

      <Layout>
        <Content
          style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            overflowY: 'hidden', 
          }}
        >
    
          <div
            style={{
              flex: 1, 
              display: 'flex',
              flexDirection: 'column',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              background: '#1a1a1a',
              minHeight: 0,
            }}
          >
        
            <div
              className="chat-scroll"
              style={{
                flex: 1, 
                overflowY: 'auto',
                padding: '16px',
                minHeight: 0,
              }}
            >
              <MessageList messages={messages} />
            </div>

        
            <div
              style={{
                padding: '16px',
                borderTop: '1px solid #434343',
                flexShrink: 0,
              }}
            >
              <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
            </div>
          </div>

          {isLoading && <Loading />}
        </Content>
      </Layout>
    </Layout>
  );
};

export default Chat;