"use client"

import * as React from "react"
import { Menu, Search, Bell, Sun, Moon, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useTheme } from "next-themes"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Sheet, SheetContent, SheetTrigger, SheetTitle, SheetHeader } from "@/components/ui/sheet"
import { Sidebar } from "./Sidebar"
import { cn } from "@/lib/utils"

export function Navbar() {
  const { theme, setTheme } = useTheme()

  return (
    <header className="sticky top-4 z-50 mx-4 border rounded-xl bg-background/80 backdrop-blur-md shadow-lg transition-colors duration-300">
      <div className="flex h-24 items-center px-4 md:px-6">
        {/* Left: Mobile Sidebar toggle */}
        <div className="flex flex-1 items-center md:hidden">
          <Sheet>
            <SheetTrigger render={<Button variant="ghost" size="icon" className="md:hidden" />}>
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle sidebar</span>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-72">
              <SheetHeader className="sr-only">
                <SheetTitle>Navigation Menu</SheetTitle>
              </SheetHeader>
              <Sidebar />
            </SheetContent>
          </Sheet>
        </div>
        <div className="hidden md:flex flex-1" />

        {/* Center: RepoLens */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <span 
            className={cn(
              "text-8xl font-extrabold tracking-tighter",
              // Light Mode
              "text-white [text-shadow:0_0_20px_rgba(180,0,1,1)] [-webkit-text-stroke:1px_rgba(180,0,1,1)]",
              // Dark Mode
              "dark:bg-clip-text dark:text-transparent dark:bg-gradient-to-r",
              "dark:from-white dark:to-[#ff007f] dark:drop-shadow-[0_0_15px_rgba(255,215,0,0.6)]"
            )}
          >
            RepoLens
          </span>
        </div>

        {/* Right: Actions */}
        <div className="flex flex-1 items-center justify-end space-x-2">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}
          >
            <Search className="h-5 w-5" />
            <span className="sr-only">Search</span>
          </Button>
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
            <span className="sr-only">Notifications</span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
          <Avatar className="h-8 w-8 cursor-pointer ml-2">
            <AvatarImage src="" alt="User" />
            <AvatarFallback><User className="h-4 w-4" /></AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  )
}
