/**
 * Unified Booking Agent - Frontend JavaScript
 * Handles chat interactions and API calls (no emojis)
 */

const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const loadingOverlay = document.getElementById('loadingOverlay');

/**
 * Use example query
 */
function useExample(btn) {
    userInput.value = btn.textContent;
    userInput.focus();
}

/**
 * Send message to the chatbot
 */
async function sendMessage(event) {
    event.preventDefault();

    const query = userInput.value.trim();
    if (!query) return;

    // Add user message
    addMessage(query, 'user');
    userInput.value = '';

    // Show loading
    showLoading(true);
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        // Add bot response
        addBotResponse(data);

    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, something went wrong. Please try again.', 'bot', true);
    } finally {
        showLoading(false);
        sendBtn.disabled = false;
    }
}

/**
 * Add a simple message to the chat
 */
function addMessage(text, type, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const avatar = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble ${isError ? 'error' : ''}">
                <p>${text}</p>
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add bot response with recommendation card
 */
function addBotResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';

    let content = `
        <div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="message-bubble">
    `;

    if (data.success && data.recommendation) {
        const rec = data.recommendation;
        const exp = data.explanation || {};

        // OUTPUT 1: Selected "Best" Option
        content += `
            <p style="color: #10b981; font-weight: 600; margin-bottom: 12px;">* SELECTED BEST OPTION</p>
            
            <div class="recommendation-card">
                <div class="recommendation-header">
                    <span class="recommendation-title">${rec.property_name}</span>
                    <span class="recommendation-platform">${rec.platform}</span>
                </div>
                
                <div class="recommendation-details">
                    <div class="detail-item">
                        <div class="detail-value">Rs.${rec.price_per_night}</div>
                        <div class="detail-label">Per Night</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-value">${rec.rating} stars</div>
                        <div class="detail-label">${rec.reviews_count} Reviews</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-value">${formatCancellation(rec.cancellation_policy)}</div>
                        <div class="detail-label">Cancellation</div>
                    </div>
                </div>
                
                <div class="recommendation-location">
                    Location: ${rec.location}
                </div>
                </div>
            </div>
            
            <!-- OUTPUT 2: Explanation of Selection Logic -->
            <div class="explanation-panel">
                <div class="explanation-title">EXPLANATION OF SELECTION LOGIC</div>
                <ul class="explanation-list">
                    ${(exp.why_selected || ['Best match for your criteria']).map(reason =>
            `<li>${reason}</li>`
        ).join('')}
                    <li>Compared ${exp.total_options_evaluated || 0} options across ${(exp.platforms_compared || []).join(', ')}</li>
                    <li>Strategy: ${formatStrategy(exp.strategy_used)}</li>
                </ul>

                </ul>
            </div>
        `;

        // OUTPUT 3: Ranked List of Accommodation Options
        if (data.all_options && data.all_options.length > 0) {
            content += `
                <div class="other-options" style="margin-top: 16px;">
                    <div class="other-options-title">RANKED LIST OF ALL OPTIONS (${data.all_options.length} found)</div>
                    <div class="options-grid" style="margin-top: 10px;">
                        ${data.all_options.slice(0, 6).map((opt, index) => `
                            <div class="option-card" style="${opt.id === rec.id ? 'border-color: #10b981; background: rgba(16, 185, 129, 0.1);' : ''}">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: ${index === 0 ? '#10b981' : '#6366f1'}; font-weight: bold;">#${index + 1}</span>
                                    <span style="font-size: 0.7rem; color: rgba(255,255,255,0.5);">${opt.platform}</span>
                                </div>
                                <div class="option-name">${opt.property_name}</div>
                                <div class="option-meta">
                                    <span>Rs.${opt.price_per_night}/night</span>
                                    <span>${opt.rating} stars</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // OUTPUT 4: Unified Normalized JSON Response (collapsible)
        const jsonId = 'json-' + Date.now();
        content += `
            <div style="margin-top: 16px;">
                <button onclick="toggleJson('${jsonId}')" style="background: rgba(99,102,241,0.2); border: 1px solid #6366f1; color: #818cf8; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 0.85rem;">
                    VIEW UNIFIED JSON RESPONSE
                </button>
                <div id="${jsonId}" style="display: none; margin-top: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 12px; overflow-x: auto;">
                    <pre style="color: #10b981; font-size: 0.75rem; margin: 0; white-space: pre-wrap;">${JSON.stringify({
            selected_best: rec,
            explanation: exp,
            all_options_count: data.all_options ? data.all_options.length : 0,
            platforms_queried: exp.platforms_compared || []
        }, null, 2)}</pre>
                </div>
            </div>
        `;
    } else {
        content += `<p>${data.message}</p>`;

        if (data.explanation && data.explanation.platforms_compared) {
            content += `
                <div class="explanation-panel">
                    <div class="explanation-title">Search Info</div>
                    <ul class="explanation-list">
                        <li>Searched: ${data.explanation.platforms_compared.join(', ')}</li>
                        <li>Options found: ${data.explanation.total_options_evaluated || 0}</li>
                    </ul>
                </div>
            `;
        }
    }

    // Add parsed query info
    if (data.parsed_query && data.parsed_query.destination) {
        content += `
            <div class="parsed-info" style="margin-top: 12px; font-size: 0.8rem; color: rgba(255,255,255,0.4);">
                Parsed: ${data.parsed_query.destination}
                ${data.parsed_query.guests ? ` | ${data.parsed_query.guests} guests` : ''}
                ${data.parsed_query.max_price ? ` | Under Rs.${data.parsed_query.max_price}` : ''}
                ${data.parsed_query.selection_strategy ? ` | ${formatStrategy(data.parsed_query.selection_strategy)}` : ''}
            </div>
        `;
    }

    // Add tools invoked
    if (data.tools_invoked && data.tools_invoked.length > 0) {
        content += `
            <div class="tools-info" style="margin-top: 8px; font-size: 0.75rem; color: rgba(255,255,255,0.3);">
                MCP Tools: ${data.tools_invoked.join(' -> ')}
            </div>
        `;
    }

    content += `
            </div>
        </div>
    `;

    messageDiv.innerHTML = content;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Toggle JSON visibility
 */
function toggleJson(id) {
    const el = document.getElementById(id);
    if (el.style.display === 'none') {
        el.style.display = 'block';
    } else {
        el.style.display = 'none';
    }
}

/**
 * Format cancellation policy for display
 */
function formatCancellation(policy) {
    const map = {
        'flexible': 'Flexible',
        'free_cancellation': 'Free',
        'moderate': 'Moderate',
        'strict': 'Strict',
        'non_refundable': 'No Refund'
    };
    return map[policy] || policy;
}

/**
 * Format strategy for display
 */
function formatStrategy(strategy) {
    const map = {
        'cheapest': 'Lowest Price',
        'highest_rating': 'Best Rated',
        'best_value': 'Best Value',
        'flexible_cancellation': 'Flexible Cancellation'
    };
    return map[strategy] || strategy;
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    loadingOverlay.classList.toggle('active', show);
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Focus input on load
userInput.focus();
