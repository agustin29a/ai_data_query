export class CreateConversationDto {
  readonly messages?: MessageDto[];
  readonly title?: string;
}

export class MessageDto {
  readonly isUser: Boolean;
  readonly content: string | ContentDto;
  readonly timestamp?: Date;
}

export class ContentDto {
  readonly query_sql?: string;
  readonly query_result?: any;
  readonly chart_base64?: string;
}