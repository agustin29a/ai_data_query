import React, { useEffect, useRef } from 'react';
import { List } from 'antd';
import type { Message } from '../../types';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div 
      ref={listRef}
      style={{ 
        flex: 1, 
        overflow: 'auto', 
        padding: '16px'
      }}
    >
      <List
        dataSource={messages}
        renderItem={(message) => (
          <List.Item style={{ border: 'none', padding: '8px 0' }}>
            <MessageBubble message={message} />
          </List.Item>
        )}
        locale={{ emptyText: 'Comienza una conversación...' }}
      />
    </div>
  );
};

export default MessageList;