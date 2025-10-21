import React from 'react';
import { Card, Tag, Space, Table } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import type { Message } from '../../types';
import ChartRenderer from '../Charts/ChartRenderer';
import { isContent } from '../../utils';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.isUser;

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      width: '100%'
    }}>
      <Card
        size="small"
        style={{
          maxWidth: '70%',
          background: isUser ? '#566778ff' : '#473e3eff',
          border: 'none',
          borderRadius: '12px',
        }}
        bodyStyle={{
          padding: '12px 16px',
          color: isUser ? 'white' : 'inherit'
        }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {isUser ? <UserOutlined /> : <RobotOutlined />}
            <span style={{ fontWeight: 'bold' }}>
              {isUser ? 'Usuario' : 'Asistente'}
            </span>
            <Tag color={isUser ? 'blue' : 'green'} style={{ margin: 0 }}>
              {message.timestamp?.toLocaleTimeString()}
            </Tag>
          </div>

          <div>
            {!isContent(message.content) && <p>{message.content}</p>}
          </div>

          {/* Mostrar SQL si existe */}
          {isContent(message.content) && (
            <Card size="small" title="Consulta SQL" style={{ marginTop: '8px' }}>
              <div style={{
                overflowX: 'auto',
                // Estilos para el scrollbar (Webkit/Chrome)
                scrollbarWidth: 'thin', // Firefox
                scrollbarColor: '#4a4a4a #2d2d2d', // Firefox (thumb track)
              }} className="custom-scrollbar">
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  customStyle={{
                    fontSize: '12px',
                    margin: 0,
                    overflowX: 'visible' // Dejamos que el div padre maneje el scroll
                  }}
                >
                  {message.content.query_sql}
                </SyntaxHighlighter>
              </div>
            </Card>
          )}
          
          {/* Mostrar datos tabulares si existen */}
          {
            (() => {
              const content = message.content;
              return isContent(content) && content && (
                <Card size="small" title="Results" style={{ marginTop: '8px' }}>
                  <Table
                    dataSource={content.query_result.data.map((row, index) => {
                      const rowData: Record<string, any> = { key: index };
                      content.query_result.columns.forEach((col, colIndex) => {
                        rowData[col] = row[colIndex];
                      });
                      return rowData;
                    })}
                    columns={content.query_result.columns.map((col) => ({
                      title: col,
                      dataIndex: col,
                      key: col,
                    }))}
                    size="small"
                    pagination={{
                      pageSize: 6,
                      showSizeChanger: false,
                      showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} registros`
                    }}
                    scroll={{ x: true }}
                  />
                </Card>
              );
            })()
          }

          {/* Mostrar gráfico si existe */}
          {isContent(message.content) && message.content.chart_base64 && (

            <ChartRenderer chartData={message.content.chart_base64} />

          )}

        </Space>
      </Card>
    </div>
  );
};

export default MessageBubble;