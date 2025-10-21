import { Model } from 'mongoose';
import { Conversation, ConversationDocument } from './schemas/conversation.schema';
import { CreateConversationDto } from './dto/create-conversation.dto';
import { UpdateConversationDto } from './dto/update-conversation.dto';
import { AddMessageDto } from './dto/add-message.dto';
import { AddMultipleMessagesDto } from './dto/add-multiple-messages.dto';
import { FindConversationsQueryDto } from './dto/find-conversations-query.dto';
export declare class ConversationsService {
    private conversationModel;
    constructor(conversationModel: Model<ConversationDocument>);
    create(createConversationDto: CreateConversationDto): Promise<Conversation>;
    findAll(query: FindConversationsQueryDto): Promise<Conversation[]>;
    findOne(id: string): Promise<Conversation>;
    findBySessionId(session_id: string): Promise<Conversation>;
    update(id: string, updateConversationDto: UpdateConversationDto): Promise<Conversation>;
    remove(id: string): Promise<Conversation>;
    addMessage(addMessageDto: AddMessageDto): Promise<Conversation>;
    getConversationHistory(session_id: string): Promise<Conversation>;
    addMultipleMessages(addMultipleMessagesDto: AddMultipleMessagesDto): Promise<Conversation>;
}
