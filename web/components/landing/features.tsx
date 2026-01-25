import {
  Sparkles,
  Blocks,
  Rocket,
  Globe,
  Shield,
  Zap,
  Code,
  GitBranch,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const features = [
  {
    icon: Sparkles,
    title: 'AI-Powered Development',
    description:
      'Describe your idea in plain language. Our AI understands your requirements and generates production-ready code.',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
  {
    icon: Blocks,
    title: 'Pre-built Modules',
    description:
      'Auth, payments, email, storage — all battle-tested modules ready to use. No more reinventing the wheel.',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    icon: Rocket,
    title: 'One-Click Deploy',
    description:
      'Push to production with a single click. Preview environments, automatic SSL, custom domains included.',
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
  },
  {
    icon: Globe,
    title: 'Global Edge Network',
    description:
      'Your apps deployed to the edge, close to your users. Fast load times, anywhere in the world.',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    icon: Shield,
    title: 'Security Built-in',
    description:
      'Enterprise-grade security by default. SOC2 compliant infrastructure, encrypted data, secure auth.',
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
  },
  {
    icon: Zap,
    title: 'Instant Scaling',
    description:
      'From zero to millions of users. Auto-scaling infrastructure that grows with your business.',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
  },
];

const workflow = [
  {
    step: '01',
    title: 'Describe',
    description: 'Tell AI what you want to build',
    icon: Code,
  },
  {
    step: '02',
    title: 'Generate',
    description: 'AI creates code from modules',
    icon: Sparkles,
  },
  {
    step: '03',
    title: 'Deploy',
    description: 'One click to production',
    icon: Rocket,
  },
  {
    step: '04',
    title: 'Iterate',
    description: 'Improve with AI assistance',
    icon: GitBranch,
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container mx-auto px-4 lg:px-8">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need to ship fast
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Stop wasting time on boilerplate. Focus on what makes your product unique.
          </p>
        </div>

        {/* How it works */}
        <div className="mt-16">
          <h3 className="text-center text-xl font-semibold mb-8">How it works</h3>
          <div className="grid gap-8 md:grid-cols-4">
            {workflow.map((item, index) => (
              <div key={item.step} className="relative text-center">
                {/* Connector line */}
                {index < workflow.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-1/2 w-full h-0.5 bg-border" />
                )}
                
                {/* Step circle */}
                <div className="relative mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <item.icon className="h-7 w-7" />
                </div>
                
                <div className="text-sm font-medium text-muted-foreground mb-1">
                  Step {item.step}
                </div>
                <h4 className="text-lg font-semibold">{item.title}</h4>
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Features grid */}
        <div className="mt-20 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="hover-lift">
              <CardHeader>
                <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg ${feature.bgColor}`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Modules showcase */}
        <div className="mt-20 rounded-2xl border bg-card p-8 md:p-12">
          <div className="grid gap-8 md:grid-cols-2 items-center">
            <div>
              <h3 className="text-2xl font-bold">37+ Ready-to-use Modules</h3>
              <p className="mt-4 text-muted-foreground">
                From authentication to payments, from databases to notifications — 
                we've got you covered with production-ready modules.
              </p>
              
              <div className="mt-6 flex flex-wrap gap-2">
                {['Auth', 'Payments', 'Email', 'Storage', 'Database', 'AI', 'Deploy', 'Analytics'].map((module) => (
                  <span
                    key={module}
                    className="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-sm font-medium"
                  >
                    {module}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              {[
                { name: 'Clerk Auth', type: 'SaaS' },
                { name: 'Stripe', type: 'Payments' },
                { name: 'Resend', type: 'Email' },
                { name: 'Supabase', type: 'Database' },
                { name: 'Railway', type: 'Deploy' },
                { name: 'Cloudflare', type: 'CDN' },
              ].map((item) => (
                <div
                  key={item.name}
                  className="rounded-lg border bg-background p-4 hover:border-primary/50 transition-colors"
                >
                  <div className="font-medium">{item.name}</div>
                  <div className="text-sm text-muted-foreground">{item.type}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
