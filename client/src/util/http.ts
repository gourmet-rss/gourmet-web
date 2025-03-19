import { ZodType } from "zod";

export const SERVER_URL = process.env.SERVER_URL || "http://127.0.0.1:8000";

async function getServerUrl() {
  if (typeof window === "undefined") {
    return SERVER_URL;
  }
  // If on frontend, fetch the server URL from the API as it doesn't exist in the static frontend app
  const data = await fetch("/api/meta").then((res) => res.json());
  return data.serverUrl;
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
  const token = await getToken();
  const serverUrl = await getServerUrl();
  const response = await fetch(`${serverUrl}${path}`, {
    headers: token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {},
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
  const token = await getToken();
  const serverUrl = await getServerUrl();
  const response = await fetch(`${serverUrl}${path}`, {
    method: "POST",
    body: JSON.stringify(requestData),
    headers: token
      ? {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        }
      : {
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
