export default async function FeedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
      <div className="mb-8 border-b border-gray-200 dark:border-gray-800 pb-4 w-full px-4">
        <div className="max-w-6xl mx-auto py-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 font-serif">
            Today&apos;s Curated Feed
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2 italic">
            Personalized content, delivered fresh daily
          </p>
        </div>
        {children}
      </div>
    </main>
  );
}
