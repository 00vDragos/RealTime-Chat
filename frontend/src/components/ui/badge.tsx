import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-full border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[rgb(var(--primary))] text-[rgb(var(--primary-foreground))] [a&]:hover:bg-[rgb(var(--primary))]/90",
        secondary:
          "border-transparent bg-[rgb(var(--secondary))] text-[rgb(var(--secondary-foreground))] [a&]:hover:bg-[rgb(var(--secondary))]/90",
        destructive:
          "border-transparent bg-[rgb(var(--destructive))] text-white [a&]:hover:bg-[rgb(var(--destructive))]/90 focus-visible:ring-[rgb(var(--destructive))]/20 dark:focus-visible:ring-[rgb(var(--destructive))]/40 dark:bg-[rgb(var(--destructive))]/60",
        outline:
          "text-[rgb(var(--foreground))] [a&]:hover:bg-[rgb(var(--accent))] [a&]:hover:text-[rgb(var(--accent-foreground))]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span"

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
