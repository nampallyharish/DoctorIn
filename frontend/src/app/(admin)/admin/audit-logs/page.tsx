"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ShieldCheck, ArrowLeft, Terminal } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { AuditLogResponseItem } from "@/types";

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogResponseItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadLogs() {
      setIsLoading(true);
      const res = await apiClient.get<AuditLogResponseItem[]>("/admin/audit-logs?page=1&per_page=50");
      setIsLoading(false);

      if (res.success && res.data) {
        setLogs(res.data);
      }
    }
    loadLogs();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <Link href="/admin" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Security & Administrative Audit Logs
        </h1>
        <p className="text-xs text-slate-500">
          Immutable event stream capturing verification decisions, credential changes, and moderation actions
        </p>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden font-mono">
        {isLoading ? (
          <div className="text-center py-20 text-xs text-slate-500">Loading audit log events...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-900 text-[11px] font-bold text-slate-200 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">Timestamp (UTC)</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Resource</th>
                  <th className="px-6 py-4">Actor</th>
                  <th className="px-6 py-4">Client IP</th>
                  <th className="px-6 py-4">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-slate-950 text-slate-300 font-mono text-[11px]">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-900/80 transition-colors">
                    <td className="px-6 py-3.5 text-teal-400 whitespace-nowrap">
                      {new Date(log.created_at).toISOString()}
                    </td>
                    <td className="px-6 py-3.5 font-bold text-emerald-400 whitespace-nowrap">
                      {log.action}
                    </td>
                    <td className="px-6 py-3.5 text-sky-400 whitespace-nowrap">{log.resource_type}</td>
                    <td className="px-6 py-3.5 text-slate-400 truncate max-w-[120px]">
                      {log.actor_id ? String(log.actor_id).slice(0, 8) + "..." : "SYSTEM"}
                    </td>
                    <td className="px-6 py-3.5 text-amber-400 whitespace-nowrap">
                      {log.ip_address || "127.0.0.1"}
                    </td>
                    <td className="px-6 py-3.5 text-slate-400 text-[10px] max-w-xs truncate">
                      {JSON.stringify(log.details || {})}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
