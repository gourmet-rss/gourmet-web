import { SERVER_URL } from "@/util/http";

export async function GET() {
  return Response.json({
    serverUrl: SERVER_URL,
  });
}
