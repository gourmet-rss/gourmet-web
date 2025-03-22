import Sidebar from "@/components/Sidebar";
import { serverGet } from "@/util/http";
import { z } from "zod";
import { auth } from "@clerk/nextjs/server";
import { flavourValidator } from "@/validators";

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
    <div className="flex relative">
      <Sidebar flavours={flavours} />
      <main className="flex-1 max-w-6xl mx-auto">{children}</main>
    </div>
  );
}
