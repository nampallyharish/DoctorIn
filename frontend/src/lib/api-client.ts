import { API_BASE_URL } from "./constants";

export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  meta?: {
    page?: number;
    per_page?: number;
    total?: number;
    total_pages?: number;
    cursor?: string;
    has_next?: boolean;
  };
  errors?: Array<{
    code: string;
    message: string;
    field?: string;
    details?: Record<string, any>;
  }>;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("doctorin_access_token");
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getToken();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    // 15-second request timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetch(url, {
        ...options,
        signal: options.signal || controller.signal,
        headers,
      });

      clearTimeout(timeoutId);

      let data: any;
      try {
        data = await response.json();
      } catch (jsonErr) {
        if (!response.ok) {
          return {
            success: false,
            data: null,
            errors: [
              {
                code: `HTTP_${response.status}`,
                message: `Server returned status ${response.status}: ${response.statusText}`,
              },
            ],
          };
        }
        return {
          success: false,
          data: null,
          errors: [
            {
              code: "PARSE_ERROR",
              message: "Invalid response format from server",
            },
          ],
        };
      }

      return data;
    } catch (error: any) {
      clearTimeout(timeoutId);

      if (error?.name === "AbortError") {
        return {
          success: false,
          data: null,
          errors: [
            {
              code: "TIMEOUT_ERROR",
              message: "Request timed out. Please check your connection and try again.",
            },
          ],
        };
      }

      const isConnectionError =
        error?.message?.includes("Failed to fetch") ||
        error?.message?.includes("NetworkError") ||
        error?.name === "TypeError";

      return {
        success: false,
        data: null,
        errors: [
          {
            code: "NETWORK_ERROR",
            message: isConnectionError
              ? "Unable to connect to DoctorIn. Please try again."
              : error?.message || "Failed to communicate with server",
          },
        ],
      };
    }
  }

  get<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  post<T>(endpoint: string, body?: any, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  put<T>(endpoint: string, body?: any, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  delete<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new APIClient();
