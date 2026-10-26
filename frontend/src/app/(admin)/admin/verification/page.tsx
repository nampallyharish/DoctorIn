"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertCircle,
  FileText,
  Clock,
  ExternalLink,
  Search,
  Building2,
  Stethoscope,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { apiClient } from "@/lib/api-client";
import {
  AdminHospitalVerificationQueueItem,
  AdminVerificationQueueItem,
} from "@/types";

export default function AdminVerificationQueuePage() {
  const [activeTab, setActiveTab] = useState<"doctors" | "hospitals">("doctors");

  const [doctorQueue, setDoctorQueue] = useState<AdminVerificationQueueItem[]>([]);
  const [hospitalQueue, setHospitalQueue] = useState<AdminHospitalVerificationQueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Rejection modal state
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [targetRequestId, setTargetRequestId] = useState<string | null>(null);
  const [targetType, setTargetType] = useState<"doctor" | "hospital">("doctor");
  const [rejectionReason, setRejectionReason] = useState("");

  const [isProcessing, setIsProcessing] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const fetchQueues = async () => {
    setIsLoading(true);
    try {
      const [docRes, hospRes] = await Promise.all([
        apiClient.get<AdminVerificationQueueItem[]>("/admin/verification/queue"),
        apiClient.get<AdminHospitalVerificationQueueItem[]>("/admin/verification/hospitals/queue"),
      ]);

      if (docRes.success && docRes.data) {
        setDoctorQueue(docRes.data);
      }
      if (hospRes.success && hospRes.data) {
        setHospitalQueue(hospRes.data);
      }
    } catch (err) {
      console.error("Failed to load verification queues", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueues();
  }, []);

  const handleApprove = async (requestId: string, type: "doctor" | "hospital") => {
    setIsProcessing(true);
    setActionMsg(null);

    const endpoint =
      type === "doctor"
        ? `/admin/verification/${requestId}/review`
        : `/admin/verification/hospitals/${requestId}/review`;

    const res = await apiClient.put(endpoint, {
      action: "approve",
      admin_notes: "Approved by administration board",
    });

    setIsProcessing(false);
    if (res.success) {
      setActionMsg(
        `✓ ${type === "doctor" ? "Doctor" : "Hospital"} application approved successfully.`
      );
      fetchQueues();
    }
  };

  const openRejectModal = (requestId: string, type: "doctor" | "hospital") => {
    setTargetRequestId(requestId);
    setTargetType(type);
    setRejectionReason("");
    setRejectModalOpen(true);
  };

  const confirmReject = async () => {
    if (!targetRequestId) return;
    setIsProcessing(true);
    setActionMsg(null);

    const endpoint =
      targetType === "doctor"
        ? `/admin/verification/${targetRequestId}/review`
        : `/admin/verification/hospitals/${targetRequestId}/review`;

    const res = await apiClient.put(endpoint, {
      action: "reject",
      admin_notes: rejectionReason || "Document mismatch or invalid registration",
      rejection_reason: rejectionReason || "Document mismatch or invalid registration",
    });

    setIsProcessing(false);
    setRejectModalOpen(false);

    if (res.success) {
      setActionMsg(
        `✗ ${targetType === "doctor" ? "Doctor" : "Hospital"} application rejected with feedback.`
      );
      fetchQueues();
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-200">
            <ShieldCheck className="w-3.5 h-3.5" /> Admin Verification Center
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight mt-1">
            Verification Queue & Inspections
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Review professional medical credentials and healthcare organization licenses
          </p>
        </div>
      </div>

      {actionMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs font-semibold flex items-center gap-2 shadow-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" /> {actionMsg}
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-3 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab("doctors")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "doctors"
              ? "bg-blue-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
          }`}
        >
          <Stethoscope className="w-4 h-4" />
          <span>Doctor Applications</span>
          <span
            className={`ml-1 px-1.5 py-0.5 rounded-full text-[10px] ${
              activeTab === "doctors" ? "bg-blue-700 text-white" : "bg-slate-100 text-slate-600"
            }`}
          >
            {doctorQueue.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("hospitals")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "hospitals"
              ? "bg-slate-900 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>Hospital Applications</span>
          <span
            className={`ml-1 px-1.5 py-0.5 rounded-full text-[10px] ${
              activeTab === "hospitals" ? "bg-slate-800 text-white" : "bg-slate-100 text-slate-600"
            }`}
          >
            {hospitalQueue.length}
          </span>
        </button>
      </div>

      {/* Doctor Applications Table */}
      {activeTab === "doctors" && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Pending Doctor Applications ({doctorQueue.length})
            </h2>
          </div>

          {isLoading ? (
            <div className="text-center py-20 text-sm text-slate-500">
              Loading doctor applications...
            </div>
          ) : doctorQueue.length === 0 ? (
            <div className="text-center py-16 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-teal-600 mx-auto" />
              <p className="text-sm font-bold text-slate-800">Doctor Queue is Clear</p>
              <p className="text-xs text-slate-400">
                All submitted doctor credentials have been inspected and evaluated.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4">Doctor Name</th>
                    <th className="px-6 py-4">Registration #</th>
                    <th className="px-6 py-4">Medical Council</th>
                    <th className="px-6 py-4">Documents</th>
                    <th className="px-6 py-4">Submitted Date</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {doctorQueue.map((item: any) => (
                    <tr key={item.request_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{item.doctor_name}</div>
                        <div className="text-[11px] text-slate-400">
                          {item.doctor_email || item.doctor_phone}
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono font-semibold text-slate-800">
                        {item.credential_number || "N/A"}
                      </td>
                      <td className="px-6 py-4">{item.issuing_authority || "N/A"}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                          <FileText className="w-3 h-3" /> {item.documents_count} file(s)
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {new Date(item.submitted_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleApprove(item.request_id, "doctor")}
                            disabled={isProcessing}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-3 py-1"
                          >
                            Approve
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => openRejectModal(item.request_id, "doctor")}
                            disabled={isProcessing}
                            className="text-xs px-3 py-1 font-bold"
                          >
                            Reject
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Hospital Applications Table */}
      {activeTab === "hospitals" && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900">
              Pending Hospital Applications ({hospitalQueue.length})
            </h2>
          </div>

          {isLoading ? (
            <div className="text-center py-20 text-sm text-slate-500">
              Loading hospital applications...
            </div>
          ) : hospitalQueue.length === 0 ? (
            <div className="text-center py-16 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-teal-600 mx-auto" />
              <p className="text-sm font-bold text-slate-800">Hospital Queue is Clear</p>
              <p className="text-xs text-slate-400">
                All submitted hospital registrations and licenses have been evaluated.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4">Hospital Name & Entity</th>
                    <th className="px-6 py-4">License / Registration #</th>
                    <th className="px-6 py-4">Representative</th>
                    <th className="px-6 py-4">Documents</th>
                    <th className="px-6 py-4">Submitted Date</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {hospitalQueue.map((item) => (
                    <tr key={item.request_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-900">{item.hospital_name}</div>
                        <div className="text-[11px] text-slate-400">
                          {item.legal_entity_name || item.hospital_type}
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono font-semibold text-slate-800">
                        {item.registration_number || "N/A"}
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-800">{item.contact_person_name || "N/A"}</div>
                        <div className="text-[11px] text-slate-400">{item.contact_person_email || item.contact_person_phone}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1 font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                          <FileText className="w-3 h-3" /> {item.documents_count} file(s)
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400">
                        {new Date(item.submitted_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleApprove(item.request_id, "hospital")}
                            disabled={isProcessing}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-3 py-1"
                          >
                            Approve
                          </Button>
                          <Button
                            variant="danger"
                            size="sm"
                            onClick={() => openRejectModal(item.request_id, "hospital")}
                            disabled={isProcessing}
                            className="text-xs px-3 py-1 font-bold"
                          >
                            Reject
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Reject Modal with Reason Input */}
      {rejectModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 border border-slate-200 shadow-xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-rose-600" />
                Reject {targetType === "doctor" ? "Doctor" : "Hospital"} Application
              </h3>
              <button
                onClick={() => setRejectModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Provide feedback for why this application is being rejected. This explanation will be displayed to the applicant so they can rectify and reapply.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Rejection Reason
              </label>
              <textarea
                rows={3}
                required
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g. License certificate is illegible or council registration number not matching official records..."
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-rose-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setRejectModalOpen(false)}
                disabled={isProcessing}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={confirmReject}
                isLoading={isProcessing}
                className="font-bold px-4"
              >
                Confirm Rejection
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
