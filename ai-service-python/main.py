from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import time
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path to import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from legal_modules.ipc_module import ipc_module
from services.rag_service import rag_service
from services.charge_prediction import charge_prediction_service
from services.translation_service import translation_service
from services.tts_service import tts_service
from services.llm_service import llm_service
from services.ai_orchestrator import ai_orchestrator
from utils.config import Config
from utils.logging import log_startup, log_user_query, log_error
from utils.validation import validate_dataset
from metrics.metrics_tracker import metrics_tracker
import os


def _format_list_field(label: str, values):
    if isinstance(values, list) and values:
        return f"{label}: {', '.join(str(value) for value in values)}"
    return None


def _format_mapping_field(label: str, mapping):
    if isinstance(mapping, dict) and mapping:
        formatted = [
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in mapping.items()
            if value and value != "not_applicable"
        ]
        if formatted:
            return f"{label}: {', '.join(formatted)}"
    return None


def build_section_context(section):
    chapter = section.get("chapter") or {}
    citation = section.get("citation") or {}
    context_lines = [
        f"Section {section.get('section_number')}: {section.get('title', 'Untitled')}"
    ]

    optional_lines = [
        f"Chapter: {chapter.get('chapter_name')}" if chapter.get("chapter_name") else None,
        f"Chapter Number: {chapter.get('chapter_number')}" if chapter.get("chapter_number") else None,
        f"Description: {section.get('description')}" if section.get("description") else None,
        f"Section Text: {section.get('section_text')}" if section.get("section_text") else None,
        f"Crime Category: {section.get('crime_category')}" if section.get("crime_category") else None,
        f"Crime Subcategory: {section.get('crime_subcategory')}" if section.get("crime_subcategory") else None,
        f"Severity Level: {section.get('severity_level')}" if section.get("severity_level") else None,
        _format_list_field("Keywords", section.get("keywords")),
        _format_list_field("Synonyms", section.get("synonyms")),
        _format_list_field("Legal Elements", section.get("legal_elements")),
        _format_list_field("Example Scenarios", section.get("example_scenarios")),
        _format_list_field("Scenario Training", section.get("scenario_training")),
        _format_list_field("Vector Search Terms", section.get("vector_search_terms")),
        _format_list_field("Related Sections", section.get("related_sections")),
        _format_mapping_field("Punishment", section.get("punishment")),
        _format_mapping_field("Crime Type Mapping", section.get("crime_type_mapping")),
        _format_list_field("Court Judgment Links", section.get("court_judgment_links")),
        f"Citation: {citation.get('law')}, Section {citation.get('section')}" if citation.get("law") and citation.get("section") else None,
        f"Verified Citation: {citation.get('verified')}" if citation.get("verified") is not None else None
    ]

    context_lines.extend(line for line in optional_lines if line)
    return "\n".join(context_lines)


def build_section_fallback_answer(section):
    chapter = section.get("chapter") or {}
    citation = section.get("citation") or {}
    punishment = section.get("punishment") or {}

    answer_parts = [
        f"Section {section.get('section_number')} of the Indian Penal Code is titled \"{section.get('title', 'Untitled')}\"."
    ]

    if section.get("description"):
        answer_parts.append(section["description"])

    if chapter.get("chapter_name"):
        answer_parts.append(f"It falls under the chapter \"{chapter['chapter_name']}\".")

    metadata_bits = []
    if section.get("crime_category"):
        metadata_bits.append(f"crime category: {section['crime_category']}")
    if section.get("crime_subcategory"):
        metadata_bits.append(f"subcategory: {section['crime_subcategory']}")
    if section.get("severity_level"):
        metadata_bits.append(f"severity: {section['severity_level']}")
    if metadata_bits:
        answer_parts.append("Metadata: " + ", ".join(metadata_bits) + ".")

    punishment_bits = [
        f"{key.replace('_', ' ').title()}: {value}"
        for key, value in punishment.items()
        if value and value != "not_applicable"
    ]
    if punishment_bits:
        answer_parts.append("Punishment details: " + "; ".join(punishment_bits) + ".")

    if section.get("legal_elements"):
        answer_parts.append("Legal elements: " + ", ".join(section["legal_elements"]) + ".")

    if section.get("related_sections"):
        answer_parts.append("Related sections: " + ", ".join(str(value) for value in section["related_sections"]) + ".")

    if citation.get("law") and citation.get("section"):
        verified_suffix = " (verified)" if citation.get("verified") else ""
        answer_parts.append(f"Citation: {citation['law']}, Section {citation['section']}{verified_suffix}.")

    return "\n\n".join(answer_parts)

