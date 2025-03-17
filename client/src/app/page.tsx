import { contentItemValidator } from "@/validators";
import Link from "next/link";
import { z } from "zod";

export default async function Home() {
  const data = await fetch("http://127.0.0.1:8000/feed").then(async (res) =>
    z
      .object({
        content: z.array(contentItemValidator),
      })
      .parse(await res.json()),
  );

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <Link
          href="/onboarding"
          className="cursor-pointer text-blue-500 underline"
        >
          Repeat onboarding
        </Link>
        <h2 className="text-2xl font-bold">Welcome!</h2>
        <h2 className="text-xl">Your top posts</h2>
        <ul className="flex flex-col gap-4">
          {data.content.map((contentItem) => (
            <li
              key={contentItem.id}
              className="rounded-md border-slate-300 border-2 p-4"
            >
              <article>
                <h3 className="text-lg font-bold">{contentItem.title}</h3>
                <p className="text-sm">{contentItem.description}</p>
              </article>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}
