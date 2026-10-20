# Generates the JARVIS voice lines (edge-tts, same voice + helmet FX as the IRONMAN game) into audio/*.mp3.
import asyncio, os, subprocess
import edge_tts

VOICE, RATE, PITCH = "en-GB-RyanNeural", "-4%", "-3Hz"
FX = "highpass=f=120,lowpass=f=9000,aecho=0.8:0.5:14:0.18,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-17:TP=-2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

LINES = {
    "boot_morning": "Good morning, sir. All systems are online.",
    "boot_afternoon": "Good afternoon, sir. All systems are online.",
    "boot_evening": "Good evening, sir. All systems are online.",
    "scan": "Scanning the room, sir.",
    "scan_done": "Scan complete. Every surface has been mapped.",
    "repulsors_on": "Repulsors online.",
    "repulsors_off": "Repulsors disengaged.",
    "rim_on": "Helmet display restored.",
    "rim_off": "Visor cleared, sir.",
    "quip_0": "At your service, sir.",
    "quip_1": "Power is at four hundred percent, sir. Shall I alert the press?",
    "quip_2": "I've taken the liberty of mapping your entire room.",
    "quip_3": "Might I suggest a less destructive hobby, sir?",
    "quip_4": "The house is secure. Mostly.",
    "quip_5": "Sir, you are standing perfectly still. Shall I run a diagnostic?",
    "wreck": "Sir, the wall has done nothing to you.",
    "lowpower": "Arc reactor running low, sir. Recharging.",
    "nohands": "Put your controllers down, sir. The suit reads your hands.",
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
