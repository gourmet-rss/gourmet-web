"use client";

import { useState, useEffect } from "react";
import { serverGet } from "@/util/http";
import { userContentItemValidator } from "@/validators";
import { z } from "zod";
import { useAuth } from "@clerk/nextjs";
import { BarChart, X, ChevronUp } from "lucide-react";

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
        className="fixed bottom-6 right-6 z-50 bg-indigo-600 hover:bg-indigo-700 text-white p-3 rounded-full shadow-lg transition-all duration-300 flex items-center justify-center"
        aria-label={`${open ? "Hide" : "Show"} embeddings visualization`}
        title={`${open ? "Hide" : "Show"} embeddings visualization`}
      >
        {open ? <X size={20} /> : <BarChart size={20} />}
      </button>
      
      {open && (
        <div className="fixed inset-0 z-40 bg-white dark:bg-gray-900 overflow-auto">
          <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6 border-b border-gray-200 dark:border-gray-800 pb-4">
              <h2 className="text-3xl font-bold font-serif text-gray-900 dark:text-gray-100">
                Content Embeddings Visualization
              </h2>
              <button 
                onClick={() => setOpen(false)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <ChevronUp size={24} />
                <span className="sr-only">Close</span>
              </button>
            </div>
            
            <div className="mb-8">
              <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">
                Top {k} Content Items:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {content.slice(0, k).map((item) => (
                  <div key={item.id} className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                    <h4 className="text-md font-bold text-gray-900 dark:text-gray-100 mb-2 line-clamp-1">{item.title}</h4>
                    <div
                      className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2"
                      dangerouslySetInnerHTML={{
                        __html: item.description.slice(0, 100) + "...",
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 overflow-hidden h-[calc(100vh-300px)]">
              <iframe src="/api/visualization" className="w-full h-full" title="Content embeddings visualization" />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
