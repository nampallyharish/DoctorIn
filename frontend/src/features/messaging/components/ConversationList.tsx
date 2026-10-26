"use client";

import React from "react";
import Link from "next/link";
import { MessageSquare, ShieldCheck } from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { ConversationResponse } from "@/types";

interface ConversationListProps {
  conversations: ConversationResponse[];
  activeId?: string;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  activeId,
}) => {
  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[650px]">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-teal-600" />
          Messages
        </h2>
        <span className="text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full font-semibold">
          {conversations.length}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
        {conversations.length === 0 ? (
          <div className="p-8 text-center space-y-2 text-slate-400">
            <MessageSquare className="w-8 h-8 mx-auto text-slate-300" />
            <p className="text-xs font-semibold text-slate-700">No active conversations</p>
            <p className="text-[11px]">Connect with other verified doctors to begin peer consultations.</p>
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeId;
            return (
              <Link
                key={conv.id}
                href={`/messages/${conv.id}`}
                className={`flex items-start gap-3 p-4 transition-colors ${
                  isActive ? "bg-teal-50/70 border-l-4 border-teal-600" : "hover:bg-slate-50"
                }`}
              >
                <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-teal-600 to-sky-600 text-white font-bold text-sm flex items-center justify-center shadow shrink-0">
                  {conv.participant.full_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
                </div>

                <div className="flex-1 min-w-0 space-y-0.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 min-w-0">
                      <span className="font-bold text-slate-900 text-xs truncate">
                        {conv.participant.full_name}
                      </span>
                      {conv.participant.verification_status === "verified" && (
                        <VerifiedBadge size="sm" />
                      )}
                    </div>
                    {conv.last_message_at && (
                      <span className="text-[10px] text-slate-400 shrink-0">
                        {new Date(conv.last_message_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    )}
                  </div>

                  <p className="text-[11px] text-slate-500 truncate">
                    {conv.last_message?.content || "Started conversation"}
                  </p>
                </div>

                {conv.unread_count > 0 && (
                  <span className="w-4 h-4 rounded-full bg-teal-600 text-white text-[10px] font-bold flex items-center justify-center shrink-0">
                    {conv.unread_count}
                  </span>
                )}
              </Link>
            );
          })
        )}
      </div>
    </div>
  );
};
