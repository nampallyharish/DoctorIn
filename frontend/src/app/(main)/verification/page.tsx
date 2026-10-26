"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  UploadCloud,
  FileText,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
  Info,
  Lock,
  User as UserIcon,
  Briefcase,
  GraduationCap,
  FileCheck,
  Building,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { apiClient } from "@/lib/api-client";
import { VerificationStatusResponse } from "@/types";

const STEPS = [
  { label: "Personal Information", icon: UserIcon },
  { label: "Professional Details", icon: Briefcase },
  { label: "Education & Credentials", icon: GraduationCap },
  { label: "Document Verification", icon: FileCheck },
];

export default function DoctorVerificationPage() {
  const [statusData, setStatusData] = useState<VerificationStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState(0);

  // Form State: Personal
  const [fullName, setFullName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [gender, setGender] = useState("male");
  const [bio, setBio] = useState("");

  // Form State: Professional
  const [specialization, setSpecialization] = useState("General Physician");
  const [subSpecialization, setSubSpecialization] = useState("");
  const [yearsOfExperience, setYearsOfExperience] = useState(3);
  const [currentHospital, setCurrentHospital] = useState("");
  const [designation, setDesignation] = useState("Consultant");
  const [areasOfExpertise, setAreasOfExpertise] = useState("");

  // Form State: Education
  const [degree, setDegree] = useState("MBBS");
  const [institution, setInstitution] = useState("");
  const [graduationYear, setGraduationYear] = useState(2018);

  // Form State: Medical Council Registration
  const [councilName, setCouncilName] = useState("National Medical Commission (NMC)");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [registrationState, setRegistrationState] = useState("");
  const [registrationCountry, setRegistrationCountry] = useState("IND");
  const [registrationDate, setRegistrationDate] = useState("");

  // Documents
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedDocKey, setUploadedDocKey] = useState<string | null>(null);
  const [uploadedDocName, setUploadedDocName] = useState<string | null>(null);
  const [uploadedDocMime, setUploadedDocMime] = useState<string | null>(null);
  const [uploadedDocSize, setUploadedDocSize] = useState<number | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchStatus = async () => {
    setIsLoading(true);
    const res = await apiClient.get<VerificationStatusResponse>("/doctors/me/verification/status");
    setIsLoading(false);
    if (res.success && res.data) {
      setStatusData(res.data);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 10 * 1024 * 1024) {
        setError("File size exceeds 10MB limit.");
        return;
      }
      setSelectedFile(file);
      setError(null);

      // Immediately upload file to secure storage
      const formData = new FormData();
      formData.append("file", file);

      try {
        const uploadRes: any = await apiClient.post(
          "/doctors/me/verification/upload-document",
          undefined,
          {
            body: formData,
            headers: {},
          }
        );

        if (uploadRes.success && uploadRes.data) {
          setUploadedDocKey(uploadRes.data.document_key);
          setUploadedDocName(uploadRes.data.document_original_name);
          setUploadedDocMime(uploadRes.data.document_mime_type);
          setUploadedDocSize(uploadRes.data.document_size_bytes);
        } else {
          setError(uploadRes.errors?.[0]?.message || "Failed to upload document.");
        }
      } catch (err) {
        setError("Error uploading document. Please try again.");
      }
    }
  };

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      setError("Please provide your full legal name.");
      return;
    }
    if (!registrationNumber.trim() || !councilName.trim()) {
      setError("Please provide your medical council and registration number.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    const expertiseList = areasOfExpertise
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const documentsList = uploadedDocKey
      ? [
          {
            document_type: "medical_license",
            document_key: uploadedDocKey,
            original_name: uploadedDocName || "medical_license.pdf",
            mime_type: uploadedDocMime || "application/pdf",
            size_bytes: uploadedDocSize || 0,
          },
        ]
      : [];

    const payload = {
      full_name: fullName.trim(),
      date_of_birth: dateOfBirth || undefined,
      gender: gender || undefined,
      bio: bio.trim() || undefined,
      specialization: specialization.trim(),
      sub_specialization: subSpecialization.trim() || undefined,
      years_of_experience: Number(yearsOfExperience),
      current_hospital: currentHospital.trim() || undefined,
      designation: designation.trim() || undefined,
      areas_of_expertise: expertiseList,
      education: [
        {
          degree: degree.trim(),
          institution: institution.trim() || "Medical College",
          graduation_year: Number(graduationYear),
        },
      ],
      council_name: councilName.trim(),
      registration_number: registrationNumber.trim(),
      registration_state: registrationState.trim() || undefined,
      registration_country: registrationCountry.trim() || "IND",
      registration_date: registrationDate || undefined,
      documents: documentsList,
    };

    const res = await apiClient.post("/doctors/me/verification/apply", payload);
    setIsSubmitting(false);

    if (res.success) {
      setSuccessMsg("Application submitted successfully. The administrative board will verify your credentials.");
      fetchStatus();
    } else {
      setError(res.errors?.[0]?.message || "Failed to submit doctor application.");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center text-sm text-slate-500">
        Loading verification portal...
      </div>
    );
  }

  const verStatus = statusData?.verification_status?.toLowerCase();
  const isVerified = verStatus === "verified";
  const isPending = verStatus === "pending" || verStatus === "under_review";
  const isRejected = verStatus === "rejected";

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-bold border border-blue-200">
            <ShieldCheck className="w-3.5 h-3.5" /> Doctor Verification & Credentialing
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Doctor Account Application
          </h1>
          <p className="text-sm text-slate-500 font-medium">
            Verify your medical registration to receive the <strong className="text-slate-800">DoctorIn Verified</strong> badge and peer privileges.
          </p>
        </div>

        {/* Current Status Card */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900">Application Status</h2>
              <p className="text-xs text-slate-500">Controlled by backend medical verification board</p>
            </div>

            <div>
              {isVerified && <VerifiedBadge size="lg" showText />}
              {isPending && (
                <Badge variant="warning" className="text-xs px-3 py-1">⏳ Under Review</Badge>
              )}
              {isRejected && (
                <Badge variant="danger" className="text-xs px-3 py-1">❌ Rejected</Badge>
              )}
              {!isVerified && !isPending && !isRejected && (
                <Badge variant="default" className="text-xs px-3 py-1">Not Applied</Badge>
              )}
            </div>
          </div>

          {isVerified && (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-emerald-800">
                <p className="font-bold">Your medical license has been verified!</p>
                <p>Your account now holds verified doctor privileges, clinical badges, and peer-to-peer messaging.</p>
              </div>
            </div>
          )}

          {isPending && (
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 flex items-start gap-3">
              <Clock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-amber-800">
                <p className="font-bold">Your verification is currently under review</p>
                <p>Our credential verification team is reviewing your registration documents. Approvals typically complete within 24–48 hours.</p>
              </div>
            </div>
          )}

          {isRejected && statusData?.admin_notes && (
            <div className="p-4 bg-rose-50 rounded-xl border border-rose-200 space-y-1 text-xs text-rose-800">
              <p className="font-bold flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-600" /> Rejection Feedback:
              </p>
              <p>{statusData.admin_notes}</p>
            </div>
          )}
        </div>

        {/* Multi-Section Application Form (if not verified and not pending) */}
        {!isVerified && !isPending && (
          <form onSubmit={handleApplySubmit} className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-8">
            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
                {error}
              </div>
            )}

            {successMsg && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-700 text-xs font-medium">
                {successMsg}
              </div>
            )}

            {/* Section 1: Personal Details */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <UserIcon className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  1. Personal Identity
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Full Legal Name (as on Medical Certificate)
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Dr. Sarah Jenkins"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Gender
                  </label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer_not_to_say">Prefer not to say</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Section 2: Professional Details */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <Briefcase className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  2. Professional Specialization & Practice
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Primary Specialization
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Cardiology, Neurology, Pediatrics"
                    value={specialization}
                    onChange={(e) => setSpecialization(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Sub-Specialization (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Interventional Cardiology"
                    value={subSpecialization}
                    onChange={(e) => setSubSpecialization(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Years of Clinical Experience
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={yearsOfExperience}
                    onChange={(e) => setYearsOfExperience(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Designation / Title
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Senior Resident, Consultant"
                    value={designation}
                    onChange={(e) => setDesignation(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Current Hospital / Clinic
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. City Apollo Hospital"
                    value={currentHospital}
                    onChange={(e) => setCurrentHospital(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            </div>

            {/* Section 3: Education & Medical Council Registration */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <GraduationCap className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  3. Education & Medical Council Registration
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Primary Medical Degree
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="MBBS / MD / MS"
                    value={degree}
                    onChange={(e) => setDegree(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Medical College / Institution
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. AIIMS New Delhi"
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Registration Number
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. NMC-2018-99412"
                    value={registrationNumber}
                    onChange={(e) => setRegistrationNumber(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Medical Council / Authority
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. National Medical Commission / State Medical Council"
                    value={councilName}
                    onChange={(e) => setCouncilName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            </div>

            {/* Section 4: Document Upload */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <FileCheck className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  4. Verification Document Upload
                </h3>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Upload Medical Registration / License Certificate (PDF or Image, max 10MB)
                </label>
                <div className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-2xl p-6 text-center transition-colors bg-slate-50 cursor-pointer relative">
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="space-y-2">
                    <UploadCloud className="w-8 h-8 text-blue-600 mx-auto" />
                    <p className="text-xs font-semibold text-slate-800">
                      {selectedFile ? selectedFile.name : "Click or drag & drop certificate here"}
                    </p>
                    <p className="text-[11px] text-slate-400">
                      Encrypted and privately stored. Only accessible to DoctorIn verification reviewers.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100">
              <Button
                type="submit"
                variant="primary"
                size="md"
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6"
                isLoading={isSubmitting}
              >
                Submit Doctor Application <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
