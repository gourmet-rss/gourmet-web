"use client";

import React from "react";
import Link from "next/link";
import { flavourValidator } from "@/validators";
import { z } from "zod";
import { usePathname } from "next/navigation";
import classNames from "classnames";

const Sidebar = ({
  flavours,
}: {
  flavours: z.infer<typeof flavourValidator>[];
}) => {
  const path = usePathname();
  return (
    <div className="basis-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      <div className="sticky top-16">
        <div className="p-4 border-b border-gray-200 dark:border-gray-800">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">
            My Flavours
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
  );
};

export default Sidebar;
