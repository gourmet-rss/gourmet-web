"use client";

import { useAuth } from "@clerk/nextjs";
import { serverPost } from "@/util/http";
import { useState } from "react";
interface FeedbackButtonsProps {
  contentId: number;
}

export default function FeedbackButtons({ contentId }: FeedbackButtonsProps) {
  const { getToken } = useAuth();
  const [clickedUp, setClickedUp] = useState(false);
  const [clickedDown, setClickedDown] = useState(false);

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
        className="btn btn-primary"
        onClick={() => {
          sendFeedback(1);
          setClickedUp(true);
          setClickedDown(false);
        }}
        disabled={clickedUp}
      >
        +
      </button>
      <button
        className="btn btn-secondary"
        onClick={() => {
          sendFeedback(-1);
          setClickedUp(false);
          setClickedDown(true);
        }}
        disabled={clickedDown}
      >
        -
      </button>
    </div>
  );
}
