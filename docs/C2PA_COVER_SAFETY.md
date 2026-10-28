# MP3 cover art and C2PA: safety gate

C2PA supports MP3 manifests in ID3v2 GEOB frames. Adding an ID3 APIC cover may change bytes covered by the signed manifest. Retaining GEOB is not the same as preserving cryptographic validity.

## Safe policy
1. Keep original officially downloaded MP3 unmodified and calculate SHA-256.
2. Store artwork as a separate PNG/JPEG in Google Drive until verified editing is possible.
3. Do not rewrite ID3/APIC on a real Suno file without C2PA validation both before and after editing.
4. Validate with a real C2PA-aware tool; synthetic unit tests cannot establish signature validity.
5. The authorized_audio_intake.py tool only reads and hashes file bytes; it does not embed artwork.
6. The experimental free_suno_download.py currently writes APIC and must not be used for real Suno audio until the safety gate is implemented.

Primary source: https://spec.c2pa.org/specifications/specifications/2.0/specs/C2PA_Specification.html
