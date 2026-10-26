"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Briefcase,
  Building2,
  MapPin,
  Clock,
  Banknote,
  ShieldCheck,
  CheckCircle2,
  Send,
  ArrowLeft,
} from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { JobPostingResponse } from "@/types";

export default function JobDetailPage() {
  const params = useParams();
  const jobId = params?.id as string;

  const [job, setJob] = useState<JobPostingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isApplying, setIsApplying] = useState(false);
  const [coverNote, setCoverNote] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadJob() {
      if (!jobId) return;
      setIsLoading(true);
      const res = await apiClient.get<JobPostingResponse>(`/jobs/${jobId}`);
      setIsLoading(false);

      if (res.success && res.data) {
        setJob(res.data);
      } else {
        setError(res.errors?.[0]?.message || "Job not found.");
      }
    }
    loadJob();
  }, [jobId]);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsApplying(true);
    setError(null);

    const res = await apiClient.post(`/jobs/${jobId}/apply`, {
      cover_note: coverNote.trim() || undefined,
    });

    setIsApplying(false);

    if (res.success) {
      setAppliedSuccess(true);
      setShowModal(false);
    } else {
      setError(res.errors?.[0]?.message || "Failed to submit application.");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center text-sm text-slate-500">
        Loading job vacancy details...
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
        <h2 className="text-xl font-bold text-slate-900">Job Opening Not Found</h2>
        <p className="text-xs text-slate-500">{error || "This position may have been filled or expired."}</p>
        <Link href="/jobs">
          <Button variant="primary" size="sm">Back to Job Board</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <Link href="/jobs" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-teal-700 font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to Medical Jobs
      </Link>

      {/* Main Header Card */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">{job.title}</h1>
            </div>

            <div className="flex items-center gap-2">
              <Link href={`/hospitals/${job.hospital_slug}`} className="text-sm font-bold text-teal-700 hover:underline">
                {job.hospital_name}
              </Link>
              {job.hospital_verified && <VerifiedBadge size="sm" />}
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
              {job.city_name && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" /> {job.city_name}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" /> {job.min_experience_years}+ yrs exp
              </span>
              <span className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5 text-slate-400" /> {job.employment_type.replace("_", " ")}
              </span>
            </div>
          </div>

          <div className="shrink-0">
            {appliedSuccess ? (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Application Submitted!
              </div>
            ) : (
              <Button variant="primary" size="md" onClick={() => setShowModal(true)}>
                1-Click Apply with Profile
              </Button>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-slate-900">Position Overview</h3>
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
            {job.description}
          </div>
        </div>

        {/* Requirements */}
        {job.requirements && (
          <div className="space-y-3 pt-4 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Clinical Requirements & Qualifications</h3>
            <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
              {job.requirements}
            </div>
          </div>
        )}

        {/* Benefits */}
        {job.benefits && (
          <div className="space-y-3 pt-4 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-900">Benefits & Department Amenities</h3>
            <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
              {job.benefits}
            </div>
          </div>
        )}
      </div>

      {/* Apply Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl w-full max-w-lg p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-6">
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-slate-900">Apply for {job.title}</h3>
              <p className="text-xs text-slate-500">
                Your verified DoctorIn profile, publications, and clinical experience will be securely shared with {job.hospital_name}.
              </p>
            </div>

            <form onSubmit={handleApply} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Cover Note for Medical Director (Optional)
                </label>
                <textarea
                  rows={4}
                  value={coverNote}
                  onChange={(e) => setCoverNote(e.target.value)}
                  placeholder="Introduce yourself and outline your specialized clinical interests..."
                  className="w-full p-3 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <Button type="button" variant="ghost" size="sm" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm" isLoading={isApplying}>
                  <Send className="w-3.5 h-3.5 mr-1" /> Submit Application
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
