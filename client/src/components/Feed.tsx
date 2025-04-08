"use client";

import { HTTPError, serverGet } from "@/util/http";
import { userContentItemValidator } from "@/validators";
import { z } from "zod";
import { redirect, usePathname } from "next/navigation";
import FeedbackButtons from "./FeedbackButtons";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import classNames from "classnames";
import { useEffect, useRef, useState } from "react";
import MoreLikeThisButton from "./MoreLikeThisButton";
import { decode } from "html-entities";

const feedGridClass = "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6";

export default function Feed({ flavourId }: { flavourId?: number }) {
  const { getToken } = useAuth();

  const [loadingPages, setLoadingPages] = useState(1);
  const [feedbackModalOpenForContentItem, setFeedbackModalOpenForContentItem] =
    useState<z.infer<typeof userContentItemValidator> | null>(null);
  const modalRef = useRef<HTMLDialogElement>(null);

  const [upvotedContentIds, setUpvotedContentIds] = useState<number[]>([]);
  const [downvotedContentIds, setDownvotedContentIds] = useState<number[]>([]);

  const path = usePathname();
  useEffect(() => {
    // scroll to top
    window.scrollTo(0, 0);
  }, [path]);

  const {
    data: content,
    error,
    refetch,
  } = useQuery({
    queryKey: ["feed", flavourId],
    refetchOnMount: "always",
    queryFn: async (): Promise<z.infer<typeof userContentItemValidator>[]> => {
      setLoadingPages((prev) => prev + 1);
      const queryParams = new URLSearchParams();
      if (content) {
        queryParams.append(
          "recommendation_ids",
          (content ?? []).map((x) => x.id).join(","),
        );
      }
      if (flavourId) {
        queryParams.append("flavour_id", flavourId.toString());
      }
      const res = await serverGet(
        `/feed?${queryParams.toString()}`,
        z.object({
          content: z.array(userContentItemValidator),
        }),
        getToken,
      ).catch((res) => {
        throw new HTTPError(res);
      });

      if (res.content.length === 0) {
        setLoadingPages(0);
      } else {
        setLoadingPages((prev) => prev - 1);
      }
      return [...(content ?? []), ...res.content];
    },
  });

  const filteredContent = content?.filter(
    (contentItem) => !downvotedContentIds.includes(contentItem.id),
  );

  if (error instanceof HTTPError && error.status === 409) {
    return redirect("/onboarding");
  }

  if (!filteredContent) {
    return (
      <div className={classNames(feedGridClass, "w-full")}>
        <LoadingTiles />
      </div>
    );
  }

  if (filteredContent.length === 0) {
    return (
      <div className="w-full">
        <p className="text-gray-500 dark:text-gray-400 text-center text-lg">
          No content found
        </p>
      </div>
    );
  }

  return (
    <ul className={feedGridClass}>
      <dialog ref={modalRef} className="modal">
        {feedbackModalOpenForContentItem && (
          <>
            <div className="modal-box">
              <h3 className="text-lg font-bold">
                {feedbackModalOpenForContentItem.title}
              </h3>
              <p className="my-2">What did you think of the article?</p>
              <FeedbackButtons
                contentId={feedbackModalOpenForContentItem.id}
                rating={feedbackModalOpenForContentItem.rating}
                withLabels
                onFeedbackSent={(rating) => {
                  setFeedbackModalOpenForContentItem(null);
                  modalRef.current?.close();
                  if (rating > 0) {
                    setUpvotedContentIds((prev) => [
                      ...prev,
                      feedbackModalOpenForContentItem.id,
                    ]);
                  } else if (rating < 0) {
                    setDownvotedContentIds((prev) => [
                      ...prev,
                      feedbackModalOpenForContentItem.id,
                    ]);
                  }
                }}
              />
            </div>
            <form method="dialog" className="modal-backdrop">
              <button>close</button>
            </form>
          </>
        )}
      </dialog>
      {filteredContent.map((contentItem) => {
        const rating = (() => {
          if (upvotedContentIds.includes(contentItem.id)) {
            return 1;
          }
          if (downvotedContentIds.includes(contentItem.id)) {
            return -1;
          }
          return contentItem.rating;
        })();
        return (
          <li
            key={contentItem.id}
            className="bg-white dark:bg-gray-900 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col h-full border border-gray-200 dark:border-gray-800"
          >
            {contentItem.media?.length ? (
              contentItem.media[0].type === "image" && (
                <div className="relative w-full h-48 overflow-hidden">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={contentItem.media[0].url}
                    alt={contentItem.media[0].type ?? ""}
                    width={100}
                    height={100}
                    className="h-full w-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  {contentItem.content_type &&
                    contentItem.content_type !== "article" &&
                    contentItem.content_type !== "unknown" && (
                      <div className="absolute top-0 left-0 bg-indigo-600 text-white px-3 py-1 text-xs uppercase tracking-wider font-bold">
                        {contentItem.content_type}
                      </div>
                    )}
                </div>
              )
            ) : (
              <div className="w-full h-48 bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center" />
            )}

            <div className="p-5 flex flex-col flex-grow">
              <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-3 space-x-2">
                <span className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">
                  {new URL(contentItem.url).hostname}
                </span>
                <span>•</span>
                <span>{new Date().toLocaleDateString()}</span>
              </div>

              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3 line-clamp-2 font-serif">
                {contentItem.title}
              </h3>

              <div
                className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-3 text-sm leading-relaxed article-content"
                dangerouslySetInnerHTML={{
                  __html: decode(contentItem.description),
                }}
              />

              <div className="mt-auto pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
                <a
                  className="inline-flex items-center text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium text-sm transition-colors"
                  href={contentItem.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => {
                    setFeedbackModalOpenForContentItem(contentItem);
                    modalRef.current?.showModal();
                  }}
                >
                  Read full article
                  <svg
                    className="w-4 h-4 ml-1"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </a>
                <div className="flex items-center space-x-2">
                  {!flavourId && (
                    <MoreLikeThisButton contentId={contentItem.id} />
                  )}
                  <FeedbackButtons
                    key={rating}
                    contentId={contentItem.id}
                    rating={rating}
                  />
                </div>
              </div>
            </div>
          </li>
        );
      })}
      {[...new Array(loadingPages)].map((_, i) => (
        <LoadingTiles key={i} onRefetch={refetch} />
      ))}
    </ul>
  );
}

function LoadingTiles({ onRefetch }: { onRefetch?: () => void }) {
  const firstTileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (onRefetch) {
      const firstItem = firstTileRef.current;
      if (firstItem) {
        const observer = new IntersectionObserver(
          (entries) => {
            if (entries[0].isIntersecting) {
              onRefetch();
            }
          },
          {
            rootMargin: "500px",
          },
        );
        observer.observe(firstItem);
        return () => {
          observer.disconnect();
        };
      }
    }
  }, [onRefetch]);

  return (
    <>
      {new Array(12).fill(null).map((_, i) => (
        <div
          ref={(ref) => {
            if (i === 0) {
              firstTileRef.current = ref;
            }
          }}
          key={i}
          className="skeleton w-full h-[400px]"
        ></div>
      ))}
    </>
  );
}
