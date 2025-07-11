import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailCatalog = () => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');
    
    useEffect(() => {
        const fetchEmails = async () => {
            try {
                const response = await axios.get(`/api/emails/?page=${page}&search=${searchTerm}`);
                setEmails(response.data.results);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching emails:', error);
            }
        };
        
        fetchEmails();
    }, [page, searchTerm]);
    
    return (
        <div>
            <input
                type="text"
                placeholder="Search emails..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            
            {loading ? (
                <p>Loading...</p>
            ) : (
                <ul>
                    {emails.map(email => (
                        <li key={email.id}>
                            <h3>{email.subject}</h3>
                            <p>From: {email.sender}</p>
                            <p>{email.body.substring(0, 100)}...</p>
                        </li>
                    ))}
                </ul>
            )}
            
            <button onClick={() => setPage(p => Math.max(1, p - 1))}>Previous</button>
            <button onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
    );
};

export default EmailCatalog;
