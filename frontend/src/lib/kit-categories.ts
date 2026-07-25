/** Curated Starter Kit categories — shared by the editor and the catalog. */

import type { KitCategory } from "@/types";

export const KIT_CATEGORIES: { value: KitCategory; label: string }[] = [
  { value: "ecommerce", label: "E-commerce" },
  { value: "dashboard", label: "Admin Dashboard" },
  { value: "saas", label: "SaaS" },
  { value: "landing", label: "Landing / Marketing" },
  { value: "blog", label: "Blog / CMS" },
  { value: "mobile", label: "Mobile" },
  { value: "api_service", label: "API Service" },
  { value: "portfolio", label: "Portfolio" },
  { value: "other", label: "Other" },
];

export const KIT_CATEGORY_LABEL: Record<KitCategory, string> = Object.fromEntries(
  KIT_CATEGORIES.map((c) => [c.value, c.label]),
) as Record<KitCategory, string>;
