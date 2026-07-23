import {
  BarChart3,
  Blocks,
  BookMarked,
  FolderKanban,
  Heart,
  LayoutDashboard,
  Library,
  Settings,
  Shield,
  Sparkles,
  Tags,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Feature not built yet — shown but flagged. */
  soon?: boolean;
  /** Only visible to moderators/admins. */
  moderatorOnly?: boolean;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

export const navSections: NavSection[] = [
  {
    title: "Overview",
    items: [{ label: "Dashboard", href: "/dashboard", icon: LayoutDashboard }],
  },
  {
    title: "Library",
    items: [
      { label: "Prompts", href: "/prompts", icon: Library },
      { label: "Categories", href: "/categories", icon: Tags },
      { label: "Collections", href: "/collections", icon: BookMarked },
      { label: "Favorites", href: "/favorites", icon: Heart },
    ],
  },
  {
    title: "Build",
    items: [
      { label: "Projects", href: "/projects", icon: FolderKanban },
      { label: "Components", href: "/components", icon: Blocks },
      { label: "Recommendations", href: "/recommendations", icon: Sparkles },
    ],
  },
  {
    title: "Insights",
    items: [
      { label: "Analytics", href: "/analytics", icon: BarChart3 },
      { label: "Moderation", href: "/moderation", icon: Shield, moderatorOnly: true },
      { label: "Settings", href: "/settings", icon: Settings },
    ],
  },
];
