"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Zap, Code, Shield, ArrowRight, Github, Star, Coffee, Menu, X } from "lucide-react"
import Link from "next/link"
import { BackgroundRemovalDemo } from "@/components/background-removal-demo"
import { XIcon } from "@/components/x-icon"
import { useState, useEffect } from "react"

export default function HomePage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      setIsScrolled(scrollTop > 50)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-neutral-950 text-white overflow-hidden">
      {/* Premium smooth background animation */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Subtle gradient mesh background */}
        <div className="absolute inset-0 bg-gradient-to-br from-orange-500/[0.02] via-transparent to-amber-500/[0.02] animate-subtle-pulse"></div>
        
        {/* Primary floating orb - main focal point */}
        <div className="absolute top-1/4 -right-32 w-80 h-80 bg-gradient-to-br from-orange-400/[0.08] via-amber-400/[0.06] to-orange-500/[0.04] rounded-full blur-3xl animate-smooth-float"></div>
        
        {/* Secondary orb for depth */}
        <div className="absolute -bottom-32 left-1/4 w-64 h-64 bg-gradient-to-tr from-amber-400/[0.06] via-orange-400/[0.04] to-amber-500/[0.02] rounded-full blur-3xl animate-smooth-float-delayed"></div>
        
        {/* Subtle accent particles */}
        <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-orange-400/[0.03] rounded-full blur-2xl animate-gentle-float"></div>
        <div className="absolute bottom-1/3 right-1/3 w-24 h-24 bg-amber-400/[0.03] rounded-full blur-xl animate-gentle-float-reverse"></div>
        
        {/* Ultra-subtle rotating gradient overlay */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full opacity-30">
          <div className="absolute inset-0 bg-gradient-conic from-orange-400/[0.01] via-transparent via-transparent via-transparent to-orange-400/[0.01] animate-ultra-slow-spin"></div>
        </div>
      </div>

      {/* Navigation - Mobile Optimized */}
      <nav className={`fixed top-0 left-0 right-0 z-50 header-transition ${
        isScrolled 
          ? 'header-scrolled' 
          : 'header-glass'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3 group">
              <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-500 rounded-lg shadow-lg shadow-orange-500/25 group-hover:shadow-orange-500/40 transition-all duration-300 group-hover:scale-110"></div>
              <span className="text-xl font-semibold text-white group-hover:text-orange-100 transition-colors duration-300">
                openBGremover
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-8">
              <Link
                href="/pricing"
                className="text-neutral-400 hover:text-white transition-all duration-300 hover:scale-105 relative group"
              >
                Pricing
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-orange-400 transition-all duration-300 group-hover:w-full"></span>
              </Link>
              <Link
                href="/docs"
                className="text-neutral-400 hover:text-white transition-all duration-300 hover:scale-105 relative group"
              >
                Documentation
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-orange-400 transition-all duration-300 group-hover:w-full"></span>
              </Link>
              <Link
                href="https://github.com/your-repo/openbgremover"
                className="flex items-center space-x-1 text-neutral-400 hover:text-white transition-all duration-300 hover:scale-105 group"
              >
                <Github className="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" />
                <span>GitHub</span>
                <Star className="w-3 h-3 group-hover:scale-125 transition-transform duration-300" />
              </Link>
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden lg:flex items-center space-x-3">
              <Link href="https://ko-fi.com/openbgremover" target="_blank">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-neutral-500 hover:text-orange-400 hover:bg-neutral-900 text-xs px-2 py-1 h-7 transition-all duration-300 hover:scale-105"
                >
                  <Coffee className="w-3 h-3 mr-1 hover:rotate-12 transition-transform duration-300" />
                  <span className="hidden xl:inline">Coffee</span>
                </Button>
              </Link>
              <Link href="/login">
                <Button
                  variant="ghost"
                  className="text-neutral-400 hover:text-white hover:bg-neutral-800 transition-all duration-300 hover:scale-105"
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button className="bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40 transition-all duration-300 hover:scale-105 hover:-translate-y-0.5">
                  Get Started
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <div className="lg:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="text-neutral-400 hover:text-white p-2"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="lg:hidden border-t border-neutral-800 py-4 space-y-4 animate-fade-in-up">
              <Link
                href="/pricing"
                className="block text-neutral-400 hover:text-white transition-colors duration-300 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link
                href="/docs"
                className="block text-neutral-400 hover:text-white transition-colors duration-300 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Documentation
              </Link>
              <Link
                href="https://github.com/your-repo/openbgremover"
                className="flex items-center space-x-2 text-neutral-400 hover:text-white transition-colors duration-300 py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                <Github className="w-4 h-4" />
                <span>GitHub</span>
                <Star className="w-3 h-3" />
              </Link>
              <div className="border-t border-neutral-800 pt-4 space-y-3">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button
                    variant="ghost"
                    className="w-full text-neutral-400 hover:text-white hover:bg-neutral-800 justify-start"
                  >
                    Sign In
                  </Button>
                </Link>
                <Link href="/signup" onClick={() => setMobileMenuOpen(false)}>
                  <Button className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white shadow-lg shadow-orange-500/20">
                    Get Started
                  </Button>
                </Link>
                <Link href="https://ko-fi.com/openbgremover" target="_blank" onClick={() => setMobileMenuOpen(false)}>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-neutral-500 hover:text-orange-400 hover:bg-neutral-900 justify-start"
                  >
                    <Coffee className="w-3 h-3 mr-2" />
                    Buy us a coffee
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section - Mobile Optimized */}
      <section className="pt-20 sm:pt-24 lg:pt-32 pb-12 sm:pb-16 relative">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(251,146,60,0.03),transparent_50%)]"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center px-3 sm:px-4 py-2 rounded-full bg-neutral-900 border border-neutral-700 text-neutral-300 text-xs sm:text-sm font-medium mb-6 sm:mb-8 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 group">
              <Github className="w-3 sm:w-4 h-3 sm:h-4 mr-2 group-hover:rotate-12 transition-transform duration-300" />
              <span className="hidden sm:inline">Open source • Transparent • No vendor lock-in</span>
              <span className="sm:hidden">Open source • No lock-in</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-6 sm:mb-8 leading-[1.1] animate-fade-in-up">
              <span className="block text-white hover:scale-105 transition-transform duration-500 inline-block">
                Background removal
              </span>
              <span className="block bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent hover:from-orange-300 hover:to-amber-300 transition-all duration-500">
                without the bullshit
              </span>
            </h1>

            <div className="space-y-4 sm:space-y-6 mb-8 sm:mb-12 animate-fade-in-up delay-200">
              <p className="text-lg sm:text-xl text-neutral-300 leading-relaxed hover:text-neutral-200 transition-colors duration-300 px-4 sm:px-0">
                Enterprise-grade AI background removal API. Pay per image processed, no expiring packages, no
                subscription traps.
              </p>
              <p className="text-base sm:text-lg text-neutral-400 leading-relaxed hover:text-neutral-300 transition-colors duration-300 px-4 sm:px-0">
                Most services are overpriced or deliver poor quality. We're different: open source, transparent pricing,
                and actually good results.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-8 sm:mb-12 animate-fade-in-up delay-400 px-4 sm:px-0">
              <Link href="/signup" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  className="w-full sm:w-auto text-base sm:text-lg px-6 sm:px-8 py-3 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40 transition-all duration-300 hover:scale-105 hover:-translate-y-1 group"
                >
                  Start removing backgrounds
                  <ArrowRight className="w-4 sm:w-5 h-4 sm:h-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>
              </Link>
              <Link href="https://github.com/your-repo/openbgremover" className="w-full sm:w-auto">
                <Button
                  variant="outline"
                  size="lg"
                  className="w-full sm:w-auto text-base sm:text-lg px-6 sm:px-8 py-3 border-neutral-600 text-neutral-300 hover:bg-neutral-800 hover:border-orange-500/50 hover:text-white transition-all duration-300 hover:scale-105 hover:-translate-y-1 group"
                >
                  <Github className="w-4 sm:w-5 h-4 sm:h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" />
                  View source code
                </Button>
              </Link>
            </div>

            {/* Clean, simple free trial mention - Mobile Optimized */}
            <div className="animate-fade-in-up delay-500 px-4 sm:px-0">
              <p className="text-neutral-400 text-base sm:text-lg mb-2">
                <span className="text-white font-semibold">50 free images</span> to get you started
              </p>
              <Link href="/pricing" className="inline-block">
                <Button
                  variant="ghost"
                  className="text-orange-400 hover:text-orange-300 hover:bg-orange-500/10 underline decoration-dotted underline-offset-4 transition-all duration-300 hover:scale-105 group text-sm sm:text-base"
                >
                  View pricing
                  <ArrowRight className="w-3 sm:w-4 h-3 sm:h-4 ml-1 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Value Props - Mobile Optimized */}
      <section className="py-12 sm:py-16 border-y border-neutral-800 bg-neutral-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8 text-center">
            <div className="space-y-3 group hover:scale-105 transition-all duration-300">
              <div className="w-2 h-2 bg-orange-400 rounded-full mx-auto group-hover:scale-150 group-hover:shadow-lg group-hover:shadow-orange-400/50 transition-all duration-300"></div>
              <h3 className="font-semibold text-white group-hover:text-orange-100 transition-colors duration-300 text-sm sm:text-base">
                No expiring packages
              </h3>
              <p className="text-xs sm:text-sm text-neutral-400 group-hover:text-neutral-300 transition-colors duration-300 px-2 sm:px-0">
                Buy image processing that lasts forever
              </p>
            </div>
            <div className="space-y-3 group hover:scale-105 transition-all duration-300">
              <div className="w-2 h-2 bg-orange-400 rounded-full mx-auto group-hover:scale-150 group-hover:shadow-lg group-hover:shadow-orange-400/50 transition-all duration-300"></div>
              <h3 className="font-semibold text-white group-hover:text-orange-100 transition-colors duration-300 text-sm sm:text-base">
                Pay only for processing
              </h3>
              <p className="text-xs sm:text-sm text-neutral-400 group-hover:text-neutral-300 transition-colors duration-300 px-2 sm:px-0">
                No monthly fees or hidden costs
              </p>
            </div>
            <div className="space-y-3 group hover:scale-105 transition-all duration-300">
              <div className="w-2 h-2 bg-orange-400 rounded-full mx-auto group-hover:scale-150 group-hover:shadow-lg group-hover:shadow-orange-400/50 transition-all duration-300"></div>
              <h3 className="font-semibold text-white group-hover:text-orange-100 transition-colors duration-300 text-sm sm:text-base">
                Enterprise quality, fair pricing
              </h3>
              <p className="text-xs sm:text-sm text-neutral-400 group-hover:text-neutral-300 transition-colors duration-300 px-2 sm:px-0">
                Same quality, fraction of the cost
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section - Mobile Optimized */}
      <section className="py-12 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-white hover:scale-105 transition-transform duration-500 inline-block">
              See the quality difference
            </h2>
            <p className="text-lg sm:text-xl text-neutral-400 leading-relaxed hover:text-neutral-300 transition-colors duration-300 px-4 sm:px-0">
              Upload an image and experience why developers choose our API over expensive alternatives
            </p>
          </div>
          <BackgroundRemovalDemo />
        </div>
      </section>

      {/* Why Different Section - Mobile Optimized */}
      <section className="py-12 sm:py-20 bg-neutral-900 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-white hover:scale-105 transition-transform duration-500 inline-block">
              Why we're different
            </h2>
            <p className="text-lg sm:text-xl text-neutral-400 leading-relaxed hover:text-neutral-300 transition-colors duration-300 px-4 sm:px-0">
              Tired of overpriced APIs with mediocre results and confusing pricing? So were we.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            <Card className="bg-neutral-800 border-neutral-700 hover:bg-neutral-750 hover:border-neutral-600 transition-all duration-300 group hover:scale-105 hover:-translate-y-2 hover:shadow-2xl hover:shadow-orange-500/10">
              <CardContent className="p-6 sm:p-8">
                <div className="w-10 sm:w-12 h-10 sm:h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center mb-4 sm:mb-6 shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 group-hover:scale-110 transition-all duration-300">
                  <Zap className="w-5 sm:w-6 h-5 sm:h-6 text-white group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4 text-white group-hover:text-orange-100 transition-colors duration-300">
                  No Bullshit Pricing
                </h3>
                <p className="text-sm sm:text-base text-neutral-400 leading-relaxed group-hover:text-neutral-300 transition-colors duration-300">
                  Pay per image processed. No monthly fees, no expiring packages, no hidden costs. Buy bulk processing
                  that never expires.
                </p>
              </CardContent>
            </Card>
            <Card className="bg-neutral-800 border-neutral-700 hover:bg-neutral-750 hover:border-neutral-600 transition-all duration-300 group hover:scale-105 hover:-translate-y-2 hover:shadow-2xl hover:shadow-orange-500/10">
              <CardContent className="p-6 sm:p-8">
                <div className="w-10 sm:w-12 h-10 sm:h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center mb-4 sm:mb-6 shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 group-hover:scale-110 transition-all duration-300">
                  <Shield className="w-5 sm:w-6 h-5 sm:h-6 text-white group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4 text-white group-hover:text-orange-100 transition-colors duration-300">
                  Enterprise Quality
                </h3>
                <p className="text-sm sm:text-base text-neutral-400 leading-relaxed group-hover:text-neutral-300 transition-colors duration-300">
                  State-of-the-art AI models, sub-2s processing, 99.9% uptime. The same quality big companies pay
                  thousands for.
                </p>
              </CardContent>
            </Card>
            <Card className="bg-neutral-800 border-neutral-700 hover:bg-neutral-750 hover:border-neutral-600 transition-all duration-300 group hover:scale-105 hover:-translate-y-2 hover:shadow-2xl hover:shadow-orange-500/10">
              <CardContent className="p-6 sm:p-8">
                <div className="w-10 sm:w-12 h-10 sm:h-12 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center mb-4 sm:mb-6 shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 group-hover:scale-110 transition-all duration-300">
                  <Code className="w-5 sm:w-6 h-5 sm:h-6 text-white group-hover:rotate-12 transition-transform duration-300" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold mb-3 sm:mb-4 text-white group-hover:text-orange-100 transition-colors duration-300">
                  Open Source
                </h3>
                <p className="text-sm sm:text-base text-neutral-400 leading-relaxed group-hover:text-neutral-300 transition-colors duration-300">
                  Full transparency. Check our code, contribute improvements, or self-host. No vendor lock-in, ever.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* API Example - Mobile Optimized */}
      <section className="py-12 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16 max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-white hover:scale-105 transition-transform duration-500 inline-block">
              Simple API, powerful results
            </h2>
            <p className="text-lg sm:text-xl text-neutral-400 leading-relaxed hover:text-neutral-300 transition-colors duration-300 px-4 sm:px-0">
              One API call. That's it. No complex setup, no SDKs to learn.
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <Card className="bg-neutral-900 border-neutral-800 shadow-2xl hover:shadow-3xl hover:scale-105 transition-all duration-300 group">
              <CardContent className="p-4 sm:p-8">
                <pre className="text-xs sm:text-sm overflow-x-auto text-neutral-300 leading-relaxed group-hover:text-neutral-200 transition-colors duration-300">
                  <code>{`curl -X POST https://api.openbgremover.com/v1/remove \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: multipart/form-data" \\
  -F "image=@/path/to/image.jpg"

# Response (< 2 seconds)
{
  "success": true,
  "result_url": "https://cdn.openbgremover.com/result.png",
  "processing_time": 1.2,
  "cost": 0.02
}`}</code>
                </pre>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Open Source CTA - Mobile Optimized */}
      <section className="py-12 sm:py-20 bg-neutral-900">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <Github className="w-12 sm:w-16 h-12 sm:h-16 text-neutral-600 mx-auto mb-6 sm:mb-8 hover:text-neutral-500 hover:scale-110 hover:rotate-12 transition-all duration-300" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4 sm:mb-6 text-white hover:scale-105 transition-transform duration-500 inline-block">
            Built in the open
          </h2>
          <p className="text-lg sm:text-xl text-neutral-400 mb-8 sm:mb-10 leading-relaxed hover:text-neutral-300 transition-colors duration-300">
            Check our code, contribute features, report issues, or fork it and run your own instance. Transparency isn't
            just a buzzword for us—it's how we build trust.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
            <Link href="https://github.com/your-repo/openbgremover" className="w-full sm:w-auto">
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-neutral-600 text-neutral-300 hover:bg-neutral-800 hover:border-orange-500/50 hover:text-white transition-all duration-300 hover:scale-105 hover:-translate-y-1 group"
              >
                <Github className="w-4 sm:w-5 h-4 sm:h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" />
                View on GitHub
              </Button>
            </Link>
            <Link href="/docs/self-hosting" className="w-full sm:w-auto">
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-neutral-600 text-neutral-300 hover:bg-neutral-800 hover:border-orange-500/50 hover:text-white transition-all duration-300 hover:scale-105 hover:-translate-y-1 group"
              >
                <Code className="w-4 sm:w-5 h-4 sm:h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" />
                Self-hosting guide
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer - Mobile Optimized */}
      <footer className="bg-neutral-950 border-t border-neutral-800 py-8 sm:py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-6 sm:gap-8">
            <div className="col-span-2 sm:col-span-3 lg:col-span-1 group">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-500 rounded-lg group-hover:scale-110 transition-transform duration-300"></div>
                <span className="text-lg font-semibold text-white group-hover:text-orange-100 transition-colors duration-300">
                  openBGremover
                </span>
              </div>
              <p className="text-neutral-400 text-sm leading-relaxed group-hover:text-neutral-300 transition-colors duration-300">
                Background removal API without the bullshit
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-3 sm:mb-4 text-white text-sm sm:text-base">Developers</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-neutral-400">
                <li>
                  <Link
                    href="/docs"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Documentation
                  </Link>
                </li>
                <li>
                  <Link
                    href="/docs/api"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    API Reference
                  </Link>
                </li>
                <li>
                  <Link
                    href="/status"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Status
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 sm:mb-4 text-white text-sm sm:text-base">Resources</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-neutral-400">
                <li>
                  <Link
                    href="https://github.com/your-repo/openbgremover"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    GitHub
                  </Link>
                </li>
                <li>
                  <Link
                    href="/changelog"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Changelog
                  </Link>
                </li>
                <li>
                  <Link
                    href="/support"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Support
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 sm:mb-4 text-white text-sm sm:text-base">Company</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-neutral-400">
                <li>
                  <Link
                    href="/pricing"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link
                    href="/contact"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Contact
                  </Link>
                </li>
                <li>
                  <Link
                    href="/privacy"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    Privacy
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 sm:mb-4 text-white text-sm sm:text-base">Compare</h4>
              <ul className="space-y-2 text-xs sm:text-sm text-neutral-400">
                <li>
                  <Link
                    href="/compare/removebg"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    vs Remove.bg
                  </Link>
                </li>
                <li>
                  <Link
                    href="/compare/photoshop"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    vs Photoshop API
                  </Link>
                </li>
                <li>
                  <Link
                    href="/compare/clipdrop"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    vs ClipDrop
                  </Link>
                </li>
                <li>
                  <Link
                    href="/compare/canva"
                    className="hover:text-orange-400 transition-colors duration-300 hover:translate-x-1 inline-block"
                  >
                    vs Canva API
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-neutral-800 mt-6 sm:mt-8 pt-6 sm:pt-8 flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
            <p className="text-neutral-400 text-xs sm:text-sm hover:text-neutral-300 transition-colors duration-300 text-center sm:text-left">
              &copy; 2024 openBGremover. Open source, always.
            </p>
            <div className="flex space-x-4">
              <Github className="w-4 h-4 text-neutral-400 hover:text-orange-400 cursor-pointer transition-all duration-300 hover:scale-125 hover:rotate-12" />
              <XIcon className="w-4 h-4 text-neutral-400 hover:text-orange-400 cursor-pointer transition-all duration-300 hover:scale-125 hover:rotate-12" />
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
