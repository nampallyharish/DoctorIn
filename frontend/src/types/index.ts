export type UserRole = "user" | "patient" | "doctor" | "hospital_admin" | "admin";

export type VerificationStatus =
  | "unverified"
  | "pending"
  | "under_review"
  | "additional_info_required"
  | "verified"
  | "rejected"
  | "suspended";

export interface User {
  id: string;
  email?: string;
  phone?: string;
  role: UserRole;
  status: string;
  email_verified: boolean;
  phone_verified: boolean;
  full_name?: string;
  profile_photo_url?: string;
}

export interface DoctorProfile {
  id: string;
  full_name: string;
  slug: string;
  headline?: string;
  profile_photo_key?: string;
  profile_photo_url?: string;
  bio?: string;
  years_of_experience?: number;
  current_organization?: string;
  website?: string;
  specializations?: string[];
  verification_status: VerificationStatus;
  verified_at?: string;
  profile_completion: number;
  education?: Array<{
    id: string;
    institution: string;
    degree: string;
    field_of_study?: string;
    start_year: number;
    end_year?: number;
  }>;
  experience?: Array<{
    id: string;
    organization: string;
    job_title: string;
    start_date: string;
    end_date?: string;
    is_current: boolean;
    description?: string;
  }>;
  publications?: Array<{
    id: string;
    title: string;
    journal?: string;
    publication_url?: string;
    publication_date?: string;
  }>;
}

export type DoctorProfileResponse = DoctorProfile;

export interface DoctorPublicProfileResponse {
  id: string;
  user_id: string;
  full_name: string;
  slug: string;
  headline?: string;
  profile_photo_key?: string;
  profile_photo_url?: string;
  bio?: string;
  years_of_experience?: number;
  current_organization?: string;
  city_name?: string;
  state_name?: string;
  country_name?: string;
  verification_status: VerificationStatus;
  verified_at?: string;
  primary_specialization?: string;
  specializations?: string[];
  education?: Array<{
    id: string;
    institution: string;
    degree: string;
    field_of_study?: string;
    start_year: number;
    end_year?: number;
  }>;
  experience?: Array<{
    id: string;
    organization: string;
    job_title: string;
    start_date: string;
    end_date?: string;
    is_current: boolean;
    description?: string;
  }>;
  achievements?: Array<{
    id: string;
    title: string;
    issuing_organization?: string;
    achievement_date?: string;
    description?: string;
  }>;
  publications?: Array<{
    id: string;
    title: string;
    journal?: string;
    publication_url?: string;
    publication_date?: string;
    abstract?: string;
  }>;
  certifications?: Array<{
    id: string;
    name: string;
    issuing_organization: string;
    issue_date?: string;
  }>;
  languages?: Array<{
    language: string;
    proficiency: string;
  }>;
  is_connected?: boolean;
  connection_status?: "none" | "pending" | "accepted" | "rejected" | "blocked";
}

export interface DoctorSearchResultItem {
  id: string;
  user_id: string;
  full_name: string;
  slug: string;
  headline?: string;
  profile_photo_key?: string;
  profile_photo_url?: string;
  primary_specialization?: string;
  specializations?: string[];
  years_of_experience?: number;
  current_organization?: string;
  city_name?: string;
  state_name?: string;
  country_name?: string;
  verification_status: VerificationStatus;
  verified_at?: string;
  bio?: string;
}

export interface LookupItem {
  id: string;
  name: string;
  slug?: string;
}

export interface AuditLogResponseItem {
  id: string;
  actor_id?: string;
  actor_name: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  created_at: string;
}

export interface AdminStatsResponse {
  total_users: number;
  total_doctors: number;
  total_verified_doctors: number;
  pending_verifications: number;
  total_hospitals: number;
  total_patients: number;
  active_jobs: number;
  pending_reports: number;
}

export interface AdminReportItem {
  id: string;
  reporter_id: string;
  reporter_name: string;
  target_type: string;
  target_id: string;
  reason: string;
  description?: string;
  status: string;
  created_at: string;
}

export interface AdminUserItem {
  id: string;
  email?: string;
  phone?: string;
  role: UserRole;
  status: string;
  is_active: boolean;
  name: string;
  slug?: string;
  verified: boolean;
  created_at: string;
}

