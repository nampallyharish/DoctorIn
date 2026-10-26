"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  ShieldCheck,
  Building2,
  Briefcase,
  AlertTriangle,
  FileText,
  Activity,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { AdminStatsResponse } from "@/types";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      setIsLoading(true);
      const res = await apiClient.get<AdminStatsResponse>("/admin/stats");
      setIsLoading(false);

      if (res.success && res.data) {
        setStats(res.data);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-200">
          <ShieldCheck className="w-3.5 h-3.5" /> DoctorIn Security & Administration
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
          Platform Overview & KPI Dashboard
        </h1>
        <p className="text-xs text-slate-500">
          Real-time metrics on registered medical specialists, verification throughput, and community health
        </p>
      </div>

      {/* KPI Tiles Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Doctors</span>
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{stats?.total_doctors ?? "–"}</div>
          <p className="text-[11px] text-teal-700 font-semibold">
            {stats?.total_verified_doctors ?? "–"} verified with active badge
          </p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Verification Queue</span>
            <div className="w-8 h-8 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-amber-600">{stats?.pending_verifications ?? "–"}</div>
          <Link href="/admin/verification" className="text-[11px] text-slate-500 hover:text-slate-900 flex items-center gap-1 font-semibold">
            Review submissions →
          </Link>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Medical Hospitals</span>
            <div className="w-8 h-8 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{stats?.total_hospitals ?? "–"}</div>
          <p className="text-[11px] text-slate-400 font-medium">
            {stats?.active_jobs ?? "–"} active vacancies posted
          </p>
        </div>

        <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Flagged Content</span>
            <div className="w-8 h-8 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-rose-600">{stats?.pending_reports ?? "–"}</div>
          <Link href="/admin/reports" className="text-[11px] text-slate-500 hover:text-slate-900 flex items-center gap-1 font-semibold">
            Open moderation queue →
          </Link>
        </div>
      </div>

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href="/admin/users"
          className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-2 group"
        >
          <div className="w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            User Management <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 transition-colors" />
          </h3>
          <p className="text-xs text-slate-500">
            Search users, view roles, and suspend or ban compromised accounts.
          </p>
        </Link>

        <Link
          href="/admin/reports"
          className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-2 group"
        >
          <div className="w-10 h-10 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center group-hover:scale-105 transition-transform">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            Content Moderation <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-rose-600 transition-colors" />
          </h3>
          <p className="text-xs text-slate-500">
            Inspect reported medical claims, takedown inappropriate posts, or dismiss reports.
          </p>
        </Link>

        <Link
          href="/admin/audit-logs"
          className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-2 group"
        >
          <div className="w-10 h-10 rounded-2xl bg-slate-100 text-slate-700 flex items-center justify-center group-hover:scale-105 transition-transform">
            <Activity className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            Security Audit Logs <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-slate-900 transition-colors" />
          </h3>
          <p className="text-xs text-slate-500">
            Immutable log trail of all verification decisions, status updates, and admin actions.
          </p>
        </Link>
      </div>
    </div>
  );
}
