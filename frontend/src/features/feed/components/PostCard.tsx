"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ThumbsUp,
  Lightbulb,
  Heart,
  PartyPopper,
  MessageCircle,
  Share2,
  MoreVertical,
  Flag,
  Send,
  Building2,
} from "lucide-react";
import { VerifiedBadge } from "@/components/shared/VerifiedBadge";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { apiClient } from "@/lib/api-client";
import { PostCommentResponse, PostResponse } from "@/types";

interface PostCardProps {
  post: PostResponse;
  currentUserId?: string;
}

export const PostCard: React.FC<PostCardProps> = ({ post, currentUserId }) => {
  const [reactionCount, setReactionCount] = useState(post.reaction_count);
  const [userReaction, setUserReaction] = useState<string | null>(post.user_reaction || null);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<PostCommentResponse[]>([]);
  const [commentText, setCommentText] = useState("");
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [reported, setReported] = useState(false);

  const handleToggleReaction = async (type: string = "like") => {
    const prevReaction = userReaction;
    const isRemoving = prevReaction === type;

    // Optimistic UI update
    setUserReaction(isRemoving ? null : type);
    setReactionCount((prev: number = 0) => (isRemoving ? Math.max(0, prev - 1) : prevReaction ? prev : prev + 1));



    const res = await apiClient.post(`/posts/${post.id}/reactions`, {
      reaction_type: type,
    });

    if (!res.success) {
      // Revert on error
      setUserReaction(prevReaction);
      setReactionCount(post.reaction_count);
    }
  };

  const handleLoadComments = async () => {
    if (!showComments) {
      const res = await apiClient.get<PostCommentResponse[]>(`/posts/${post.id}/comments`);
      if (res.success && res.data) {
        setComments(res.data);
      }
    }
    setShowComments(!showComments);
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    setIsSubmittingComment(true);
    const res = await apiClient.post(`/posts/${post.id}/comments`, {
      content: commentText.trim(),
    });
    setIsSubmittingComment(false);

    if (res.success && res.data) {
      setComments([...comments, res.data as any]);
      setCommentText("");
    }
  };

  const handleReportPost = async () => {
    await apiClient.post(`/posts/${post.id}/report`, {
      reason: "inappropriate",
      description: "Flagged by user via feed action",
    });
    setReported(true);
  };

  return (
    <article className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
      {/* Author Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-600 to-sky-600 text-white font-bold text-base flex items-center justify-center shadow shrink-0">
            {post.author_name.split(" ").map((n: string) => n[0]).slice(0, 2).join("")}
          </div>

          <div className="space-y-0.5">
            <div className="flex items-center gap-1.5">
              {post.author_slug ? (
                <Link href={`/doctors/${post.author_slug}`} className="font-bold text-slate-900 text-sm hover:underline">
                  {post.author_name}
                </Link>
              ) : (
                <span className="font-bold text-slate-900 text-sm">{post.author_name}</span>
              )}
              {post.author_verified && <VerifiedBadge size="sm" />}
            </div>

            {post.author_headline && (
              <p className="text-xs text-slate-500 line-clamp-1">{post.author_headline}</p>
            )}
            <p className="text-[11px] text-slate-400">
              {new Date(post.created_at).toLocaleDateString()} • {post.post_type.replace("_", " ")}
            </p>
          </div>
        </div>

        {/* Post Options / Report */}
        <button
          type="button"
          onClick={handleReportPost}
          title="Report this post"
          className="text-slate-400 hover:text-rose-500 p-1.5 rounded-lg hover:bg-slate-50"
        >
          <Flag className={`w-4 h-4 ${reported ? "text-rose-500 fill-rose-500" : ""}`} />
        </button>
      </div>

      {/* Post Content */}
      <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line pt-1">
        {post.content}
      </div>

      {/* Stats Bar */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-100">
        <span className="flex items-center gap-1">
          <ThumbsUp className="w-3.5 h-3.5 text-teal-600" /> {reactionCount} reactions
        </span>
        <button type="button" onClick={handleLoadComments} className="hover:underline">
          {(post.comments_count ?? post.comment_count ?? 0) + comments.length} comments
        </button>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-100 text-xs font-semibold text-slate-600">
        <button
          type="button"
          onClick={() => handleToggleReaction("like")}
          className={`flex items-center justify-center gap-2 py-2 rounded-xl transition-colors ${
            userReaction === "like"
              ? "bg-teal-50 text-teal-700 font-bold"
              : "hover:bg-slate-50 text-slate-600"
          }`}
        >
          <ThumbsUp className={`w-4 h-4 ${userReaction === "like" ? "text-teal-600 fill-teal-600" : ""}`} />
          <span>Like</span>
        </button>

        <button
          type="button"
          onClick={handleLoadComments}
          className="flex items-center justify-center gap-2 py-2 rounded-xl hover:bg-slate-50 text-slate-600"
        >
          <MessageCircle className="w-4 h-4" />
          <span>Comment</span>
        </button>
      </div>

      {/* Comments Drawer */}
      {showComments && (
        <div className="space-y-4 pt-3 border-t border-slate-100">
          {/* Add Comment Input */}
          <form onSubmit={handleAddComment} className="flex gap-2">
            <input
              type="text"
              placeholder="Add your medical perspective..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500"
            />
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmittingComment} disabled={!commentText.trim()}>
              <Send className="w-3.5 h-3.5" />
            </Button>
          </form>

          {/* Comment List */}
          <div className="space-y-3 pt-2">
            {comments.map((c) => (
              <div key={c.id} className="p-3 bg-slate-50 rounded-2xl border border-slate-100 space-y-1 text-xs">
                <div className="flex items-center gap-1.5 font-bold text-slate-900">
                  <span>{c.author_name}</span>
                  {c.author_verified && <VerifiedBadge size="sm" />}
                  <span className="text-[10px] text-slate-400 font-normal ml-auto">
                    {new Date(c.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                <p className="text-slate-700 leading-normal">{c.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </article>
  );
};
