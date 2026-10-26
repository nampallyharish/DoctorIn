"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Building2,
  MapPin,
  Globe,
  Mail,
  Phone,
  Bed,
  Award,
  Briefcase,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { HospitalResponse } from "@/types";

export default function HospitalPublicProfilePage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [hospital, setHospital] = useState<HospitalResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHospital() {
      if (!slug) return;
      setIsLoading(true);
      const res = await apiClient.get<HospitalResponse>(`/hospitals/${slug}`);
      setIsLoading(false);

      if (res.success && res.data) {
        setHospital(res.data);
      } else {
        setError(res.errors?.[0]?.message || "Hospital not found.");
      }
    }
    loadHospital();
  }, [slug]);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center text-sm text-slate-500">
        Loading hospital profile...
      </div>
    );
  }

  if (error || !hospital) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
        <h2 className="text-xl font-bold text-slate-900">Hospital Not Found</h2>
        <p className="text-xs text-slate-500">{error || "This organization profile is unavailable."}</p>
        <Link href="/doctors">
          <Button variant="primary" size="sm">Explore Directory</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hospital Banner & Header */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm relative overflow-hidden space-y-6">
        <div className="absolute top-0 left-0 right-0 h-28 bg-gradient-to-r from-sky-800 via-teal-800 to-slate-900" />

        <div className="relative pt-12 flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-sky-700 to-teal-700 text-white font-bold text-3xl flex items-center justify-center border-4 border-white shadow-xl shrink-0">
              <Building2 className="w-12 h-12" />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  {hospital.name}
                </h1>
                {hospital.verification_status === "verified" && <VerifiedBadge size="lg" showText />}
              </div>

              <p className="text-sm font-semibold text-teal-700">
                {hospital.tagline || hospital.hospital_type.replace("_", " ")}
              </p>

              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                {hospital.city_name && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" /> {hospital.city_name}
                  </span>
                )}
                {hospital.total_beds && (
                  <span className="flex items-center gap-1">
                    <Bed className="w-3.5 h-3.5 text-slate-400" /> {hospital.total_beds} Inpatient Beds
                  </span>
                )}
                {hospital.website && (
                  <a
                    href={hospital.website}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-teal-700 hover:underline"
                  >
                    <Globe className="w-3.5 h-3.5" /> Official Website
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        {hospital.about && (
          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              About the Institution
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
              {hospital.about}
            </p>
          </div>
        )}
      </div>

      {/* Clinical Departments */}
      {hospital.departments && hospital.departments.length > 0 && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-4">
          <h2 className="text-lg font-extrabold text-slate-900">Clinical Departments & Centers of Excellence</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {hospital.departments.map((dept: any) => (
              <div key={dept.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <h3 className="text-sm font-bold text-slate-900">{dept.name}</h3>
                {dept.description && (
                  <p className="text-xs text-slate-500 leading-relaxed">{dept.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
