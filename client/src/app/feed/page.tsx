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
          <li key={contentItem.id} className="card card-border">
            <article className="card-body">
              <h3 className="card-title">{contentItem.title}</h3>
              {contentItem.image_url ? (
                <Image
                  src={contentItem.image_url}
                  alt={contentItem.image_text ?? ""}
                  width={100}
                  height={100}
                  className="w-full h-48 object-cover"
                />
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
