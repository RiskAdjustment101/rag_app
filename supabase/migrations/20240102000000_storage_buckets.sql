-- Create storage bucket for user documents
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'documents',
  'documents', 
  false,  -- Private bucket
  52428800,  -- 50MB limit
  ARRAY['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/markdown']
);

-- Storage policies for documents bucket
-- Users can upload to their own folder
CREATE POLICY "Users can upload their own documents" ON storage.objects
FOR INSERT WITH CHECK (
  auth.uid() IS NOT NULL AND
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can view their own documents
CREATE POLICY "Users can view their own documents" ON storage.objects
FOR SELECT USING (
  auth.uid() IS NOT NULL AND
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can update their own documents
CREATE POLICY "Users can update their own documents" ON storage.objects
FOR UPDATE USING (
  auth.uid() IS NOT NULL AND
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can delete their own documents
CREATE POLICY "Users can delete their own documents" ON storage.objects
FOR DELETE USING (
  auth.uid() IS NOT NULL AND
  bucket_id = 'documents' AND
  (storage.foldername(name))[1] = auth.uid()::text
);