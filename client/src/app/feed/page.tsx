import { HTTPError, serverFetch } from "@/util/http";
import { userContentItemValidator } from "@/validators";
import { z } from "zod";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import Image from "next/image";

export default async function Feed() {
  const { getToken, sessionId } = await auth();

  if (!sessionId) {
    return redirect("/");
  }

  try {
    const data = await serverFetch(
      "/feed",
      z.object({
        content: z.array(userContentItemValidator),
      }),
      getToken,
    );

    return (
      <ul className="flex flex-col gap-4">
        {data.content.map((contentItem) => (
          <li key={contentItem.id} className="card card-border bg-slate-500/5">
            <article className="card-body">
              <h3 className="card-title">{contentItem.title}</h3>
              {contentItem.media?.length ? (
                (contentItem.media[0].medium === "image" ||
                  contentItem.media[0].type?.startsWith("image/")) && (
                  <div className="w-full h-48">
                    <Image
                      src={contentItem.media[0].url}
                      alt={
                        contentItem.media[0].medium ??
                        contentItem.media[0].type ??
                        ""
                      }
                      width={contentItem.media[0].width ?? 100}
                      height={contentItem.media[0].height ?? 100}
                      className="h-full w-auto object-cover mx-auto"
                    />
                  </div>
                )
              ) : (
                <div className="w-full h-4" />
              )}
              <p
                dangerouslySetInnerHTML={{ __html: contentItem.description }}
              />
              <div className="flex justify-between items-center gap-2">
                <a
                  className="link link-hover"
                  href={contentItem.url}
                  target="_blank"
                >
                  Read article ({new URL(contentItem.url).hostname})
                </a>
                <div className="flex gap-2">
                  <button className="btn btn-primary">+</button>
                  <button className="btn btn-secondary">-</button>
                </div>
              </div>
            </article>
          </li>
        ))}
      </ul>
    );
  } catch (error) {
    if (error instanceof HTTPError && error.status === 409) {
      return redirect("/onboarding");
    }
    throw error;
  }
}
