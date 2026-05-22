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
    edges: [],
    tileConnections: [] // Keeps track of tile-to-tile connections
};

io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);
    socket.emit('init_graph', graphState);

    // 1. Add a new blank node from the drawer
    socket.on('add_node', (nodeData) => {
        graphState.nodes[nodeData.id] = nodeData;
        io.emit('node_added', nodeData);
        
        // Automatically link the new node to other tiles if a tile connection exists
        graphState.tileConnections.forEach(conn => {
            if (conn.source === nodeData.deviceId) {
                // The new node belongs to a source tile, connect it to all target nodes
                const targetNodes = Object.values(graphState.nodes).filter(n => n.deviceId === conn.target);
                targetNodes.forEach(targetNode => {
                    const edgeData = { source: nodeData.id, target: targetNode.id };
                    graphState.edges.push(edgeData);
                    io.emit('edge_added', edgeData);
                });
            } else if (conn.target === nodeData.deviceId) {
                // The new node belongs to a target tile, connect all source nodes to it
                const sourceNodes = Object.values(graphState.nodes).filter(n => n.deviceId === conn.source);
                sourceNodes.forEach(sourceNode => {
                    const edgeData = { source: sourceNode.id, target: nodeData.id };
                    graphState.edges.push(edgeData);
                    io.emit('edge_added', edgeData);
                });
            }
        });
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
        // Record the connection between the tiles if it hasn't been recorded yet
        const connectionExists = graphState.tileConnections.some(
            conn => conn.source === data.source && conn.target === data.target
        );
        
        if (!connectionExists) {
            graphState.tileConnections.push({ source: data.source, target: data.target });
        }

        const sourceNodes = Object.values(graphState.nodes).filter(n => n.deviceId === data.source);
        const targetNodes = Object.values(graphState.nodes).filter(n => n.deviceId === data.target);
        
        sourceNodes.forEach(sourceNode => {
            targetNodes.forEach(targetNode => {
                // Only create the edge if it doesn't already exist to avoid duplicates
                const edgeExists = graphState.edges.some(
                    e => e.source === sourceNode.id && e.target === targetNode.id
                );
                if (!edgeExists) {
                    const edgeData = { source: sourceNode.id, target: targetNode.id };
                    graphState.edges.push(edgeData);
                    io.emit('edge_added', edgeData);
                }
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