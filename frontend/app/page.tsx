'use client'

import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

import { getAccessToken } from "@auth0/nextjs-auth0"

export default function Page() {
  const fetchData = async () => {
    try {
      const token = await getAccessToken()
      const response = await fetch('/trueapi/test', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
      );
      const result = await response.json();
      console.log('Data fetched successfully:', result);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">
                    Building Your Application
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Data Fetching</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <main className="flex-1 p-4">
          <h1 className="text-2xl font-bold">Data Fetching</h1>
          <div className="mt-4">
            <button className="btn" onClick={fetchData}>Fetch Data</button>
          </div>
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
