"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import {
  Briefcase,
  Building2,
  MapPin,
  Clock,
  Banknote,
  ShieldCheck,
  Search,
  ArrowRight,
} from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { JobPostingResponse } from "@/types";

function JobsPageContent() {
  const [jobs, setJobs] = useState<JobPostingResponse[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const fetchJobs = async () => {
    setIsLoading(true);
    const res = await apiClient.get<JobPostingResponse[]>("/jobs?page=1&per_page=20");
    setIsLoading(false);

    if (res.success && res.data) {
      setJobs(res.data);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const filteredJobs = jobs.filter((job) => {
    if (!searchTerm.trim()) return true;
    const term = searchTerm.toLowerCase();
    return (
      job.title.toLowerCase().includes(term) ||
      job.hospital_name.toLowerCase().includes(term) ||
      (job.city_name && job.city_name.toLowerCase().includes(term))
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header & Search */}
      <div className="space-y-4 max-w-3xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-50 text-teal-700 text-xs font-semibold border border-teal-200">
          <Briefcase className="w-3.5 h-3.5" /> Medical Careers & Hospital Openings
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          Medical Job Board
        </h1>
        <p className="text-sm text-slate-600">
          Explore clinical consultant positions, surgical fellowships, and hospital department vacancies.
        </p>

        <div className="pt-2 flex items-center gap-2 bg-white p-2 rounded-2xl border border-slate-200 shadow-sm">
          <Search className="w-5 h-5 text-teal-600 ml-2" />
          <input
            type="text"
            placeholder="Search by job title, hospital, or city..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full py-2 bg-transparent text-sm focus:outline-none"
          />
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between text-xs font-semibold text-slate-500 border-b border-slate-200 pb-3">
        <span>Showing {filteredJobs.length} active positions</span>
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <div className="text-center py-20 text-sm text-slate-500">
          Loading medical job opportunities...
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
          <Briefcase className="w-8 h-8 text-slate-300 mx-auto" />
          <p className="text-base font-bold text-slate-800">No job openings found</p>
          <p className="text-xs text-slate-400">Try adjusting your search criteria or check back later.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <div
              key={job.id}
              className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <h3 className="font-bold text-slate-900 text-base leading-snug">{job.title}</h3>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-teal-700">{job.hospital_name}</span>
                      {job.hospital_verified && <VerifiedBadge size="sm" />}
                    </div>
                  </div>
                  <Badge variant="info" className="text-[10px] uppercase tracking-wider shrink-0">
                    {job.employment_type.replace("_", " ")}
                  </Badge>
                </div>

                <div className="space-y-1 text-xs text-slate-500 pt-1">
                  {job.city_name && (
                    <p className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" /> {job.city_name}
                    </p>
                  )}
                  <p className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" /> {job.min_experience_years}+ years experience
                  </p>
                  {job.salary_min && (
                    <p className="flex items-center gap-1.5 text-slate-700 font-semibold">
                      <Banknote className="w-3.5 h-3.5 text-emerald-600" />
                      ₹{(job.salary_min / 100000).toFixed(1)}L - ₹{((job.salary_max || job.salary_min) / 100000).toFixed(1)}L / yr
                    </p>
                  )}
                </div>

                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed pt-1">
                  {job.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <Link href={`/jobs/${job.id}`}>
                  <Button variant="primary" size="sm" className="w-full text-xs flex items-center justify-center gap-1">
                    View Details & Apply <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-sm text-slate-500">Loading Job Board...</div>}>
      <JobsPageContent />
    </Suspense>
  );
}
