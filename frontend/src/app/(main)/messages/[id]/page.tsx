"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ConversationList } from "@/features/messaging/components/ConversationList";
import { ChatWindow } from "@/features/messaging/components/ChatWindow";
import { apiClient } from "@/lib/api-client";
import { ConversationResponse } from "@/types";

export default function ActiveConversationPage() {
  const params = useParams();
  const conversationId = params?.id as string;

  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [activeConv, setActiveConv] = useState<ConversationResponse | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      const res = await apiClient.get<ConversationResponse[]>("/conversations");
      setIsLoading(false);

      if (res.success && res.data) {
        setConversations(res.data);
        const current = res.data.find((c) => c.id === conversationId);
        setActiveConv(current);
      }
    }
    loadData();
  }, [conversationId]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Conversation List Sidebar */}
        <div className="hidden lg:block lg:col-span-4">
          <ConversationList conversations={conversations} activeId={conversationId} />
        </div>

        {/* Right Active Chat Window */}
        <div className="lg:col-span-8">
          <ChatWindow conversationId={conversationId} conversation={activeConv} />
        </div>
      </div>
    </div>
  );
}
