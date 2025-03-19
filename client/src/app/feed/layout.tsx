import Link from "next/link";

export default async function FeedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
      <Link
        href="/onboarding"
        className="cursor-pointer text-blue-500 underline"
      >
        Repeat onboarding
      </Link>
      <h2 className="text-2xl font-bold">Your Top Posts</h2>
      {children}
    </main>
  );
}
