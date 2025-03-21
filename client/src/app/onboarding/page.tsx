"use client";

import { useState } from "react";
import { contentItemValidator } from "@/validators";
import { z } from "zod";
import classNames from "classnames";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { serverGet, serverPost } from "@/util/http";
import { useAuth } from "@clerk/nextjs";
import { ArrowLeft, Check } from "lucide-react";
import { motion } from "framer-motion";

const MIN_ITEMS = 3;

export default function ContentPicker() {
  const [selectedContentIds, setSelectedContentIds] = useState<number[]>([]);

  const { getToken } = useAuth();

  const [newContentIds, setNewContentIds] = useState<number[]>([]);

  const { data: content } = useQuery({
    queryKey: ["onboarding", selectedContentIds],
    placeholderData: (prev) => prev,
    queryFn: async (): Promise<z.infer<typeof contentItemValidator>[]> => {
      const q =
        selectedContentIds.length > 0
          ? new URLSearchParams({
              selected_content: selectedContentIds.join(","),
              unselected_content: content
                ? content
                    .map((c) => c.id)
                    .filter((id) => !selectedContentIds.includes(id))
                    .join(",")
                : "",
            })
          : new URLSearchParams();
      const newData = await serverGet(
        `/onboarding?${q.toString()}`,
        z.object({
          content: z.array(contentItemValidator),
        }),
        getToken,
      );
      if (!content) {
        return newData.content;
      }
      const newContentIds: number[] = [];
      const ret = content.map((existingItem) => {
        const match = newData.content.find(
          (item) => item.id === existingItem.id,
        );
        if (match) {
          return match;
        }
        const item = newData.content.pop()!;
        newContentIds.push(item.id);
        return item;
      });
      setNewContentIds(newContentIds);
      return ret;
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
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <Link
          href="/"
          className="flex items-center text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          <span>Back to feed</span>
        </Link>
      </div>

      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-3 text-gray-900 dark:text-white">
          Personalize your feed
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl">
          Pick 3 or more articles that interest you, and we&apos;ll curate
          content tailored to your preferences.
        </p>
        {selectedContentIds.length > 0 && (
          <div className="mt-3 text-sm font-medium">
            <span className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
              {selectedContentIds.length} selected
            </span>
          </div>
        )}
      </div>

      <div className="mb-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {content
            ? content.map((contentItem) => {
                const isSelected = selectedContentIds.includes(contentItem.id);
                return (
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
                    className="text-left w-full"
                  >
                    <motion.div
                      className={classNames(
                        "h-full p-5 rounded-lg transition-all duration-200 flex flex-col justify-between",
                        isSelected
                          ? "bg-indigo-50 dark:bg-indigo-900/30 border-2 border-indigo-500 shadow-md"
                          : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-sm",
                      )}
                      initial={
                        newContentIds.includes(contentItem.id)
                          ? { scale: 0.8, opacity: 0 }
                          : false
                      }
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{
                        type: "spring",
                        stiffness: 300,
                        damping: 20,
                        delay: newContentIds.includes(contentItem.id)
                          ? 0.1 * newContentIds.indexOf(contentItem.id)
                          : 0,
                      }}
                    >
                      <div className="flex-grow">
                        <h3 className="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">
                          {contentItem.title}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3">
                          {contentItem.description}
                        </p>
                      </div>
                      {isSelected && (
                        <div className="flex justify-end mt-3">
                          <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-indigo-500 text-white">
                            <Check className="h-4 w-4" />
                          </span>
                        </div>
                      )}
                    </motion.div>
                  </button>
                );
              })
            : Array(12)
                .fill(null)
                .map((_, i) => (
                  <div key={i} className="h-48 rounded-lg skeleton"></div>
                ))}
        </div>
      </div>

      <div className="flex justify-center">
        <div
          className={classNames({
            tooltip: selectedContentIds.length < MIN_ITEMS,
          })}
          data-tip={`Select at least ${MIN_ITEMS} items to continue`}
        >
          <button
            className={classNames(
              "btn btn-lg px-8",
              selectedContentIds.length >= MIN_ITEMS
                ? "btn-primary"
                : "btn-disabled",
            )}
            onClick={() => mutate()}
            disabled={selectedContentIds.length < MIN_ITEMS}
          >
            {isSubmitting && (
              <span className="loading loading-spinner mr-2"></span>
            )}
            {isSubmitting ? "Preparing your feed..." : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
