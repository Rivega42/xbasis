"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Play,
  Save,
  Copy,
  Check,
  Undo,
  Redo,
  Search,
  Settings,
  Maximize2,
  Minimize2,
  FileCode,
  Terminal,
} from "lucide-react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  theme?: "light" | "dark";
  readOnly?: boolean;
  onRun?: () => void;
  onSave?: () => void;
  fileName?: string;
  className?: string;
}

const LANGUAGE_COLORS: Record<string, string> = {
  javascript: "text-yellow-500",
  typescript: "text-blue-500",
  python: "text-green-500",
  html: "text-orange-500",
  css: "text-pink-500",
  json: "text-gray-500",
  markdown: "text-purple-500",
};

export function CodeEditor({
  value,
  onChange,
  language = "javascript",
  theme = "dark",
  readOnly = false,
  onRun,
  onSave,
  fileName = "untitled.js",
  className,
}: CodeEditorProps) {
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [history, setHistory] = useState<string[]>([value]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const lines = value.split("\n");
  const lineCount = lines.length;

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [value]);

  const handleChange = useCallback(
    (newValue: string) => {
      onChange(newValue);
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push(newValue);
      if (newHistory.length > 100) newHistory.shift();
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
    },
    [onChange, history, historyIndex]
  );

  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      onChange(history[newIndex]);
    }
  }, [historyIndex, history, onChange]);

  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      onChange(history[newIndex]);
    }
  }, [historyIndex, history, onChange]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Tab") {
        e.preventDefault();
        const textarea = textareaRef.current;
        if (textarea) {
          const start = textarea.selectionStart;
          const end = textarea.selectionEnd;
          const newValue = value.substring(0, start) + "  " + value.substring(end);
          handleChange(newValue);
          setTimeout(() => {
            textarea.selectionStart = textarea.selectionEnd = start + 2;
          }, 0);
        }
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        onSave?.();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === "z") {
        e.preventDefault();
        if (e.shiftKey) {
          handleRedo();
        } else {
          handleUndo();
        }
      }
    },
    [value, handleChange, onSave, handleUndo, handleRedo]
  );

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }, []);

  return (
    <div
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
          <FileCode className={cn("h-4 w-4", LANGUAGE_COLORS[language] || "text-gray-500")} />
          <span className={cn("text-sm font-medium", theme === "dark" ? "text-gray-200" : "text-gray-700")}>
            {fileName}
          </span>
          <span className={cn("text-xs px-2 py-0.5 rounded", theme === "dark" ? "bg-gray-700 text-gray-400" : "bg-gray-200 text-gray-500")}>
            {language}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={handleUndo} disabled={historyIndex === 0} title="Undo (Ctrl+Z)">
            <Undo className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={handleRedo} disabled={historyIndex === history.length - 1} title="Redo (Ctrl+Shift+Z)">
            <Redo className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={handleCopy} title="Copy code">
            {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="sm" onClick={toggleFullscreen} title="Toggle fullscreen">
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
          {onSave && (
            <Button variant="ghost" size="sm" onClick={onSave} title="Save (Ctrl+S)">
              <Save className="h-4 w-4" />
            </Button>
          )}
          {onRun && (
            <Button variant="default" size="sm" onClick={onRun} className="ml-2">
              <Play className="h-4 w-4 mr-1" />
              Run
            </Button>
          )}
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Line Numbers */}
        {showLineNumbers && (
          <div
            className={cn(
              "flex flex-col py-3 px-2 text-right select-none border-r",
              theme === "dark" ? "bg-gray-800 border-gray-700 text-gray-500" : "bg-gray-50 border-gray-200 text-gray-400"
            )}
            style={{ minWidth: "3rem" }}
          >
            {Array.from({ length: lineCount }, (_, i) => (
              <span key={i + 1} className="text-xs leading-6 font-mono">
                {i + 1}
              </span>
            ))}
          </div>
        )}

        {/* Code Input */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          spellCheck={false}
          className={cn(
            "flex-1 p-3 font-mono text-sm leading-6 resize-none outline-none",
            theme === "dark" ? "bg-gray-900 text-gray-100" : "bg-white text-gray-900",
            readOnly && "cursor-default"
          )}
          style={{ tabSize: 2 }}
        />
      </div>

      {/* Status Bar */}
      <div
        className={cn(
          "flex items-center justify-between px-3 py-1 text-xs border-t",
          theme === "dark" ? "bg-gray-800 border-gray-700 text-gray-400" : "bg-gray-50 border-gray-200 text-gray-500"
        )}
      >
        <div className="flex items-center gap-4">
          <span>Lines: {lineCount}</span>
          <span>Characters: {value.length}</span>
        </div>
        <div className="flex items-center gap-2">
          <span>UTF-8</span>
          <span>•</span>
          <span>{language.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
}

export default CodeEditor;
