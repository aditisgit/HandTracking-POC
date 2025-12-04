const videoInput = document.getElementById('videoInput');
const videoOutput = document.getElementById('videoOutput');
const ctx = videoOutput.getContext('2d');
const statusBadge = document.getElementById('statusBadge');
const dangerOverlay = document.getElementById('dangerOverlay');
const fpsValue = document.getElementById('fpsValue');

// Navigation elements
const landingSection = document.getElementById('landing-section');
const trackingSection = document.getElementById('tracking-section');
const enterBtn = document.getElementById('enterBtn');
const backBtn = document.getElementById('backBtn');
const errorMessage = document.getElementById('error-message');

let stream = null;
let ws = null;
let isRunning = false;
let lastFrameTime = 0;
let frameCount = 0;
let lastFpsUpdate = 0;

// Configuration
const WS_URL = 'ws://localhost:8000/ws';
const FRAME_WIDTH = 640;
const FRAME_HEIGHT = 480;

// Set canvas size
videoOutput.width = FRAME_WIDTH;
videoOutput.height = FRAME_HEIGHT;

// Event Listeners
enterBtn.addEventListener('click', async () => {
    errorMessage.classList.add('hidden');
    enterBtn.disabled = true;
    enterBtn.textContent = 'Starting...';
    
    const success = await startCamera();
    
    if (success) {
        landingSection.classList.add('hidden');
        trackingSection.classList.remove('hidden');
    } else {
        enterBtn.disabled = false;
        enterBtn.textContent = 'Start Hand Tracking';
    }
});

backBtn.addEventListener('click', () => {
    stopCamera();
    trackingSection.classList.add('hidden');
    landingSection.classList.remove('hidden');
    enterBtn.disabled = false;
    enterBtn.textContent = 'Start Hand Tracking';
});

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: FRAME_WIDTH }, 
                height: { ideal: FRAME_HEIGHT } 
            } 
        });
        videoInput.srcObject = stream;
        await videoInput.play();

        connectWebSocket();
        
        isRunning = true;
        processFrame();
        return true;
    } catch (err) {
        console.error('Error accessing camera:', err);
        errorMessage.textContent = 'Could not access camera. Please ensure you have granted permission.';
        errorMessage.classList.remove('hidden');
        return false;
    }
}

function stopCamera() {
    isRunning = false;
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    if (ws) {
        ws.close();
        ws = null;
    }
    
    ctx.clearRect(0, 0, FRAME_WIDTH, FRAME_HEIGHT);
    statusBadge.textContent = 'SAFE';
    statusBadge.style.backgroundColor = 'var(--safe-color)';
    dangerOverlay.classList.add('hidden');
}

let lastFrameSentTime = 0;
const FRAME_INTERVAL = 1000 / 15; // Cap at 15 FPS to reduce load
let watchdogTimer = null;

function connectWebSocket() {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket');
        resetWatchdog();
    };
    
    ws.onmessage = (event) => {
        resetWatchdog();
        const data = JSON.parse(event.data);
        
        // Draw processed image
        const img = new Image();
        img.onload = () => {
            ctx.drawImage(img, 0, 0, FRAME_WIDTH, FRAME_HEIGHT);
            
            // Draw state overlay on top of the image
            drawStateOverlay(data.state);
        };
        img.src = 'data:image/jpeg;base64,' + data.image;
        
        // Update state
        updateState(data.state);
        
        // Calculate FPS
        updateFPS();
        
        // Request next frame processing
        if (isRunning) {
            requestAnimationFrame(processFrame);
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        if (isRunning) {
            // Auto-reconnect after 1 second
            setTimeout(connectWebSocket, 1000);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function drawStateOverlay(state) {
    ctx.save();
    ctx.font = 'bold 24px Arial';
    
    let color = '#00FF00'; // SAFE
    let text = state;

    if (state === 'WARNING') color = '#FFFF00';
    if (state === 'DANGER') {
        color = '#FF0000';
        text = 'DANGER DANGER'; // Update text for DANGER state
    }
    
    ctx.fillStyle = color;
    ctx.fillText(text, 20, 40);
    
    // Flash effect for DANGER
    if (state === 'DANGER') {
        const now = Date.now();
        if (Math.floor(now / 200) % 2 === 0) { // Flash every 200ms
            ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
            ctx.fillRect(0, 0, FRAME_WIDTH, FRAME_HEIGHT);
        }
    }
    ctx.restore();
}

function resetWatchdog() {
    if (watchdogTimer) clearTimeout(watchdogTimer);
    if (isRunning) {
        watchdogTimer = setTimeout(() => {
            console.warn('Watchdog triggered - restarting frame loop');
            if (ws && ws.readyState === WebSocket.OPEN) {
                processFrame();
            }
        }, 2000); // Restart if no response for 2 seconds
    }
}

function processFrame() {
    if (!isRunning || !ws || ws.readyState !== WebSocket.OPEN) {
        if (isRunning && ws && ws.readyState === WebSocket.CONNECTING) {
             // Wait for connection
             return;
        }
        return;
    }

    // Rate limiting
    const now = performance.now();
    if (now - lastFrameSentTime < FRAME_INTERVAL) {
        requestAnimationFrame(processFrame);
        return;
    }
    lastFrameSentTime = now;

    // Draw current video frame to a temporary canvas to get bytes
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = FRAME_WIDTH; // Full resolution
    tempCanvas.height = FRAME_HEIGHT;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(videoInput, 0, 0, tempCanvas.width, tempCanvas.height);
    
    // Convert to blob/bytes
    tempCanvas.toBlob((blob) => {
        if (blob) {
            blob.arrayBuffer().then(buffer => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(buffer);
                }
            });
        }
    }, 'image/jpeg', 0.9); // High quality
}

function updateState(state) {
    statusBadge.textContent = state;
    
    if (state === 'SAFE') {
        statusBadge.style.backgroundColor = 'var(--safe-color)';
        dangerOverlay.classList.add('hidden');
    } else if (state === 'WARNING') {
        statusBadge.style.backgroundColor = 'var(--warning-color)';
        dangerOverlay.classList.add('hidden');
    } else if (state === 'DANGER') {
        statusBadge.style.backgroundColor = 'var(--danger-color)';
        dangerOverlay.classList.remove('hidden');
    }
}

function updateFPS() {
    frameCount++;
    const now = performance.now();
    if (now - lastFpsUpdate >= 1000) {
        fpsValue.textContent = frameCount;
        frameCount = 0;
        lastFpsUpdate = now;
    }
}
