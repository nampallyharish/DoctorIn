"use client";

import React from "react";
import { Building2, MapPin, Briefcase, Calendar, ExternalLink } from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { DoctorProfileResponse, DoctorPublicProfileResponse } from "@/types";

interface DoctorHeaderProps {
  doctor: DoctorPublicProfileResponse | DoctorProfileResponse;
  isOwner?: boolean;
}

export const DoctorProfileHeader: React.FC<DoctorHeaderProps> = ({ doctor, isOwner }) => {
  return (
    <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm relative overflow-hidden">
      {/* Decorative gradient banner */}
      <div className="absolute top-0 left-0 right-0 h-28 bg-gradient-to-r from-teal-700 via-sky-800 to-slate-900" />

      <div className="relative pt-12 flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
        {/* Avatar & Names */}
        <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
          <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-gradient-to-tr from-teal-600 to-sky-600 text-white font-bold text-3xl flex items-center justify-center border-4 border-white shadow-xl shrink-0">
            {doctor.full_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                {doctor.full_name}
              </h1>
              {doctor.verification_status === "verified" && <VerifiedBadge size="lg" showText />}
              {doctor.verification_status !== "verified" && (
                <Badge variant="warning">Verification {doctor.verification_status}</Badge>
              )}
            </div>

            <p className="text-sm font-semibold text-teal-700">
              {doctor.headline || "Medical Specialist"}
            </p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
              {doctor.current_organization && (
                <span className="flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" /> {doctor.current_organization}
                </span>
              )}
              {doctor.years_of_experience !== undefined && (
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-slate-400" /> {doctor.years_of_experience} yrs clinical exp
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Specialization Badges */}
        <div className="flex flex-wrap gap-1.5 self-start sm:self-end pt-2">
          {doctor.specializations?.map((spec: any) => (
            <Badge key={spec.id} variant="info" className="bg-sky-50 text-sky-700">
              {spec.name}
            </Badge>
          ))}
        </div>
      </div>

      {/* Biography */}
      {doctor.bio && (
        <div className="mt-6 pt-6 border-t border-slate-100">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            Professional Biography
          </h3>
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
            {doctor.bio}
          </p>
        </div>
      )}
    </div>
  );
};
