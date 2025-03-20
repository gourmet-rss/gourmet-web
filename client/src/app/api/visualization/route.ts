import { serverFetch } from "@/util/http";
import { auth } from "@clerk/nextjs/server";

export const GET = async () => {
  const { getToken } = await auth();

  const res = await serverFetch("/visualization", getToken);

  return res;
};
