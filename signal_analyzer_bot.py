#!/usr/bin/env python3
"""
Signal Analyzer Bot with Google Generative AI
Monitors WiFi signal strength in real-time and provides AI-powered analysis
"""

import google.generativeai as genai
import time
import requests
from datetime import datetime
from collections import deque
import json
import os

# Configuration
SERVER_HOST = "http://172.20.10.8:5000"
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")
CHECK_INTERVAL = 5  # seconds
USE_SIMPLE_PROMPTS = False  # Set to True if getting API errors

# Configure Gemini
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')  # Correct model for your API

# Store signal history (last 50 readings)
signal_history = deque(maxlen=50)
conversation_history = []
chat_session = None  # Store chat session for context continuity

def get_signal_data():
    """Fetch latest signal data from server"""
    try:
        response = requests.get(f"{SERVER_HOST}/api/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get('latest_signal')
    except Exception as e:
        print(f"⚠️  Could not fetch signal data: {e}")
    return None

def analyze_signal_trend():
    """Analyze signal strength trend"""
    if len(signal_history) < 2:
        return "insufficient_data", 0
    
    recent = list(signal_history)[-5:]  # Last 5 readings
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
        return "No signal data available yet."
    
    recent_signals = list(signal_history)[-10:]  # Last 10 readings
    
    signals_list = [s['signal'] for s in recent_signals]
    current_signal = signals_list[-1]
    avg_signal = sum(signals_list) / len(signals_list)
    min_signal = min(signals_list)
    max_signal = max(signals_list)
    
    trend, change = analyze_signal_trend()
    quality, emoji = get_signal_quality(current_signal)
    
    context = f"""📊 CURRENT WIFI SIGNAL STATUS:

Current Signal: {current_signal} dBm {emoji}
Quality: {quality}

Recent Statistics (last {len(recent_signals)} readings):
- Average: {avg_signal:.1f} dBm
- Strongest: {max_signal} dBm
- Weakest: {min_signal} dBm
- Variation: {max_signal - min_signal} dBm

Trend: {trend.upper()}
Change: {change:+.1f} dBm over last 5 readings

Signal History (last 10):
"""
    
    for i, s in enumerate(recent_signals[-10:], 1):
        quality_text, emoji_icon = get_signal_quality(s['signal'])
        context += f"{i}. {s['signal']} dBm {emoji_icon} @ {s.get('timestamp', 'N/A')}\n"
    
    return context

def get_ai_analysis():
    """Get AI analysis of current signal status with ChatGPT-like personality"""
    global chat_session
    
    context = build_context()
    trend, change = analyze_signal_trend()
    
    if len(signal_history) < 2:
        friendly_msgs = [
            "🤖 Hey there! Just getting warmed up... collecting some initial data to give you the best insights!",
            "🤖 Hold tight! I'm gathering signal data to provide you with meaningful analysis.",
            "🤖 Starting up! Give me a moment to collect enough data points, and I'll have some great insights for you!"
        ]
        import random
        return random.choice(friendly_msgs)
    
    # Initialize chat session if not exists for continuous conversation
    if chat_session is None:
        chat_session = model.start_chat(history=[])
    
    # Build engaging, personality-rich prompt
    if USE_SIMPLE_PROMPTS:
        # Simpler prompt to avoid API issues
        prompt = f"""You are Magenta, a friendly WiFi assistant.

Current signal: {list(signal_history)[-1]['signal']} dBm
Trend: {trend} (Change: {change:+.1f} dBm)

Give a brief, friendly 2-sentence analysis with one helpful tip."""
    else:
        # Full personality prompt
        prompt = f"""You are Magenta 🤖, a super friendly and knowledgeable WiFi expert assistant with a ChatGPT-like personality!

Your personality traits:
- Enthusiastic and encouraging
- Conversational and warm (use phrases like "Hey!", "Great news!", "Uh oh", "Here's the thing")
- Explain technical concepts in simple, relatable terms
- Show genuine care about the user's WiFi experience
- Use analogies and comparisons when helpful
- Celebrate good signals and provide reassurance during bad ones
- Vary your response style (sometimes brief, sometimes detailed, always engaging)

CURRENT SITUATION:
{context}

Based on this WiFi data:
- Current signal: {list(signal_history)[-1]['signal']} dBm
- Trend: {trend} (Change: {change:+.1f} dBm)

Provide a natural, conversational analysis:
1. Give an upbeat assessment of the current signal quality
2. Explain what the trend means in everyday language
3. Offer ONE practical tip or insight

Response style guidelines:
- Be warm and personable (like chatting with a tech-savvy friend)
- Keep it brief (2-4 sentences max) but punchy
- Use emojis sparingly for emphasis
- Vary your opening (don't always start the same way)
- If signal is improving, celebrate it! If declining, be reassuring and helpful

Remember: You're building a relationship with the user over time. Be consistently friendly and helpful!"""
    
    try:
        # Generate analysis with chat context
        response = chat_session.send_message(prompt)
        
        # Check if response was blocked
        if not response.text:
            # Try again with simpler prompt
            simple_prompt = f"""You are a friendly WiFi assistant. Current signal: {list(signal_history)[-1]['signal']} dBm, trend: {trend}. Give a brief, friendly analysis in 2 sentences."""
            response = chat_session.send_message(simple_prompt)
        
        analysis = response.text.strip() if response.text else "Signal data received! I'm analyzing... 📡"
        
        # Store in conversation history with richer context
        conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'analysis': analysis,
            'signal': list(signal_history)[-1]['signal'],
            'trend': trend
        })
        
        # Keep last 30 analyses for better context
        if len(conversation_history) > 30:
            conversation_history.pop(0)
        
        return analysis
    
    except Exception as e:
        # Detailed error logging
        error_msg = str(e)
        print(f"\n⚠️  AI Error Details: {error_msg}")
        
        # Provide friendly fallback with manual analysis
        quality, emoji = get_signal_quality(list(signal_history)[-1]['signal'])
        fallback = f"📡 Current signal: {list(signal_history)[-1]['signal']} dBm {emoji} ({quality})\n"
        
        if trend == "improving":
            fallback += "� Great news! Your signal is improving! Keep doing what you're doing! ✨"
        elif trend == "degrading":
            fallback += "📉 Signal is declining a bit. Try moving closer to your router or reducing interference. 💪"
        else:
            fallback += "➡️ Signal is nice and stable! Everything looks good! 😊"
        
        return fallback

