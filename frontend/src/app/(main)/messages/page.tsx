"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { MessageSquare, ShieldCheck, Lock, Users } from "lucide-react";
import { ConversationList } from "@/features/messaging/components/ConversationList";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { ConversationResponse } from "@/types";

export default function MessagesHubPage() {
  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadConversations() {
      setIsLoading(true);
      const res = await apiClient.get<ConversationResponse[]>("/conversations");
      setIsLoading(false);

      if (res.success && res.data) {
        setConversations(res.data);
      } else {
        setError(res.errors?.[0]?.message || "Failed to load conversations.");
      }
    }
    loadConversations();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-50 text-teal-700 text-xs font-semibold border border-teal-200">
            <Lock className="w-3.5 h-3.5" /> Doctor-to-Doctor Encrypted Channel
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
            Clinical Peer Messaging
          </h1>
          <p className="text-xs text-slate-500">
            Direct communication is strictly restricted to DoctorIn Verified medical practitioners.
          </p>
        </div>
      </div>

      {error ? (
        <div className="bg-rose-50 border border-rose-200 rounded-3xl p-8 text-center space-y-3 max-w-lg mx-auto">
          <ShieldCheck className="w-8 h-8 text-rose-600 mx-auto" />
          <h3 className="text-base font-bold text-rose-900">Verification Required</h3>
          <p className="text-xs text-rose-700 leading-relaxed">{error}</p>
          <Link href="/verification">
            <Button variant="primary" size="sm">Go to Verification Portal</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Conversation List Sidebar */}
          <div className="lg:col-span-4">
            <ConversationList conversations={conversations} />
          </div>

          {/* Empty Selection State */}
          <div className="hidden lg:flex lg:col-span-8 bg-white rounded-3xl border border-slate-200 shadow-sm h-[650px] flex-col items-center justify-center p-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-3xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <MessageSquare className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900">Select a Conversation</h3>
              <p className="text-xs text-slate-500 max-w-sm">
                Choose a doctor thread from the left, or search the verified directory to connect with a colleague.
              </p>
            </div>
            <Link href="/doctors">
              <Button variant="outline" size="sm" className="text-xs">
                <Users className="w-3.5 h-3.5 mr-1" /> Browse Doctor Directory
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
