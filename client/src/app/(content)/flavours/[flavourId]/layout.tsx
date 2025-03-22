import { HTTPError, serverGet } from "@/util/http";
import { auth } from "@clerk/nextjs/server";
import { notFound, redirect } from "next/navigation";
import { z } from "zod";
import FlavourSettings from "./FlavourSettings";
import Link from "next/link";

export default async function FlavourLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ flavourId: string }>;
}) {
  const { sessionId, userId } = await auth();

  if (!userId) {
    return redirect("/");
  }

  const { getToken } = await auth();

  const { flavourId } = await params;

  const { flavour } = await serverGet(
    `/flavours/${flavourId}`,
    z.object({
      flavour: z.object({
        nickname: z.string(),
      }),
    }),
    getToken,
  ).catch((res) => {
    if (res.status === 404) {
      notFound();
    }
    throw new HTTPError(res);
  });

  if (!sessionId) {
    return redirect("/");
  }
  return (
    <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
      <div className="mb-8 border-b border-gray-200 dark:border-gray-800 pb-4 w-full px-4">
        <div className="max-w-6xl mx-auto py-8">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 mb-4"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to main feed
          </Link>

          <div className="flex justify-between items-center gap-4">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 font-serif">
              {flavour.nickname}
            </h1>
            <FlavourSettings flavourId={flavourId} />
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2 italic">
            Posts from this flavour
          </p>
        </div>
        {children}
      </div>
    </main>
  );
}
