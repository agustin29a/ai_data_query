import { useState, useCallback, useEffect } from 'react';
import type { Message, ChatState, ChatSession } from '../types';
import { ApiService } from '../services/api';
import { SessionService } from '../services/sessionService';

export const useChat = () => {
  const [chatState, setChatState] = useState<ChatState>({
    _id: Date.now().toString(),
    messages: [],
    isLoading: false,
    error: null,
    currentSessionId: null,
    isSidebarCollapsed: false,
  });
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  // Cargar sesiones al inicializar
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const sessions = await SessionService.getSessions();
      setSessions(sessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  }, []);

  const createNewSession = useCallback(async (userMessage: string) => {
    try {
      // Usar el nuevo servicio que crea sesión y procesa el mensaje
      const apiResponse = await ApiService.sendMessage(userMessage, undefined);
          // Crear mensaje del usuario
      const userMessageObj: Message = {
        _id: Date.now().toString(),
        content: userMessage,
        isUser: true,
        timestamp: new Date(),
      };

      // Crear mensaje del bot basado en la respuesta de la API
      const botMessage: Message = {
        _id: Date.now().toString(),
        content: {
          query_sql: apiResponse.sql_generado,
          chart_base64: apiResponse.chart ? apiResponse.chart.chart_image : '',
          query_result: apiResponse.resultados,
        },
        isUser: false,
        timestamp: new Date(),
        sql: apiResponse.sql_generado,    
      };

      setChatState(prev => ({
        ...prev,
        _id: apiResponse._id,
        messages: [userMessageObj, botMessage],
        isLoading: false,
        error: null,
        currentSessionId: apiResponse._id,
        isSidebarCollapsed: false,
      }));

      return apiResponse._id;

    } catch (error) {
      console.error('Error creating session with message:', error);
      throw error;
    }
  }, []);

  const sendMessageToExistingSession = useCallback(async (content: string, sessionId: string) => {
    try {
      // Enviar mensaje a la API existente
      const apiResponse = await ApiService.sendMessage(content, sessionId);

      const userMessage: Message = {
        _id: Date.now().toString(),
        content: apiResponse.pregunta,
        isUser: true,
        timestamp: new Date(),
      };

      // Crear mensaje del bot basado en la respuesta de la API
      const botMessage: Message = {
        _id: Date.now().toString(),
        content: {
          query_sql: apiResponse.sql_generado,
          chart_base64: apiResponse.chart ? apiResponse.chart.chart_image : '',
          query_result: apiResponse.resultados,
        },
        isUser: false,
        timestamp: new Date(),
        sql: apiResponse.sql_generado,    
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, userMessage, botMessage],
        isLoading: false,
      }));

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      const errorBotMessage: Message = {
        _id: (Date.now() + 1).toString(),
        content: `Error: ${errorMessage}`,
        isUser: false,
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorBotMessage],
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    setChatState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      if (chatState.currentSessionId) {
        // Sesión existente: enviar mensaje y guardar en la sesión
        await sendMessageToExistingSession(content, chatState.currentSessionId);
      } else {
        // Nueva sesión: crear sesión con el mensaje
        await createNewSession(content);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error sending message';
      
      const errorBotMessage: Message = {
        _id: (Date.now() + 1).toString(),
        content: `Error: ${errorMessage}`,
        isUser: false,
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorBotMessage],
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, [chatState.currentSessionId, createNewSession, sendMessageToExistingSession]);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await SessionService.deleteSession(sessionId);
      setChatState(prev => ({
        ...prev,
        currentSessionId: prev.currentSessionId === sessionId ? null : prev.currentSessionId,
        messages: prev.currentSessionId === sessionId ? [] : prev.messages,
      }));
      loadSessions();
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  }, []);

  const selectSession = useCallback(async (sessionId: string) => {
    try {
      const messagesSession = await SessionService.getSessionMessages(sessionId);
      
      const dataMessages: Message[] = messagesSession.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));

      setChatState(prev => ({
        ...prev,
        currentSessionId: sessionId,
        messages: dataMessages,
      }));
      loadSessions();
    } catch (error) {
      console.error('Error loading session messages:', error);
    }
  }, []);

  const toggleSidebar = useCallback(() => {
    setChatState(prev => ({ ...prev, isSidebarCollapsed: !prev.isSidebarCollapsed }));
  }, []);

  const handleNewSession = useCallback(() => {
    setChatState(prev => ({
      ...prev,
      currentSessionId: null,
      messages: [],
    }));

    loadSessions();
  }, []);

  return {
    messages: chatState.messages,
    isLoading: chatState.isLoading,
    error: chatState.error,
    currentSessionId: chatState.currentSessionId,
    isSidebarCollapsed: chatState.isSidebarCollapsed,
    sendMessage,
    createNewSession,
    deleteSession,
    selectSession,
    toggleSidebar,
    loadSessions,
    sessions, 
    handleNewSession// Exponer todo el estado de la sesión
  };
};