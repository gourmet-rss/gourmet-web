"use client";

import { useAuth } from "@clerk/nextjs";
import { serverPost } from "@/util/http";
import { useState } from "react";
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
    <div className="flex gap-2">
      <button
        className={`btn ${clickedUp ? "btn-primary-disabled" : "btn-primary"}`}
        onClick={() => {
          const rating = !clickedUp ? 1 : -1;
          sendFeedback(rating);
          setClickedUp(!clickedUp);
          setClickedDown(false);
        }}
      >
        +
      </button>
      <button
        className={`btn ${clickedDown ? "btn-secondary-disabled" : "btn-secondary"}`}
        onClick={() => {
          const rating = !clickedDown ? -1 : 1;
          sendFeedback(rating);
          setClickedUp(false);
          setClickedDown(!clickedDown);
        }}
      >
        -
      </button>
    </div>
  );
}
