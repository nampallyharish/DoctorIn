"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Building2,
  ShieldCheck,
  UploadCloud,
  FileCheck,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowRight,
  User as UserIcon,
  Phone,
  Mail,
  MapPin,
  Globe,
  Building,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { apiClient } from "@/lib/api-client";
import { HospitalVerificationStatusResponse } from "@/types";

export default function HospitalApplyPage() {
  const [statusData, setStatusData] = useState<HospitalVerificationStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Section 1: Hospital Info
  const [name, setName] = useState("");
  const [hospitalType, setHospitalType] = useState("general");
  const [description, setDescription] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [website, setWebsite] = useState("");
  const [address, setAddress] = useState("");
  const [cityName, setCityName] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [yearEstablished, setYearEstablished] = useState<number>(2010);

  // Section 2: Organization Details
  const [legalEntityName, setLegalEntityName] = useState("");
  const [registrationNumber, setRegistrationNumber] = useState("");
  const [ownershipType, setOwnershipType] = useState("Private");
  const [accreditations, setAccreditations] = useState("NABH, NABL");

  // Section 3: Authorized Representative / Contact Person
  const [contactName, setContactName] = useState("");
  const [contactDesignation, setContactDesignation] = useState("Medical Superintendent");
  const [contactPhone, setContactPhone] = useState("");
  const [contactEmail, setContactEmail] = useState("");

  // Section 4: Facilities
  const [departments, setDepartments] = useState("Cardiology, Emergency, Pediatrics, Orthopedics");
  const [bedCount, setBedCount] = useState<number>(150);
  const [hasEmergencyServices, setHasEmergencyServices] = useState(true);

  // Section 5: Documents
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
    const res = await apiClient.get<HospitalVerificationStatusResponse>(
      "/hospitals/me/verification/status"
    );
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

      const formData = new FormData();
      formData.append("file", file);

      try {
        const uploadRes: any = await apiClient.post(
          "/hospitals/upload-document",
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
          setError(uploadRes.errors?.[0]?.message || "Failed to upload hospital document.");
        }
      } catch (err) {
        setError("Error uploading file. Please try again.");
      }
    }
  };

  const handleHospitalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !legalEntityName.trim() || !registrationNumber.trim()) {
      setError("Please fill in the hospital name, legal entity name, and license/registration number.");
      return;
    }
    if (!contactName.trim() || !contactPhone.trim() || !contactEmail.trim()) {
      setError("Please provide the authorized representative's contact information.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    const deptList = departments
      .split(",")
      .map((d) => d.trim())
      .filter(Boolean);

    const accredList = accreditations
      .split(",")
      .map((a) => a.trim())
      .filter(Boolean);

    const docList = uploadedDocKey
      ? [
          {
            document_type: "hospital_license",
            document_key: uploadedDocKey,
            original_name: uploadedDocName || "hospital_license.pdf",
            mime_type: uploadedDocMime || "application/pdf",
            size_bytes: uploadedDocSize || 0,
          },
        ]
      : [];

    const payload = {
      name: name.trim(),
      hospital_type: hospitalType,
      description: description.trim() || undefined,
      email: email.trim() || undefined,
      phone: phone.trim() || undefined,
      website: website.trim() || undefined,
      address: address.trim() || undefined,
      city_name: cityName.trim() || undefined,
      state: state.trim() || undefined,
      country: "India",
      pincode: pincode.trim() || undefined,
      year_established: Number(yearEstablished) || undefined,
      legal_entity_name: legalEntityName.trim(),
      registration_number: registrationNumber.trim(),
      ownership_type: ownershipType,
      accreditations: accredList,
      contact_person_name: contactName.trim(),
      contact_person_designation: contactDesignation.trim(),
      contact_person_phone: contactPhone.trim(),
      contact_person_email: contactEmail.trim(),
      departments: deptList,
      bed_count: Number(bedCount) || undefined,
      has_emergency_services: hasEmergencyServices,
      documents: docList,
    };

    const res = await apiClient.post("/hospitals/apply", payload);
    setIsSubmitting(false);

    if (res.success) {
      setSuccessMsg("Hospital application submitted successfully. Our verification team will review your credentials.");
      fetchStatus();
    } else {
      setError(res.errors?.[0]?.message || "Failed to submit hospital verification application.");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center text-sm text-slate-500">
        Loading hospital application...
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
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 text-white text-xs font-bold">
            <Building2 className="w-3.5 h-3.5" /> Institutional Healthcare Onboarding
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Register Hospital Account
          </h1>
          <p className="text-sm text-slate-500 font-medium">
            Verify your healthcare organization to manage medical departments, post career openings, and verify doctor affiliations.
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900">Hospital Verification Status</h2>
              <p className="text-xs text-slate-500">Institutional inspection and validation</p>
            </div>

            <div>
              {isVerified && (
                <Badge variant="success" className="text-xs px-3 py-1">
                  ✓ Verified Organization
                </Badge>
              )}
              {isPending && (
                <Badge variant="warning" className="text-xs px-3 py-1">⏳ Under Review</Badge>
              )}
              {isRejected && (
                <Badge variant="danger" className="text-xs px-3 py-1">❌ Rejected</Badge>
              )}
              {!isVerified && !isPending && !isRejected && (
                <Badge variant="default" className="text-xs px-3 py-1">Not Created</Badge>
              )}
            </div>
          </div>

          {isVerified && (
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-emerald-800">
                <p className="font-bold">Hospital profile verified!</p>
                <p>Your hospital is officially accredited on DoctorIn. You can manage departments and publish career posts.</p>
              </div>
            </div>
          )}

          {isPending && (
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 flex items-start gap-3">
              <Clock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="space-y-1 text-xs text-amber-800">
                <p className="font-bold">Institutional application under review</p>
                <p>Administrative officers are inspecting your establishment licenses and authorized contacts. Review concludes in 24–48 hours.</p>
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

        {/* Application Form */}
        {!isVerified && !isPending && (
          <form onSubmit={handleHospitalSubmit} className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-xs space-y-8">
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

            {/* 1. Hospital Information */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <Building2 className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  1. Hospital & Facility Information
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Hospital / Organization Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Metro Specialty Hospital & Research Center"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Hospital Type
                  </label>
                  <select
                    value={hospitalType}
                    onChange={(e) => setHospitalType(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="super_specialty">Super Specialty Hospital</option>
                    <option value="multi_specialty">Multi Specialty Hospital</option>
                    <option value="general">General Hospital</option>
                    <option value="clinic">Clinic / Polyclinic</option>
                    <option value="research_institute">Research Institute</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Year Established
                  </label>
                  <input
                    type="number"
                    min="1800"
                    max="2030"
                    value={yearEstablished}
                    onChange={(e) => setYearEstablished(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Official Contact Email
                  </label>
                  <input
                    type="email"
                    placeholder="admin@metrohospital.org"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Official Helpline / Phone
                  </label>
                  <input
                    type="tel"
                    placeholder="+91 22 8877 6655"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Full Address & City
                  </label>
                  <input
                    type="text"
                    placeholder="12 Medical Square, Bandra West, Mumbai"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            </div>

            {/* 2. Legal & Regulatory Details */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  2. Organization & Licensing
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Legal Entity Name (as registered)
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Metro Healthcare Services Pvt Ltd"
                    value={legalEntityName}
                    onChange={(e) => setLegalEntityName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Clinical Establishment / License Number
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CE-MH-2015-09941"
                    value={registrationNumber}
                    onChange={(e) => setRegistrationNumber(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Ownership Type
                  </label>
                  <select
                    value={ownershipType}
                    onChange={(e) => setOwnershipType(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="Private">Private Limited</option>
                    <option value="Public">Public Limited</option>
                    <option value="Trust">Trust / Non-Profit</option>
                    <option value="Government">Government / Public Health</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Accreditations (comma separated)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. NABH, NABL, JCI"
                    value={accreditations}
                    onChange={(e) => setAccreditations(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            </div>

            {/* 3. Authorized Representative */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <UserIcon className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  3. Authorized Representative
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Representative Full Name
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Dr. Rajesh Gupta"
                    value={contactName}
                    onChange={(e) => setContactName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Designation
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Medical Director / CEO"
                    value={contactDesignation}
                    onChange={(e) => setContactDesignation(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Representative Phone
                  </label>
                  <input
                    type="tel"
                    required
                    placeholder="+91 98765 43210"
                    value={contactPhone}
                    onChange={(e) => setContactPhone(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Representative Email
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="r.gupta@metrohospital.org"
                    value={contactEmail}
                    onChange={(e) => setContactEmail(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>
              </div>
            </div>

            {/* 4. Facilities */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <Building className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  4. Clinical Capacity & Facilities
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Active Departments (comma separated)
                  </label>
                  <input
                    type="text"
                    placeholder="Cardiology, Neurology, Oncology, Emergency"
                    value={departments}
                    onChange={(e) => setDepartments(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Total Bed Capacity
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={bedCount}
                    onChange={(e) => setBedCount(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  />
                </div>

                <div className="flex items-center pt-6">
                  <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-slate-700">
                    <input
                      type="checkbox"
                      checked={hasEmergencyServices}
                      onChange={(e) => setHasEmergencyServices(e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                    />
                    <span>24/7 Emergency & Trauma Services Available</span>
                  </label>
                </div>
              </div>
            </div>

            {/* 5. Document Upload */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                <FileCheck className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  5. Institutional License Upload
                </h3>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Upload Clinical License / Establishment Certificate (PDF, PNG, JPG, max 10MB)
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
                      {selectedFile ? selectedFile.name : "Click or drag & drop license certificate here"}
                    </p>
                    <p className="text-[11px] text-slate-400">
                      Stored in secure, encrypted storage. Only accessible to DoctorIn compliance officers.
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
                className="bg-slate-900 hover:bg-slate-800 text-white font-bold px-6"
                isLoading={isSubmitting}
              >
                Submit Hospital Application <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
