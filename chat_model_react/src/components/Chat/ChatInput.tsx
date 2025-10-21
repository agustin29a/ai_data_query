import React, { useState } from 'react';
import { Input, Button, Space } from 'antd';
import { SendOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Space.Compact style={{ width: '100%' }}>
      <TextArea
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Realizá tu conulta..."
        autoSize={{ minRows: 1, maxRows: 4 }}
        disabled={isLoading}
        style={{ borderRadius: '6px 0 0 6px' }}
      />
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={handleSend}
        loading={isLoading}
        style={{ borderRadius: '0 6px 6px 0', height: 'auto' }}
      >
        Enviar
      </Button>
    </Space.Compact>
  );
};

export default ChatInput;