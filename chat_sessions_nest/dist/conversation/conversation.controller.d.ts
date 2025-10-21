import { ConversationsService } from '../conversation/conversation.service';
import { CreateConversationDto } from './dto/create-conversation.dto';
import { UpdateConversationDto } from './dto/update-conversation.dto';
import { AddMessageDto } from './dto/add-message.dto';
import { AddMultipleMessagesDto } from './dto/add-multiple-messages.dto';
import { FindConversationsQueryDto } from './dto/find-conversations-query.dto';
export declare class ConversationsController {
    private readonly conversationsService;
    constructor(conversationsService: ConversationsService);
    create(createConversationDto: CreateConversationDto): Promise<import("./schemas/conversation.schema").Conversation>;
    findAll(query: FindConversationsQueryDto): Promise<import("./schemas/conversation.schema").Conversation[]>;
    findOne(id: string): Promise<import("./schemas/conversation.schema").Conversation>;
    findBySessionId(session_id: string): Promise<import("./schemas/conversation.schema").Conversation>;
    update(id: string, updateConversationDto: UpdateConversationDto): Promise<import("./schemas/conversation.schema").Conversation>;
    remove(id: string): Promise<import("./schemas/conversation.schema").Conversation>;
    addMessage(addMessageDto: AddMessageDto): Promise<import("./schemas/conversation.schema").Conversation>;
    getConversationHistory(session_id: string): Promise<import("./schemas/conversation.schema").Conversation>;
    addMultipleMessages(addMultipleMessagesDto: AddMultipleMessagesDto): Promise<import("./schemas/conversation.schema").Conversation>;
}
