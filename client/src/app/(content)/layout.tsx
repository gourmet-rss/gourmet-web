import { serverGet } from "@/util/http";
import { z } from "zod";
import { auth } from "@clerk/nextjs/server";
import { flavourValidator } from "@/validators";
import ContentLayoutClient from "@/app/(content)/ContentLayoutClient";
import Header from "@/components/Header";
import Visualization from "../visualization";

export default async function ContentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { getToken } = await auth();

  const { flavours } = await serverGet(
    "/flavours",
    z.object({ flavours: z.array(flavourValidator) }),
    getToken,
  );

  return (
    <>
      <Visualization />
      <Header hasSidebar />
      <ContentLayoutClient flavours={flavours}>{children}</ContentLayoutClient>
    </>
  );
}
