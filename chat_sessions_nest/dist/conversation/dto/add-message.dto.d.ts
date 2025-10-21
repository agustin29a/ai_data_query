export declare class AddMessageDto {
    readonly _id: string;
    readonly isUser: Boolean;
    readonly content: string | ContentDto;
}
export declare class ContentDto {
    readonly query_sql?: string;
    readonly query_result?: any;
    readonly chart_base64?: string;
}
