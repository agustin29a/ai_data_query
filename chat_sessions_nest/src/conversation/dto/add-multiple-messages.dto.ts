import { ContentDto } from './add-message.dto';

export class AddMultipleMessagesDto {
  _id: string;
  messages: {
    isUser: boolean;
    content: string | ContentDto ;
    timestamp?: Date;
  }[];
}