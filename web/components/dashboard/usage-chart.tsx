"use client";

import { cn } from "@/lib/utils";

interface UsageData {
  label: string;
  value: number;
  max: number;
  color?: string;
}

interface UsageChartProps {
  title: string;
  data: UsageData[];
  className?: string;
}

export function UsageChart({ title, data, className }: UsageChartProps) {
  return (
    <div className={cn("rounded-lg border bg-card p-6", className)}>
      <h3 className="font-semibold mb-4">{title}</h3>
      <div className="space-y-4">
        {data.map((item, index) => {
          const percentage = Math.min((item.value / item.max) * 100, 100);
          return (
            <div key={index}>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">{item.label}</span>
                <span className="font-medium">
                  {item.value.toLocaleString()} / {item.max.toLocaleString()}
                </span>
              </div>
              <div className="h-2 rounded-full bg-secondary overflow-hidden">
                <div
                  className={cn(
                    "h-full rounded-full transition-all",
                    item.color || "bg-primary",
                    percentage > 90 && "bg-red-500",
                    percentage > 75 && percentage <= 90 && "bg-yellow-500"
                  )}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}>
      </div>
    </div>
  );
}

export default UsageChart;
