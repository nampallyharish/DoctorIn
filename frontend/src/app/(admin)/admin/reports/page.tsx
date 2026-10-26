"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Trash2,
  ArrowLeft,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { apiClient } from "@/lib/api-client";
import { AdminReportItem } from "@/types";

export default function AdminReportsPage() {
  const [reports, setReports] = useState<AdminReportItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const fetchReports = async () => {
    setIsLoading(true);
    const res = await apiClient.get<AdminReportItem[]>("/admin/reports?page=1&per_page=20");
    setIsLoading(false);

    if (res.success && res.data) {
      setReports(res.data);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleReviewAction = async (reportId: string, action: "resolve_takedown" | "dismiss") => {
    const res = await apiClient.put(`/admin/reports/${reportId}/review`, {
      action,
      review_notes: `Processed by admin via moderation queue`,
    });

    if (res.success) {
      setActionMsg(`Report action '${action.toUpperCase()}' completed.`);
      fetchReports();
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <Link href="/admin" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Community Content Moderation Queue
        </h1>
        <p className="text-xs text-slate-500">
          Review posts, comments, or medical claims flagged by users for misinformation or policy violations
        </p>
      </div>

      {actionMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" /> {actionMsg}
        </div>
      )}

      {/* Reports Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="text-center py-20 text-sm text-slate-500">Loading moderation queue...</div>
        ) : reports.length === 0 ? (
          <div className="text-center py-16 space-y-2">
            <CheckCircle2 className="w-8 h-8 text-teal-600 mx-auto" />
            <p className="text-sm font-bold text-slate-800">Moderation Queue is Clean</p>
            <p className="text-xs text-slate-400">There are no pending reports requiring action.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4">Reporter</th>
                  <th className="px-6 py-4">Target Type</th>
                  <th className="px-6 py-4">Reason</th>
                  <th className="px-6 py-4">Notes</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {reports.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4 font-bold text-slate-900">{r.reporter_name}</td>
                    <td className="px-6 py-4 uppercase font-semibold text-teal-700">{r.target_type}</td>
                    <td className="px-6 py-4">
                      <Badge variant="warning" className="uppercase text-[10px]">
                        {r.reason}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-slate-500">{r.description || "–"}</td>
                    <td className="px-6 py-4">
                      <span className="font-semibold text-slate-700">{r.status.toUpperCase()}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {r.status === "pending" ? (
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => handleReviewAction(r.id, "resolve_takedown")}
                            className="text-[11px] py-1 px-2.5"
                          >
                            Takedown
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleReviewAction(r.id, "dismiss")}
                            className="text-[11px] py-1 px-2.5"
                          >
                            Dismiss
                          </Button>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[11px] italic">Processed</span>
                      )}
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
