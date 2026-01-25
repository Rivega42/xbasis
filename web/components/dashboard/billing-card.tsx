"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn, formatCurrency, formatNumber } from "@/lib/utils";
import { CreditCard, Zap, ArrowRight } from "lucide-react";
import Link from "next/link";

interface BillingCardProps {
  plan: {
    name: string;
    tokensIncluded: number;
    price: number;
  };
  usage: {
    tokensUsed: number;
    tokensRemaining: number;
    periodEnd: string;
  };
  className?: string;
}

export function BillingCard({ plan, usage, className }: BillingCardProps) {
  const usagePercentage = (usage.tokensUsed / plan.tokensIncluded) * 100;
  const isLow = usage.tokensRemaining < plan.tokensIncluded * 0.1;

  return (
    <div className={cn("rounded-lg border bg-card p-6", className)}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CreditCard className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Billing</h3>
        </div>
        <Badge variant={plan.name === "Free" ? "secondary" : "default"}>
          {plan.name}
        </Badge>
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-muted-foreground">Token Usage</span>
            <span className={cn("font-medium", isLow && "text-red-500")}>
              {formatNumber(usage.tokensUsed)} / {formatNumber(plan.tokensIncluded)}
            </span>
          </div>
          <div className="h-2 rounded-full bg-secondary overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all bg-primary",
                usagePercentage > 90 && "bg-red-500",
                usagePercentage > 75 && usagePercentage <= 90 && "bg-yellow-500"
              )}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
        </div>

        {isLow && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-yellow-500/10 text-yellow-600 dark:text-yellow-400">
            <Zap className="h-4 w-4" />
            <span className="text-sm">Running low on tokens</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-2">
          <div>
            <p className="text-2xl font-bold">{formatCurrency(plan.price)}</p>
            <p className="text-xs text-muted-foreground">per month</p>
          </div>
          <Button asChild variant={isLow ? "default" : "outline"}>
            <Link href="/dashboard/billing">
              {isLow ? "Buy Tokens" : "Manage"}
              <ArrowRight className="h-4 w-4 ml-1" />
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}

export default BillingCard;
