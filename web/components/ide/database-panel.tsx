"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Database,
  Table as TableIcon,
  Play,
  Plus,
  Trash2,
  Edit,
  Eye,
  RefreshCw,
  Download,
  Search,
  ChevronRight,
  ChevronDown,
  Key,
  Hash,
  Type,
  Calendar,
  ToggleLeft,
} from "lucide-react";

interface Column {
  name: string;
  type: string;
  nullable: boolean;
  primaryKey?: boolean;
  foreignKey?: string;
  default?: string;
}

interface TableInfo {
  name: string;
  columns: Column[];
  rowCount: number;
}

interface QueryResult {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  executionTime: number;
}

interface DatabasePanelProps {
  tables: TableInfo[];
  onRunQuery: (query: string) => Promise<QueryResult>;
  onRefresh: () => void;
  theme?: "light" | "dark";
  className?: string;
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  integer: <Hash className="h-3 w-3" />,
  bigint: <Hash className="h-3 w-3" />,
  serial: <Hash className="h-3 w-3" />,
  varchar: <Type className="h-3 w-3" />,
  text: <Type className="h-3 w-3" />,
  boolean: <ToggleLeft className="h-3 w-3" />,
  timestamp: <Calendar className="h-3 w-3" />,
  date: <Calendar className="h-3 w-3" />,
  uuid: <Key className="h-3 w-3" />,
};

