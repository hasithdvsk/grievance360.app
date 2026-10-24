"""
Grievance360 Multilingual & Voice Router
Endpoints for audio grievance ingestion (Whisper voice-to-text),
regional language translation, and localized status updates.
"""

import os
import shutil
import tempfile
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field

from services.multilingual_service import (
    SUPPORTED_LANGUAGES,
    transcribe_voice_note,
    transcribe_audio_detailed,
    translate_to_english,
    translate_from_english,
    detect_language_script,
)
from services.nlp_engine import (
    classify_bureau_and_priority,
    check_duplicate_complaint,
)
from services.db_service import (
    calculate_dynamic_sla,
    get_all_complaints_for_duplicate_check,
    resolve_institution,
    resolve_bureau,
    save_complaint_and_audit,
)

BUREAU_CODE_MAP: Dict[str, str] = {
    "Anti-Ragging Bureau": "BUR_RAGGING",
    "Approval Bureau": "BUR_APPROVAL",
    "Finance Bureau": "BUR_FINANCE",
    "Legal Bureau": "BUR_LEGAL",
    "Generic Bureau": "BUR_GENERIC",
}

router = APIRouter(prefix="/api/v1/multilingual", tags=["Multilingual & Voice"])


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, example="IN_PROGRESS: Action is being reviewed by Nodal Officer.")
    target_language: str = Field(..., example="hi", description="Language code: te, ta, hi, mr, bn, en")
    source_language: Optional[str] = Field("en", example="en")


class TranslationResponse(BaseModel):
    original_text: str
    source_language: str
    target_language: str
    target_language_name: str
    translated_text: str


@router.get("/languages", summary="Get Supported Regional Indian Languages")
async def get_supported_languages():
    """
    Returns the list of supported regional Indian languages with native scripts.
    """
    return {
        "supported_languages": list(SUPPORTED_LANGUAGES.values()),
        "total_languages": len(SUPPORTED_LANGUAGES),
    }


