'use client'

import { useState, useEffect } from 'react'
import { FileText, Upload, Trash2, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

interface Document {
  id: string
  filename: string
  file_size: number
  file_type: string
  chunks_created: number
  total_tokens: number
  upload_date: string
  processing_status: string
}

interface DocumentManagerProps {
  apiUrl: string
  onDocumentUploaded?: (document: Document) => void
}

export default function DocumentManager({ apiUrl, onDocumentUploaded }: DocumentManagerProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDocuments()
  }, [])

  const getAuthToken = () => {
    const session = JSON.parse(localStorage.getItem('supabase.auth.token') || '{}')
    return session?.access_token
  }

  const loadDocuments = async () => {
    try {
      const token = getAuthToken()
      if (!token) {
        throw new Error('Not authenticated')
      }

      // Note: This endpoint would need to be implemented in the backend
      // For now, we'll simulate loading documents
      setDocuments([])
      setIsLoading(false)
    } catch (err) {
      console.error('Failed to load documents:', err)
      setError('Failed to load documents')
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!file) return

    // Validate file
    const maxSize = 50 * 1024 * 1024 // 50MB
    const allowedTypes = ['pdf', 'docx', 'doc', 'txt']
    const fileExtension = file.name.split('.').pop()?.toLowerCase()

    if (file.size > maxSize) {
      setError('File too large. Maximum size is 50MB.')
      return
    }

    if (!fileExtension || !allowedTypes.includes(fileExtension)) {
      setError('Unsupported file type. Please upload PDF, DOCX, or TXT files.')
      return
    }

    setIsUploading(true)
    setError(null)
    setSuccess(null)
    setUploadProgress(0)

    try {
      const token = getAuthToken()
      if (!token) {
        throw new Error('Not authenticated')
      }

      const formData = new FormData()
      formData.append('file', file)

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch(`${apiUrl}/api/rag/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const result = await response.json()
      
      // Add to documents list
      const newDocument: Document = {
        id: result.document_id,
        filename: result.filename,
        file_size: result.file_size,
        file_type: result.file_type,
        chunks_created: result.chunks_created,
        total_tokens: result.total_tokens,
        upload_date: new Date().toISOString(),
        processing_status: result.processing_status
      }

      setDocuments(prev => [newDocument, ...prev])
      setSuccess(`Successfully uploaded ${file.name}`)
      
      if (onDocumentUploaded) {
        onDocumentUploaded(newDocument)
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setError(errorMessage)
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000)
    }
  }

  const handleDeleteDocument = async (documentId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete \"${filename}\"? This action cannot be undone.`)) {
      return
    }

    try {
      const token = getAuthToken()
      if (!token) {
        throw new Error('Not authenticated')
      }

      const response = await fetch(`${apiUrl}/api/rag/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Delete failed')
      }

      // Remove from documents list
      setDocuments(prev => prev.filter(doc => doc.id !== documentId))
      setSuccess(`Successfully deleted ${filename}`)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Delete failed'
      setError(errorMessage)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div className=\"bg-white rounded-lg shadow-sm border border-claude-gray-200 p-6\">
      <div className=\"flex items-center justify-between mb-6\">
        <h3 className=\"text-lg font-semibold text-claude-gray-900\">Document Manager</h3>
        <div className=\"text-sm text-claude-gray-600\">
          {documents.length} document{documents.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Upload Area */}
      <div className=\"mb-6\">
        <div
          className=\"border-2 border-dashed border-claude-gray-300 rounded-lg p-8 text-center hover:border-claude-orange transition-colors cursor-pointer\"
          onClick={() => document.getElementById('file-upload')?.click()}
        >
          <Upload className=\"w-12 h-12 text-claude-gray-400 mx-auto mb-4\" />
          <p className=\"text-lg font-medium text-claude-gray-900 mb-2\">
            Upload documents to your knowledge base
          </p>
          <p className=\"text-claude-gray-600 mb-4\">
            Drag and drop files here, or click to browse
          </p>
          <p className=\"text-sm text-claude-gray-500\">
            Supports PDF, DOCX, and TXT files up to 50MB
          </p>
          
          {isUploading && (
            <div className=\"mt-4\">
              <div className=\"bg-claude-gray-200 rounded-full h-2 mb-2\">
                <div
                  className=\"bg-claude-orange h-2 rounded-full transition-all duration-300\"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className=\"text-sm text-claude-gray-600\">
                Uploading... {uploadProgress}%
              </p>
            </div>
          )}
        </div>
        
        <input
          id=\"file-upload\"
          type=\"file\"
          accept=\".pdf,.docx,.doc,.txt\"
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
          className=\"hidden\"
          disabled={isUploading}
        />
      </div>

      {/* Messages */}
      {error && (
        <div className=\"mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-700\">
          <AlertCircle className=\"w-4 h-4\" />
          <span className=\"text-sm\">{error}</span>
          <button
            onClick={() => setError(null)}
            className=\"ml-auto text-red-500 hover:text-red-700\"
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div className=\"mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-2 text-green-700\">
          <CheckCircle className=\"w-4 h-4\" />
          <span className=\"text-sm\">{success}</span>
        </div>
      )}

      {/* Documents List */}
      <div className=\"space-y-3\">
        {isLoading ? (
          <div className=\"text-center py-8\">
            <Loader2 className=\"w-8 h-8 animate-spin text-claude-orange mx-auto mb-2\" />
            <p className=\"text-claude-gray-600\">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className=\"text-center py-8\">
            <FileText className=\"w-12 h-12 text-claude-gray-300 mx-auto mb-4\" />
            <p className=\"text-claude-gray-600 mb-2\">No documents uploaded yet</p>
            <p className=\"text-sm text-claude-gray-500\">
              Upload your first document to get started with AI-powered document search
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className=\"flex items-center justify-between p-4 border border-claude-gray-200 rounded-lg hover:bg-claude-gray-50 transition\"
            >
              <div className=\"flex items-center space-x-3\">
                <FileText className=\"w-8 h-8 text-claude-orange\" />
                <div>
                  <h4 className=\"font-medium text-claude-gray-900\">{doc.filename}</h4>
                  <div className=\"flex items-center space-x-4 text-sm text-claude-gray-600\">
                    <span>{formatFileSize(doc.file_size)}</span>
                    <span>{doc.chunks_created} chunks</span>
                    <span>{doc.total_tokens.toLocaleString()} tokens</span>
                    <span>Uploaded {formatDate(doc.upload_date)}</span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                className=\"p-2 text-red-600 hover:bg-red-50 rounded-lg transition\"
                title=\"Delete document\"
              >
                <Trash2 className=\"w-4 h-4\" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}