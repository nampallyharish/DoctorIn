"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  Search,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Ban,
  RotateCcw,
  ArrowLeft,
} from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { AdminUserItem } from "@/types";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUserItem[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const fetchUsers = async () => {
    setIsLoading(true);
    const params = new URLSearchParams();
    if (searchTerm.trim()) params.set("q", searchTerm.trim());
    if (roleFilter) params.set("role", roleFilter);

    const res = await apiClient.get<AdminUserItem[]>(`/admin/users?${params.toString()}`);
    setIsLoading(false);

    if (res.success && res.data) {
      setUsers(res.data);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter]);

  const handleStatusUpdate = async (userId: string, action: "activate" | "suspend" | "ban") => {
    const res = await apiClient.put(`/admin/users/${userId}/status`, {
      action,
      reason: `Action executed by administrator via UI portal`,
    });

    if (res.success) {
      setStatusMsg(`User status updated to ${action.toUpperCase()}`);
      fetchUsers();
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <Link href="/admin" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            User Account Management
          </h1>
          <p className="text-xs text-slate-500">
            Inspect platform accounts, verify roles, and apply security suspensions
          </p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 bg-white border border-slate-300 rounded-xl text-xs font-semibold focus:outline-none"
          >
            <option value="">All Roles</option>
            <option value="doctor">Doctors</option>
            <option value="patient">Patients</option>
            <option value="hospital_admin">Hospitals</option>
            <option value="admin">Administrators</option>
          </select>
        </div>
      </div>

      {statusMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" /> {statusMsg}
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="text-center py-20 text-sm text-slate-500">Loading accounts...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Verification</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Created Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">{u.name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{u.email || u.phone || "No identifier"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="info" className="uppercase text-[10px]">
                        {u.role}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      {u.verified ? (
                        <VerifiedBadge size="sm" showText />
                      ) : (
                        <span className="text-slate-400">Unverified</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          u.status === "active"
                            ? "bg-emerald-50 text-emerald-700"
                            : u.status === "suspended"
                            ? "bg-amber-50 text-amber-700"
                            : "bg-rose-50 text-rose-700"
                        }`}
                      >
                        {u.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {u.status !== "active" && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStatusUpdate(u.id, "activate")}
                            className="text-[11px] py-1 px-2 text-emerald-700"
                          >
                            Reactivate
                          </Button>
                        )}
                        {u.status === "active" && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStatusUpdate(u.id, "suspend")}
                            className="text-[11px] py-1 px-2 text-amber-700"
                          >
                            Suspend
                          </Button>
                        )}
                        {u.status !== "banned" && (
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => handleStatusUpdate(u.id, "ban")}
                            className="text-[11px] py-1 px-2"
                          >
                            Ban
                          </Button>
                        )}
                      </div>
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
