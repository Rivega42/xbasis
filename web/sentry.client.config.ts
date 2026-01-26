import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Performance monitoring
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

  // Session replay (optional)
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  // Only enable in production
  enabled: process.env.NODE_ENV === "production",

  // Environment
  environment: process.env.NODE_ENV,

  // Disable PII
  sendDefaultPii: false,

  // Ignore common errors
  ignoreErrors: [
    // Browser extensions
    "top.GLOBALS",
    // Network errors
    "Network request failed",
    "Failed to fetch",
    "Load failed",
    // Cancelled requests
    "AbortError",
  ],
});
