"use client";

import { useState } from "react";
import { contentItemValidator } from "@/validators";
import { z } from "zod";
import classNames from "classnames";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { serverFetch, serverPost } from "@/util/http";
import { useAuth } from "@clerk/nextjs";

export default function ContentPicker() {
  const [selectedContentIds, setSelectedContentIds] = useState<number[]>([]);

  const { getToken } = useAuth();

  const { data } = useQuery({
    queryKey: ["onboarding", selectedContentIds],
    queryFn: async () => {
      const q =
        selectedContentIds.length > 0
          ? new URLSearchParams({
              existing_content: selectedContentIds.join(","),
            })
          : new URLSearchParams();
      return serverFetch(
        `/onboarding?${q.toString()}`,
        z.object({
          content: z.array(contentItemValidator),
        }),
        getToken,
      );
    },
  });

  const handleOnSubmit = async () => {
    const minDuration = 2000;
    const start = Date.now();
    await serverPost(
      `/onboarding`,
      { selected_content: selectedContentIds },
      getToken,
    );
    const duration = Date.now() - start;
    if (duration < minDuration) {
      await new Promise((resolve) =>
        setTimeout(resolve, minDuration - duration),
      );
    }
  };

  const router = useRouter();

  const { mutate, isPending: isSubmitting } = useMutation({
    mutationFn: handleOnSubmit,
    onSuccess: () => {
      router.push("/");
    },
  });

  return (
    <div>
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <Link href="/" className="cursor-pointer text-blue-500 underline">
          Exit onboarding
        </Link>
        <div>
          <h2 className="text-2xl font-bold mb-4">Get started</h2>
          <p className="text-slate-500">
            Pick 3 or more posts that seem interesting and we&apos;ll help you
            find more like them.
          </p>
        </div>
        <ul className="grid grid-cols-2 lg:grid-cols-4 grid-rows-[120px_120px] gap-4 w-full">
          {data ? (
            <>
              {data.content.map((contentItem) => (
                <button
                  key={contentItem.id}
                  onClick={() =>
                    setSelectedContentIds((prev) => {
                      if (prev.includes(contentItem.id)) {
                        return prev.filter((id) => id !== contentItem.id);
                      } else {
                        return [...prev, contentItem.id];
                      }
                    })
                  }
                >
                  <li
                    className={classNames(
                      "text-start bg-slate-100/20 p-4 cursor-pointer hover:bg-slate-200/30 h-full flex items-center rounded-md",
                      selectedContentIds.includes(contentItem.id) &&
                        "border-slate-400/50 border-2",
                    )}
                  >
                    {contentItem.title}
                  </li>
                </button>
              ))}
            </>
          ) : (
            <>
              {new Array(12).fill(null).map((_, i) => (
                <li key={i} className="skeleton w-full h-full"></li>
              ))}
            </>
          )}
        </ul>
        <div
          className={classNames({
            tooltip: selectedContentIds.length < 3,
          })}
          data-tip="Select 3 posts to continue"
        >
          <button
            className="btn"
            onClick={() => mutate()}
            disabled={selectedContentIds.length < 3}
          >
            {isSubmitting && <span className="loading loading-spinner"></span>}
            {isSubmitting ? "Preparing your feed..." : "Continue"}
          </button>
        </div>
      </main>
    </div>
  );
}
