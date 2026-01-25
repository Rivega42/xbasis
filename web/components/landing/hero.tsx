import Link from 'next/link';
import { ArrowRight, Sparkles, Zap, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function Hero() {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-32">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 gradient-bg" />
      
      <div className="container mx-auto px-4 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          {/* Badge */}
          <Badge variant="secondary" className="mb-6 animate-fade-in">
            <Sparkles className="mr-1 h-3 w-3" />
            AI-Powered Development Platform
          </Badge>

          {/* Headline */}
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl animate-fade-in">
            From idea to{' '}
            <span className="gradient-text">production</span>
            <br />
            in days, not months
          </h1>

          {/* Subheadline */}
          <p className="mt-6 text-lg text-muted-foreground md:text-xl max-w-2xl mx-auto animate-fade-in">
            Describe what you want to build. Our AI generates code from battle-tested modules, 
            deploys automatically, and gives you a live product.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in">
            <Button size="xl" asChild>
              <Link href="/register">
                Start Building Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="xl" variant="outline" asChild>
              <Link href="#features">See How It Works</Link>
            </Button>
          </div>

          {/* Trust indicators */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-muted-foreground animate-fade-in">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span>Deploy in minutes</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              <span>Production-ready code</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-500" />
              <span>AI-assisted development</span>
            </div>
          </div>
        </div>

        {/* Hero Image/Demo */}
        <div className="mt-16 mx-auto max-w-5xl animate-fade-in">
          <div className="relative rounded-xl border bg-card shadow-2xl overflow-hidden">
            {/* Fake browser header */}
            <div className="flex items-center gap-2 border-b bg-muted/50 px-4 py-3">
              <div className="flex gap-1.5">
                <div className="h-3 w-3 rounded-full bg-red-500" />
                <div className="h-3 w-3 rounded-full bg-yellow-500" />
                <div className="h-3 w-3 rounded-full bg-green-500" />
              </div>
              <div className="flex-1 text-center">
                <span className="text-xs text-muted-foreground">xbasis.app/dashboard</span>
              </div>
            </div>
            
            {/* Dashboard preview */}
            <div className="p-6 bg-gradient-to-br from-background to-muted/30">
              <div className="grid gap-4 md:grid-cols-3">
                {/* Stats cards */}
                <div className="rounded-lg border bg-card p-4">
                  <div className="text-sm text-muted-foreground">Projects</div>
                  <div className="text-2xl font-bold">3</div>
                </div>
                <div className="rounded-lg border bg-card p-4">
                  <div className="text-sm text-muted-foreground">Deployments</div>
                  <div className="text-2xl font-bold text-green-500">12</div>
                </div>
                <div className="rounded-lg border bg-card p-4">
                  <div className="text-sm text-muted-foreground">AI Tokens</div>
                  <div className="text-2xl font-bold">85K</div>
                </div>
              </div>
              
              {/* AI Chat preview */}
              <div className="mt-4 rounded-lg border bg-card p-4">
                <div className="flex items-start gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
                    <Sparkles className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium">AI Assistant</div>
                    <div className="mt-1 text-sm text-muted-foreground">
                      I've created your authentication module with JWT tokens, 
                      password hashing, and OAuth support. Ready to deploy?
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
