export const APP_NAME = "DoctorIn";
export const APP_TAGLINE = "Connect with Verified Medical Professionals.";
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const USER_ROLES = {
  PATIENT: "patient",
  DOCTOR: "doctor",
  HOSPITAL_ADMIN: "hospital_admin",
  ADMIN: "admin",
} as const;

export const VERIFICATION_STATUS = {
  UNVERIFIED: "unverified",
  PENDING: "pending",
  UNDER_REVIEW: "under_review",
  ADDITIONAL_INFO_REQUIRED: "additional_info_required",
  VERIFIED: "verified",
  REJECTED: "rejected",
  SUSPENDED: "suspended",
} as const;
