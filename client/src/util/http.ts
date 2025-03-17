import { ZodType } from "zod";

const SERVER_URL = "http://127.0.0.1:8000";

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
  const response = await fetch(`${SERVER_URL}${path}`, {
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
  const response = await fetch(`${SERVER_URL}${path}`, {
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
