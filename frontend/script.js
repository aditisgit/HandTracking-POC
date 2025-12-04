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
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${protocol}//${window.location.host}/ws`;
const FRAME_WIDTH = 640;
const FRAME_HEIGHT = 480;
const SEND_WIDTH = 320; // Downscale for network transmission
const SEND_HEIGHT = 240;

// Offscreen canvas for downscaling
const offscreenCanvas = document.createElement('canvas');
offscreenCanvas.width = SEND_WIDTH;
offscreenCanvas.height = SEND_HEIGHT;
const offscreenCtx = offscreenCanvas.getContext('2d');

// Set canvas size
videoOutput.width = FRAME_WIDTH;
videoOutput.height = FRAME_HEIGHT;

// Virtual Object Config (Must match backend)
const CIRCLE_CENTER = { x: 320, y: 240 };
const CIRCLE_RADIUS = 50;

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
        renderLoop(); // Start the local rendering loop
        processFrame(); // Start the network loop
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

let isProcessing = false; // Flow control flag
let latestState = 'SAFE';
let latestPoint = null;

function connectWebSocket() {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        console.log('Connected to WebSocket');
        isProcessing = false;
        resetWatchdog();
    };
    
    ws.onmessage = (event) => {
        resetWatchdog();
        isProcessing = false; // Server responded, ready for next frame
        
        try {
            const data = JSON.parse(event.data);
            latestState = data.state;
            latestPoint = data.point;
            
            // Update DOM state
            updateState(latestState);
            
            // Calculate FPS (Network FPS)
            updateFPS();
            
            // Trigger next network frame immediately
            if (isRunning) {
                processFrame();
            }
        } catch (e) {
            console.error("Error parsing WS message", e);
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
        isProcessing = false;
    };
}

function renderLoop() {
    if (!isRunning) return;

    // 1. Draw the local video feed directly (Zero latency)
    ctx.drawImage(videoInput, 0, 0, FRAME_WIDTH, FRAME_HEIGHT);
    
    // 2. Draw Virtual Object (Blue Circle)
    ctx.beginPath();
    ctx.arc(CIRCLE_CENTER.x, CIRCLE_CENTER.y, CIRCLE_RADIUS, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(0, 0, 255, 1)'; // Opaque blue
    ctx.fill();
    
    // 3. Draw Boundary Point if detected
    if (latestPoint) {
        const [x, y] = latestPoint;
        // Scale point if backend processed a different resolution
        const scaleX = FRAME_WIDTH / SEND_WIDTH;
        const scaleY = FRAME_HEIGHT / SEND_HEIGHT;
        
        const displayX = x * scaleX;
        const displayY = y * scaleY;

        ctx.beginPath();
        ctx.arc(displayX, displayY, 5, 0, 2 * Math.PI);
        ctx.fillStyle = 'red';
        ctx.fill();
        
        // Draw line to center
        ctx.beginPath();
        ctx.moveTo(displayX, displayY);
        ctx.lineTo(CIRCLE_CENTER.x, CIRCLE_CENTER.y);
        ctx.strokeStyle = 'yellow';
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    // 4. Draw State Overlay
    drawStateOverlay(latestState);
    
    // Loop
    requestAnimationFrame(renderLoop);
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
    if (!isRunning) return;

    if (!ws || ws.readyState !== WebSocket.OPEN) {
        // If connecting, keep trying
        if (ws && ws.readyState === WebSocket.CONNECTING) {
            requestAnimationFrame(processFrame);
        }
        return;
    }

    // Flow control: Don't send if server is still processing
    if (isProcessing) {
        return;
    }

    isProcessing = true;

    // 1. Draw video to offscreen canvas (Downscaled)
    offscreenCtx.drawImage(videoInput, 0, 0, SEND_WIDTH, SEND_HEIGHT);
    
    // 2. Get blob data (Low quality is fine for tracking)
    offscreenCanvas.toBlob((blob) => {
        if (blob && ws.readyState === WebSocket.OPEN) {
             ws.send(blob);
        } else {
             isProcessing = false; // Reset if failed
        }
    }, 'image/jpeg', 0.5);
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
