import React from 'react';
import { Layout, Menu, Button, Typography, Space, Dropdown } from 'antd';
import { 
  MenuUnfoldOutlined, 
  MenuFoldOutlined, 
  PlusOutlined, 
  DeleteOutlined, 
  MoreOutlined,
  MessageOutlined 
} from '@ant-design/icons';
import type { ChatSession } from '../../types';

const { Sider } = Layout;
const { Text } = Typography;

interface SidebarProps {
  sessions: ChatSession [];
  currentSessionId: string | null;
  isCollapsed: boolean;
  onToggle: () => void;
  onNewSession: () => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  isCollapsed,
  onToggle,
  onNewSession,
  onSelectSession,
  onDeleteSession,
}) => {

  const menuItems = sessions.map(session => ({
    key: session._id,
    icon: <MessageOutlined />,
    label: (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text 
          ellipsis={{ tooltip: '' }} 
          style={{ 
            color: currentSessionId === session._id ? '#1890ff' : 'inherit',
            flex: 1 
          }}
        >
          {session.title || 'Consulta sin título'}
        </Text>
        <Dropdown
          menu={{
            items: [
              {
                key: 'delete',
                label: 'Eliminar',
                icon: <DeleteOutlined />,
                danger: true,
                onClick: (e) => {
                  e.domEvent.stopPropagation();
                  onDeleteSession(session._id);
                },
              },
            ],
          }}
          trigger={['click']}
        >
          <Button
            type="text"
            size="small"
            icon={<MoreOutlined />}
            onClick={(e) => e.stopPropagation()}
            style={{ marginLeft: 8 }}
          />
        </Dropdown>
      </div>
    ),
    onClick: () => onSelectSession(session._id),
  }));

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={isCollapsed}
      width={280}
      style={{
        borderRight: '1px solid #434343',
      }}
    >
      <div style={{ 
        padding: '16px', 
        borderBottom: '1px solid #434343',
        display: 'flex', 
        flexDirection: 'column',
        gap: '12px'
      }}>
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button
            type="text"
            icon={isCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={onToggle}
            style={{ color: 'white' }}
          />
        </Space>
        
        {!isCollapsed && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onNewSession}
            block
          >
            Nueva Consulta
          </Button>
        )}
      </div>

      {!isCollapsed && (
        <Menu
          mode="inline"
          selectedKeys={currentSessionId ? [currentSessionId] : []}
          items={menuItems}
          style={{ 
            background: '#1a1a1a',
            border: 'none',
            overflow: 'auto'
          }}
          theme="dark"
        />
      )}
    </Sider>
  );
};

export default Sidebar;