export function DatabasePanel({
  tables,
  onRunQuery,
  onRefresh,
  theme = "dark",
  className,
}: DatabasePanelProps) {
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredTables = tables.filter((t) =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleTableExpanded = useCallback((tableName: string) => {
    setExpandedTables((prev) => {
      const next = new Set(prev);
      if (next.has(tableName)) {
        next.delete(tableName);
      } else {
        next.add(tableName);
      }
      return next;
    });
  }, []);

  const handleRunQuery = useCallback(async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await onRunQuery(query);
      setQueryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query execution failed");
      setQueryResult(null);
    } finally {
      setIsLoading(false);
    }
  }, [query, onRunQuery]);

  const handleSelectTable = useCallback((tableName: string) => {
    setSelectedTable(tableName);
    setQuery(`SELECT * FROM ${tableName} LIMIT 100;`);
  }, []);

  const exportToCSV = useCallback(() => {
    if (!queryResult) return;
    const headers = queryResult.columns.join(",");
    const rows = queryResult.rows.map((row) =>
      queryResult.columns.map((col) => JSON.stringify(row[col] ?? "")).join(",")
    );
    const csv = [headers, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "query_result.csv";
    a.click();
    URL.revokeObjectURL(url);
  }, [queryResult]);

  return (
    <div
      className={cn(
        "flex h-full rounded-lg border overflow-hidden",
        theme === "dark" ? "bg-gray-900 border-gray-700" : "bg-white border-gray-200",
        className
      )}
    >
      {/* Sidebar - Tables */}
      <div
        className={cn(
          "w-64 flex flex-col border-r",
          theme === "dark" ? "bg-gray-800 border-gray-700" : "bg-gray-50 border-gray-200"
        )}
      >
        <div className={cn("p-3 border-b", theme === "dark" ? "border-gray-700" : "border-gray-200")}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-500" />
              <span className={cn("font-medium text-sm", theme === "dark" ? "text-gray-200" : "text-gray-700")}>
                Tables
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={onRefresh}>
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-gray-400" />
            <Input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search tables..."
              className="pl-7 h-8 text-sm"
            />
          </div>
        </div>

        <div className="flex-1 overflow-auto p-2">
          {filteredTables.map((table) => (
            <div key={table.name} className="mb-1">
              <button
                onClick={() => toggleTableExpanded(table.name)}
                onDoubleClick={() => handleSelectTable(table.name)}
                className={cn(
                  "w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm text-left",
                  theme === "dark"
                    ? "hover:bg-gray-700 text-gray-300"
                    : "hover:bg-gray-200 text-gray-700",
                  selectedTable === table.name && (theme === "dark" ? "bg-gray-700" : "bg-gray-200")
                )}
              >
                {expandedTables.has(table.name) ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronRight className="h-3 w-3" />
                )}
                <TableIcon className="h-3 w-3 text-blue-500" />
                <span className="flex-1 truncate">{table.name}</span>
                <Badge variant="secondary" className="text-xs">
                  {table.rowCount}
                </Badge>
              </button>

              {expandedTables.has(table.name) && (
                <div className="ml-6 mt-1 space-y-0.5">
                  {table.columns.map((col) => (
                    <div
                      key={col.name}
                      className={cn(
                        "flex items-center gap-2 px-2 py-1 text-xs rounded",
                        theme === "dark" ? "text-gray-400" : "text-gray-500"
                      )}
                    >
                      {col.primaryKey ? (
                        <Key className="h-3 w-3 text-yellow-500" />
                      ) : (
                        TYPE_ICONS[col.type.toLowerCase()] || <Type className="h-3 w-3" />
                      )}
                      <span className="flex-1 truncate">{col.name}</span>
                      <span className="text-gray-500">{col.type}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Tabs defaultValue="query" className="flex-1 flex flex-col">
          <div className={cn("border-b", theme === "dark" ? "border-gray-700" : "border-gray-200")}>
            <TabsList className="m-2">
              <TabsTrigger value="query">Query</TabsTrigger>
              <TabsTrigger value="structure">Structure</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="query" className="flex-1 flex flex-col m-0 p-0">
            {/* Query Input */}
            <div className={cn("p-3 border-b", theme === "dark" ? "border-gray-700" : "border-gray-200")}>
              <div className="flex gap-2">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter SQL query..."
                  className={cn(
                    "flex-1 p-2 rounded border font-mono text-sm resize-none",
                    theme === "dark"
                      ? "bg-gray-800 border-gray-600 text-gray-100"
                      : "bg-white border-gray-300 text-gray-900"
                  )}
                  rows={3}
                />
                <div className="flex flex-col gap-2">
                  <Button onClick={handleRunQuery} disabled={isLoading || !query.trim()}>
                    <Play className="h-4 w-4 mr-1" />
                    Run
                  </Button>
                  {queryResult && (
                    <Button variant="outline" onClick={exportToCSV}>
                      <Download className="h-4 w-4 mr-1" />
                      CSV
                    </Button>
                  )}
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="flex-1 overflow-auto p-3">
              {isLoading && (
                <div className="flex items-center justify-center h-32">
                  <RefreshCw className="h-6 w-6 animate-spin text-blue-500" />
                </div>
              )}

              {error && (
                <div className="p-4 rounded bg-red-500/10 border border-red-500/20 text-red-500">
                  {error}
                </div>
              )}

              {queryResult && !isLoading && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className={cn("text-sm", theme === "dark" ? "text-gray-400" : "text-gray-500")}>
                      {queryResult.rowCount} rows in {queryResult.executionTime}ms
                    </span>
                  </div>
                  <div className="rounded border overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {queryResult.columns.map((col) => (
                            <TableHead key={col}>{col}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {queryResult.rows.map((row, i) => (
                          <TableRow key={i}>
                            {queryResult.columns.map((col) => (
                              <TableCell key={col}>
                                {row[col] === null ? (
                                  <span className="text-gray-400 italic">NULL</span>
                                ) : (
                                  String(row[col])
                                )}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="structure" className="flex-1 overflow-auto m-0 p-3">
            {selectedTable ? (
              <div>
                <h3 className={cn("text-lg font-medium mb-4", theme === "dark" ? "text-gray-200" : "text-gray-800")}>
                  {selectedTable}
                </h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Column</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Nullable</TableHead>
                      <TableHead>Default</TableHead>
                      <TableHead>Key</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tables
                      .find((t) => t.name === selectedTable)
                      ?.columns.map((col) => (
                        <TableRow key={col.name}>
                          <TableCell className="font-medium">{col.name}</TableCell>
                          <TableCell>{col.type}</TableCell>
                          <TableCell>{col.nullable ? "Yes" : "No"}</TableCell>
                          <TableCell>{col.default || "-"}</TableCell>
                          <TableCell>
                            {col.primaryKey && <Badge variant="default">PK</Badge>}
                            {col.foreignKey && <Badge variant="secondary">FK → {col.foreignKey}</Badge>}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-gray-400">
                Select a table to view its structure
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default DatabasePanel;
