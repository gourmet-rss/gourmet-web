"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { flavourValidator } from "@/validators";
import { z } from "zod";
import { usePathname } from "next/navigation";
import classNames from "classnames";

const Sidebar = ({
  flavours,
  isOpen,
  onToggle,
}: {
  flavours: z.infer<typeof flavourValidator>[];
  isOpen: boolean;
  onToggle: () => void;
}) => {
  const path = usePathname();

  // Close sidebar on navigation on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024 && isOpen) {
        onToggle();
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [isOpen, onToggle]);

  return (
    <>
      {/* Hamburger button for mobile */}
      <button
        onClick={onToggle}
        className="lg:hidden fixed z-20 top-3 left-4 p-2 rounded-md"
        aria-label="Toggle sidebar"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-gray-700 dark:text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          {isOpen ? (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          ) : (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          )}
        </svg>
      </button>

      {/* Overlay for mobile when sidebar is open */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black opacity-70 z-10"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div
        className={classNames(
          "fixed lg:static inset-y-0 left-0 z-10 w-screen sm:w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-transform duration-300 ease-in-out",
          {
            "translate-x-0": isOpen,
            "-translate-x-full lg:translate-x-0": !isOpen,
          },
        )}
      >
        <div className="sticky top-16">
          <div className="p-4 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white">
              My Flavours ✨
            </h2>
          </div>
          <div>
            <ul className="py-2">
              {flavours.map((flavour) => {
                const isSelected = path === `/flavours/${flavour.id}`;
                return (
                  <li
                    key={flavour.id}
                    className={classNames(
                      "hover:bg-gray-100 dark:hover:bg-gray-800",
                      {
                        "bg-gray-100 dark:bg-gray-800": isSelected,
                      },
                    )}
                  >
                    <Link
                      href={`/flavours/${flavour.id}`}
                      className="px-4 py-2 flex items-center text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white cursor-default"
                      onClick={onToggle}
                    >
                      <span className="truncate">{flavour.nickname}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
