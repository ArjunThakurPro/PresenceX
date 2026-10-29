from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


import io
import numpy as np
import librosa
import streamlit as st


def voice_embedding(audio_bytes):
    try:
        # 1. Check whether audio data exists
        if not audio_bytes:
            st.error("No audio data received.")
            return None

        if hasattr(audio_bytes, "getvalue"):
            audio_bytes = audio_bytes.getvalue()
        elif hasattr(audio_bytes, "read"):
            audio_bytes = audio_bytes.read()

        if not isinstance(audio_bytes, (bytes, bytearray, memoryview)):
            st.error("The voice recording could not be read.")
            return None

        # 2. Load the voice encoder
        encoder = load_voice_encoder()

        # 3. Decode audio and convert it to 16 kHz mono
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)

        # 4. Check if audio was successfully loaded
        if audio is None or len(audio) == 0:
            st.error("Could not decode the audio.")
            return None

        # 5. Convert to float32
        audio = audio.astype(np.float32)

        # 6. Remove DC offset
        audio = audio - np.mean(audio)

        # 7. Normalize volume
        max_val = np.max(np.abs(audio))

        if max_val > 0:
            audio = audio / max_val

        # 8. Remove silence from beginning/end
        audio, _ = librosa.effects.trim(audio, top_db=30)

        # 9. Check minimum audio duration
        duration = len(audio) / sr

        if duration < 1.0:
            st.error(
                f"Voice recording is too short ({duration:.2f}s). "
                "Please record at least 2–3 seconds."
            )
            return None

        # 10. Limit extremely long recordings
        if duration > 15:
            audio = audio[: 15 * sr]

        # 11. Preprocess audio for the encoder
        wav = preprocess_wav(audio)

        # 12. Generate voice embedding
        embedding = encoder.embed_utterance(wav)

        # 13. Validate embedding
        if embedding is None:
            st.error("Voice embedding generation failed.")
            return None

        embedding = np.asarray(embedding, dtype=np.float32)

        if embedding.size == 0:
            st.error("Generated embedding is empty.")
            return None

        # 14. Convert NumPy array to list for database storage
        return embedding.tolist()

    except Exception as e:
        st.error(f"Voice Recognition Error: {str(e)}")
        return None


def identify_voice(new_embedding, stored_disc, threshold=0.65):
    if new_embedding is None or not stored_disc:
        return None, 0.0

    try:
        if isinstance(stored_disc, dict):
            candidates = stored_disc.items()
        else:
            candidates = stored_disc
    except Exception:
        candidates = []

    best_score = -1.0
    best_sid = None
    for sid, embedding in candidates:
        if embedding is None:
            continue
        try:
            embedding_array = np.asarray(embedding, dtype=float)
            norm_a = np.linalg.norm(new_embedding)
            norm_b = np.linalg.norm(embedding_array)
            if norm_a == 0 or norm_b == 0:
                similarity = 0.0
            else:
                similarity = float(
                    np.dot(new_embedding, embedding_array) / (norm_a * norm_b)
                )
        except (TypeError, ValueError):
            continue

        if similarity > best_score:
            best_score = similarity
            best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score


def process_bulk_audio(audio, candidates_disc, threshold_value=0.65):
    try:
        encoder = load_voice_encoder()
        audio_bytes, sr = librosa.load(
            io.BytesIO(audio), sr=16000
        )  # converts it into a numerical representation called an audio waveform.
        segments = librosa.effect.split(
            audio_bytes, top_db=30
        )  # segments contains the start and end sample positions of each detected non-silent section.
        identified_results = {}
        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            segment_audio = audio_bytes[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)
            sid, score = identify_voice(embedding, candidates_disc, threshold_value)
            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score
        return identified_results
    except Exception:
        st.error("Bulk Process Error")
        return {}
