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
exports.ConversationsController = void 0;
const common_1 = require("@nestjs/common");
const conversation_service_1 = require("../conversation/conversation.service");
const create_conversation_dto_1 = require("./dto/create-conversation.dto");
const update_conversation_dto_1 = require("./dto/update-conversation.dto");
const add_message_dto_1 = require("./dto/add-message.dto");
const add_multiple_messages_dto_1 = require("./dto/add-multiple-messages.dto");
const find_conversations_query_dto_1 = require("./dto/find-conversations-query.dto");
let ConversationsController = class ConversationsController {
    constructor(conversationsService) {
        this.conversationsService = conversationsService;
    }
    create(createConversationDto) {
        return this.conversationsService.create(createConversationDto);
    }
    findAll(query) {
        return this.conversationsService.findAll(query);
    }
    findOne(id) {
        return this.conversationsService.findOne(id);
    }
    findBySessionId(session_id) {
        return this.conversationsService.findBySessionId(session_id);
    }
    update(id, updateConversationDto) {
        return this.conversationsService.update(id, updateConversationDto);
    }
    remove(id) {
        return this.conversationsService.remove(id);
    }
    addMessage(addMessageDto) {
        return this.conversationsService.addMessage(addMessageDto);
    }
    getConversationHistory(session_id) {
        return this.conversationsService.getConversationHistory(session_id);
    }
    async addMultipleMessages(addMultipleMessagesDto) {
        return this.conversationsService.addMultipleMessages(addMultipleMessagesDto);
    }
};
exports.ConversationsController = ConversationsController;
__decorate([
    (0, common_1.Post)(),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [create_conversation_dto_1.CreateConversationDto]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "create", null);
__decorate([
    (0, common_1.Get)(),
    __param(0, (0, common_1.Query)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [find_conversations_query_dto_1.FindConversationsQueryDto]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "findAll", null);
__decorate([
    (0, common_1.Get)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "findOne", null);
__decorate([
    (0, common_1.Get)('session/:session_id'),
    __param(0, (0, common_1.Param)('session_id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "findBySessionId", null);
__decorate([
    (0, common_1.Patch)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, update_conversation_dto_1.UpdateConversationDto]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "update", null);
__decorate([
    (0, common_1.Delete)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "remove", null);
__decorate([
    (0, common_1.Post)('message'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [add_message_dto_1.AddMessageDto]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "addMessage", null);
__decorate([
    (0, common_1.Get)('history/:session_id'),
    __param(0, (0, common_1.Param)('session_id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], ConversationsController.prototype, "getConversationHistory", null);
__decorate([
    (0, common_1.Post)('multiple-messages'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [add_multiple_messages_dto_1.AddMultipleMessagesDto]),
    __metadata("design:returntype", Promise)
], ConversationsController.prototype, "addMultipleMessages", null);
exports.ConversationsController = ConversationsController = __decorate([
    (0, common_1.Controller)('conversations'),
    __metadata("design:paramtypes", [conversation_service_1.ConversationsService])
], ConversationsController);
//# sourceMappingURL=conversation.controller.js.map