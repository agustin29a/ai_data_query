import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Conversation, ConversationDocument } from './schemas/conversation.schema';
import { CreateConversationDto } from './dto/create-conversation.dto';
import { UpdateConversationDto } from './dto/update-conversation.dto';
import { AddMessageDto } from './dto/add-message.dto';
import { AddMultipleMessagesDto } from './dto/add-multiple-messages.dto';
import { FindConversationsQueryDto } from './dto/find-conversations-query.dto';

@Injectable()
export class ConversationsService {
  constructor(
    @InjectModel(Conversation.name)
    private conversationModel: Model<ConversationDocument>,
  ) { }

  async create(createConversationDto: CreateConversationDto): Promise<Conversation> {
    const createdConversation = new this.conversationModel(createConversationDto);
    return createdConversation.save();
  }

  async findAll(query: FindConversationsQueryDto): Promise<Conversation[]> {
    const { sortByDate } = query;

    let sortQuery = this.conversationModel.find();

    if (sortByDate) {
      const sortOrder = sortByDate === 'asc' || sortByDate === '1' ? 1 : -1;
      sortQuery = sortQuery.sort({ createdAt: sortOrder });
    }

    return sortQuery.exec();
  }

  async findOne(id: string): Promise<Conversation> {
    return this.conversationModel.findById(id).exec();
  }

  async findBySessionId(session_id: string): Promise<Conversation> {
    return this.conversationModel.findOne({ session_id }).exec();
  }

  async update(id: string, updateConversationDto: UpdateConversationDto): Promise<Conversation> {
    return this.conversationModel
      .findByIdAndUpdate(id, updateConversationDto, { new: true })
      .exec();
  }

  async remove(id: string): Promise<Conversation> {
    return this.conversationModel.findByIdAndDelete(id).exec();
  }

  async addMessage(addMessageDto: AddMessageDto): Promise<Conversation> {
    const { _id, isUser, content } = addMessageDto;

    const message = {
      isUser,
      content,
      timestamp: new Date(),
    };

    return this.conversationModel
      .findOneAndUpdate(
        { _id },
        { $push: { messages: message } },
        { new: true, upsert: true }
      )
      .exec();
  }

  async getConversationHistory(session_id: string): Promise<Conversation> {
    return this.conversationModel
      .findOne({ session_id })
      .select('messages')
      .exec();
  }

  async addMultipleMessages(addMultipleMessagesDto: AddMultipleMessagesDto): Promise<Conversation> {
    const { _id, messages } = addMultipleMessagesDto;

    // Preparar los mensajes con timestamp si no viene
    const messagesWithTimestamp = messages.map(message => ({
      ...message,
      timestamp: message.timestamp || new Date(),
    }));

    return this.conversationModel
      .findOneAndUpdate(
        { _id },
        {
          $push: {
            messages: {
              $each: messagesWithTimestamp
            }
          }
        },
        { new: true, upsert: true }
      )
      .exec();
  }
}