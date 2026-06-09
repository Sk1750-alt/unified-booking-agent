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
    
    if (type === 'user') {
        messageDiv.className = "max-w-md self-end w-full flex justify-end animate-fade-in";
        messageDiv.innerHTML = `
            <div class="flex items-start gap-4 flex-row-reverse">
                <div class="w-10 h-10 rounded-xl glass-panel border-white/20 flex-shrink-0 flex items-center justify-center bg-white/5">
                    <i class="fas fa-user text-neon-cyan"></i>
                </div>
                <div class="glass-panel p-4 px-6 rounded-3xl rounded-tr-none neon-border-cyan">
                    <p class="text-sm text-white/95">${text}</p>
                </div>
            </div>
        `;
    } else {
        messageDiv.className = "max-w-2xl self-start w-full animate-fade-in";
        messageDiv.innerHTML = `
            <div class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-xl glass-panel neon-border-purple flex-shrink-0 flex items-center justify-center bg-white/5">
                    <i class="fas fa-robot text-neon-purple"></i>
                </div>
                <div class="glass-panel p-5 rounded-3xl rounded-tl-none ${isError ? 'border-red-500/50 shadow-[0_0_10px_rgba(239,68,68,0.2)]' : 'neon-border-purple'} relative">
                    <p class="text-sm ${isError ? 'text-red-400' : 'text-white/95'} leading-relaxed">${text}</p>
                </div>
            </div>
        `;
    }

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add bot response with recommendation card
 */
function addBotResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'max-w-2xl self-start w-full animate-fade-in';

    let content = `
        <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl glass-panel neon-border-purple flex-shrink-0 flex items-center justify-center bg-white/5">
                <i class="fas fa-robot text-neon-purple"></i>
            </div>
            <div class="glass-panel p-5 rounded-3xl rounded-tl-none neon-border-purple relative w-full bg-deep-space/20">
    `;

    if (data.success && data.recommendation) {
        const rec = data.recommendation;
        const exp = data.explanation || {};

        // Conversational message
        if (data.message) {
            content += `
                <div class="conversational-response text-sm text-white/90 leading-relaxed mb-5">
                    ${formatMarkdown(data.message)}
                </div>
            `;
        }

        // OUTPUT 1: Selected "Best" Option
        content += `
            <p class="text-xs font-bold text-neon-purple uppercase tracking-tighter mb-4 flex items-center gap-1.5">
                <i class="fas fa-star text-neon-purple"></i> Selected Best Option
            </p>
            
            <div class="relative w-full max-w-[480px] mb-5">
                <div class="absolute inset-0 bg-neon-purple/10 blur-3xl -z-10"></div>
                <div class="glass-panel rounded-[24px] overflow-hidden border-white/10 w-full bg-white/5">
                    <div class="p-5 relative">
                        <!-- Motel visual background -->
                        <div class="w-full h-40 rounded-xl bg-gradient-to-b from-white/5 to-transparent flex items-center justify-center relative overflow-hidden mb-4">
                            <img alt="Hotel Visual" class="w-full h-full object-cover opacity-80" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB9CqssFOwEd6XO7q9ShlIEMKcdqA4V9I87c5krfwVlT2kuMZe_HdtkcCvbZ77GTzrAL7ZZyfQrREALib_Yx73C1NB4rqi687TwHLIGOPxQnlE4xMgGlhiTnLbhDLW2Ovmxt6Vxzv9MYTZnA35OQvpZFdCAJURl6-aItHe66O3PEgg_26D_feT89g8G_NUAgBaU-5oDWJqdcaSevD6oV0yhnuTODT6ef6lr-ranjJu3yLRjSsyPlF15CfKXiINjuVZXrh7jQAkyqPOg"/>
                            
                            <!-- Platform badge -->
                            <div class="absolute top-3 left-3 bg-neon-purple/80 backdrop-blur-md px-3 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest text-white">
                                ${rec.platform}
                            </div>
                        </div>
                        
                        <div class="flex justify-between items-start gap-4">
                            <div class="flex-1">
                                <h3 class="text-base font-bold text-white mb-1">${rec.property_name}</h3>
                                <p class="text-[11px] text-white/50 mb-3 flex items-center gap-1">
                                    <i class="fas fa-map-marker-alt text-neon-cyan"></i> ${rec.location}
                                </p>
                                <div class="flex gap-4 items-center">
                                    <div>
                                        <div class="text-[9px] text-white/40 uppercase tracking-wider">Price</div>
                                        <div class="text-sm font-bold text-neon-cyan">Rs. ${rec.price_per_night} <span class="text-[9px] font-normal text-white/60">/ night</span></div>
                                    </div>
                                    <div>
                                        <div class="text-[9px] text-white/40 uppercase tracking-wider">Rating</div>
                                        <div class="text-sm font-bold text-neon-purple">${rec.rating} ★ <span class="text-[9px] font-normal text-white/60">(${rec.reviews_count})</span></div>
                                    </div>
                                    <div>
                                        <div class="text-[9px] text-white/40 uppercase tracking-wider">Cancellation</div>
                                        <div class="text-xs font-semibold text-white/80">${formatCancellation(rec.cancellation_policy)}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Small Map Snippet -->
                            <div class="w-14 h-14 rounded-lg overflow-hidden border border-white/10 flex-shrink-0">
                                <img alt="Map" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD1mayDwFP7G4DzNCY4oyLG7TrbCJm7mXNhpbubHVCZWzZcb25PnES6Vunt-yj8zdwzhkUcLIWms2Ru6XEOfBdvDlIjgkX7Vu3YSd0f7f2v5w2mUATHxE6cMRsi7kDgp_R3rqTs1m-BWCxdLP_AlQZt0FflW1w1j-Dad98305p6zCAI4DhhxSFfdssw-poC9jhz5Es6QNtWKt4EikDgTXDuJkYtU6Dy6sL58NyiqnEGVwmp2fqBg28aH6SvLUhKg-_JI7oc9mYfvuXy"/>
                            </div>
                        </div>
                        
                        <!-- Action button -->
                        <button class="w-full mt-4 py-2.5 bg-gradient-to-r from-neon-purple to-neon-cyan rounded-xl font-bold text-[10px] uppercase tracking-widest text-white hover:opacity-90 active:scale-[0.98] transition-all">
                            Book on ${rec.platform}
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- OUTPUT 2: Explanation of Selection Logic -->
            <div class="glass-panel p-4 rounded-xl border-white/10 w-full max-w-[480px] bg-white/5 mb-5">
                <div class="text-[10px] font-bold text-neon-purple uppercase tracking-wider mb-2">EXPLANATION OF SELECTION LOGIC</div>
                <ul class="space-y-1 text-xs text-white/80 list-disc list-inside">
                    ${(exp.why_selected || ['Best match for your criteria']).map(reason =>
                        `<li>${reason}</li>`
                    ).join('')}
                    <li>Compared ${exp.total_options_evaluated || 0} options across ${(exp.platforms_compared || []).join(', ')}</li>
                    <li>Strategy: ${formatStrategy(exp.strategy_used)}</li>
                </ul>
            </div>
        `;

        // OUTPUT 3: Ranked List of Accommodation Options
        if (data.all_options && data.all_options.length > 0) {
            content += `
                <div class="mt-4 w-full max-w-[480px] mb-5">
                    <div class="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2">Ranked Options (${data.all_options.length} found)</div>
                    <div class="grid grid-cols-2 gap-2">
                        ${data.all_options.slice(0, 6).map((opt, index) => `
                            <div class="glass-panel p-2.5 rounded-xl border-white/5 relative hover:border-white/10 transition-all bg-white/5 ${opt.id === rec.id ? 'border-neon-cyan/50 bg-neon-cyan/5 shadow-[0_0_8px_rgba(0,210,255,0.2)]' : ''}">
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-[10px] font-bold ${index === 0 ? 'text-neon-cyan' : 'text-white/40'}">#${index + 1}</span>
                                    <span class="text-[8px] text-white/30 uppercase tracking-widest">${opt.platform}</span>
                                </div>
                                <div class="text-xs font-semibold text-white/95 truncate">${opt.property_name}</div>
                                <div class="flex justify-between items-center mt-1.5 text-[10px] text-white/60">
                                    <span>Rs.${opt.price_per_night}/n</span>
                                    <span class="text-neon-purple">${opt.rating}★</span>
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
            <div class="mt-4 w-full max-w-[480px]">
                <button onclick="toggleJson('${jsonId}')" class="bg-white/5 border border-white/15 hover:bg-white/10 text-white/60 hover:text-white px-3 py-1.5 rounded-lg cursor-pointer text-[10px] uppercase tracking-wider font-semibold transition-all">
                    View Unified JSON Response
                </button>
                <div id="${jsonId}" style="display: none;" class="mt-2 bg-black/40 border border-white/10 rounded-xl p-3 overflow-x-auto">
                    <pre class="text-[10px] text-green-400 font-mono leading-relaxed whitespace-pre-wrap">${JSON.stringify({
                        selected_best: rec,
                        explanation: exp,
                        all_options_count: data.all_options ? data.all_options.length : 0,
                        platforms_queried: exp.platforms_compared || []
                    }, null, 2)}</pre>
                </div>
            </div>
        `;
    } else {
        content += `<div class="conversational-response text-sm text-white/80 leading-relaxed">${formatMarkdown(data.message)}</div>`;

        if (data.explanation && data.explanation.platforms_compared) {
            content += `
                <div class="glass-panel p-4 rounded-xl border-white/10 mt-3 w-full max-w-[480px] bg-white/5">
                    <div class="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2">Search Info</div>
                    <ul class="space-y-1 text-xs text-white/80 list-disc list-inside">
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
            <div class="border-t border-white/5 mt-4 pt-3 flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-white/30 uppercase tracking-wider">
                <span>Destination: <strong class="text-white/60">${data.parsed_query.destination}</strong></span>
                ${data.parsed_query.guests ? `<span>Guests: <strong class="text-white/60">${data.parsed_query.guests}</strong></span>` : ''}
                ${data.parsed_query.max_price ? `<span>Max Price: <strong class="text-white/60">Rs.${data.parsed_query.max_price}</strong></span>` : ''}
                ${data.parsed_query.selection_strategy ? `<span>Strategy: <strong class="text-white/60">${formatStrategy(data.parsed_query.selection_strategy)}</strong></span>` : ''}
            </div>
        `;
    }

    // Add tools invoked
    if (data.tools_invoked && data.tools_invoked.length > 0) {
        content += `
            <div class="text-[9px] text-white/20 uppercase tracking-widest mt-2">
                MCP Flow: ${data.tools_invoked.join(' → ')}
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

/**
 * Helper to format basic markdown (bold, lists, and linebreaks)
 */
function formatMarkdown(text) {
    if (!text) return '';
    // Escape HTML to prevent injection
    let escaped = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    
    // Replace bold text **word**
    let formatted = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Replace markdown bullet points
    formatted = formatted.replace(/^\s*[-*]\s+(.*?)$/gm, '<li>$1</li>');
    // Group lists into <ul> block
    formatted = formatted.replace(/((?:<li>.*?<\/li>\s*)+)/gs, '<ul>$1</ul>');
    // Replace newlines with <br> (but not right after list tags)
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