app = FastAPI(title="JURIS AI - Legal Intelligence Platform", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to track request metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        metrics_tracker.record_request(duration, success=True)
        return response
    except Exception as e:
        duration = time.time() - start_time
        metrics_tracker.record_request(duration, success=False)
        raise

# Request models
class QueryRequest(BaseModel):
    query: str
    language: str = "english"
    profession: str = "general"
    enable_voice: bool = False
    stream: bool = False

class ScenarioRequest(BaseModel):
    scenario: str
    language: str = "english"
    profession: str = "general"
    enable_voice: bool = False
    stream: bool = False

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    language: str = "english"


def _merge_pro_payload(base_response: Dict, pro_payload: Dict) -> Dict:
    merged = dict(base_response)
    merged.update(
        {
            "understanding": pro_payload.get("understanding"),
            "severity": pro_payload.get("severity", {}),
            "ipc_sections": pro_payload.get("ipc_sections", []),
            "steps": pro_payload.get("steps", []),
            "complaint_draft": pro_payload.get("complaint_draft"),
            "evidence_checklist": pro_payload.get("evidence_checklist", []),
            "court_flow": pro_payload.get("court_flow", {}),
            "tips": pro_payload.get("tips", []),
            "donts": pro_payload.get("donts", []),
            "audio_text": pro_payload.get("audio_text"),
            "persona": pro_payload.get("persona"),
            "validation": pro_payload.get("validation", {}),
            "sections_referenced": pro_payload.get("sections_referenced", merged.get("sections_referenced", [])),
            "matched_sections": pro_payload.get("matched_sections", merged.get("matched_sections", [])),
            "charges": pro_payload.get("charges", merged.get("charges", [])),
            "analysis": pro_payload.get("analysis", merged.get("analysis")),
            "complete_response": pro_payload.get("complete_response", merged.get("complete_response")),
            "structured_response": pro_payload,
        }
    )
    return merged

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "JURIS AI Python Service",
        "components": {
            "database": "connected",  # In real implementation, check actual connection
            "redis": "connected",     # In real implementation, check actual connection
            "faiss_index": "loaded",
            "llm": "available"
        }
    }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return metrics_tracker.get_metrics()

