import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function Home() {
  const { sessionId } = await auth();

  if (sessionId) {
    return redirect("/feed");
  }

  return (
    <div className="flex justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-5">Welcome</h1>
        <p className="mb-5">Sign up or sign in to get started</p>
      </div>
    </div>
  );
}
