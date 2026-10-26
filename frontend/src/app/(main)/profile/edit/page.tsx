"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  User,
  GraduationCap,
  Briefcase,
  Award,
  BookOpen,
  Plus,
  Trash2,
  CheckCircle2,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { ProfileCompletionBar } from "@/features/doctor/components/ProfileCompletionBar";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { DoctorProfileResponse } from "@/types";

export default function EditDoctorProfilePage() {
  const [profile, setProfile] = useState<DoctorProfileResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"general" | "education" | "experience" | "publications">("general");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);
  const router = useRouter();

  // General Form State
  const [fullName, setFullName] = useState("");
  const [headline, setHeadline] = useState("");
  const [yearsOfExp, setYearsOfExp] = useState<number | "">("");
  const [currentOrg, setCurrentOrg] = useState("");
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");

  // Sub-resource Modal/Form States
  const [eduDegree, setEduDegree] = useState("");
  const [eduInst, setEduInst] = useState("");
  const [eduStartYear, setEduStartYear] = useState(2015);
  const [eduEndYear, setEduEndYear] = useState<number | "">(2020);

  const [expTitle, setExpTitle] = useState("");
  const [expOrg, setExpOrg] = useState("");
  const [expStartDate, setExpStartDate] = useState("2020-01-01");
  const [expIsCurrent, setExpIsCurrent] = useState(true);

  const [pubTitle, setPubTitle] = useState("");
  const [pubJournal, setPubJournal] = useState("");
  const [pubUrl, setPubUrl] = useState("");

  const loadProfile = async () => {
    setIsLoading(true);
    const res = await apiClient.get<DoctorProfileResponse>("/doctors/me");
    setIsLoading(false);

    if (res.success && res.data) {
      setProfile(res.data);
      setFullName(res.data.full_name || "");
      setHeadline(res.data.headline || "");
      setYearsOfExp(res.data.years_of_experience ?? "");
      setCurrentOrg(res.data.current_organization || "");
      setBio(res.data.bio || "");
      setWebsite(res.data.website || "");
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSaveGeneral = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMsg(null);

    const res = await apiClient.put("/doctors/me", {
      full_name: fullName,
      headline,
      years_of_experience: yearsOfExp !== "" ? Number(yearsOfExp) : undefined,
      current_organization: currentOrg,
      bio,
      website,
    });

    setIsSaving(false);
    if (res.success) {
      setStatusMsg("Profile updated successfully!");
      loadProfile();
    }
  };

  const handleAddEducation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eduDegree || !eduInst) return;

    await apiClient.post("/doctors/me/education", {
      degree: eduDegree,
      institution: eduInst,
      start_year: Number(eduStartYear),
      end_year: eduEndYear !== "" ? Number(eduEndYear) : undefined,
    });

    setEduDegree("");
    setEduInst("");
    loadProfile();
  };

  const handleDeleteEducation = async (id: string) => {
    await apiClient.delete(`/doctors/me/education/${id}`);
    loadProfile();
  };

  const handleAddExperience = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!expTitle || !expOrg) return;

    await apiClient.post("/doctors/me/experience", {
      job_title: expTitle,
      organization: expOrg,
      start_date: expStartDate,
      is_current: expIsCurrent,
    });

    setExpTitle("");
    setExpOrg("");
    loadProfile();
  };

  const handleDeleteExperience = async (id: string) => {
    await apiClient.delete(`/doctors/me/experience/${id}`);
    loadProfile();
  };

  const handleAddPublication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pubTitle) return;

    await apiClient.post("/doctors/me/publications", {
      title: pubTitle,
      journal: pubJournal || undefined,
      publication_url: pubUrl || undefined,
    });

    setPubTitle("");
    setPubJournal("");
    setPubUrl("");
    loadProfile();
  };

  const handleDeletePublication = async (id: string) => {
    await apiClient.delete(`/doctors/me/publications/${id}`);
    loadProfile();
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center text-sm text-slate-500">
        Loading doctor profile editor...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Edit Professional Profile
          </h1>
          <p className="text-xs text-slate-500">
            Manage your credentials, clinical history, and publications
          </p>
        </div>

        {profile && (
          <Link href={`/doctors/${profile.slug}`}>
            <Button variant="outline" size="sm" className="flex items-center gap-1 text-xs">
              View Public Profile <ExternalLink className="w-3.5 h-3.5" />
            </Button>
          </Link>
        )}
      </div>

      {/* Profile Completion Bar */}
      {profile && <ProfileCompletionBar percentage={profile.profile_completion} />}

      {/* Tabs */}
      <div className="flex bg-slate-200/80 p-1.5 rounded-2xl gap-1 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab("general")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
            activeTab === "general" ? "bg-white text-teal-800 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <User className="w-4 h-4" /> Overview & Bio
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("education")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
            activeTab === "education" ? "bg-white text-teal-800 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <GraduationCap className="w-4 h-4" /> Education ({profile?.education?.length || 0})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("experience")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
            activeTab === "experience" ? "bg-white text-teal-800 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Briefcase className="w-4 h-4" /> Experience ({profile?.experience?.length || 0})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("publications")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all shrink-0 ${
            activeTab === "publications" ? "bg-white text-teal-800 shadow-sm" : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <BookOpen className="w-4 h-4" /> Publications ({profile?.publications?.length || 0})
        </button>
      </div>

      {statusMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {statusMsg}
        </div>
      )}

      {/* Tab: Overview & Bio */}
      {activeTab === "general" && (
        <form onSubmit={handleSaveGeneral} className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Headline</label>
              <input
                type="text"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                placeholder="Senior Consultant Cardiologist"
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Current Hospital / Clinic</label>
              <input
                type="text"
                value={currentOrg}
                onChange={(e) => setCurrentOrg(e.target.value)}
                placeholder="AIIMS New Delhi"
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Years of Clinical Experience</label>
              <input
                type="number"
                min="0"
                max="70"
                value={yearsOfExp}
                onChange={(e) => setYearsOfExp(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Professional Biography</label>
            <textarea
              rows={5}
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Detail your clinical focus, surgical expertise, and background..."
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
          </div>

          <div className="flex justify-end">
            <Button type="submit" variant="primary" size="md" isLoading={isSaving}>
              Save Profile Changes
            </Button>
          </div>
        </form>
      )}

      {/* Tab: Education */}
      {activeTab === "education" && (
        <div className="space-y-6">
          <form onSubmit={handleAddEducation} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-teal-600" /> Add Medical Degree
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input
                type="text"
                required
                placeholder="Degree (e.g. MD Cardiology, MBBS)"
                value={eduDegree}
                onChange={(e) => setEduDegree(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="text"
                required
                placeholder="Institution (e.g. AIIMS New Delhi)"
                value={eduInst}
                onChange={(e) => setEduInst(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="number"
                placeholder="Start Year"
                value={eduStartYear}
                onChange={(e) => setEduStartYear(Number(e.target.value))}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="number"
                placeholder="Graduation Year"
                value={eduEndYear}
                onChange={(e) => setEduEndYear(e.target.value === "" ? "" : Number(e.target.value))}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
            </div>
            <Button type="submit" variant="primary" size="sm">Add Degree</Button>
          </form>

          {/* List existing */}
          <div className="space-y-3">
            {(profile?.education || []).map((edu: any) => (
              <div key={edu.id} className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center justify-between shadow-sm">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">{edu.degree}</h4>
                  <p className="text-xs text-slate-500">{edu.institution} ({edu.start_year} – {edu.end_year || "Present"})</p>
                </div>
                <button type="button" onClick={() => handleDeleteEducation(edu.id)} className="text-rose-500 hover:text-rose-700 p-2">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Experience */}
      {activeTab === "experience" && (
        <div className="space-y-6">
          <form onSubmit={handleAddExperience} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-teal-600" /> Add Clinical Position
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input
                type="text"
                required
                placeholder="Job Title (e.g. Senior Consultant)"
                value={expTitle}
                onChange={(e) => setExpTitle(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="text"
                required
                placeholder="Hospital / Clinic Name"
                value={expOrg}
                onChange={(e) => setExpOrg(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="date"
                value={expStartDate}
                onChange={(e) => setExpStartDate(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <div className="flex items-center gap-2 px-2">
                <input
                  type="checkbox"
                  id="currExp"
                  checked={expIsCurrent}
                  onChange={(e) => setExpIsCurrent(e.target.checked)}
                  className="rounded text-teal-600"
                />
                <label htmlFor="currExp" className="text-xs font-semibold text-slate-700">Currently practicing here</label>
              </div>
            </div>
            <Button type="submit" variant="primary" size="sm">Add Experience</Button>
          </form>

          {/* List existing */}
          <div className="space-y-3">
            {(profile?.experience || []).map((exp: any) => (
              <div key={exp.id} className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center justify-between shadow-sm">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">{exp.job_title}</h4>
                  <p className="text-xs text-slate-500">{exp.organization} • {exp.is_current ? "Present" : exp.end_date}</p>
                </div>
                <button type="button" onClick={() => handleDeleteExperience(exp.id)} className="text-rose-500 hover:text-rose-700 p-2">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Publications */}
      {activeTab === "publications" && (
        <div className="space-y-6">
          <form onSubmit={handleAddPublication} className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-teal-600" /> Add Publication / Research Paper
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input
                type="text"
                required
                placeholder="Paper Title"
                value={pubTitle}
                onChange={(e) => setPubTitle(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm sm:col-span-2"
              />
              <input
                type="text"
                placeholder="Journal Name (e.g. NEJM, Lancet)"
                value={pubJournal}
                onChange={(e) => setPubJournal(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
              <input
                type="url"
                placeholder="Publication URL / DOI link"
                value={pubUrl}
                onChange={(e) => setPubUrl(e.target.value)}
                className="px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm"
              />
            </div>
            <Button type="submit" variant="primary" size="sm">Add Publication</Button>
          </form>

          {/* List existing */}
          <div className="space-y-3">
            {(profile?.publications || []).map((pub: any) => (
              <div key={pub.id} className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center justify-between shadow-sm">
                <div>
                  <h4 className="text-sm font-bold text-slate-900">{pub.title}</h4>
                  {pub.journal && <p className="text-xs text-slate-500">{pub.journal}</p>}
                </div>
                <button type="button" onClick={() => handleDeletePublication(pub.id)} className="text-rose-500 hover:text-rose-700 p-2">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
