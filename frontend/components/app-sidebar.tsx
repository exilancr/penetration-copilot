"use client"

import * as React from "react"
import {
  Frame,
  Map,
  PieChart,
  UserCircle,
  BriefcaseBusiness,
  HandCoins,
  Carrot,
  BookHeart,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"

const data = {
  navMain: [
    {
      title: "Profiles",
      url: "#",
      icon: UserCircle,
      isActive: true,
      items: [
        {
          title: "My profiles",
          url: "#",
        },
        {
          title: "All profiles",
          url: "#",
        },
      ],
    },
    {
      title: "Jobs",
      url: "#",
      icon: BriefcaseBusiness,
      items: [
        {
          title: "All jobs",
          url: "#",
        },
        {
          title: "Featured",
          url: "#",
        },
        {
          title: "Applied",
          url: "#",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Support",
      url: "https://onlyfans.com/smallsharky",
      icon: HandCoins,
    },
    {
      title: "Feedback",
      url: "https://pornhub.com/video/search?search=ass+licking",
      icon: Carrot,
    },
  ],
  projects: [
    {
      name: "Design Engineering",
      url: "#",
      icon: Frame,
    },
    {
      name: "Sales & Marketing",
      url: "#",
      icon: PieChart,
    },
    {
      name: "Travel",
      url: "#",
      icon: Map,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <a href="/">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <BookHeart  className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Penetration Copilot</span>
                  <span className="truncate text-xs">USS Enterprise</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
