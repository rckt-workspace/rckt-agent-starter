import { useState, useRef, useEffect, FormEvent, ChangeEvent } from 'react'
import { sendMessage, sendDocumentMessage, ApiError } from './services/agentApi'

interface Message {
  id: string
  sender: 'user' | 'assistant'
  text: string
  fileName?: string
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: '¡Hola! Soy tu asistente de RCKT. Puedes hacerme preguntas o adjuntar un documento (.pdf, .docx, .txt, .md, .csv) para analizarlo.',
    },
  ])
  const [inputText, setInputText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setErrorMessage(null)
    }
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    const text = inputText.trim()
    if (!text && !selectedFile) {
      return
    }

    if (isLoading) {
      return
    }

    const messageToSend = text || 'Por favor analiza este documento.'
    const fileToSend = selectedFile

    // Add user message to state
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: messageToSend,
      fileName: fileToSend ? fileToSend.name : undefined,
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    handleRemoveFile()
    setIsLoading(true)
    setErrorMessage(null)

    try {
      let responseAnswer = ''
      if (fileToSend) {
        const response = await sendDocumentMessage(messageToSend, fileToSend)
        responseAnswer = response.answer
      } else {
        const response = await sendMessage(messageToSend)
        responseAnswer = response.answer
      }

      const assistantMsg: Message = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: responseAnswer,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        setErrorMessage(error.detail)
      } else if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage('Ocurrió un error inesperado al conectar con el servidor.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="header-title-group">
          <div className="header-icon">R</div>
          <div>
            <h1>RCKT Assistant</h1>
            <span className="header-subtitle">Chat y análisis de documentos</span>
          </div>
        </div>
      </header>

      <section className="chat-messages" aria-label="Mensajes del chat">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.sender}`}>
            <div className="message-bubble">
              {msg.fileName && (
                <div className="attached-file-badge">
                  <span>📄</span>
                  <span>{msg.fileName}</span>
                </div>
              )}
              <p>{msg.text}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-bubble">
              <div className="loading-dots">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </section>

      <footer className="chat-input-area">
        {errorMessage && (
          <div className="error-banner">
            <span>⚠️ {errorMessage}</span>
            <button
              type="button"
              className="file-remove-btn"
              onClick={() => setErrorMessage(null)}
              aria-label="Cerrar error"
            >
              ✕
            </button>
          </div>
        )}

        {selectedFile && (
          <div className="file-preview-banner">
            <div className="file-preview-info">
              <span>📄</span>
              <strong>{selectedFile.name}</strong>
              <small>({(selectedFile.size / 1024).toFixed(1)} KB)</small>
            </div>
            <button
              type="button"
              className="file-remove-btn"
              onClick={handleRemoveFile}
              title="Quitar archivo"
              aria-label="Quitar archivo"
            >
              ✕
            </button>
          </div>
        )}

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt,.md,.csv"
            style={{ display: 'none' }}
          />

          <button
            type="button"
            className="attach-btn"
            onClick={() => fileInputRef.current?.click()}
            title="Adjuntar documento (.pdf, .docx, .txt, .md, .csv)"
            aria-label="Adjuntar archivo"
            disabled={isLoading}
          >
            📎
          </button>

          <input
            type="text"
            className="chat-input"
            placeholder={
              selectedFile
                ? 'Escribe tu pregunta sobre el documento...'
                : 'Escribe un mensaje o adjunta un documento...'
            }
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isLoading}
          />

          <button
            type="submit"
            className="send-btn"
            disabled={isLoading || (!inputText.trim() && !selectedFile)}
          >
            {isLoading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </footer>
    </div>
  )
}
