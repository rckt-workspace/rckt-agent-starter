import { useState, useRef, useEffect, KeyboardEvent, ChangeEvent } from 'react'
import { sendMessage, sendDocumentMessage, ApiError } from './services/agentApi'

interface Message {
  id: string
  sender: 'user' | 'assistant'
  text: string
  fileName?: string
  fileSize?: string
}

const SUGGESTIONS = [
  {
    title: '📄 Analizar Documento',
    desc: 'Adjunta un PDF, DOCX o CSV para extraer y resumir sus puntos clave.',
    prompt: 'Por favor analiza este documento y resume los puntos más importantes.',
    isDoc: true,
  },
  {
    title: '🚀 ¿Qué es RCKT?',
    desc: 'Conoce los sistemas de crecimiento y servicios que ofrece la empresa.',
    prompt: '¿Qué servicios y sistemas ofrece RCKT para hacer crecer un negocio?',
  },
  {
    title: '🧠 Advisory & CAIO',
    desc: 'Aprende cómo funciona el servicio de dirección de IA fraccional.',
    prompt: 'Explícame en qué consiste el servicio de Advisory / CAIO fraccional de RCKT.',
  },
  {
    title: '📊 Sistemas de Performance',
    desc: 'Descubre el sistema de publicidad supervisada y creatividad con IA.',
    prompt: '¿Cómo funcionan el Performance Media System y el Creative Performance System de RCKT?',
  },
]

