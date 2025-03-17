import { HTTPError, serverFetch } from "@/util/http";
import { contentItemValidator } from "@/validators";
import { z } from "zod";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function Feed() {
  const { getToken, sessionId } = await auth();

  if (!sessionId) {
    return redirect("/");
  }

  try {
    const data = await serverFetch(
      "/feed",
      z.object({
        content: z.array(contentItemValidator),
      }),
      getToken,
    );

    return (
      <ul className="flex flex-col gap-4">
        {data.content.map((contentItem) => (
          <li key={contentItem.id} className="card card-border">
            <article className="card-body">
              <h3 className="card-title">{contentItem.title}</h3>
              <p>{contentItem.description}</p>
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
