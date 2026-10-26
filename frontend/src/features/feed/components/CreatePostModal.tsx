"use client";

import React, { useState } from "react";
import { Stethoscope, Image, BookOpen, Award, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";

interface CreatePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPostCreated: () => void;
}

export const CreatePostModal: React.FC<CreatePostModalProps> = ({
  isOpen,
  onClose,
  onPostCreated,
}) => {
  const [content, setContent] = useState("");
  const [postType, setPostType] = useState<string>("text");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setIsSubmitting(true);
    setError(null);

    const res = await apiClient.post("/posts", {
      content: content.trim(),
      post_type: postType,
      visibility: "public",
    });

    setIsSubmitting(false);

    if (res.success) {
      setContent("");
      onPostCreated();
      onClose();
    } else {
      setError(res.errors?.[0]?.message || "Failed to publish post.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-xl p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-6 relative">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-6 top-6 text-slate-400 hover:text-slate-600"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="space-y-1">
          <h2 className="text-lg font-extrabold text-slate-900">Share Professional Medical Update</h2>
          <p className="text-xs text-slate-500">Publish insights, clinical research, or achievements to the network</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-medium">
            {error}
          </div>
        )}

        {/* Post Type Selector */}
        <div className="flex bg-slate-100 p-1 rounded-xl text-xs font-semibold gap-1">
          {[
            { id: "text", label: "Insight", icon: Stethoscope },
            { id: "case_study", label: "Case Study", icon: FileText },
            { id: "publication", label: "Publication", icon: BookOpen },
            { id: "achievement", label: "Achievement", icon: Award },
          ].map((type) => (
            <button
              key={type.id}
              type="button"
              onClick={() => setPostType(type.id)}
              className={`flex-1 py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                postType === type.id
                  ? "bg-white text-teal-800 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <type.icon className="w-3.5 h-3.5" />
              <span>{type.label}</span>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            rows={6}
            required
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Share clinical observations, discuss medical advancements, or announce research findings..."
            className="w-full p-4 bg-slate-50 border border-slate-300 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white resize-none"
          />

          <div className="flex items-center justify-between pt-2 border-t border-slate-100">
            <p className="text-[11px] text-slate-400">
              Posts adhere to DoctorIn content moderation guidelines.
            </p>

            <div className="flex gap-2">
              <Button type="button" variant="ghost" size="sm" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting} disabled={!content.trim()}>
                Publish Post
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
