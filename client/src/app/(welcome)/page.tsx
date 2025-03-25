import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { SignInButton, SignUpButton } from "@clerk/nextjs";
import {
  ArrowRight,
  Coffee,
  CupSoda,
  Utensils,
  Croissant,
  ChefHat,
} from "lucide-react";

export default async function Home() {
  const { sessionId } = await auth();

  if (sessionId) {
    return redirect("/feed");
  }

  return (
    <div className="px-4 py-12 md:py-20 relative overflow-hidden">
      {/* Decorative food icons */}
      <div className="hidden md:block absolute top-20 right-10 text-indigo-200 dark:text-indigo-900 opacity-20 transform rotate-12">
        <Coffee className="w-24 h-24" />
      </div>
      <div className="hidden md:block absolute bottom-40 left-10 text-indigo-200 dark:text-indigo-900 opacity-20 transform -rotate-12">
        <Croissant className="w-32 h-32" />
      </div>
      <div className="hidden md:block absolute top-1/2 right-1/4 text-indigo-200 dark:text-indigo-900 opacity-10 transform rotate-45">
        <CupSoda className="w-20 h-20" />
      </div>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto mb-16 md:mb-24 relative">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="relative">
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight tracking-tight mb-6">
              Feed your <span className="text-indigo-600 dark:text-indigo-400 relative">
                curiosity
                <svg
                  className="absolute -bottom-2 left-0 w-full"
                  viewBox="0 0 200 8"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M0,5 C50,0 150,10 200,5"
                    stroke="currentColor"
                    strokeWidth="3"
                    fill="none"
                    strokeLinecap="round"
                  />
                </svg>
              </span> daily
            </h1>
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
              Gourmet serves up the internet&apos;s tastiest articles, fresh from the oven and seasoned to your taste. No empty calories here!
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <SignUpButton>
                <button className="group px-6 py-3 text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-all duration-300 transform hover:-translate-y-1 hover:shadow-md flex items-center justify-center">
                  Take a bite{" "}
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </SignUpButton>
              <SignInButton>
                <button className="px-6 py-3 text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md transition-all duration-300 transform hover:-translate-y-1">
                  Back for seconds?
                </button>
              </SignInButton>
            </div>
          </div>
          <div className="relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg blur opacity-25 animate-pulse"></div>
            <div className="relative bg-white dark:bg-gray-900 p-6 rounded-lg shadow-xl border border-gray-200 dark:border-gray-800 transform transition-all duration-500 hover:rotate-1">
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <ChefHat className="h-16 w-16 text-indigo-600 dark:text-indigo-400" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: <Coffee className="h-6 w-6" />, title: "Tech News" },
                  { icon: <Utensils className="h-6 w-6" />, title: "Cooking" },
                  { icon: <CupSoda className="h-6 w-6" />, title: "Gaming" },
                  { icon: <Croissant className="h-6 w-6" />, title: "Books" },
                ].map((item, i) => (
                  <div
                    key={i}
                    className="bg-gray-100 dark:bg-gray-800 rounded-md p-4 h-32 flex flex-col justify-between transform transition-all duration-300 hover:scale-105 hover:shadow-md"
                  >
                    <div className="text-indigo-600 dark:text-indigo-400">
                      {item.icon}
                    </div>
                    <div>
                      <div className="font-medium text-gray-800 dark:text-gray-200">
                        {item.title}
                      </div>
                      <div className="w-full h-2 bg-indigo-200 dark:bg-indigo-800 rounded-full mt-2 overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 dark:bg-indigo-400 rounded-full"
                          style={{ width: `${Math.random() * 50 + 50}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-5xl mx-auto mb-16 md:mb-24 relative">
        <div className="absolute -left-10 top-1/2 transform -translate-y-1/2 hidden md:block">
          <div className="w-20 h-20 border-l-2 border-t-2 border-indigo-200 dark:border-indigo-800 rounded-tl-3xl"></div>
        </div>
        <div className="absolute -right-10 top-1/2 transform -translate-y-1/2 hidden md:block">
          <div className="w-20 h-20 border-r-2 border-b-2 border-indigo-200 dark:border-indigo-800 rounded-br-3xl"></div>
        </div>

        <h2 className="font-serif text-3xl md:text-4xl font-bold text-gray-900 dark:text-white text-center mb-4">
          Our Secret Sauce
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
          What makes Gourmet so deliciously different? We&apos;ve got the perfect recipe for your daily reading.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-800 transform transition-all duration-300 hover:scale-105 hover:shadow-lg group">
            <div className="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4 mx-auto group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800/30 transition-colors">
              <Utensils className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="font-serif text-xl font-bold text-gray-900 dark:text-white mb-3 text-center">
              Handpicked Ingredients
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-center">
              We source only the finest content from across the web. No junk
              food here—just the good stuff.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-800 transform transition-all duration-300 hover:scale-105 hover:shadow-lg group">
            <div className="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4 mx-auto group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800/30 transition-colors">
              <ChefHat className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="font-serif text-xl font-bold text-gray-900 dark:text-white mb-3 text-center">
              Chef&apos;s Special
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-center">
              Our AI chef learns your taste preferences and prepares a
              personalized menu just for you.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-800 transform transition-all duration-300 hover:scale-105 hover:shadow-lg group">
            <div className="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4 mx-auto group-hover:bg-indigo-200 dark:group-hover:bg-indigo-800/30 transition-colors">
              <Coffee className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h3 className="font-serif text-xl font-bold text-gray-900 dark:text-white mb-3 text-center">
              Perfect Presentation
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-center">
              Beautifully plated articles in our elegant newspaper-inspired
              design. A feast for your eyes!
            </p>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="max-w-4xl mx-auto mb-16 md:mb-24">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-1 transform transition-all duration-300 hover:rotate-1 hover:scale-[1.01]">
          <div className="bg-white dark:bg-gray-900 rounded-lg p-8 md:p-12">
            <div className="flex flex-col items-center text-center">
              <div className="mb-6 relative">
                <svg
                  className="h-16 w-16 text-indigo-600 dark:text-indigo-400"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M9.13456 9H5.25654C4.85754 9 4.58854 8.407 4.81254 8.079C5.68954 6.777 6.41454 4.674 6.69754 3H9.13456C9.51856 3 9.83156 3.313 9.83156 3.697V8.303C9.83156 8.687 9.51856 9 9.13456 9Z"
                    fill="currentColor"
                  />
                  <path
                    d="M18.4655 9H14.5875C14.1885 9 13.9195 8.407 14.1435 8.079C15.0205 6.777 15.7455 4.674 16.0285 3H18.4655C18.8495 3 19.1625 3.313 19.1625 3.697V8.303C19.1625 8.687 18.8495 9 18.4655 9Z"
                    fill="currentColor"
                  />
                  <path
                    d="M9.13456 21H5.25654C4.85754 21 4.58854 20.407 4.81254 20.079C5.68954 18.777 6.41454 16.674 6.69754 15H9.13456C9.51856 15 9.83156 15.313 9.83156 15.697V20.303C9.83156 20.687 9.51856 21 9.13456 21Z"
                    fill="currentColor"
                  />
                  <path
                    d="M18.4655 21H14.5875C14.1885 21 13.9195 20.407 14.1435 20.079C15.0205 18.777 15.7455 16.674 16.0285 15H18.4655C18.8495 15 19.1625 15.313 19.1625 15.697V20.303C19.1625 20.687 18.8495 21 18.4655 21Z"
                    fill="currentColor"
                  />
                </svg>
              </div>
              <p className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 mb-6 font-serif italic">
                Gourmet is like having a Michelin-star chef for my brain! It serves up exactly the content I&apos;m hungry for, right when I want it.
              </p>
              <div className="flex items-center justify-center">
                <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-full flex items-center justify-center mr-3">
                  <ChefHat className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-white">
                    Alex Rodriguez
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Food Blogger & Tech Enthusiast
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-4xl mx-auto relative">
        <div className="bg-white dark:bg-gray-900 rounded-lg p-8 md:p-12 shadow-xl border border-gray-200 dark:border-gray-800 text-center">
          <h2 className="font-serif text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
            Ready to satisfy your appetite for great content?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Join our table of content connoisseurs. We promise you&apos;ll never go hungry for good reads again!
          </p>
          <SignUpButton>
            <button className="px-8 py-4 text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-md transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg group">
              Grab a seat at the table
              <ArrowRight className="ml-2 inline-block h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </SignUpButton>
        </div>
      </section>
    </div>
  );
}
