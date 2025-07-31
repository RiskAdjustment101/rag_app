import Link from 'next/link'
import { FileText, MessageSquare, Zap, Shield, Upload, Search } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-claude-cream to-white dark:from-claude-gray-900 dark:to-claude-gray-800">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 dark:bg-claude-gray-900/80 backdrop-blur-sm z-50 border-b border-claude-gray-200 dark:border-claude-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-claude-orange">RAG App</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-claude-gray-600 hover:text-claude-gray-900 dark:text-claude-gray-300 dark:hover:text-white">
                Sign In
              </Link>
              <Link href="/register" className="bg-claude-orange text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-5xl sm:text-6xl font-bold text-claude-gray-900 dark:text-white mb-6">
            Your Documents, <span className="text-claude-orange">Intelligently Understood</span>
          </h2>
          <p className="text-xl text-claude-gray-600 dark:text-claude-gray-300 mb-10 max-w-3xl mx-auto">
            Upload documents, ask questions, and get intelligent answers powered by advanced AI. 
            Experience Claude-like interactions with your own knowledge base.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" className="bg-claude-orange text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-orange-600 transition transform hover:scale-105">
              Start Free Trial
            </Link>
            <Link href="/demo" className="bg-white dark:bg-claude-gray-800 text-claude-gray-900 dark:text-white px-8 py-4 rounded-lg text-lg font-semibold border-2 border-claude-gray-200 dark:border-claude-gray-600 hover:border-claude-orange transition">
              Watch Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-claude-gray-900">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-3xl font-bold text-center text-claude-gray-900 dark:text-white mb-12">
            Powerful Features for Document Intelligence
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Upload className="w-8 h-8 text-claude-orange" />}
              title="Easy Upload"
              description="Drag and drop PDFs, Word docs, and text files. We handle the rest automatically."
            />
            <FeatureCard
              icon={<MessageSquare className="w-8 h-8 text-claude-orange" />}
              title="Natural Chat"
              description="Ask questions in plain English. Get accurate, contextual answers from your documents."
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8 text-claude-orange" />}
              title="Lightning Fast"
              description="Advanced vector search ensures you get relevant answers in milliseconds."
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-claude-orange" />}
              title="Secure & Private"
              description="Your documents are encrypted and isolated. Only you can access your data."
            />
            <FeatureCard
              icon={<FileText className="w-8 h-8 text-claude-orange" />}
              title="Multiple Formats"
              description="Support for PDF, DOCX, TXT, and Markdown files up to 50MB each."
            />
            <FeatureCard
              icon={<Search className="w-8 h-8 text-claude-orange" />}
              title="Smart Search"
              description="Find information across all your documents with intelligent semantic search."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-claude-orange to-orange-600">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-3xl font-bold text-white mb-6">
            Ready to Transform Your Document Workflow?
          </h3>
          <p className="text-xl text-white/90 mb-8">
            Join thousands of users who are already experiencing the power of AI-driven document intelligence.
          </p>
          <Link href="/register" className="bg-white text-claude-orange px-8 py-4 rounded-lg text-lg font-semibold hover:bg-claude-cream transition transform hover:scale-105 inline-block">
            Get Started Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-claude-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h4 className="text-xl font-bold mb-4 text-claude-orange">RAG App</h4>
              <p className="text-claude-gray-400">
                Intelligent document understanding powered by advanced AI.
              </p>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Product</h5>
              <ul className="space-y-2 text-claude-gray-400">
                <li><Link href="/features" className="hover:text-white">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white">Pricing</Link></li>
                <li><Link href="/demo" className="hover:text-white">Demo</Link></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Company</h5>
              <ul className="space-y-2 text-claude-gray-400">
                <li><Link href="/about" className="hover:text-white">About</Link></li>
                <li><Link href="/blog" className="hover:text-white">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Legal</h5>
              <ul className="space-y-2 text-claude-gray-400">
                <li><Link href="/privacy" className="hover:text-white">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white">Terms</Link></li>
                <li><Link href="/security" className="hover:text-white">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-claude-gray-800 text-center text-claude-gray-400">
            <p>&copy; 2024 RAG Application. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-claude-gray-50 dark:bg-claude-gray-800 p-6 rounded-xl hover:shadow-lg transition">
      <div className="mb-4">{icon}</div>
      <h4 className="text-xl font-semibold text-claude-gray-900 dark:text-white mb-2">{title}</h4>
      <p className="text-claude-gray-600 dark:text-claude-gray-300">{description}</p>
    </div>
  )
}