import { API_BASE_URL } from "./constants";

export const CLIENT_TIMEOUT_MS = 25000; // 25 seconds client UX timeout policy

export class ApiError extends Error {
  public code: "OFFLINE" | "TIMEOUT" | "SERVER_ERROR" | "VALIDATION_ERROR" | "MALFORMED_RESPONSE" | "UNKNOWN";
  public statusCode?: number;

  constructor(
    message: string,
    code: "OFFLINE" | "TIMEOUT" | "SERVER_ERROR" | "VALIDATION_ERROR" | "MALFORMED_RESPONSE" | "UNKNOWN",
    statusCode?: number
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.statusCode = statusCode;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  // Check browser online status before initiating external request
  const isLocal = url.includes("localhost") || url.includes("127.0.0.1");
  if (!isLocal && typeof navigator !== "undefined" && !navigator.onLine) {
    throw new ApiError(
      "No internet connection. You can continue editing your details. Feasibility analysis will run once you reconnect.",
      "OFFLINE"
    );
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, CLIENT_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      signal: controller.signal,
    });
  } catch (netErr: any) {
    clearTimeout(timeoutId);

    if (netErr?.name === "AbortError") {
      throw new ApiError(
        "The connection is taking too long. Your entered information is safely preserved.",
        "TIMEOUT"
      );
    }

    if (typeof navigator !== "undefined" && !navigator.onLine) {
      throw new ApiError(
        "Internet connection was lost during the request. Your information remains safely saved.",
        "OFFLINE"
      );
    }

    throw new ApiError(
      "GramaVise advisory service is temporarily unreachable. Please check your connection or try again shortly.",
      "SERVER_ERROR"
    );
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let errorMessage = "";
    let errorCode: ApiError["code"] = "SERVER_ERROR";

    if (typeof errorData.detail === "string") {
      errorMessage = errorData.detail;
    } else if (Array.isArray(errorData.detail)) {
      const messages = errorData.detail
        .map((item: any) => item.msg || item.message || (typeof item === "string" ? item : JSON.stringify(item)))
        .filter(Boolean);
      errorMessage = Array.from(new Set(messages)).join("; ");
    } else if (errorData.detail?.message) {
      errorMessage = errorData.detail.message;
    } else if (errorData.message) {
      errorMessage = errorData.message;
    } else if (response.status === 422) {
      errorMessage = "Invalid business or financial assumptions provided. Please verify your inputs.";
      errorCode = "VALIDATION_ERROR";
    } else if (response.status >= 500) {
      errorMessage = "GramaVise advisory service encountered an unexpected error. Your draft remains saved.";
      errorCode = "SERVER_ERROR";
    } else {
      errorMessage = `Server request failed (Status ${response.status}: ${response.statusText})`;
      errorCode = "UNKNOWN";
    }

    throw new ApiError(errorMessage, errorCode, response.status);
  }

  try {
    return await response.json() as T;
  } catch (parseErr) {
    throw new ApiError(
      "Received a malformed response from the advisory engine. Please retry.",
      "MALFORMED_RESPONSE",
      response.status
    );
  }
}
