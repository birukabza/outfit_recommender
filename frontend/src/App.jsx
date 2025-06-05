import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import { useState, useEffect } from 'react'
import axios from 'axios'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Chat from './pages/Chat'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          await axios.get('http://localhost:5000/validate-token', {
            headers: {
              Authorization: `Bearer ${token}`
            }
          })
          setIsAuthenticated(true)
        } catch (error) {
          localStorage.removeItem('token')
          setIsAuthenticated(false)
        }
      }
      setIsLoading(false)
    }

    validateToken()
  }, [])

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Loading...
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Routes>
          <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/register" element={<Register setIsAuthenticated={setIsAuthenticated} />} />
          <Route 
            path="/chat" 
            element={
              isAuthenticated ? 
                <Chat /> : 
                <Navigate to="/login" replace />
            } 
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App 