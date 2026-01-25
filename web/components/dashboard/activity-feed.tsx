"use client";

import { cn, formatDate } from "@/lib/utils";
import {
  Rocket,
  Code,
  MessageSquare,
  CreditCard,
  Settings,
  AlertCircle,
  CheckCircle,
  LucideIcon,
} from "lucide-react";

type ActivityType = "deploy" | "code" | "chat" | "billing" | "settings" | "error" | "success";

interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  timestamp: string;
  projectName?: string;
}

interface ActivityFeedProps {
  activities: Activity[];
  className?: string;
}

const ACTIVITY_ICONS: Record<ActivityType, { icon: LucideIcon; color: string }> = {
  deploy: { icon: Rocket, color: "text-blue-500 bg-blue-500/10" },
  code: { icon: Code, color: "text-purple-500 bg-purple-500/10" },
  chat: { icon: MessageSquare, color: "text-green-500 bg-green-500/10" },
  billing: { icon: CreditCard, color: "text-yellow-500 bg-yellow-500/10" },
  settings: { icon: Settings, color: "text-gray-500 bg-gray-500/10" },
  error: { icon: AlertCircle, color: "text-red-500 bg-red-500/10" },
  success: { icon: CheckCircle, color: "text-green-500 bg-green-500/10" },
};

export function ActivityFeed({ activities, className }: ActivityFeedProps) {
  return (
    <div className={cn("rounded-lg border bg-card p-6", className)}>
      <h3 className="font-semibold mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No recent activity
          </p>
        ) : (
          activities.map((activity) => {
            const { icon: Icon, color } = ACTIVITY_ICONS[activity.type];
            return (
              <div key={activity.id} className="flex gap-3">
                <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-full", color)}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium leading-tight">
                    {activity.title}
                    {activity.projectName && (
                      <span className="text-muted-foreground"> in {activity.projectName}</span>
                    )}
                  </p>
                  {activity.description && (
                    <p className="text-xs text-muted-foreground mt-0.5 truncate">
                      {activity.description}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDate(activity.timestamp)}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default ActivityFeed;
