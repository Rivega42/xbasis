import Link from 'next/link';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

const plans = [
  {
    name: 'Free',
    description: 'Perfect for trying things out',
    price: 0,
    interval: 'forever',
    features: [
      '1 project',
      '10K AI tokens/month',
      'Subdomain hosting',
      'Community support',
      'Basic analytics',
    ],
    cta: 'Start Free',
    href: '/register',
    popular: false,
  },
  {
    name: 'Pro',
    description: 'For serious builders',
    price: 29,
    interval: 'month',
    features: [
      '5 projects',
      '100K AI tokens/month',
      'Custom domains',
      'Priority support',
      'Advanced analytics',
      'Team collaboration (soon)',
      'API access',
    ],
    cta: 'Get Pro',
    href: '/register?plan=pro',
    popular: true,
  },
  {
    name: 'Team',
    description: 'For growing teams',
    price: 99,
    interval: 'month',
    features: [
      '20 projects',
      '500K AI tokens/month',
      'Custom domains',
      'Priority support',
      'Advanced analytics',
      'Team collaboration',
      'API access',
      'SSO (soon)',
      'Audit logs',
    ],
    cta: 'Get Team',
    href: '/register?plan=team',
    popular: false,
  },
];

const faqs = [
  {
    question: 'What are AI tokens?',
    answer:
      'AI tokens are used when you interact with our AI assistant. Each message you send and receive uses tokens. Average conversation uses about 1,000-2,000 tokens.',
  },
  {
    question: 'Can I upgrade or downgrade anytime?',
    answer:
      "Yes! You can change your plan at any time. When upgrading, you'll be charged the prorated amount. When downgrading, the change takes effect at the next billing cycle.",
  },
  {
    question: 'Do you offer refunds?',
    answer:
      "We offer a 14-day money-back guarantee. If you're not satisfied, contact us for a full refund.",
  },
  {
    question: 'What payment methods do you accept?',
    answer:
      'We accept all major credit cards, PayPal, and in some regions, local payment methods through our payment partner Paddle.',
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="py-20 md:py-32 bg-muted/30">
      <div className="container mx-auto px-4 lg:px-8">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start free, upgrade when you're ready. No hidden fees.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={cn(
                'relative flex flex-col',
                plan.popular && 'border-primary shadow-lg scale-105'
              )}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                  Most Popular
                </Badge>
              )}
              
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              
              <CardContent className="flex-1">
                <div className="mb-6">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-muted-foreground">/{plan.interval}</span>
                </div>
                
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              
              <CardFooter>
                <Button
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                  size="lg"
                  asChild
                >
                  <Link href={plan.href}>{plan.cta}</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Token packs */}
        <div className="mt-16 text-center">
          <h3 className="text-xl font-semibold">Need more AI tokens?</h3>
          <p className="mt-2 text-muted-foreground">
            Buy additional tokens anytime. No subscription required.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            {[
              { tokens: '10K', price: 5 },
              { tokens: '50K', price: 20 },
              { tokens: '100K', price: 35 },
            ].map((pack) => (
              <div
                key={pack.tokens}
                className="rounded-lg border bg-card px-6 py-4 text-center hover:border-primary/50 transition-colors"
              >
                <div className="text-lg font-bold">{pack.tokens} tokens</div>
                <div className="text-muted-foreground">${pack.price}</div>
              </div>
            ))}
          </div>
        </div>

        {/* FAQs */}
        <div className="mt-20">
          <h3 className="text-center text-2xl font-bold">Frequently Asked Questions</h3>
          <div className="mt-8 grid gap-6 md:grid-cols-2">
            {faqs.map((faq) => (
              <div key={faq.question} className="rounded-lg border bg-card p-6">
                <h4 className="font-semibold">{faq.question}</h4>
                <p className="mt-2 text-sm text-muted-foreground">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
