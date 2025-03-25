import Feed from "@/components/Feed";

export default async function FlavourPage({
  params,
}: {
  params: Promise<{ flavourId: string }>;
}) {
  const { flavourId } = await params;

  return <Feed flavourId={Number(flavourId)} />;
}
