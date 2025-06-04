import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import { useState } from 'react'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Register from './pages/Register'
import Chat from './pages/Chat'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

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