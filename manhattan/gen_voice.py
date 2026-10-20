# MANHATTAN voice lines: slow, deep, calm, with a big distant echo. edge-tts -> audio/*.mp3
import asyncio, os, subprocess
import edge_tts

VOICE, RATE, PITCH = "en-US-ChristopherNeural", "-18%", "-9Hz"
FX = ("lowpass=f=7500,highpass=f=70,aecho=0.8:0.6:90|170:0.22|0.12,"
      "acompressor=threshold=-20dB:ratio=3,loudnorm=I=-17:TP=-2")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

LINES = {
    "boot": "I can see every atom in this room.",
    "explode_0": "It was never solid.",
    "explode_1": "Everything comes apart, if you look closely enough.",
    "crush_0": "Matter is only a suggestion.",
    "crush_1": "Smaller.",
    "release": "Gone. As it was always going to be.",
    "idle": "I have already seen what you will break next.",
    "many": "Nothing in this room is permanent.",
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
