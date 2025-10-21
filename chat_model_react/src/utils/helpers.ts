import type { Content } from '../types/chat.type';

export const isContent = (value: any): value is Content =>
  value && typeof value === 'object' && 'query_sql' in value;
