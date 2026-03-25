#!/usr/bin/env python3
"""
Interactive Signal Analyzer Bot - Chat with Magenta in real-time!
Enhanced with ChatGPT-like personality and responsiveness
"""

import google.generativeai as genai
import time
import requests
from datetime import datetime
from collections import deque
import json
import threading
import sys
import os

# Configuration
SERVER_HOST = "http://172.20.10.8:5000"
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")
CHECK_INTERVAL = 5  # seconds

# Configure Gemini
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')  # Correct model for your API

# Store signal history and conversation
signal_history = deque(maxlen=50)
conversation_history = []
chat_session = None
monitoring_active = True

def get_signal_data():
    """Fetch latest signal data from server"""
    try:
        response = requests.get(f"{SERVER_HOST}/api/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('latest_signal')
    except:
        pass
    return None

def analyze_signal_trend():
    """Analyze signal strength trend"""
    if len(signal_history) < 2:
        return "insufficient_data", 0
    
    recent = list(signal_history)[-5:]
    older = list(signal_history)[-10:-5] if len(signal_history) >= 10 else recent
    
    recent_avg = sum([s['signal'] for s in recent]) / len(recent)
    older_avg = sum([s['signal'] for s in older]) / len(older)
    
    change = recent_avg - older_avg
    
    if change > 5:
        return "improving", change
    elif change < -5:
        return "degrading", change
    else:
        return "stable", change

def get_signal_quality(signal_dbm):
    """Classify signal quality"""
    if signal_dbm >= -50:
        return "Excellent", "🟢"
    elif signal_dbm >= -60:
        return "Very Good", "🟢"
    elif signal_dbm >= -70:
        return "Good", "🟡"
    elif signal_dbm >= -80:
        return "Fair", "🟠"
    else:
        return "Poor", "🔴"

def build_context():
    """Build context for AI from signal history"""
    if not signal_history:
        return "No signal data collected yet."
    
    recent_signals = list(signal_history)[-10:]
    signals_list = [s['signal'] for s in recent_signals]
    current_signal = signals_list[-1]
    avg_signal = sum(signals_list) / len(signals_list)
    min_signal = min(signals_list)
    max_signal = max(signals_list)
    
    trend, change = analyze_signal_trend()
    quality, emoji = get_signal_quality(current_signal)
    
    context = f"""Current Signal: {current_signal} dBm {emoji} ({quality})
Average (last {len(recent_signals)}): {avg_signal:.1f} dBm
Range: {min_signal} to {max_signal} dBm
Trend: {trend} ({change:+.1f} dBm)"""
    
    return context

def chat_with_magenta(user_message, auto_mode=False):
    """Chat with Magenta - enhanced personality and responsiveness"""
    global chat_session
    
    if chat_session is None:
        chat_session = model.start_chat(history=[])
    
    context = build_context()
    
    # Build personality-rich prompt
    if auto_mode:
        # Automatic monitoring mode
        prompt = f"""You are Magenta 🤖, a super friendly WiFi expert with ChatGPT's conversational charm!

Personality: Warm, encouraging, knowledgeable, playful, and genuinely helpful

CURRENT WIFI STATUS:
{context}

Provide a quick, engaging update:
- Comment on the current signal quality
- Mention any trends you notice
- Give a helpful tip or observation

Style: Conversational and upbeat (2-3 sentences). Vary your openings! Use phrases like:
"Hey!", "Looking good!", "Quick update:", "Here's what I'm seeing:", "Heads up!", etc.

Be like a helpful friend checking in, not a robot reporting data!"""
    else:
        # Interactive chat mode
        prompt = f"""You are Magenta 🤖, a friendly WiFi expert with ChatGPT's personality!

Traits: Warm, knowledgeable, conversational, helpful, and engaging

CURRENT WIFI STATUS:
{context}

USER: "{user_message}"

Respond naturally:
- Answer their question directly and clearly
- Reference signal data when relevant
- Be friendly and conversational
- Explain technical terms simply
- Show personality and empathy
- Keep responses concise but complete

Talk like a knowledgeable friend, not a formal assistant!"""
    
    try:
        response = chat_session.send_message(prompt)
        analysis = response.text.strip()
        
        # Store conversation
        conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message if not auto_mode else "[auto]",
            'magenta_response': analysis,
            'context': context
        })
        
        if len(conversation_history) > 30:
            conversation_history.pop(0)
        
        return analysis
    
    except Exception as e:
        return f"😅 Oops! Hit a little snag: {e}\nBut I'm still here for you!"

