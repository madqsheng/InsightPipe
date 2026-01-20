const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
    healthCheck: async () => {
        const res = await fetch(`${API_BASE_URL}/../health`);
        if (!res.ok) throw new Error('Backend not healthy');
        return res.json();
    },

    generatePrompt: async (userInput) => {
        const res = await fetch(`${API_BASE_URL}/prompt/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_input: userInput })
        });
        if (!res.ok) throw new Error('Failed to generate prompt');
        return res.json();
    },

    saveDocument: async (title, content, overwrite = true) => {
        const res = await fetch(`${API_BASE_URL}/docs/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, overwrite })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to save document');
        }
        return res.json();
    },

    listDocuments: async () => {
        const res = await fetch(`${API_BASE_URL}/docs`);
        if (!res.ok) throw new Error('Failed to list documents');
        return res.json();
    },

    getDocument: async (filename) => {
        const res = await fetch(`${API_BASE_URL}/docs/${filename}`);
        if (!res.ok) throw new Error('Failed to load document');
        return res.json();
    }
};
