import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import Visualization from "./visualization";
import Image from "next/image";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Gourmet",
  description: "A deliciously curated RSS reader",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
    >
      <Providers>
        <html lang="en">
          <body
            className={`${geistSans.variable} ${geistMono.variable} antialiased`}
          >
            <div className="flex items-center justify-between h-12 px-3 gap-2 border-b">
              <div className="flex items-center gap-2">
                <Image src="/logo.svg" alt="Gourmet Logo" width={32} height={32} className="h-8 w-8" />
                <span className="font-semibold text-lg">gourmet</span>
              </div>
              <div className="flex items-center gap-2">
                <SignedIn>
                  <UserButton />
                </SignedIn>
                <SignedOut>
                  <SignInButton>
                    <button className="btn">Sign in</button>
                  </SignInButton>
                  <SignUpButton>
                    <button className="btn">Sign up</button>
                  </SignUpButton>
                </SignedOut>
              </div>
            </div>
            <Visualization />
            <div className="lg:max-w-4/6 !mx-auto">{children}</div>
          </body>
        </html>
      </Providers>
    </ClerkProvider>
  );
}
