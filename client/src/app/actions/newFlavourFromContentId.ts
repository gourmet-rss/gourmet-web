"use server";

import { auth } from "@clerk/nextjs/server";
import { serverPost } from "@/util/http";
import { z } from "zod";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export default async function newFlavourFromContentId(contentId: number) {
  const { getToken } = await auth();

  const { id: flavourId } = await serverPost(
    `/flavours`,
    {
      content_id: contentId,
    },
    getToken,
    z.object({ id: z.number() }),
  );

  revalidatePath("/flavours");

  return redirect(`/flavours/${flavourId}`);
}
