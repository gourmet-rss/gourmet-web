"use client";

import { useAuth } from "@clerk/nextjs";
import { serverPost } from "@/util/http";
import { useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";

interface FeedbackButtonsProps {
  contentId: number;
  rating: number;
}

export default function FeedbackButtons({
  contentId,
  rating,
}: FeedbackButtonsProps) {
  const { getToken } = useAuth();
  const [clickedUp, setClickedUp] = useState(rating > 0);
  const [clickedDown, setClickedDown] = useState(rating < 0);

  const sendFeedback = async (rating: number) => {
    try {
      await serverPost(
        "/feedback",
        { content_id: contentId, rating },
        getToken,
      );
    } catch (error) {
      console.error(
        `Error sending feedback for ${contentId} (${rating}):`,
        error,
      );
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        className={`p-1.5 rounded-full transition-colors ${
          clickedUp
            ? "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400"
            : "text-gray-500 hover:text-green-600 hover:bg-green-50 dark:text-gray-400 dark:hover:text-green-400 dark:hover:bg-green-900/20"
        }`}
        aria-label="Like"
        onClick={() => {
          const rating = !clickedUp ? 1 : -1;
          sendFeedback(rating);
          setClickedUp(!clickedUp);
          setClickedDown(false);
        }}
      >
        <ThumbsUp size={18} className={clickedUp ? "fill-current" : ""} />
      </button>
      <button
        className={`p-1.5 rounded-full transition-colors ${
          clickedDown
            ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400"
            : "text-gray-500 hover:text-red-600 hover:bg-red-50 dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-900/20"
        }`}
        aria-label="Dislike"
        onClick={() => {
          const rating = !clickedDown ? -1 : 1;
          sendFeedback(rating);
          setClickedUp(false);
          setClickedDown(!clickedDown);
        }}
      >
        <ThumbsDown size={18} className={clickedDown ? "fill-current" : ""} />
      </button>
    </div>
  );
}
