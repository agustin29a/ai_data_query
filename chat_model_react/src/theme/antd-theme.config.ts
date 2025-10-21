// theme/antd-theme.config.ts
import type { ThemeConfig } from 'antd';
import { theme } from 'antd';

export const appTheme: ThemeConfig = {
    algorithm: theme.darkAlgorithm,
    token: {
        colorPrimary: '#1890ff',
        colorBgBase: '#0f0f0f',
        colorBgContainer: '#1a1a1a',
        colorBgElevated: '#262626',
        colorBorder: '#434343',
        colorTextSecondary: 'rgba(255, 255, 255, 0.65)',
        colorTextTertiary: 'rgba(255, 255, 255, 0.45)',
        borderRadius: 8,
        wireframe: false,
    },
    components: {
        Layout: {
            bodyBg: '#0f0f0f',
            headerBg: '#1a1a1a',
            siderBg: '#1a1a1a',
        },
        Card: {
            colorBgContainer: '#1a1a1a',
            colorBorderSecondary: '#434343',
        },
        Input: {
            colorBgContainer: '#262626',
            colorBorder: '#434343',
            colorText: '#ffffff',
        },
        Button: {
            colorBgContainer: '#1890ff',
            colorText: '#ffffff',
        },
    },
};