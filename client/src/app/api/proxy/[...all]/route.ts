import { SERVER_URL } from "@/util/http";
import { auth } from "@clerk/nextjs/server";
import { NextRequest } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { all: string[] } },
) {
  return handleRequest(request, params.all, "GET");
}

export async function POST(
  request: NextRequest,
  { params }: { params: { all: string[] } },
) {
  return handleRequest(request, params.all, "POST");
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { all: string[] } },
) {
  return handleRequest(request, params.all, "PUT");
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { all: string[] } },
) {
  return handleRequest(request, params.all, "DELETE");
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { all: string[] } },
) {
  return handleRequest(request, params.all, "PATCH");
}

async function handleRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string,
) {
  try {
    // Get the auth session
    const { getToken } = await auth();
    const token = await getToken();

    // Build the target URL
    const path = pathSegments.join("/");
    const url = new URL(path, SERVER_URL);

    // Preserve query parameters
    const searchParams = request.nextUrl.searchParams;
    searchParams.forEach((value, key) => {
      url.searchParams.append(key, value);
    });

    // Prepare headers
    const headers = new Headers(request.headers);

    // Add auth token if available
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    // Remove headers that would cause issues
    headers.delete("host");

    // Create fetch options
    const fetchOptions: RequestInit = {
      method,
      headers,
      redirect: "follow",
    };

    // Add body for methods that support it
    if (["POST", "PUT", "PATCH"].includes(method)) {
      const contentType = request.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        fetchOptions.body = JSON.stringify(await request.json());
      } else {
        fetchOptions.body = await request.text();
      }
    }

    // Forward the request to the backend
    const response = await fetch(url.toString(), fetchOptions);

    // Create a new response with the same status, headers, and body
    const responseHeaders = new Headers(response.headers);
    const responseData = await response.arrayBuffer();

    return new Response(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(JSON.stringify({ error: "Internal Server Error" }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }
}
