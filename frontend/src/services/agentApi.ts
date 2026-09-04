const BASE_URL = import.meta.env.VITE_AGENT_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')


export interface ChatResponse {
  answer: string
}

export interface AgentInfo {
  name: string
  version: string
}

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

/**
 * Sends a plain text message to POST /api/chat.
 */
export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    let errorDetail = 'Error al procesar el mensaje.'
    try {
      const errorData = await response.json()
      if (errorData?.detail) {
        errorDetail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
      }
    } catch {
      // Fallback if response body is not JSON
    }
    throw new ApiError(response.status, errorDetail)
  }

  return response.json()
}

/**
 * Sends a message along with an attached document to POST /api/chat/document using multipart/form-data.
 */
export async function sendDocumentMessage(message: string, file: File): Promise<ChatResponse> {
  const formData = new FormData()
  formData.append('message', message)
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/api/chat/document`, {
    method: 'POST',
    // Do not set Content-Type header; browser sets multipart/form-data with proper boundary automatically
    body: formData,
  })

  if (!response.ok) {
    let errorDetail = 'Error al procesar el documento.'
    try {
      const errorData = await response.json()
      if (errorData?.detail) {
        errorDetail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
      }
    } catch {
      // Fallback if response body is not JSON
    }
    throw new ApiError(response.status, errorDetail)
  }

  return response.json()
}
