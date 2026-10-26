"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Stethoscope,
  Plus,
  TrendingUp,
  ShieldCheck,
  Building2,
  Users,
  Search,
} from "lucide-react";
import { PostCard } from "@/features/feed/components/PostCard";
import { CreatePostModal } from "@/features/feed/components/CreatePostModal";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { PostResponse } from "@/types";

export default function MedicalFeedPage() {
  const [posts, setPosts] = useState<PostResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchFeed = async () => {
    setIsLoading(true);
    const res = await apiClient.get<PostResponse[]>("/posts/feed?page=1&per_page=20");
    setIsLoading(false);
    if (res.success && res.data) {
      setPosts(res.data);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left / Main Feed Stream */}
        <div className="lg:col-span-8 space-y-6">
          {/* Create Post Prompt Box */}
          <div className="bg-white rounded-3xl p-4 sm:p-6 border border-slate-200 shadow-sm flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-teal-600 text-white flex items-center justify-center font-bold text-sm shrink-0">
              <Stethoscope className="w-5 h-5" />
            </div>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="flex-1 text-left px-4 py-3 bg-slate-50 hover:bg-slate-100/80 rounded-2xl border border-slate-200 text-xs font-medium text-slate-500 transition-colors"
            >
              Share a medical insight, case study, or research paper...
            </button>
            <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)} className="shrink-0 text-xs">
              <Plus className="w-4 h-4 mr-1" /> Post
            </Button>
          </div>

          {/* Posts Stream */}
          {isLoading ? (
            <div className="text-center py-20 text-sm text-slate-500 space-y-3">
              <div className="animate-spin w-8 h-8 border-4 border-teal-600 border-t-transparent rounded-full mx-auto" />
              <p>Loading medical feed updates...</p>
            </div>
          ) : posts.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 space-y-3">
              <TrendingUp className="w-8 h-8 text-teal-600 mx-auto" />
              <h3 className="text-base font-bold text-slate-900">Welcome to the Medical Feed</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Be the first to share clinical observations, surgery outcomes, or breakthrough research!
              </p>
              <Button variant="primary" size="sm" onClick={() => setIsModalOpen(true)}>
                Publish First Post
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </div>

        {/* Right Sticky Sidebar */}
        <div className="hidden lg:block lg:col-span-4 space-y-6 sticky top-24">
          {/* Verified Network Card */}
          <div className="bg-gradient-to-br from-teal-900 to-slate-900 text-white rounded-3xl p-6 shadow-md space-y-3">
            <div className="inline-flex items-center gap-1 text-xs font-bold text-teal-400 bg-teal-950/60 px-2.5 py-1 rounded-full border border-teal-800">
              <ShieldCheck className="w-3.5 h-3.5" /> DoctorIn Verification
            </div>
            <h3 className="text-sm font-bold">Peer-Reviewed Community</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Medical posts on DoctorIn are authored by certified doctors and verified medical institutions.
            </p>
            <Link href="/verification" className="block pt-1">
              <Button variant="primary" size="sm" className="w-full text-xs">
                Submit Your Verification
              </Button>
            </Link>
          </div>

          {/* Quick Discover Doctors Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Explore Network
            </h4>
            <div className="space-y-2 text-xs">
              <Link href="/doctors" className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 text-slate-700 font-medium">
                <span className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-teal-600" /> Doctor Directory
                </span>
                <span className="text-slate-400">→</span>
              </Link>
              <Link href="/search?specialization_slug=cardiology" className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 text-slate-700 font-medium">
                <span className="flex items-center gap-2">
                  <Stethoscope className="w-4 h-4 text-sky-600" /> Cardiologists
                </span>
                <span className="text-slate-400">→</span>
              </Link>
              <Link href="/search?verified_only=true" className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 text-slate-700 font-medium">
                <span className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" /> Verified Practitioners
                </span>
                <span className="text-slate-400">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Modal */}
      <CreatePostModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPostCreated={fetchFeed}
      />
    </div>
  );
}
