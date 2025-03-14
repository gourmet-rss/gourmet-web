"use client";

import { useState } from "react";
import { contentItemValidator } from "@/validators";
import { z } from "zod";
import classNames from "classnames";
import { useMutation, useQuery } from "@tanstack/react-query";
import Button from "@/components/Button";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ContentPicker() {
  const [selectedContentIds, setSelectedContentIds] = useState<number[]>([]);

  const { data } = useQuery({
    queryKey: ["onboarding", selectedContentIds],
    queryFn: () => {
      const q =
        selectedContentIds.length > 0
          ? new URLSearchParams({
              existing_content: selectedContentIds.join(","),
            })
          : new URLSearchParams();
      return fetch(`http://127.0.0.1:8000/onboarding?${q.toString()}`).then(
        async (res) =>
          z
            .object({
              content: z.array(contentItemValidator),
            })
            .parse(await res.json()),
      );
    },
  });

  const handleOnSubmit = async () => {
    const minDuration = 2000;
    const start = Date.now();
    await fetch("http://127.0.0.1:8000/onboarding", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_content: selectedContentIds,
      }),
    });
    const duration = Date.now() - start;
    if (duration < minDuration) {
      await new Promise((resolve) =>
        setTimeout(resolve, minDuration - duration),
      );
    }
  };

  const router = useRouter();

  const {
    mutate,
    isPending: isSubmitting,
    data: result,
  } = useMutation({
    mutationFn: handleOnSubmit,
    onSuccess: () => {
      router.push("/");
    },
  });

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <Link href="/" className="cursor-pointer text-blue-500 underline">
          Exit onboarding
        </Link>
        <div>
          <h2 className="text-2xl font-bold mb-4">Get started</h2>
          <p className="text-slate-500">
            Pick a few posts that seem interesting and we&apos;ll help you find
            more like them.
          </p>
        </div>
        <ul className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
                  "rounded-md bg-slate-100 p-4 cursor-pointer",
                  selectedContentIds.includes(contentItem.id) && "bg-slate-200",
                )}
              >
                {contentItem.title}
              </li>
            </button>
          ))}
        </ul>
        <Button onClick={mutate}>
          {isSubmitting ? "Completing onboarding..." : "Submit"}
        </Button>
      </main>
    </div>
  );
}
