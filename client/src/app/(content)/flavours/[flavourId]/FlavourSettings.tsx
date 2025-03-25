import DeleteFlavourButton from "./DeleteFlavourButton";
import { serverDelete } from "@/util/http";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

interface FlavourSettingsProps {
  flavourId: string;
}

export default function FlavourSettings({ flavourId }: FlavourSettingsProps) {
  const onDelete = async () => {
    "use server";
    const { getToken } = await auth();
    await serverDelete(`/flavours/${flavourId}`, getToken);
    revalidatePath("/flavours");
    redirect("/");
  };

  return <DeleteFlavourButton onDelete={onDelete} />;
}
