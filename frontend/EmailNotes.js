import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailNotes = ({ emailId }) => {
    const [notes, setNotes] = useState([]);
    const [newNote, setNewNote] = useState('');
    
    useEffect(() => {
        axios.get(`/api/emails/${emailId}/notes/`)
            .then(response => setNotes(response.data))
            .catch(error => console.error('Error fetching notes:', error));
    }, [emailId]);
    
    const handleSubmit = (e) => {
        e.preventDefault();
        axios.post(`/api/emails/${emailId}/notes/`, { content: newNote })
            .then(response => {
                setNotes([...notes, response.data]);
                setNewNote('');
            })
            .catch(error => console.error('Error creating note:', error));
    };
    
    return (
        <div>
            <h3>Notes</h3>
            <ul>
                {notes.map(note => (
                    <li key={note.id}>
                        <p>{note.content}</p>
                        <small>By {note.author} on {new Date(note.created_at).toLocaleString()}</small>
                    </li>
                ))}
            </ul>
            
            <form onSubmit={handleSubmit}>
                <textarea
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    minLength={10}
                    required
                />
                <button type="submit">Add Note</button>
            </form>
        </div>
    );
};

export default EmailNotes;
