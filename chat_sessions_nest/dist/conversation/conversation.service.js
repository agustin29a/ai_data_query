"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConversationsService = void 0;
const common_1 = require("@nestjs/common");
const mongoose_1 = require("@nestjs/mongoose");
const mongoose_2 = require("mongoose");
const conversation_schema_1 = require("./schemas/conversation.schema");
let ConversationsService = class ConversationsService {
    constructor(conversationModel) {
        this.conversationModel = conversationModel;
    }
    async create(createConversationDto) {
        const createdConversation = new this.conversationModel(createConversationDto);
        return createdConversation.save();
    }
    async findAll(query) {
        const { sortByDate } = query;
        let sortQuery = this.conversationModel.find();
        if (sortByDate) {
            const sortOrder = sortByDate === 'asc' || sortByDate === '1' ? 1 : -1;
            sortQuery = sortQuery.sort({ createdAt: sortOrder });
        }
        return sortQuery.exec();
    }
    async findOne(id) {
        return this.conversationModel.findById(id).exec();
    }
    async findBySessionId(session_id) {
        return this.conversationModel.findOne({ session_id }).exec();
    }
    async update(id, updateConversationDto) {
        return this.conversationModel
            .findByIdAndUpdate(id, updateConversationDto, { new: true })
            .exec();
    }
    async remove(id) {
        return this.conversationModel.findByIdAndDelete(id).exec();
    }
    async addMessage(addMessageDto) {
        const { _id, isUser, content } = addMessageDto;
        const message = {
            isUser,
            content,
            timestamp: new Date(),
        };
        return this.conversationModel
            .findOneAndUpdate({ _id }, { $push: { messages: message } }, { new: true, upsert: true })
            .exec();
    }
    async getConversationHistory(session_id) {
        return this.conversationModel
            .findOne({ session_id })
            .select('messages')
            .exec();
    }
    async addMultipleMessages(addMultipleMessagesDto) {
        const { _id, messages } = addMultipleMessagesDto;
        const messagesWithTimestamp = messages.map(message => ({
            ...message,
            timestamp: message.timestamp || new Date(),
        }));
        return this.conversationModel
            .findOneAndUpdate({ _id }, {
            $push: {
                messages: {
                    $each: messagesWithTimestamp
                }
            }
        }, { new: true, upsert: true })
            .exec();
    }
};
exports.ConversationsService = ConversationsService;
exports.ConversationsService = ConversationsService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, mongoose_1.InjectModel)(conversation_schema_1.Conversation.name)),
    __metadata("design:paramtypes", [mongoose_2.Model])
], ConversationsService);
//# sourceMappingURL=conversation.service.js.map