export interface AdminVerificationQueueItem {
  id: string;
  doctor_id: string;
  doctor_name: string;
  doctor_slug: string;
  doctor_email?: string;
  doctor_phone?: string;
  specialization?: string;
  status: VerificationStatus;
  submitted_at: string;
  documents_count: number;
  documents?: Array<{
    id: string;
    document_type: string;
    document_key: string;
    original_name: string;
    size_bytes: number;
    mime_type: string;
    uploaded_at: string;
  }>;
}

export interface VerificationStatusResponse {
  doctor_id?: string | null;
  verification_status?: VerificationStatus | string | null;
  verified_at?: string | null;
  submitted_at?: string | null;
  admin_notes?: string | null;
  rejection_reason?: string | null;
  documents?: Array<{
    id: string;
    document_type: string;
    original_name: string;
    uploaded_at: string;
    download_url?: string;
  }>;
}

export interface HospitalVerificationStatusResponse {
  hospital_id?: string | null;
  hospital_name?: string | null;
  verification_status?: string | null;
  verified_at?: string | null;
  latest_request_id?: string | null;
  latest_request_status?: string | null;
  admin_notes?: string | null;
  rejection_reason?: string | null;
  submitted_at?: string | null;
  reviewed_at?: string | null;
  documents?: Array<{
    id: string;
    document_type: string;
    original_name: string;
    uploaded_at?: string;
    download_url?: string;
  }>;
}

export interface AdminHospitalVerificationQueueItem {
  request_id: string;
  hospital_id: string;
  hospital_name: string;
  hospital_type: string;
  legal_entity_name?: string;
  registration_number?: string;
  contact_person_name?: string;
  contact_person_email?: string;
  contact_person_phone?: string;
  city?: string;
  status: string;
  submitted_at: string;
  documents_count: number;
}


export interface PostResponse {
  id: string;
  author_id: string;
  author_doctor_id?: string;
  author_name: string;
  author_slug?: string;
  author_avatar_key?: string;
  author_verified: boolean;
  author_headline?: string;
  post_type: string;
  title?: string;
  content: string;
  media_keys?: string[];
  reactions_count: number;
  reaction_count?: number;
  comments_count: number;
  comment_count?: number;
  user_reaction?: string;
  created_at: string;
}

export interface PostCommentResponse {
  id: string;
  post_id: string;
  user_id: string;
  author_name: string;
  author_avatar_key?: string;
  author_verified: boolean;
  content: string;
  created_at: string;
}

export interface DepartmentResponse {
  id: string;
  hospital_id: string;
  name: string;
  description?: string;
  head_doctor_id?: string;
  created_at: string;
}

export interface HospitalResponse {
  id: string;
  name: string;
  slug: string;
  tagline?: string;
  hospital_type: string;
  about?: string;
  website?: string;
  email?: string;
  phone?: string;
  address_line1?: string;
  city_name?: string;
  total_beds?: number;
  accreditations: string[];
  verification_status: VerificationStatus;
  verified_at?: string;
  logo_key?: string;
  departments: DepartmentResponse[];
  created_at: string;
}

export interface JobPostingResponse {
  id: string;
  hospital_id: string;
  hospital_name: string;
  hospital_slug: string;
  hospital_logo_key?: string;
  hospital_verified: boolean;
  title: string;
  slug: string;
  employment_type: string;
  city_name?: string;
  min_experience_years: number;
  max_experience_years?: number;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  description: string;
  requirements?: string;
  benefits?: string;
  status: string;
  application_deadline?: string;
  views_count: number;
  applications_count: number;
  created_at: string;
}

export interface ParticipantSummary {
  doctor_id: string;
  user_id: string;
  full_name: string;
  slug: string;
  headline?: string;
  profile_photo_key?: string;
  verification_status: string;
}

export interface ConversationResponse {
  id: string;
  conversation_type: string;
  last_message_at?: string;
  participant: ParticipantSummary;
  last_message?: {
    content: string;
    sender_id: string;
    created_at: string;
  };
  unread_count: number;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_name: string;
  sender_avatar_key?: string;
  is_self: boolean;
  content: string;
  message_type: string;
  is_edited: boolean;
  created_at: string;
}
