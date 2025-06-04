import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import ChatIcon from '@mui/icons-material/Chat'

function Navbar({ isAuthenticated, setIsAuthenticated }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    navigate('/login')
  }

  return (
    <AppBar position="static">
      <Toolbar>
        <ChatIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI Chat
        </Typography>
        <Box>
          {isAuthenticated ? (
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          ) : (
            <>
              <Button color="inherit" component={RouterLink} to="/login">
                Login
              </Button>
              <Button color="inherit" component={RouterLink} to="/register">
                Register
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar 