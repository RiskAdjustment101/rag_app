'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import ChatInterface from '@/components/chat/ChatInterface'
import DocumentManager from '@/components/documents/DocumentManager'
import { LogOut, MessageSquare, FileText } from 'lucide-react'

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [activeTab, setActiveTab] = useState<'chat' | 'documents'>('chat')
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://rag-app-9pwbjw.fly.dev'

  const handleSignOut = async () => {
    await signOut()
  }

  const handleDocumentUploaded = () => {
    // Refresh or notify chat that new document is available
    console.log('Document uploaded successfully')
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-claude-cream to-white">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-claude-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-claude-orange">RAG IQ</h1>
                <span className="ml-4 text-claude-gray-600">Document Intelligence</span>
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
          {/* Tab Navigation */}
          <div className="flex space-x-1 bg-claude-gray-100 p-1 rounded-lg mb-6 w-fit">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'chat'
                  ? 'bg-white text-claude-orange shadow-sm'
                  : 'text-claude-gray-600 hover:text-claude-gray-900'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>AI Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition ${
                activeTab === 'documents'
                  ? 'bg-white text-claude-orange shadow-sm'
                  : 'text-claude-gray-600 hover:text-claude-gray-900'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Documents</span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="h-[calc(100vh-200px)]">
            {activeTab === 'chat' && (
              <ChatInterface 
                apiUrl={apiUrl}
                onDocumentUpload={(file) => {
                  // Switch to documents tab and upload
                  setActiveTab('documents')
                  // This would trigger the upload in DocumentManager
                }}
              />
            )}
            
            {activeTab === 'documents' && (
              <DocumentManager 
                apiUrl={apiUrl}
                onDocumentUploaded={handleDocumentUploaded}
              />
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}

