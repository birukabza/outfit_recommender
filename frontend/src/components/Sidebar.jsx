import { useState, useEffect } from 'react'
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import axios from 'axios'

function Sidebar({ onSessionSelect, currentSessionId }) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [sessionToDelete, setSessionToDelete] = useState(null)

  const fetchSessions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/sessions', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      setSessions(response.data)
    } catch (error) {
      console.error('Error fetching sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSessions()
  }, [])

  const handleNewChat = () => {
    onSessionSelect(null)
  }

  const handleDeleteClick = (event, session) => {
    event.stopPropagation()
    setSessionToDelete(session)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    try {
      await axios.delete(`http://localhost:5000/sessions/${sessionToDelete._id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      // If the deleted session was the current one, clear the chat
      if (sessionToDelete._id === currentSessionId) {
        onSessionSelect(null)
      }
      
      // Refresh the sessions list
      fetchSessions()
    } catch (error) {
      console.error('Error deleting session:', error)
    } finally {
      setDeleteDialogOpen(false)
      setSessionToDelete(null)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setSessionToDelete(null)
  }

  return (
    <Box
      sx={{
        width: 260,
        height: '100%',
        borderRight: 1,
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleNewChat}
          sx={{ mb: 2 }}
        >
          New Chat
        </Button>
      </Box>
      <Divider />
      <List sx={{ flex: 1, overflow: 'auto' }}>
        {sessions.map((session) => (
          <ListItem 
            key={session._id} 
            disablePadding
            secondaryAction={
              <IconButton 
                edge="end" 
                aria-label="delete"
                onClick={(e) => handleDeleteClick(e, session)}
                sx={{ 
                  opacity: 0.7,
                  '&:hover': {
                    opacity: 1,
                    color: 'error.main'
                  }
                }}
              >
                <DeleteIcon />
              </IconButton>
            }
          >
            <ListItemButton
              selected={session._id === currentSessionId}
              onClick={() => onSessionSelect(session._id)}
            >
              <ListItemText
                primary={new Date(session.created_at).toLocaleDateString()}
                secondary={new Date(session.created_at).toLocaleTimeString()}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Delete Chat Session</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this chat session? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Sidebar