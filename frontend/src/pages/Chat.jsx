import { useState, useEffect, useRef } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  CircularProgress
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import axios from 'axios'

function Chat() {
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    const userMessage = {
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setLoading(true)

    try {
      const response = await axios.post('http://localhost:5000/chat', {
        message: newMessage,
        session_id: sessionId
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })

      // Update session ID if it's a new session
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      const botMessage = {
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        text: 'Sorry, there was an error processing your message.',
        sender: 'bot',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        height: 'calc(100vh - 200px)',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        {/* Messages Container */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2
          }}
        >
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                gap: 1
              }}
            >
              {message.sender === 'bot' && (
                <Avatar sx={{ bgcolor: 'primary.main' }}>B</Avatar>
              )}
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                  color: message.sender === 'user' ? 'white' : 'text.primary'
                }}
              >
                <Typography variant="body1">{message.text}</Typography>
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7
                  }}
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
              </Paper>
              {message.sender === 'user' && (
                <Avatar sx={{ bgcolor: 'secondary.main' }}>U</Avatar>
              )}
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', gap: 1 }}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>B</Avatar>
              <Paper elevation={1} sx={{ p: 2 }}>
                <CircularProgress size={20} />
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Container */}
        <Box
          component="form"
          onSubmit={handleSend}
          sx={{
            p: 2,
            bgcolor: 'background.paper',
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            gap: 1
          }}
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            disabled={loading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2
              }
            }}
          />
          <IconButton
            color="primary"
            type="submit"
            disabled={!newMessage.trim() || loading}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark'
              }
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  )
}

export default Chat 