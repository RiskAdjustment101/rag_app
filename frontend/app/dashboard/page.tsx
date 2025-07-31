'use client'

import { useAuth } from '@/lib/auth-context'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import { LogOut, Upload, FileText, MessageSquare } from 'lucide-react'

export default function DashboardPage() {
  const { user, signOut } = useAuth()

  const handleSignOut = async () => {
    await signOut()
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-claude-cream to-white">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-claude-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-claude-orange">RAG App</h1>
                <span className="ml-4 text-claude-gray-600">Dashboard</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-claude-gray-600">
                  Welcome, {user?.email}
                </span>
                <button
                  onClick={handleSignOut}
                  className="flex items-center space-x-2 text-claude-gray-600 hover:text-claude-gray-900 transition"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-claude-gray-900 mb-2">
              Welcome to your document intelligence platform
            </h2>
            <p className="text-claude-gray-600">
              Upload documents and start chatting with your knowledge base using AI.
            </p>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <ActionCard
              icon={<Upload className="w-8 h-8 text-claude-orange" />}
              title="Upload Documents"
              description="Add PDFs, Word docs, or text files to your knowledge base"
              action="Upload Files"
              disabled={true}
              comingSoon={true}
            />
            <ActionCard
              icon={<MessageSquare className="w-8 h-8 text-claude-orange" />}
              title="Start Chatting"
              description="Ask questions about your documents and get AI-powered answers"
              action="New Chat"
              disabled={true}
              comingSoon={true}
            />
            <ActionCard
              icon={<FileText className="w-8 h-8 text-claude-orange" />}
              title="Manage Documents"
              description="View, organize, and delete your uploaded documents"
              action="View Documents"
              disabled={true}
              comingSoon={true}
            />
          </div>

          {/* Stats/Overview */}
          <div className="bg-white rounded-lg shadow-sm border border-claude-gray-200 p-6">
            <h3 className="text-lg font-semibold text-claude-gray-900 mb-4">
              Your Account Overview
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Documents" value="0" />
              <StatCard label="Conversations" value="0" />
              <StatCard label="Messages" value="0" />
              <StatCard label="Storage Used" value="0 MB" />
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

function ActionCard({ 
  icon, 
  title, 
  description, 
  action, 
  disabled = false, 
  comingSoon = false 
}: {
  icon: React.ReactNode
  title: string
  description: string
  action: string
  disabled?: boolean
  comingSoon?: boolean
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-claude-gray-200 p-6 hover:shadow-md transition">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-claude-gray-900 mb-2">{title}</h3>
      <p className="text-claude-gray-600 mb-4 text-sm">{description}</p>
      <button
        disabled={disabled}
        className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition ${
          disabled
            ? 'bg-claude-gray-100 text-claude-gray-400 cursor-not-allowed'
            : 'bg-claude-orange text-white hover:bg-orange-600'
        }`}
      >
        {comingSoon ? 'Coming Soon' : action}
      </button>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold text-claude-gray-900">{value}</div>
      <div className="text-sm text-claude-gray-600">{label}</div>
    </div>
  )
}