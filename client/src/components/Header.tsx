import Link from "next/link";
import Image from "next/image";
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
import { Cog } from "lucide-react";
import classNames from "classnames";

export default function Header({ hasSidebar }: { hasSidebar?: boolean }) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm sticky top-0 z-20">
      <div
        className={classNames("max-w-6xl mx-auto px-4", {
          "pl-18 lg:pl-4": hasSidebar,
        })}
      >
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="cursor-pointer">
            <div className="flex items-center gap-3">
              <Image
                src="/logo.svg"
                alt="Gourmet Logo"
                width={32}
                height={32}
                className="h-10 w-10 border-2 border-neutral-300 dark:border-neutral-700 rounded-full"
              />
              <div className="flex flex-col">
                <span className="font-serif font-bold text-xl text-gray-900 dark:text-white leading-tight tracking-tight">
                  gourmet
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  curated content daily
                </span>
              </div>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <SignedIn>
              <div className="dropdown dropdown-end">
                <div
                  tabIndex={0}
                  role="button"
                  className="btn btn-ghost btn-circle"
                >
                  <Cog className="h-5 w-5" />
                </div>
                <ul
                  tabIndex={0}
                  className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
                >
                  <li>
                    <Link href="/onboarding">Repeat onboarding</Link>
                  </li>
                </ul>
              </div>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
            <SignedOut>
              <SignInButton>
                <button className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors">
                  Sign in
                </button>
              </SignInButton>
              <SignUpButton>
                <button className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-colors">
                  Sign up
                </button>
              </SignUpButton>
            </SignedOut>
          </div>
        </div>
      </div>
    </header>
  );
}