# RAG endpoint for legal questions
@app.post("/rag")
async def rag_query(request: QueryRequest):
    """Process legal questions using RAG pipeline"""
    try:
        log_user_query(request.query)
        
        # Get similar sections using RAG
        similar_sections = rag_service.search_similar_sections(request.query)
        
        # Build context from similar sections
        context_parts = []
        for item in similar_sections:
            section = item["section"]
            context_parts.append(build_section_context(section))
        
        context = "\n\n".join(context_parts)
        
        # Create prompt for LLM with guardrails
        prompt = f"""You are a legal assistant specialized in the Indian Penal Code (IPC 1860).

You must only use IPC sections 1–511.

You must not reference any other law.

Only use information retrieved from the IPC dataset provided in the context below.

If the answer cannot be found in the dataset respond:

"This information is not available in the IPC dataset."

Context:
{context}

Question: {request.query}

Answer:"""
        
        # Generate response using LLM service
        response = llm_service.generate_response(prompt, max_tokens=Config.MAX_OUTPUT_TOKENS)

        if response == "AI reasoning service temporarily unavailable." and similar_sections:
            response = build_section_fallback_answer(similar_sections[0]["section"])
        
        # Translate if needed
        if request.language != "english":
            translated_response = translation_service.translate(response, request.language)
            if translated_response:
                response = translated_response
        
        # Generate TTS if requested
        audio_path = None
        if request.enable_voice:
            audio_path = tts_service.synthesize_speech(response, request.language)
        
        base_response = {
            "analysis": response,
            "complete_response": response,  # For regular queries, analysis and complete_response are the same
            "audio_path": audio_path if request.enable_voice else None,
            "sections_referenced": [item["section"]["section_number"] for item in similar_sections],
            "matched_sections": [item["section"] for item in similar_sections]
        }

        pro_payload = await ai_orchestrator.process(
            request.query,
            persona=request.profession,
            language=request.language,
        )
        return _merge_pro_payload(base_response, pro_payload)
        
    except Exception as e:
        log_error(f"RAG query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Charge prediction endpoint
@app.post("/predict-charges")
async def predict_charges(request: ScenarioRequest):
    """Predict possible IPC charges from a crime scenario"""
    try:
        log_user_query(f"Scenario: {request.scenario}")
        
        # Predict charges
        predictions = charge_prediction_service.predict_charges(request.scenario)
        
        # Format response
        analysis_text = f"Based on the scenario provided, the following IPC sections may be applicable:"
        response = {
            "analysis": analysis_text,
            "charges": predictions
        }
        
        # Translate if needed
        if request.language != "english":
            translated_analysis = translation_service.translate(response["analysis"], request.language)
            if translated_analysis:
                response["analysis"] = translated_analysis
                analysis_text = translated_analysis
                
            # Translate charge titles and punishments
            for charge in response["charges"]:
                translated_title = translation_service.translate(charge["title"], request.language)
                if translated_title:
                    charge["title"] = translated_title
                    
                translated_punishment = translation_service.translate(charge["punishment"], request.language)
                if translated_punishment:
                    charge["punishment"] = translated_punishment
        
        # Generate TTS if requested - for complete response including charges
        audio_path = None
        if request.enable_voice:
            # Create complete text for audio including charges
            complete_text = analysis_text + "\n\nPredicted Charges:\n"
            for i, charge in enumerate(predictions, 1):
                complete_text += f"{i}. Section {charge['section']}: {charge['title']}\n"
                complete_text += f"   Confidence: {charge['confidence'] * 100:.1f}%\n"
                if charge.get('punishment'):
                    # Format punishment text
                    punishment_parts = []
                    p = charge['punishment']
                    if p.get('imprisonment') and p['imprisonment'] != 'not_applicable':
                        punishment_parts.append(f"Imprisonment: {p['imprisonment']}")
                    if p.get('fine') and p['fine'] != 'not_applicable':
                        punishment_parts.append(f"Fine: {p['fine']}")
                    if p.get('cognizable') and p['cognizable'] != 'not_applicable':
                        punishment_parts.append(f"Cognizable: {p['cognizable']}")
                    if p.get('bailable') and p['bailable'] != 'not_applicable':
                        punishment_parts.append(f"Bailable: {p['bailable']}")
                    if p.get('triable_by') and p['triable_by'] != 'not_applicable':
                        punishment_parts.append(f"Triable by: {p['triable_by']}")
                    
                    if punishment_parts:
                        complete_text += f"   Punishment: {', '.join(punishment_parts)}\n"
                complete_text += "\n"
            
            audio_path = tts_service.synthesize_speech(complete_text, request.language)
            # Return the complete text as analysis so frontend and backend have the full response
            response["analysis"] = complete_text
        
        base_response = {
            "analysis": response["analysis"],  # Original intro text
            "complete_response": complete_text if request.enable_voice else response["analysis"],  # Full text for audio
            "charges": response["charges"],
            "audio_path": audio_path if request.enable_voice else None
        }
        pro_payload = await ai_orchestrator.process(
            request.scenario,
            persona=request.profession,
            language=request.language,
        )
        return _merge_pro_payload(base_response, pro_payload)
        
    except Exception as e:
        log_error(f"Charge prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# TTS endpoint for generating audio from text
@app.post("/generate-audio")
async def generate_audio(request: TTSRequest):
    """Generate audio for given text"""
    try:
        audio_path = tts_service.synthesize_speech(request.text, request.language)
        
        return {
            "audio_path": audio_path
        }
        
    except Exception as e:
        log_error(f"Audio generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio generation failed")


@app.post("/pro/analyze")
async def analyze_pro(request: QueryRequest):
    try:
        log_user_query(f"JurisAI Pro: {request.query}")
        payload = await ai_orchestrator.process(
            request.query,
            persona=request.profession,
            language=request.language,
        )
        return payload
    except Exception as e:
        log_error(f"JurisAI Pro analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/pro/stream")
async def stream_pro(request: QueryRequest):
    try:
        return StreamingResponse(
            ai_orchestrator.stream(
                request.query,
                persona=request.profession,
                language=request.language,
            ),
            media_type="application/x-ndjson",
        )
    except Exception as e:
        log_error(f"JurisAI Pro streaming failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# TTS endpoint
@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        audio_path = tts_service.synthesize_speech(request.text, request.language)
        
        if not audio_path:
            raise HTTPException(status_code=500, detail="TTS synthesis failed")
            
        return {"audio_path": audio_path}
        
    except Exception as e:
        log_error(f"TTS failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# IPC section lookup endpoint
@app.get("/ipc-section/{section_number}")
async def get_ipc_section(section_number: int):
    """Get details of a specific IPC section"""
    try:
        section = ipc_module.get_section(section_number)
        
        if not section:
            raise HTTPException(status_code=404, detail="IPC section not found")
            
        return section
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(f"IPC section lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get all IPC sections endpoint
@app.get("/ipc-sections")
async def get_all_ipc_sections():
    """Get all IPC sections"""
    try:
        sections = ipc_module.get_all_sections()
        return {"sections": sections, "total": len(sections)}
        
    except Exception as e:
        log_error(f"IPC sections lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Related sections endpoint
@app.get("/ipc-section/{section_number}/related")
async def get_related_sections(section_number: int):
    """Get related IPC sections"""
    try:
        related_sections = ipc_module.get_related_sections(section_number)
        return {"related_sections": related_sections}
        
    except Exception as e:
        log_error(f"Related sections lookup failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    # Validate dataset before starting
    # Handle path differently when running from ai-service-python directory
    dataset_relative_path = Config.LEGAL_ACTS["IPC"]["dataset"]
    if os.getcwd().endswith("ai-service-python"):
        dataset_path = os.path.join("..", dataset_relative_path)
    else:
        dataset_path = os.path.join(os.getcwd(), dataset_relative_path)
        
    print(f"Validating dataset at: {dataset_path}")
    if not validate_dataset(dataset_path):
        log_error("Dataset validation failed. Exiting.")
        exit(1)
    
    log_startup()
    uvicorn.run(app, host="0.0.0.0", port=8000)
