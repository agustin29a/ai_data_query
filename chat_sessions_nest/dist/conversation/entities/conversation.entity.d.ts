export declare class Conversation {
    id: string;
    userId: string;
    userQuery: string;
    generatedSQL: string;
    queryResult: any;
    chartBase64?: string;
    chartType?: string;
    hasChart: boolean;
    timestamp: Date;
    createdAt: Date;
    updatedAt: Date;
}
