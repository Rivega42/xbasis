"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn, formatDate } from "@/lib/utils";
import {
  Folder,
  Globe,
  Clock,
  MoreHorizontal,
  Play,
  Pause,
  Trash2,
  Settings,
  ExternalLink,
  GitBranch,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type ProjectStatus = "active" | "deploying" | "stopped" | "error";

interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  url?: string;
  lastDeployedAt?: string;
  createdAt: string;
  framework?: string;
}

interface ProjectCardProps {
  project: Project;
  onStart?: (id: string) => void;
  onStop?: (id: string) => void;
  onDelete?: (id: string) => void;
}

const STATUS_CONFIG: Record<ProjectStatus, { color: string; label: string }> = {
  active: { color: "bg-green-500", label: "Active" },
  deploying: { color: "bg-yellow-500 animate-pulse", label: "Deploying" },
  stopped: { color: "bg-gray-500", label: "Stopped" },
  error: { color: "bg-red-500", label: "Error" },
};

export function ProjectCard({ project, onStart, onStop, onDelete }: ProjectCardProps) {
  const statusConfig = STATUS_CONFIG[project.status];

  return (
    <div className="group relative rounded-lg border bg-card p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Folder className="h-5 w-5 text-primary" />
          </div>
          <div>
            <Link
              href={`/dashboard/projects/${project.id}`}
              className="font-semibold hover:text-primary transition-colors"
            >
              {project.name}
            </Link>
            {project.framework && (
              <Badge variant="secondary" className="ml-2 text-xs">
                {project.framework}
              </Badge>
            )}
          </div>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href={`/dashboard/projects/${project.id}`}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Link>
            </DropdownMenuItem>
            {project.url && (
              <DropdownMenuItem asChild>
                <a href={project.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Site
                </a>
              </DropdownMenuItem>
            )}
            <DropdownMenuSeparator />
            {project.status === "stopped" ? (
              <DropdownMenuItem onClick={() => onStart?.(project.id)}>
                <Play className="h-4 w-4 mr-2" />
                Start
              </DropdownMenuItem>
            ) : (
              <DropdownMenuItem onClick={() => onStop?.(project.id)}>
                <Pause className="h-4 w-4 mr-2" />
                Stop
              </DropdownMenuItem>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => onDelete?.(project.id)}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {project.description && (
        <p className="mt-3 text-sm text-muted-foreground line-clamp-2">
          {project.description}
        </p>
      )}

      <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <div className={cn("h-2 w-2 rounded-full", statusConfig.color)} />
          <span>{statusConfig.label}</span>
        </div>

        {project.url && (
          <a
            href={project.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-primary transition-colors"
          >
            <Globe className="h-3 w-3" />
            <span className="truncate max-w-[150px]">
              {project.url.replace(/^https?:\/\//, "")}
            </span>
          </a>
        )}

        <div className="flex items-center gap-1 ml-auto">
          <Clock className="h-3 w-3" />
          <span>
            {project.lastDeployedAt
              ? formatDate(project.lastDeployedAt)
              : formatDate(project.createdAt)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default ProjectCard;
