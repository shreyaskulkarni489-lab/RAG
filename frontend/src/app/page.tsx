'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/lib/auth-context';
import { ChatMessage, Conversation } from '@/types';
import { SourceCard } from '@/components/Chat/SourceCard';
import { SuggestedQuestions } from '@/components/Chat/SuggestedQuestions';
import { Send, ThumbsUp, ThumbsDown, Bot, User as UserIcon, Plus, MessageSquare, Loader2 } from 'lucide-react';

export default function ChatPage() {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (token) {
      fetchConversations();
    }
  }, [token]);

  useEffect(() => {
    if (currentConvId && token) {
      fetchConversationHistory(currentConvId);
    }
  }, [currentConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const fetchConversations = async () => {
    try {
      const res = await fetch('/api/chat/conversations', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchConversationHistory = async (convId: string) => {
    try {
      const res = await fetch(`/api/chat/conversations/${convId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSendMessage = async (questionText?: string) => {
    const text = questionText || inputQuestion;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          question: text,
          conversation_id: currentConvId
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Error getting response');

      if (!currentConvId && data.conversation_id) {
        setCurrentConvId(data.conversation_id);
        fetchConversations();
      }

      const asstMsg: ChatMessage = {
        id: data.id,
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        created_at: new Date().toISOString()
      };

      setMessages((prev) => [...prev, asstMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        role: 'assistant',
        content: `Error: ${err.message || 'Unable to fetch response.'}`,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (msgId: string | undefined, feedback: 'up' | 'down') => {
    if (!msgId || !token) return;
    try {
      await fetch(`/api/chat/message/${msgId}/feedback?feedback=${feedback}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, feedback } : m))
      );
    } catch (e) {
      console.error(e);
    }
  };

  const startNewChat = () => {
    setCurrentConvId(null);
    setMessages([]);
  };

  return (
    <div className="flex flex-1 h-[calc(100vh-4rem)] overflow-hidden bg-slate-50">
      {/* Sidebar - Conversation History */}
      <aside className="w-64 border-r border-slate-200 bg-white flex flex-col hidden md:flex">
        <div className="p-3 border-b border-slate-200">
          <button
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-blue-50 text-blue-700 font-medium text-xs rounded-xl border border-blue-200 hover:bg-blue-100 transition"
          >
            <Plus className="w-4 h-4" />
            New Conversation
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <div className="text-[11px] font-semibold text-slate-400 px-3 py-1 uppercase tracking-wider">
            Past Chats
          </div>
          {conversations.length === 0 ? (
            <div className="text-xs text-slate-400 p-3 text-center">No past chats yet</div>
          ) : (
            conversations.map((c) => (
              <button
                key={c.id}
                onClick={() => setCurrentConvId(c.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center gap-2 truncate transition ${
                  currentConvId === c.id
                    ? 'bg-blue-600 text-white font-medium shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate">{c.title}</span>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full bg-slate-50">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {messages.length === 0 ? (
            <SuggestedQuestions onSelect={(q) => handleSendMessage(q)} />
          ) : (
            messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-3 max-w-3xl ${
                  m.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white shadow-sm ${
                    m.role === 'user' ? 'bg-slate-700' : 'bg-blue-600'
                  }`}
                >
                  {m.role === 'user' ? <UserIcon className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`rounded-2xl p-4 text-sm shadow-sm ${
                    m.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>

                  {/* Sources Component */}
                  {m.sources && m.sources.length > 0 && <SourceCard sources={m.sources} />}

                  {/* Feedback buttons */}
                  {m.role === 'assistant' && (
                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-slate-100">
                      <span className="text-[10px] text-slate-400">Was this helpful?</span>
                      <button
                        onClick={() => handleFeedback(m.id, 'up')}
                        className={`p-1 rounded hover:bg-slate-100 ${
                          m.feedback === 'up' ? 'text-green-600 font-bold' : 'text-slate-400'
                        }`}
                      >
                        <ThumbsUp className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => handleFeedback(m.id, 'down')}
                        className={`p-1 rounded hover:bg-slate-100 ${
                          m.feedback === 'down' ? 'text-red-600 font-bold' : 'text-slate-400'
                        }`}
                      >
                        <ThumbsDown className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="flex gap-3 max-w-3xl mr-auto items-center">
              <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-none text-xs text-slate-500 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                Retrieving college documents & generating verified answer...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 bg-white border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="max-w-3xl mx-auto flex gap-2"
          >
            <input
              type="text"
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              placeholder="Ask a question about admissions, fees, hostel, exams..."
              className="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-sm"
            />
            <button
              type="submit"
              disabled={loading || !inputQuestion.trim()}
              className="px-4 py-2.5 bg-blue-600 text-white rounded-xl font-medium text-sm hover:bg-blue-700 transition flex items-center justify-center shadow-md shadow-blue-600/20 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
