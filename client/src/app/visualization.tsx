"use client";

import { useState, useEffect } from "react";
import { serverGet } from "@/util/http";
import { userContentItemValidator } from "@/validators";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";

const k = 5;

const getContent = async (getToken: () => Promise<string | null>) =>
  await serverGet(
    "/feed",
    z.object({
      content: z.array(userContentItemValidator),
    }),
    getToken,
  );

export default function Visualization() {
  const [open, setOpen] = useState(false);
  const [content, setContent] = useState<
    z.infer<typeof userContentItemValidator>[]
  >([]);
  const { getToken } = useAuth();

  useEffect(() => {
    getContent(getToken).then((data) => setContent(data.content));
  }, [getToken]);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="btn btn-primary fixed bottom-4 left-20 z-50 shadow-md"
      >
        {open ? "Hide" : "Show"} embeddings visualisation
      </button>
      {open && (
        <div className="fixed top-0 left-0 w-full h-full z-40 bg-white">
          <div className="flex flex-col gap-4">
            <h2 className="text-2xl font-bold">
              The first {k} content items are:
            </h2>
            {content.slice(0, k).map((item) => (
              <div key={item.id}>
                <h3 className="text-md font-bold">{item.title}</h3>
                <p
                  className="text-sm"
                  dangerouslySetInnerHTML={{
                    __html: item.description.slice(0, 100) + "...",
                  }}
                />
              </div>
            ))}
          </div>
          <iframe src="/api/visualization" className="w-full h-full" />
        </div>
      )}
    </>
  );
}
