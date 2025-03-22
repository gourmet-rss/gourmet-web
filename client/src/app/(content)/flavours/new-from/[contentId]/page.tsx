import { serverPost } from "@/util/http";
import { auth } from "@clerk/nextjs/server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";

export default async function NewFlavourFromContentIdPage({
  params,
}: {
  params: Promise<{ contentId: string }>;
}) {
  const { contentId } = await params;

  const { getToken } = await auth();

  const { id: flavourId } = await serverPost(
    `/flavours`,
    {
      content_id: parseInt(contentId),
    },
    getToken,
    z.object({ id: z.number() }),
  );

  revalidatePath("/flavours");

  return redirect(`/flavours/${flavourId}`);
}
