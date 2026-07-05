const WebSocket = require('ws');
const ws = new WebSocket('ws://127.0.0.1:8000/ws/platform');
ws.on('open', () => { console.log('connected'); ws.close(); });
ws.on('error', (e) => console.error('error:', e.message));
ws.on('close', (c) => console.log('closed', c));
