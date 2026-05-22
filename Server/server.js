const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const path = require('path');

// This forces Express to look relative to where server.js actually lives
app.use(express.static(path.join(__dirname, 'public')));
let graphState = {
    nodes: {},
    edges: []
};

io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
    socket.emit('init_graph', graphState);

    // 1. Add a new blank node from the drawer
    socket.on('add_node', (nodeData) => {
        graphState.nodes[nodeData.id] = nodeData;
        io.emit('node_added', nodeData);
    });

    // 2. Live-update the drawing
    socket.on('update_node', (data) => {
        if(graphState.nodes[data.id]) {
            graphState.nodes[data.id].image = data.image;
            // Broadcast the new image to all viewers
            io.emit('node_updated', data); 
        }
    });

    // 3. Move nodes around the viewer
    socket.on('move_node', (data) => {
        if(graphState.nodes[data.id]) {
            graphState.nodes[data.id].x = data.x;
            graphState.nodes[data.id].y = data.y;
            socket.broadcast.emit('node_moved', data);
        }
    });

    // 4. Create connections between nodes
    socket.on('add_edge', (edgeData) => {
        graphState.edges.push(edgeData);
        io.emit('edge_added', edgeData);
    });

    // 5. Connect all nodes from one tile to another
    socket.on('connect_tiles', (data) => {
        const sourceNodes = Object.values(graphState.nodes).filter(n => n.deviceId === data.source);
        const targetNodes = Object.values(graphState.nodes).filter(n => n.deviceId === data.target);
        
        sourceNodes.forEach(sourceNode => {
            targetNodes.forEach(targetNode => {
                const edgeData = { source: sourceNode.id, target: targetNode.id };
                graphState.edges.push(edgeData);
                io.emit('edge_added', edgeData);
            });
        });
    });
    
    socket.on('python_update', (data) => {
        socket.broadcast.emit('python_update', data);
    });

});

server.listen(1234, '0.0.0.0', () => {
    console.log('Server running on port 1234');
});