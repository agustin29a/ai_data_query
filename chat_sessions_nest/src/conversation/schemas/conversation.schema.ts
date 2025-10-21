// src/schemas/conversation.schema.ts
import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ConversationDocument = Conversation & Document;

@Schema()
export class Content {
  @Prop() query_sql?: string;
  @Prop({ type: Object }) query_result?: any;
  @Prop() chart_base64?: string;
}

export const ContentSchema = SchemaFactory.createForClass(Content);

@Schema()
export class Message {
  @Prop({ required: true })
  isUser: boolean;
  // Puede ser texto (para user) o Content (para assistant)
  @Prop({ type: Object, required: true })
  content: string | Content;

  @Prop({ default: Date.now })
  timestamp: Date;
}

export const MessageSchema = SchemaFactory.createForClass(Message);

@Schema({ timestamps: true })
export class Conversation {

  @Prop({ type: [MessageSchema], default: [] })
  messages: Message[];

  @Prop()
  title?: string;
}

export const ConversationSchema = SchemaFactory.createForClass(Conversation);