@router.post(
    "/submit-voice",
    status_code=status.HTTP_201_CREATED,
    summary="Submit Voice Note Grievance",
    description=(
        "Accepts voice note (.mp3, .wav, .m4a), transcribes audio to text via Whisper, "
        "translates regional Indic language (Telugu, Tamil, Hindi, Marathi, Bengali) to English, "
        "and registers the complaint into the central AICTE triage engine."
    ),
)
async def submit_voice_grievance(
    audio_file: UploadFile = File(..., description="Audio file in .mp3, .wav, or .m4a format"),
    title: Optional[str] = Form(None, description="Optional grievance subject"),
    complainant_role: str = Form("STUDENT", description="STUDENT, FACULTY, STAFF, PARENTS, CITIZEN"),
    complainant_email: Optional[str] = Form(None, description="Optional complainant email address"),
    complainant_phone: Optional[str] = Form(None, description="Contact phone number"),
    institution_aicte_id: Optional[str] = Form(None, description="Target AICTE Institution ID"),
    source_language: Optional[str] = Form("auto", description="Audio language: te, ta, hi, mr, bn, en, or auto"),
):
    # 1. Validate file extension
    filename = audio_file.filename or "voice_note.wav"
    ext = os.path.splitext(filename)[1].lower()
    allowed_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".aac", ".flac", ".webm"]
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}",
        )

    # 2. Save audio file to temporary file for Whisper processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        shutil.copyfileobj(audio_file.file, temp_audio)
        temp_audio_path = temp_audio.name

    try:
        # 3. Transcribe audio to plain text via Whisper
        transcription_res = transcribe_audio_detailed(temp_audio_path, language=source_language)
        raw_transcription = transcription_res.get("text", "").strip()
        whisper_lang = transcription_res.get("language")
        whisper_used = transcription_res.get("whisper_used", False)

        if not raw_transcription:
            raw_transcription = "Voice note audio received. Content logged for nodal review."

        # 4. Auto-detect language if not explicitly provided
        detected_lang = source_language
        if not detected_lang or detected_lang == "auto":
            detected_lang = whisper_lang or detect_language_script(raw_transcription)

        # 5. Translate regional Indian language to English if not already English
        translated_english = raw_transcription
        if detected_lang.lower() not in ["en", "english"]:
            translated_english = translate_to_english(raw_transcription, detected_lang)

        # 6. Compose grievance Title
        final_title = title.strip() if title and title.strip() else f"Voice Grievance ({SUPPORTED_LANGUAGES.get(detected_lang, {}).get('name', 'Indic')}): {translated_english[:50]}..."
        combined_text = f"{final_title}. {translated_english}"

        # 7. Run AI Semantic Classification & Duplicate Check
        classification = classify_bureau_and_priority(combined_text)
        assigned_bureau_name = classification["bureau_name"]
        computed_priority = classification["priority"]

        # 8. Resolve Bureau & Institution
        bureau_id, bureau_name, base_sla_hours = resolve_bureau(assigned_bureau_name)
        institution_id, inst_name, inst_city, inst_state = resolve_institution(
            None, institution_aicte_id
        )

        # 9. Dynamic SLA Calculation & Status Determination
        sla_deadline = calculate_dynamic_sla(base_sla_hours, computed_priority)

        # 10. Persist Complaint & Audit Log if complainant_email is provided
        record = None
        is_duplicate = False
        master_id = None
        message = ""

        if complainant_email and complainant_email.strip():
            recent_complaints = get_all_complaints_for_duplicate_check()
            is_duplicate, master_id, similarity_score = check_duplicate_complaint(
                combined_text, recent_complaints, threshold=0.85
            )
            complaint_status = "SUBMITTED" if is_duplicate else "AUTO_ASSIGNED"

            record = save_complaint_and_audit(
                title=final_title,
                description=f"[Voice Transcription ({detected_lang})]: {raw_transcription}\n\n[English Translation]: {translated_english}",
                complainant_role=complainant_role,
                complainant_email=complainant_email,
                complainant_phone=complainant_phone,
                institution_id=institution_id,
                institution_name=inst_name,
                institution_city=inst_city,
                institution_state=inst_state,
                bureau_id=bureau_id,
                bureau_name=bureau_name,
                priority=computed_priority,
                status=complaint_status,
                is_duplicate=is_duplicate,
                master_complaint_id=master_id,
                sla_deadline=sla_deadline,
            )

            message = (
                f"Voice grievance transcribed ({detected_lang}) and routed to {bureau_name} "
                f"with {computed_priority} priority."
            )
            if is_duplicate:
                message += f" Flagged as duplicate of master ticket {master_id}."

        bureau_code = BUREAU_CODE_MAP.get(assigned_bureau_name, "BUR_GENERIC")

        # Standard Prompt 12 payload format
        response_payload = {
            "transcription": raw_transcription,
            "english_translation": translated_english,
            "detected_language": detected_lang.lower(),
            "assigned_bureau": bureau_code,
            "priority": computed_priority,
            # Frontend convenience aliases
            "englishText": translated_english,
            "detectedLanguage": detected_lang.lower(),
            "assignedBureau": assigned_bureau_name,
            "assignedBureauCode": bureau_code,
            "language_name": SUPPORTED_LANGUAGES.get(detected_lang, {}).get("name", "Unknown"),
            "status": "success",
            "whisper_used": whisper_used,
        }

        if record:
            response_payload["tracking_id"] = record["tracking_id"]
            response_payload["complaint_id"] = record["complaint_id"]
            response_payload["sla_deadline"] = record["sla_deadline"]
            response_payload["is_duplicate"] = is_duplicate
            response_payload["master_complaint_id"] = master_id
            response_payload["message"] = message

        return response_payload

    finally:
        # Cleanup temporary audio file
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception:
                pass


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate Grievance Text or Status Updates",
    description="Translates complaint updates, directives, or Action Taken Reports into regional languages.",
)
async def translate_text(payload: TranslationRequest):
    tgt = payload.target_language.lower().strip()
    src = (payload.source_language or "en").lower().strip()

    if tgt not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language '{tgt}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}",
        )

    # If translating from English to regional language
    if src == "en" and tgt != "en":
        translated = translate_from_english(payload.text, tgt)
    elif src != "en" and tgt == "en":
        translated = translate_to_english(payload.text, src)
    elif src == tgt:
        translated = payload.text
    else:
        # Cross translation: regional -> English -> regional
        eng = translate_to_english(payload.text, src)
        translated = translate_from_english(eng, tgt)

    tgt_info = SUPPORTED_LANGUAGES.get(tgt, {})
    return TranslationResponse(
        original_text=payload.text,
        source_language=src,
        target_language=tgt,
        target_language_name=tgt_info.get("name", tgt),
        translated_text=translated,
    )