def background_monitor():
    """Background thread for monitoring signals"""
    global monitoring_active
    
    while monitoring_active:
        signal_data = get_signal_data()
        if signal_data:
            signal_history.append(signal_data)
        time.sleep(CHECK_INTERVAL)

def print_status():
    """Print current status"""
    if not signal_history:
        print("\n📡 No signal data yet... waiting for readings...")
        return
    
    latest = signal_history[-1]
    quality, emoji = get_signal_quality(latest['signal'])
    
    print(f"\n{'='*70}")
    print(f"📡 CURRENT STATUS - {datetime.now().strftime('%I:%M:%S %p')}")
    print(f"{'='*70}")
    print(f"Signal: {latest['signal']} dBm {emoji} ({quality})")
    print(f"Network: {latest.get('ssid', 'Unknown')}")
    print(f"Readings: {len(signal_history)}")
    
    trend, change = analyze_signal_trend()
    if trend != "insufficient_data":
        trend_icon = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"Trend: {trend_icon} {trend} ({change:+.1f} dBm)")
    print("="*70)

def interactive_mode():
    """Interactive chat mode"""
    global monitoring_active
    
    print("\n" + "="*70)
    print("🤖 MAGENTA - Interactive WiFi Assistant")
    print("   Your friendly AI companion for WiFi monitoring!")
    print("="*70)
    print(f"\n📡 Monitoring: {SERVER_HOST}")
    print(f"⏱️  Update Interval: {CHECK_INTERVAL} seconds")
    print("\n💬 COMMANDS:")
    print("   - Just type naturally to chat with Magenta")
    print("   - Type 'status' for current signal info")
    print("   - Type 'auto' for automatic updates")
    print("   - Type 'quit' or 'exit' to leave")
    print("="*70)
    
    # Start background monitoring
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()
    
    print("\n👋 Hi! I'm Magenta! Ask me anything about your WiFi signal!")
    print("   (Background monitoring started...)\n")
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            # Check commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Magenta: Thanks for chatting! Stay connected! 📡✨")
                monitoring_active = False
                break
            
            elif user_input.lower() == 'status':
                print_status()
                continue
            
            elif user_input.lower() == 'auto':
                print("\n🤖 Switching to auto-update mode...")
                print("   (Press Ctrl+C to stop)\n")
                try:
                    while True:
                        if signal_history:
                            print_status()
                            response = chat_with_magenta("", auto_mode=True)
                            print(f"\n💬 Magenta: {response}\n")
                        time.sleep(CHECK_INTERVAL)
                except KeyboardInterrupt:
                    print("\n\n🤖 Back to chat mode! What would you like to know?")
                    continue
            
            # Regular chat
            print("\n🤖 Magenta: ", end="", flush=True)
            response = chat_with_magenta(user_input)
            
            # Simulate typing effect for personality
            for char in response:
                print(char, end="", flush=True)
                time.sleep(0.01)  # Small delay for typing effect
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Magenta: Caught that interrupt! Type 'quit' to exit properly.")
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue
    
    # Save session on exit
    try:
        with open('magenta_chat_session.json', 'w') as f:
            json.dump({
                'signal_history': list(signal_history),
                'conversation_history': conversation_history,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        print("\n💾 Chat session saved to: magenta_chat_session.json")
    except:
        pass
    
    print("\n🌟 See you next time!")

if __name__ == "__main__":
    try:
        interactive_mode()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
