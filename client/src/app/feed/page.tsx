import { HTTPError, serverGet } from "@/util/http";
import { userContentItemValidator } from "@/validators";
import { z } from "zod";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Image from "next/image";
import FeedbackButtons from "./FeedbackButtons";

export const feedGridClass =
  "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6";

export default async function Feed() {
  const { getToken, sessionId } = await auth();

  if (!sessionId) {
    return redirect("/");
  }

  try {
    const data = await serverGet(
      "/feed",
      z.object({
        content: z.array(userContentItemValidator),
      }),
      getToken,
    );

    return (
      <div className={feedGridClass}>
        {data.content.map((contentItem) => (
          <div
            key={contentItem.id}
            className="bg-white dark:bg-gray-900 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col h-full border border-gray-200 dark:border-gray-800"
          >
            {contentItem.media?.length ? (
              (contentItem.media[0].medium === "image" ||
                contentItem.media[0].type?.startsWith("image/")) && (
                <div className="relative w-full h-48 overflow-hidden">
                  <Image
                    src={contentItem.media[0].url}
                    alt={
                      contentItem.media[0].medium ??
                      contentItem.media[0].type ??
                      ""
                    }
                    width={contentItem.media[0].width ?? 100}
                    height={contentItem.media[0].height ?? 100}
                    className="h-full w-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  <div className="absolute top-0 left-0 bg-indigo-600 text-white px-3 py-1 text-xs uppercase tracking-wider font-bold">
                    Featured
                  </div>
                </div>
              )
            ) : (
              <div className="w-full h-48 bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center">
                <span className="text-white text-lg font-bold">
                  Gourmet Article
                </span>
              </div>
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
                dangerouslySetInnerHTML={{ __html: contentItem.description }}
              />

              <div className="mt-auto pt-4 border-t border-gray-100 dark:border-gray-800 flex justify-between items-center">
                <a
                  className="inline-flex items-center text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium text-sm transition-colors"
                  href={contentItem.url}
                  target="_blank"
                  rel="noopener noreferrer"
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
                <FeedbackButtons
                  contentId={contentItem.id}
                  rating={contentItem.rating}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  } catch (error) {
    if (error instanceof HTTPError && error.status === 409) {
      return redirect("/onboarding");
    }
    throw error;
  }
}