def send_analysis_to_server(analysis):
    """Send AI analysis to server (optional - for web display)"""
    try:
        requests.post(
            f"{SERVER_HOST}/api/ai_analysis",
            json={'analysis': analysis, 'timestamp': datetime.now().isoformat()},
            timeout=2
        )
    except:
        pass  # Server endpoint may not exist yet

def chat_with_magenta(user_message):
    """Interactive chat with Magenta - ask questions about your WiFi!"""
    global chat_session
    
    if chat_session is None:
        chat_session = model.start_chat(history=[])
    
    context = build_context()
    
    # Enhanced prompt for user questions
    enhanced_prompt = f"""You are Magenta 🤖, a friendly WiFi expert assistant with ChatGPT's conversational style!

CURRENT WIFI STATUS:
{context}

USER QUESTION/MESSAGE: "{user_message}"

Respond naturally and helpfully:
- Answer their question directly and clearly
- Reference the current signal data when relevant
- Be warm, encouraging, and conversational
- Use simple language, avoid jargon unless necessary
- Keep it concise but complete
- Show personality and empathy

Remember: You're a helpful friend who happens to know a lot about WiFi!"""
    
    try:
        response = chat_session.send_message(enhanced_prompt)
        return response.text.strip()
    except Exception as e:
        return f"😅 Oops! Something went wrong: {e}\nBut I'm still here to help - try asking again!"

