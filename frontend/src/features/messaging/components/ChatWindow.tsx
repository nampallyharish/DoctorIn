"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Send, ShieldCheck, Lock, ArrowLeft } from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { ConversationResponse, MessageResponse } from "@/types";

interface ChatWindowProps {
  conversationId: string;
  conversation?: ConversationResponse;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  conversationId,
  conversation,
}) => {
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchMessages = async () => {
    setIsLoading(true);
    const res = await apiClient.get<MessageResponse[]>(`/conversations/${conversationId}/messages`);
    setIsLoading(false);
    if (res.success && res.data) {
      setMessages(res.data);
      setTimeout(scrollToBottom, 100);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, [conversationId]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setIsSending(true);
    const content = inputText.trim();
    setInputText("");

    const res = await apiClient.post<MessageResponse>(`/conversations/${conversationId}/messages`, {
      content,
      message_type: "text",
    });

    setIsSending(false);

    if (res.success && res.data) {
      setMessages((prev) => [...prev, res.data as MessageResponse]);
      setTimeout(scrollToBottom, 50);
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col h-[650px] overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-3">
          <Link href="/messages" className="lg:hidden text-slate-400 hover:text-slate-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>

          {conversation?.participant && (
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-teal-600 text-white font-bold text-sm flex items-center justify-center shadow shrink-0">
                {conversation.participant.full_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
              </div>
              <div>
                <div className="flex items-center gap-1.5 font-bold text-slate-900 text-xs">
                  <span>{conversation.participant.full_name}</span>
                  <VerifiedBadge size="sm" />
                </div>
                <p className="text-[11px] text-teal-700 font-medium">
                  {conversation.participant.headline || "Verified Medical Specialist"}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full font-semibold border border-emerald-200">
          <Lock className="w-3 h-3 text-emerald-600" />
          <span>Doctor-to-Doctor Encrypted</span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/30">
        {isLoading ? (
          <div className="text-center py-20 text-xs text-slate-400">Loading conversation history...</div>
        ) : messages.length === 0 ? (
          <div className="text-center py-20 text-xs text-slate-400 space-y-1">
            <p className="font-semibold text-slate-700">Encrypted Consultation Channel</p>
            <p>Send a message to discuss patient case referrals or research collaboration.</p>
          </div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`flex flex-col ${m.is_self ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed shadow-sm ${
                  m.is_self
                    ? "bg-teal-600 text-white rounded-br-none"
                    : "bg-white text-slate-800 border border-slate-200 rounded-bl-none"
                }`}
              >
                {m.content}
              </div>
              <span className="text-[10px] text-slate-400 px-1 pt-0.5">
                {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input Box */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-100 flex gap-2 bg-white">
        <input
          type="text"
          required
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type a clinical note or message..."
          className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
        <Button type="submit" variant="primary" size="sm" isLoading={isSending} disabled={!inputText.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </form>
    </div>
  );
};
