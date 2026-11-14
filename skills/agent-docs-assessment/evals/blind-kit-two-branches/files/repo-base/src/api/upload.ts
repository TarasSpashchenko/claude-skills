import { showErrorToast } from '@/utils/toast'

export interface UploadResult {
  id: string
  url: string
}

export async function uploadFile(file: File, onProgress?: (percent: number) => void): Promise<UploadResult> {
  if (file.size === 0) {
    throw new Error('Cannot upload an empty file')
  }
  const form = new FormData()
  form.append('file', file)
  onProgress?.(0)
  const response = await fetch('/api/uploads', {
    method: 'POST',
    body: form,
    credentials: 'include',
  })
  if (!response.ok) {
    showErrorToast(response.status)
    throw response
  }
  onProgress?.(100)
  const result = (await response.json()) as UploadResult
  if (!result.id || !result.url) {
    throw new Error('Upload response is missing id or url')
  }
  return result
}
