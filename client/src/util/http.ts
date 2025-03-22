import deepmerge from "deepmerge";
import { ZodType } from "zod";

export const SERVER_URL = process.env.SERVER_URL || "http://127.0.0.1:8000";

async function getHeaders(getToken: () => Promise<string | null>) {
  const headers: Record<string, string> = {};
  if (typeof window === "undefined") {
    const token = await getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
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

export async function serverFetch(
  path: string,
  getToken: () => Promise<string | null>,
  options?: RequestInit,
) {
  // Use the proxy route handler when on the client side
  const url =
    typeof window === "undefined"
      ? `${SERVER_URL}${path}`
      : `/api/proxy${path}`;

  const opts: RequestInit = {
    headers: await getHeaders(getToken),
  };

  const finalOpts = deepmerge(opts, options || {});

  const response = await fetch(url, finalOpts);

  return response;
}

export async function serverGet<T>(
  path: string,
  validator: ZodType<T>,
  getToken: () => Promise<string | null>,
) {
  const response = await serverFetch(path, getToken);

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
  const response = await serverFetch(path, getToken, {
    method: "POST",
    body: JSON.stringify(requestData),
    headers: {
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

export async function serverDelete<T>(
  path: string,
  getToken: () => Promise<string | null>,
  validator?: ZodType<T> | null,
) {
  const response = await serverFetch(path, getToken, {
    method: "DELETE",
    headers: {
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
