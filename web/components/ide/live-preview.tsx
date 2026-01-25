"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  RefreshCw,
  ExternalLink,
  Smartphone,
  Tablet,
  Monitor,
  Maximize2,
  Minimize2,
  Copy,
  Check,
  Eye,
  Code,
  AlertCircle,
} from "lucide-react";

type ViewportSize = "mobile" | "tablet" | "desktop" | "full";

interface LivePreviewProps {
  url?: string;
  html?: string;
  theme?: "light" | "dark";
  className?: string;
  onError?: (error: string) => void;
}

const VIEWPORT_SIZES: Record<ViewportSize, { width: number; height: number; label: string }> = {
  mobile: { width: 375, height: 667, label: "Mobile" },
  tablet: { width: 768, height: 1024, label: "Tablet" },
  desktop: { width: 1280, height: 800, label: "Desktop" },
  full: { width: 0, height: 0, label: "Full" },
};

export function LivePreview({
  url,
  html,
  theme = "dark",
  className,
  onError,
}: LivePreviewProps) {
  const [viewport, setViewport] = useState<ViewportSize>("full");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSource, setShowSource] = useState(false);
  const [copied, setCopied] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [key, setKey] = useState(0);

  const handleRefresh = useCallback(() => {
    setKey((k) => k + 1);
    setIsLoading(true);
    setError(null);
  }, []);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleIframeError = useCallback(() => {
    setIsLoading(false);
    const errorMessage = "Failed to load preview";
    setError(errorMessage);
    onError?.(errorMessage);
  }, [onError]);

  const handleOpenExternal = useCallback(() => {
    if (url) {
      window.open(url, "_blank");
    } else if (html) {
      const blob = new Blob([html], { type: "text/html" });
      const blobUrl = URL.createObjectURL(blob);
      window.open(blobUrl, "_blank");
    }
  }, [url, html]);

  const handleCopySource = useCallback(async () => {
    if (html) {
      await navigator.clipboard.writeText(html);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [html]);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const iframeSrc = url || (html ? `data:text/html;charset=utf-8,${encodeURIComponent(html)}` : undefined);

  const viewportStyle =
    viewport === "full"
      ? { width: "100%", height: "100%" }
      : {
          width: VIEWPORT_SIZES[viewport].width,
          height: VIEWPORT_SIZES[viewport].height,
          maxWidth: "100%",
          maxHeight: "100%",
        };

  return (
    <div
      ref={containerRef}
      className={cn(
        "flex flex-col rounded-lg border overflow-hidden",
        theme === "dark" ? "bg-gray-900 border-gray-700" : "bg-white border-gray-200",
        isFullscreen && "fixed inset-0 z-50 rounded-none",
        className
      )}
    >
      {/* Toolbar */}
      <div
        className={cn(
          "flex items-center justify-between px-3 py-2 border-b",
          theme === "dark" ? "bg-gray-800 border-gray-700" : "bg-gray-50 border-gray-200"
        )}
      >
        <div className="flex items-center gap-2">
          <Eye className="h-4 w-4 text-green-500" />
          <span className={cn("text-sm font-medium", theme === "dark" ? "text-gray-200" : "text-gray-700")}>
            Preview
          </span>
          {url && (
            <span className={cn("text-xs truncate max-w-[200px]", theme === "dark" ? "text-gray-400" : "text-gray-500")}>
              {url}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {/* Viewport Buttons */}
          <div className={cn("flex items-center rounded-md p-0.5", theme === "dark" ? "bg-gray-700" : "bg-gray-200")}>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewport("mobile")}
              className={cn(viewport === "mobile" && (theme === "dark" ? "bg-gray-600" : "bg-white"))}
              title="Mobile view"
            >
              <Smartphone className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewport("tablet")}
              className={cn(viewport === "tablet" && (theme === "dark" ? "bg-gray-600" : "bg-white"))}
              title="Tablet view"
            >
              <Tablet className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewport("desktop")}
              className={cn(viewport === "desktop" && (theme === "dark" ? "bg-gray-600" : "bg-white"))}
              title="Desktop view"
            >
              <Monitor className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setViewport("full")}
              className={cn(viewport === "full" && (theme === "dark" ? "bg-gray-600" : "bg-white"))}
              title="Full width"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>

          <div className={cn("w-px h-6 mx-1", theme === "dark" ? "bg-gray-600" : "bg-gray-300")} />

          {html && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSource(!showSource)}
              className={cn(showSource && "text-blue-500")}
              title="Toggle source"
            >
              <Code className="h-4 w-4" />
            </Button>
          )}

          <Button variant="ghost" size="sm" onClick={handleRefresh} disabled={isLoading} title="Refresh">
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          </Button>

          {html && (
            <Button variant="ghost" size="sm" onClick={handleCopySource} title="Copy HTML">
              {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
            </Button>
          )}

          <Button variant="ghost" size="sm" onClick={handleOpenExternal} title="Open in new tab">
            <ExternalLink className="h-4 w-4" />
          </Button>

          <Button variant="ghost" size="sm" onClick={toggleFullscreen} title="Toggle fullscreen">
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {showSource && html ? (
          <div className="flex flex-1">
            {/* Source Panel */}
            <div className={cn("w-1/2 border-r overflow-auto", theme === "dark" ? "border-gray-700" : "border-gray-200")}>
              <pre className={cn("p-4 text-xs font-mono whitespace-pre-wrap", theme === "dark" ? "text-gray-300" : "text-gray-700")}>
                {html}
              </pre>
            </div>
            {/* Preview Panel */}
            <div className="w-1/2 flex items-center justify-center p-4 bg-gray-100 dark:bg-gray-800">
              <div
                className="bg-white shadow-lg rounded overflow-hidden"
                style={viewport !== "full" ? viewportStyle : { width: "100%", height: "100%" }}
              >
                {iframeSrc && (
                  <iframe
                    key={key}
                    ref={iframeRef}
                    src={iframeSrc}
                    className="w-full h-full border-0"
                    onLoad={handleLoad}
                    onError={handleIframeError}
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                    title="Live Preview"
                  />
                )}
              </div>
            </div>
          </div>
        ) : (
          <div
            className={cn(
              "flex-1 flex items-center justify-center p-4",
              viewport !== "full" && "bg-gray-100 dark:bg-gray-800"
            )}
          >
            {error ? (
              <div className="flex flex-col items-center gap-4 text-center">
                <AlertCircle className="h-12 w-12 text-red-500" />
                <div>
                  <p className={cn("font-medium", theme === "dark" ? "text-gray-200" : "text-gray-800")}>
                    Preview Error
                  </p>
                  <p className={cn("text-sm", theme === "dark" ? "text-gray-400" : "text-gray-500")}>
                    {error}
                  </p>
                </div>
                <Button onClick={handleRefresh}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              </div>
            ) : iframeSrc ? (
              <div
                className={cn(
                  "bg-white shadow-lg rounded overflow-hidden",
                  viewport !== "full" && "border"
                )}
                style={viewportStyle}
              >
                <iframe
                  key={key}
                  ref={iframeRef}
                  src={iframeSrc}
                  className="w-full h-full border-0"
                  onLoad={handleLoad}
                  onError={handleIframeError}
                  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                  title="Live Preview"
                />
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 text-center">
                <Eye className="h-12 w-12 text-gray-400" />
                <p className={cn("text-sm", theme === "dark" ? "text-gray-400" : "text-gray-500")}>
                  No preview available
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div
        className={cn(
          "flex items-center justify-between px-3 py-1 text-xs border-t",
          theme === "dark" ? "bg-gray-800 border-gray-700 text-gray-400" : "bg-gray-50 border-gray-200 text-gray-500"
        )}
      >
        <div className="flex items-center gap-4">
          {viewport !== "full" && (
            <span>
              {VIEWPORT_SIZES[viewport].width} × {VIEWPORT_SIZES[viewport].height}
            </span>
          )}
          <span>{VIEWPORT_SIZES[viewport].label}</span>
        </div>
        <div className="flex items-center gap-2">
          {isLoading && <span className="text-blue-500">Loading...</span>}
          {!isLoading && !error && <span className="text-green-500">Ready</span>}
          {error && <span className="text-red-500">Error</span>}
        </div>
      </div>
    </div>
  );
}

export default LivePreview;