def main():
    """Main monitoring loop with enhanced personality and responsiveness"""
    print("=" * 70)
    print("🤖 MAGENTA - Your Friendly WiFi Signal Analyzer")
    print("   Powered by Google Gemini AI 🧠")
    print("=" * 70)
    print(f"📡 Server: {SERVER_HOST}")
    print(f"⏱️  Check Interval: {CHECK_INTERVAL} seconds")
    print(f"🤖 AI Model: Google Gemini Pro")
    print("=" * 70)
    print()
    print("� Hey there! I'm Magenta, your WiFi buddy!")
    print("   I'll monitor your signal and give you friendly, real-time insights.")
    print()
    print("💡 TIP: While I'm running, you can ask me questions!")
    print("   (Feature coming in interactive mode)")
    print()
    print("�🔍 Starting signal monitoring...")
    print("Press Ctrl+C to stop")
    print()
    
    cycle_count = 0
    last_quality = None
    
    try:
        while True:
            cycle_count += 1
            
            # Fetch signal data
            signal_data = get_signal_data()
            
            if signal_data:
                signal_history.append(signal_data)
                
                current_signal = signal_data.get('signal')
                quality, emoji = get_signal_quality(current_signal)
                
                # Detect quality changes for extra commentary
                quality_changed = (last_quality and quality != last_quality)
                last_quality = quality
                
                print(f"\n{'='*70}")
                print(f"📡 CYCLE #{cycle_count} - {datetime.now().strftime('%I:%M:%S %p')}")
                print(f"{'='*70}")
                print(f"Signal Strength: {current_signal} dBm {emoji} ({quality})")
                print(f"Network: {signal_data.get('ssid', 'Unknown')}")
                print(f"Data Points Collected: {len(signal_history)}")
                
                if quality_changed:
                    print(f"⚡ Quality changed from {last_quality} to {quality}!")
                
                # Get AI analysis with personality
                print(f"\n💬 MAGENTA'S TAKE:")
                print(f"{'-'*70}")
                analysis = get_ai_analysis()
                print(analysis)
                print(f"{'-'*70}")
                
                # Send to server for web display
                send_analysis_to_server(analysis)
                
                # Show trend with engaging visualization
                trend, change = analyze_signal_trend()
                if trend != "insufficient_data":
                    if trend == "improving":
                        trend_emoji = "📈 ✨"
                        trend_msg = "Getting better!"
                    elif trend == "degrading":
                        trend_emoji = "📉 ⚠️"
                        trend_msg = "Declining"
                    else:
                        trend_emoji = "➡️ 😌"
                        trend_msg = "Holding steady"
                    
                    print(f"\n{trend_emoji} Trend: {trend_msg} ({change:+.1f} dBm)")
                
                # Fun milestone celebrations
                if cycle_count % 10 == 0:
                    print(f"\n🎉 Milestone: {cycle_count} cycles completed!")
                
            else:
                print(f"\n⚠️  Hmm, can't reach the server right now...")
                print(f"   Make sure {SERVER_HOST} is up and running!")
                print(f"   Don't worry, I'll keep trying! 💪")
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("� MAGENTA SIGNING OFF!")
        print("="*70)
        print(f"🎯 Total cycles completed: {cycle_count}")
        print(f"📊 Signal readings analyzed: {len(signal_history)}")
        print(f"💬 AI insights generated: {len(conversation_history)}")
        print()
        
        # Enhanced summary with personality
        if signal_history:
            all_signals = [s['signal'] for s in signal_history]
            avg_signal = sum(all_signals) / len(all_signals)
            best_signal = max(all_signals)
            worst_signal = min(all_signals)
            
            print("📊 SESSION SUMMARY:")
            print(f"   ├─ Average Signal: {avg_signal:.1f} dBm")
            print(f"   ├─ Best Signal: {best_signal} dBm 🏆")
            print(f"   ├─ Worst Signal: {worst_signal} dBm")
            print(f"   └─ Variation: {best_signal - worst_signal} dBm")
            print()
            
            # AI-powered session summary
            print("💬 FINAL THOUGHTS FROM MAGENTA:")
            print("-" * 70)
            try:
                summary_prompt = f"""You monitored WiFi signals for {cycle_count} cycles.
Average: {avg_signal:.1f} dBm, Best: {best_signal} dBm, Worst: {worst_signal} dBm

Give a brief, friendly 2-sentence farewell summary of the session.
Be warm and encouraging, like saying goodbye to a friend!"""
                
                farewell = model.generate_content(summary_prompt)
                print(farewell.text.strip())
            except:
                print("It was great monitoring your WiFi with you! Stay connected! 📡✨")
            print("-" * 70)
        
        print("\n✅ Session data preserved in memory")
        
        # Save session data
        try:
            with open('signal_analysis_session.json', 'w') as f:
                json.dump({
                    'signal_history': list(signal_history),
                    'conversation_history': conversation_history,
                    'summary': {
                        'cycles': cycle_count,
                        'duration_seconds': cycle_count * CHECK_INTERVAL,
                        'timestamp': datetime.now().isoformat()
                    }
                }, f, indent=2)
            print("💾 Full session saved to: signal_analysis_session.json")
            print("\n🌟 Thanks for using Magenta! See you next time! 👋")
        except Exception as e:
            print(f"⚠️  Couldn't save session file: {e}")
            print("\n👋 But hey, we still had a great session together!")

if __name__ == "__main__":
    main()
