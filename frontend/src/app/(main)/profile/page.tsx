"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  User as UserIcon,
  Stethoscope,
  Building2,
  ShieldCheck,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowRight,
  Mail,
  Phone,
  Calendar,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { apiClient } from "@/lib/api-client";
import {
  HospitalVerificationStatusResponse,
  User,
  VerificationStatusResponse,
} from "@/types";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [doctorStatus, setDoctorStatus] = useState<VerificationStatusResponse | null>(null);
  const [hospitalStatus, setHospitalStatus] = useState<HospitalVerificationStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [userRes, docRes, hospRes] = await Promise.all([
          apiClient.get<User>("/auth/me"),
          apiClient.get<VerificationStatusResponse>("/doctors/me/verification/status"),
          apiClient.get<HospitalVerificationStatusResponse>("/hospitals/me/verification/status"),
        ]);

        if (userRes.success && userRes.data) {
          setUser(userRes.data);
        }
        if (docRes.success && docRes.data) {
          setDoctorStatus(docRes.data);
        }
        if (hospRes.success && hospRes.data) {
          setHospitalStatus(hospRes.data);
        }
      } catch (err) {
        console.error("Failed to load profile data", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm font-semibold text-slate-500">Loading your profile...</p>
        </div>
      </div>
    );
  }

  // Doctor status helpers
  const docVerStatus = doctorStatus?.verification_status?.toLowerCase();
  const isDoctorVerified = docVerStatus === "verified";
  const isDoctorPending = docVerStatus === "pending" || docVerStatus === "under_review";
  const isDoctorRejected = docVerStatus === "rejected";
  const isDoctorNotApplied = !docVerStatus || docVerStatus === "not_applied" || docVerStatus === "unverified";

  // Hospital status helpers
  const hospVerStatus = hospitalStatus?.verification_status?.toLowerCase();
  const isHospitalVerified = hospVerStatus === "verified";
  const isHospitalPending = hospVerStatus === "pending" || hospVerStatus === "under_review";
  const isHospitalRejected = hospVerStatus === "rejected";
  const isHospitalNotCreated = !hospVerStatus || hospVerStatus === "not_created" || hospVerStatus === "unverified";

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Account & Role Management
          </h1>
          <p className="text-sm text-slate-500 font-medium">
            Manage your personal profile, credentials, and organization verifications.
          </p>
        </div>

        {/* 1. User Details Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-black text-xl">
                <UserIcon className="w-7 h-7" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-slate-900">
                    {user?.email?.split("@")[0] || "User Account"}
                  </h2>
                  <Badge variant="default" className="text-xs uppercase font-bold tracking-wider">
                    {user?.role || "USER"}
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Standard Account Holder
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link href="/profile/edit">
                <Button variant="outline" size="sm">
                  Edit Personal Info
                </Button>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
              <span className="text-slate-400 font-medium flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5" /> Email
              </span>
              <p className="font-semibold text-slate-800 break-all">{user?.email || "Not provided"}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
              <span className="text-slate-400 font-medium flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5" /> Phone
              </span>
              <p className="font-semibold text-slate-800">{user?.phone || "Not provided"}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/60 space-y-1">
              <span className="text-slate-400 font-medium flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Account Status
              </span>
              <p className="font-semibold text-slate-800 capitalize">{user?.status || "Active"}</p>
            </div>
          </div>
        </div>

        {/* Action Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 2. Doctor Account Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
                  <Stethoscope className="w-6 h-6" />
                </div>
                <div>
                  {isDoctorVerified && (
                    <Badge variant="success" className="text-xs px-2.5 py-1">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Verified Doctor
                    </Badge>
                  )}
                  {isDoctorPending && (
                    <Badge variant="warning" className="text-xs px-2.5 py-1">
                      <Clock className="w-3.5 h-3.5 mr-1 text-amber-600" /> Pending Verification
                    </Badge>
                  )}
                  {isDoctorRejected && (
                    <Badge variant="danger" className="text-xs px-2.5 py-1">
                      <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" /> Application Rejected
                    </Badge>
                  )}
                  {isDoctorNotApplied && (
                    <Badge variant="default" className="text-xs px-2.5 py-1 text-slate-500">
                      Not Applied
                    </Badge>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-900">Doctor Account</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Provide your medical council registration, degrees, and hospital affiliations to unlock verified doctor status and clinical messaging privileges.
                </p>
              </div>

              {isDoctorRejected && doctorStatus?.admin_notes && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 space-y-1">
                  <span className="font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600" /> Reason for Rejection:
                  </span>
                  <p>{doctorStatus.admin_notes}</p>
                </div>
              )}

              {isDoctorPending && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-amber-600" /> Verification In Progress
                  </p>
                  <p className="text-amber-700">
                    Your credentials are being reviewed by our administrative board. This usually takes 24–48 hours.
                  </p>
                </div>
              )}

              {isDoctorVerified && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Verified Badge Active
                  </p>
                  <p className="text-emerald-700">
                    You have full access to doctor search ranking, peer recommendations, and clinical messaging.
                  </p>
                </div>
              )}
            </div>

            <div className="pt-2 border-t border-slate-100">
              {isDoctorVerified ? (
                <Link href="/doctors" className="w-full block">
                  <Button variant="outline" size="md" className="w-full justify-between">
                    <span>View Doctor Profile</span>
                    <ExternalLink className="w-4 h-4 text-slate-400" />
                  </Button>
                </Link>
              ) : isDoctorPending ? (
                <Link href="/verification" className="w-full block">
                  <Button variant="outline" size="md" className="w-full justify-between">
                    <span>View Verification Progress</span>
                    <ArrowRight className="w-4 h-4 text-slate-400" />
                  </Button>
                </Link>
              ) : (
                <Link href="/verification" className="w-full block">
                  <Button variant="primary" size="md" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold justify-between">
                    <span>{isDoctorRejected ? "Reapply for Doctor Account" : "Apply for Doctor Account"}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>

          {/* 3. Create Hospital Account Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="w-12 h-12 rounded-xl bg-slate-900 flex items-center justify-center text-white shadow-sm">
                  <Building2 className="w-6 h-6" />
                </div>
                <div>
                  {isHospitalVerified && (
                    <Badge variant="success" className="text-xs px-2.5 py-1">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Verified Hospital
                    </Badge>
                  )}
                  {isHospitalPending && (
                    <Badge variant="warning" className="text-xs px-2.5 py-1">
                      <Clock className="w-3.5 h-3.5 mr-1 text-amber-600" /> Pending Verification
                    </Badge>
                  )}
                  {isHospitalRejected && (
                    <Badge variant="danger" className="text-xs px-2.5 py-1">
                      <XCircle className="w-3.5 h-3.5 mr-1 text-rose-600" /> Application Rejected
                    </Badge>
                  )}
                  {isHospitalNotCreated && (
                    <Badge variant="default" className="text-xs px-2.5 py-1 text-slate-500">
                      Not Created
                    </Badge>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-900">Healthcare Organization</h3>
                <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                  Register and verify a hospital, clinic, or medical institution to manage departments, post healthcare career vacancies, and affiliate clinical doctors.
                </p>
              </div>

              {isHospitalRejected && hospitalStatus?.admin_notes && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 space-y-1">
                  <span className="font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-600" /> Reason for Rejection:
                  </span>
                  <p>{hospitalStatus.admin_notes}</p>
                </div>
              )}

              {isHospitalPending && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-amber-600" /> Application Under Review
                  </p>
                  <p className="text-amber-700">
                    Your institutional license and registration documents are undergoing administrative review.
                  </p>
                </div>
              )}

              {isHospitalVerified && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Organization Verified
                  </p>
                  <p className="text-emerald-700">
                    Your hospital is active on DoctorIn. You can post job openings and manage medical staff.
                  </p>
                </div>
              )}
            </div>

            <div className="pt-2 border-t border-slate-100">
              {isHospitalVerified ? (
                <Link href="/hospitals" className="w-full block">
                  <Button variant="outline" size="md" className="w-full justify-between">
                    <span>View Hospital Page</span>
                    <ExternalLink className="w-4 h-4 text-slate-400" />
                  </Button>
                </Link>
              ) : isHospitalPending ? (
                <Link href="/hospitals/apply" className="w-full block">
                  <Button variant="outline" size="md" className="w-full justify-between">
                    <span>View Application Status</span>
                    <ArrowRight className="w-4 h-4 text-slate-400" />
                  </Button>
                </Link>
              ) : (
                <Link href="/hospitals/apply" className="w-full block">
                  <Button variant="primary" size="md" className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold justify-between">
                    <span>{isHospitalRejected ? "Reapply for Hospital Account" : "Create Hospital Account"}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
