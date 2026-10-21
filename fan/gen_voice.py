# FAN POWERS voice lines (JARVIS voice + helmet FX, same as ../gen_voice.py) -> audio/*.mp3
import asyncio, os, subprocess
import edge_tts

VOICE, RATE, PITCH = "en-GB-RyanNeural", "-4%", "-3Hz"
FX = "highpass=f=120,lowpass=f=9000,aecho=0.8:0.5:14:0.18,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-17:TP=-2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

LINES = {
    "boot": "Wind control online. Point at your fan, sir.",
    "linked": "Fan locked. It's all yours.",
    "on": "Wind's up.",
    "max": "Full power, sir. Hold onto something.",
    "off": "Shutting it down.",
    "swing_on": "Sweep engaged.",
    "swing_off": "Holding steady.",
    "offline": "I can't reach the fan. Start the link on your PC, sir.",
}

async def main():
    os.makedirs(OUT, exist_ok=True)
    for key, text in LINES.items():
        raw = os.path.join(OUT, key + "_raw.mp3")
        await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", FX, "-ac", "1", "-ar", "44100",
                        "-b:a", "128k", os.path.join(OUT, key + ".mp3")], check=True)
        os.remove(raw)
        print("ok", key)

asyncio.run(main())
