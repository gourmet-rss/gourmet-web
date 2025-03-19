import { ZodType } from "zod";

export const SERVER_URL = process.env.SERVER_URL || "http://127.0.0.1:8000";

async function getHeaders(getToken: () => Promise<string | null>) {
  const headers = new Headers();
  if (typeof window === "undefined") {
    const token = await getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }
  return headers;
}

export class HTTPError extends Error {
  public readonly status: number;
  constructor(public readonly response: Response) {
    super(`HTTP error! status: ${response.status}`);
    this.name = "HTTPError";
    this.status = response.status;
  }
}

export async function serverFetch<T>(
  path: string,
  validator: ZodType<T>,
  getToken: () => Promise<string | null>,
) {
  // Use the proxy route handler when on the client side
  const url =
    typeof window === "undefined"
      ? `${SERVER_URL}${path}`
      : `/api/proxy${path}`;

  const headers = await getHeaders(getToken);

  const response = await fetch(url, {
    headers,
  });

  if (!response.ok) {
    throw new HTTPError(response);
  }
  const data = await response.json();
  return validator.parse(data);
}

export async function serverPost<T>(
  path: string,
  requestData: unknown,
  getToken: () => Promise<string | null>,
  validator?: ZodType<T> | null,
) {
  // Use the proxy route handler when on the client side
  const url =
    typeof window === "undefined"
      ? `${SERVER_URL}${path}`
      : `/api/proxy${path}`;

  const headers = await getHeaders(getToken);

  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify(requestData),
    headers: {
      ...headers,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new HTTPError(response);
  }
  if (validator) {
    const data = await response.json();
    return validator.parse(data);
  }
  return response.json();
}
