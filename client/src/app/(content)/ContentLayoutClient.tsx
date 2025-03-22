"use client";

import React, { useState } from "react";
import Sidebar from "@/components/Sidebar";
import { flavourValidator } from "@/validators";
import { z } from "zod";

export default function ContentLayoutClient({
  children,
  flavours,
}: {
  children: React.ReactNode;
  flavours: z.infer<typeof flavourValidator>[];
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex">
      <Sidebar
        flavours={flavours}
        isOpen={isSidebarOpen}
        onToggle={toggleSidebar}
      />
      <main className="flex-1 max-w-6xl mx-auto px-4 pt-4 lg:px-6">
        {children}
      </main>
    </div>
  );
}
