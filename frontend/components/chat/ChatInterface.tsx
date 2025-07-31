'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Upload, FileText, Bot, User, Loader2, AlertCircle } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Array<{
    document_id: string
    filename: string
    relevance_score: number
    chunk_count: number
  }>
}

interface ChatInterfaceProps {
  onDocumentUpload?: (file: File) => void
  apiUrl: string
}

export default function ChatInterface({ onDocumentUpload, apiUrl }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant. Upload documents and ask me questions about them. I can help you understand and find information in your documents.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      // Get auth token from session storage or localStorage
      const session = JSON.parse(localStorage.getItem('supabase.auth.token') || '{}')
      const token = session?.access_token

      if (!token) {
        throw new Error('Not authenticated')
      }

      // Prepare chat history for context
      const chatHistory = messages.slice(-5).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await fetch(`${apiUrl}/api/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: input,
          chat_history: chatHistory
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to get response')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        sources: data.sources
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && onDocumentUpload) {
      onDocumentUpload(file)
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className=\"flex flex-col h-full bg-white rounded-lg shadow-sm border border-claude-gray-200\">
      {/* Chat Header */}
      <div className=\"flex items-center justify-between p-4 border-b border-claude-gray-200\">
        <div className=\"flex items-center space-x-2\">
          <Bot className=\"w-6 h-6 text-claude-orange\" />
          <h3 className=\"text-lg font-semibold text-claude-gray-900\">AI Assistant</h3>
        </div>
        <button
          onClick={() => fileInputRef.current?.click()}
          className=\"flex items-center space-x-2 px-3 py-2 text-sm bg-claude-orange text-white rounded-lg hover:bg-orange-600 transition\"
        >
          <Upload className=\"w-4 h-4\" />
          <span>Upload Document</span>
        </button>
        <input
          ref={fileInputRef}
          type=\"file\"
          accept=\".pdf,.docx,.doc,.txt\"
          onChange={handleFileUpload}
          className=\"hidden\"
        />
      </div>

      {/* Messages */}
      <div className=\"flex-1 overflow-y-auto p-4 space-y-4\">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-claude-orange text-white'
                  : 'bg-claude-gray-50 text-claude-gray-900'
              }`}
            >
              <div className=\"flex items-start space-x-2\">
                {message.role === 'assistant' && (
                  <Bot className=\"w-5 h-5 mt-0.5 text-claude-orange\" />
                )}
                {message.role === 'user' && (
                  <User className=\"w-5 h-5 mt-0.5 text-white\" />
                )}
                <div className=\"flex-1\">
                  <div className=\"whitespace-pre-wrap\">{message.content}</div>
                  
                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className=\"mt-3 pt-3 border-t border-claude-gray-200\">
                      <div className=\"text-sm font-medium text-claude-gray-600 mb-2\">
                        Sources:
                      </div>
                      <div className=\"space-y-1\">
                        {message.sources.map((source, index) => (
                          <div
                            key={index}
                            className=\"flex items-center space-x-2 text-sm text-claude-gray-600\"
                          >
                            <FileText className=\"w-4 h-4\" />
                            <span>{source.filename}</span>
                            <span className=\"text-xs text-claude-gray-500\">
                              ({Math.round(source.relevance_score * 100)}% relevant)
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div
                    className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-white/70' : 'text-claude-gray-500'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className=\"flex justify-start\">
            <div className=\"bg-claude-gray-50 rounded-lg p-4 max-w-[80%]\">
              <div className=\"flex items-center space-x-2\">
                <Bot className=\"w-5 h-5 text-claude-orange\" />
                <Loader2 className=\"w-4 h-4 animate-spin text-claude-orange\" />
                <span className=\"text-claude-gray-600\">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Display */}
      {error && (
        <div className=\"mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-700\">
          <AlertCircle className=\"w-4 h-4\" />
          <span className=\"text-sm\">{error}</span>
        </div>
      )}

      {/* Input */}
      <div className=\"p-4 border-t border-claude-gray-200\">
        <div className=\"flex space-x-2\">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder=\"Ask a question about your documents...\"
            className=\"flex-1 p-3 border border-claude-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-claude-orange focus:border-transparent\"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className=\"px-4 py-2 bg-claude-orange text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition\"
          >
            <Send className=\"w-5 h-5\" />
          </button>
        </div>
        <div className=\"text-xs text-claude-gray-500 mt-2\">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}