export interface Content {
    query_sql?: string;
    query_result?: any;
    chart_base64?: string;
}
export interface Message {
    _id?: string;
    role: 'user' | 'assistant';
    content: string | Content;
    timestamp: Date;
}
export interface Conversation {
    _id?: string;
    messages: Message[];
    created_at?: Date;
    updated_at?: Date;
}