export default function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Sync theme with data-theme attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`
    }
  }, [inputText])

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }

  const handleNewChat = () => {
    setMessages([])
    setInputText('')
    setSelectedFile(null)
    setErrorMessage(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

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

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const handleCopy = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      // Ignore clipboard write failures
    }
  }

  const submitMessage = async (textToSend: string, fileToSend: File | null) => {
    const trimmed = textToSend.trim()
    if (!trimmed && !fileToSend) return
    if (isLoading) return

    const finalQuestion = trimmed || 'Por favor analiza este documento.'

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: finalQuestion,
      fileName: fileToSend ? fileToSend.name : undefined,
      fileSize: fileToSend ? formatFileSize(fileToSend.size) : undefined,
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    handleRemoveFile()
    setIsLoading(true)
    setErrorMessage(null)

    try {
      let answer = ''
      if (fileToSend) {
        const res = await sendDocumentMessage(finalQuestion, fileToSend)
        answer = res.answer
      } else {
        const res = await sendMessage(finalQuestion)
        answer = res.answer
      }

      const assistantMsg: Message = {
        id: `asst-${Date.now()}`,
        sender: 'assistant',
        text: answer,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        setErrorMessage(error.detail)
      } else if (error instanceof Error) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage('Error al conectar con el servidor.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submitMessage(inputText, selectedFile)
    }
  }

  const handleSuggestionClick = (prompt: string, isDoc?: boolean) => {
    if (isDoc) {
      setInputText(prompt)
      fileInputRef.current?.click()
    } else {
      submitMessage(prompt, null)
    }
  }

  return (
    <div className="app-layout">
      {/* Minimal Top Header */}
      <header className="top-header">
        <div className="header-brand">
          <div className="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="brand-title">RCKT Assistant</span>
          <span className="badge-version">v1.1</span>
        </div>

        <div className="header-actions">
          <button type="button" className="icon-btn" onClick={handleNewChat} title="Iniciar nueva conversación">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Nuevo chat</span>
          </button>

          <button
            type="button"
            className="icon-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
          >
            {theme === 'dark' ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="5" />
                <line x1="12" y1="1" x2="12" y2="3" />
                <line x1="12" y1="21" x2="12" y2="23" />
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                <line x1="1" y1="12" x2="3" y2="12" />
                <line x1="21" y1="12" x2="23" y2="12" />
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
        </div>
      </header>

      {/* Main Conversation Stream */}
      <main className="chat-viewport">
        {messages.length === 0 ? (
          <div className="hero-state">
            <div className="hero-avatar">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
            </div>
            <h1 className="hero-title">¿En qué puedo ayudarte hoy?</h1>
            <p className="hero-subtitle">
              Pregunta lo que necesites o adjunta un documento (<strong>.pdf, .docx, .csv, .txt, .md</strong>) para
              analizarlo de inmediato.
            </p>

            <div className="suggestions-grid">
              {SUGGESTIONS.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="suggestion-card"
                  onClick={() => handleSuggestionClick(item.prompt, item.isDoc)}
                >
                  <strong>{item.title}</strong>
                  <span>{item.desc}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-content-wrap">
            {messages.map((msg) => (
              <div key={msg.id} className={`msg-row ${msg.sender}`}>
                {msg.sender === 'assistant' && (
                  <div className="msg-avatar assistant">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                  </div>
                )}

                <div className="msg-bubble">
                  {msg.fileName && (
                    <div className="msg-file-chip">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <span>{msg.fileName}</span>
                      {msg.fileSize && <small style={{ opacity: 0.7 }}>({msg.fileSize})</small>}
                    </div>
                  )}

                  <div className="msg-text">{msg.text}</div>

                  {msg.sender === 'assistant' && (
                    <div className="msg-actions">
                      <button
                        type="button"
                        className="action-btn"
                        onClick={() => handleCopy(msg.text, msg.id)}
                        title="Copiar respuesta"
                      >
                        {copiedId === msg.id ? (
                          <>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10a37f" strokeWidth="2.5">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                            <span style={{ color: '#10a37f' }}>Copiado</span>
                          </>
                        ) : (
                          <>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                            </svg>
                            <span>Copiar</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="msg-row assistant">
                <div className="msg-avatar assistant">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                </div>
                <div className="msg-bubble">
                  <div className="typing-bubble">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Floating Bottom Input Dock */}
      <footer className="chat-bottom-dock">
        {errorMessage && (
          <div className="floating-error">
            <span>⚠️ {errorMessage}</span>
            <button
              type="button"
              className="dismiss-btn"
              onClick={() => setErrorMessage(null)}
              aria-label="Cerrar error"
            >
              ✕
            </button>
          </div>
        )}

        <div className="input-capsule">
          {/* File Attachment Chip */}
          {selectedFile && (
            <div className="dock-file-preview">
              <div className="dock-file-info">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <strong>{selectedFile.name}</strong>
                <span className="dock-file-size">({formatFileSize(selectedFile.size)})</span>
              </div>
              <button
                type="button"
                className="dock-remove-file"
                onClick={handleRemoveFile}
                title="Quitar archivo adjunto"
                aria-label="Quitar archivo"
              >
                ✕
              </button>
            </div>
          )}

          <div className="capsule-row">
            {/* Hidden native input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.md,.csv"
              style={{ display: 'none' }}
            />

            {/* Paperclip Button */}
            <button
              type="button"
              className="clip-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Adjuntar documento (.pdf, .docx, .txt, .md, .csv)"
              aria-label="Adjuntar archivo"
              disabled={isLoading}
            >
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            </button>

            {/* Auto-expanding Textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              className="capsule-textarea"
              placeholder={
                selectedFile
                  ? 'Escribe tu pregunta sobre el documento...'
                  : 'Envía un mensaje o adjunta un documento...'
              }
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />

            {/* Send Button */}
            <button
              type="button"
              className="submit-arrow-btn"
              onClick={() => submitMessage(inputText, selectedFile)}
              disabled={isLoading || (!inputText.trim() && !selectedFile)}
              aria-label="Enviar mensaje"
              title="Enviar mensaje"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="19" x2="12" y2="5" />
                <polyline points="5 12 12 5 19 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="dock-disclaimer">
          RCKT Assistant procesa documentos en memoria temporalmente. La IA puede cometer errores.
        </div>
      </footer>
    </div>
  )
}
