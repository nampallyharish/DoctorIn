"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  GraduationCap,
  Briefcase,
  Award,
  BookOpen,
  Building2,
  Calendar,
  ExternalLink,
  ShieldCheck,
  MessageSquare,
} from "lucide-react";
import { DoctorProfileHeader } from "@/features/doctor/components/DoctorProfileHeader";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { apiClient } from "@/lib/api-client";
import { DoctorPublicProfileResponse } from "@/types";

export default function DoctorPublicProfilePage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [doctor, setDoctor] = useState<DoctorPublicProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDoctor() {
      if (!slug) return;
      setIsLoading(true);
      const res = await apiClient.get<DoctorPublicProfileResponse>(`/doctors/${slug}`);
      setIsLoading(false);

      if (res.success && res.data) {
        setDoctor(res.data);
      } else {
        setError(res.errors?.[0]?.message || "Doctor profile not found.");
      }
    }
    loadDoctor();
  }, [slug]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center space-y-3">
        <div className="animate-spin w-8 h-8 border-4 border-teal-600 border-t-transparent rounded-full mx-auto" />
        <p className="text-sm text-slate-500">Loading verified medical profile...</p>
      </div>
    );
  }

  if (error || !doctor) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto">
          ⚠️
        </div>
        <h2 className="text-xl font-bold text-slate-900">Profile Not Found</h2>
        <p className="text-xs text-slate-500">{error || "This doctor profile is unavailable or inactive."}</p>
        <Link href="/doctors">
          <Button variant="primary" size="sm">Browse Doctor Directory</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Profile Header */}
      <DoctorProfileHeader doctor={doctor} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Education & Experience Timeline */}
        <div className="lg:col-span-8 space-y-8">
          {/* Clinical Experience */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
            <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-teal-600" />
              Clinical Experience
            </h2>

            {doctor.experience && doctor.experience.length > 0 ? (
              <div className="space-y-6 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {doctor.experience.map((exp: any) => (
                  <div key={exp.id} className="relative pl-8 space-y-1">
                    <div className="absolute left-2 top-1.5 w-3.5 h-3.5 rounded-full bg-teal-600 border-2 border-white shadow" />
                    <h3 className="text-sm font-bold text-slate-900">{exp.job_title}</h3>
                    <p className="text-xs text-teal-700 font-medium">{exp.organization}</p>
                    <p className="text-xs text-slate-400 flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(exp.start_date).getFullYear()} –{" "}
                      {exp.is_current ? "Present" : exp.end_date ? new Date(exp.end_date).getFullYear() : "N/A"}
                    </p>
                    {exp.description && (
                      <p className="text-xs text-slate-600 pt-1 leading-relaxed">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No clinical experience entries added yet.</p>
            )}
          </div>

          {/* Medical Education */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
            <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-sky-600" />
              Medical Education & Degrees
            </h2>

            {doctor.education && doctor.education.length > 0 ? (
              <div className="space-y-4">
                {doctor.education.map((edu: any) => (
                  <div key={edu.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-bold text-slate-900">{edu.degree}</h3>
                      <span className="text-xs text-slate-400 font-medium">
                        {edu.start_year} – {edu.end_year || "Present"}
                      </span>
                    </div>
                    <p className="text-xs text-sky-700 font-medium">{edu.institution}</p>
                    {edu.field_of_study && (
                      <p className="text-xs text-slate-500">Specialty: {edu.field_of_study}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No education entries added yet.</p>
            )}
          </div>

          {/* Publications & Research */}
          {doctor.publications && doctor.publications.length > 0 && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
              <h2 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-600" />
                Publications & Clinical Research
              </h2>

              <div className="space-y-4">
                {doctor.publications.map((pub: any) => (
                  <div key={pub.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1.5">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-sm font-bold text-slate-900 leading-snug">{pub.title}</h3>
                      {pub.publication_url && (
                        <a
                          href={pub.publication_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-indigo-600 hover:text-indigo-700 shrink-0"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                    {pub.journal && (
                      <p className="text-xs text-slate-500 font-medium">{pub.journal}</p>
                    )}
                    {pub.abstract && (
                      <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed pt-1">
                        {pub.abstract}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Verification & Interaction */}
        <div className="lg:col-span-4 space-y-6">
          {/* Verification Badge Details Card */}
          <div className="bg-gradient-to-br from-teal-50 to-sky-50 rounded-3xl p-6 border border-teal-200 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-teal-800 font-bold text-sm">
              <ShieldCheck className="w-5 h-5 text-teal-600" />
              DoctorIn Verification
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              This doctor has verified registration status and credentials evaluated by the DoctorIn Medical Verification team.
            </p>
          </div>

          {/* Achievements & Awards */}
          {doctor.achievements && doctor.achievements.length > 0 && (
            <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Award className="w-4 h-4 text-amber-500" />
                Honors & Achievements
              </h3>
              <div className="space-y-3">
                {doctor.achievements.map((ach: any) => (
                  <div key={ach.id} className="text-xs space-y-0.5 border-b border-slate-100 pb-2 last:border-0 last:pb-0">
                    <p className="font-semibold text-slate-800">{ach.title}</p>
                    {ach.issuing_organization && (
                      <p className="text-slate-400">{ach.issuing_organization}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action CTA: Messaging Rule Note */}
          <div className="bg-slate-900 text-white rounded-3xl p-6 space-y-3 shadow-md">
            <div className="flex items-center gap-2 text-sm font-bold text-teal-400">
              <MessageSquare className="w-4 h-4" /> Peer-to-Peer Medical Messaging
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Direct doctor-to-doctor messaging is reserved for verified medical practitioners on DoctorIn.
            </p>
            <Link href="/login" className="block pt-1">
              <Button variant="primary" size="sm" className="w-full text-xs">
                Sign in to Message
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
