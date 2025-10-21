import { Controller, Get, Post, Body, Patch, Param, Delete, Query } from '@nestjs/common';
import { ConversationsService } from '../conversation/conversation.service';
import { CreateConversationDto } from './dto/create-conversation.dto';
import { UpdateConversationDto } from './dto/update-conversation.dto';
import { AddMessageDto } from './dto/add-message.dto';
import { AddMultipleMessagesDto } from './dto/add-multiple-messages.dto';
import { FindConversationsQueryDto } from './dto/find-conversations-query.dto';

@Controller('conversations')
export class ConversationsController {
  constructor(private readonly conversationsService: ConversationsService) {}

  @Post()
  create(@Body() createConversationDto: CreateConversationDto) {
    return this.conversationsService.create(createConversationDto);
  }

  @Get()
  findAll(@Query() query: FindConversationsQueryDto) {
    return this.conversationsService.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.conversationsService.findOne(id);
  }

  @Get('session/:session_id')
  findBySessionId(@Param('session_id') session_id: string) {
    return this.conversationsService.findBySessionId(session_id);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() updateConversationDto: UpdateConversationDto) {
    return this.conversationsService.update(id, updateConversationDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.conversationsService.remove(id);
  }

  @Post('message')
  addMessage(@Body() addMessageDto: AddMessageDto) {
    return this.conversationsService.addMessage(addMessageDto);
  }

  @Get('history/:session_id')
  getConversationHistory(@Param('session_id') session_id: string) {
    return this.conversationsService.getConversationHistory(session_id);
  }

  @Post('multiple-messages')
  async addMultipleMessages(@Body() addMultipleMessagesDto: AddMultipleMessagesDto) {
    return this.conversationsService.addMultipleMessages(addMultipleMessagesDto);
}
}