import os

API_URL = os.getenv("API_BASE_URL", "http://api:8000")
WS_URL  = os.getenv("WS_URL", "ws://localhost:8000")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from typing import Dict, List, Any
import requests
from websocket import WebSocketApp
import threading

st.set_page_config(
    page_title="Medical NLP Pipeline",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global dark mode */
    html, body, .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
     /*  DataFrame “grid” cells & headers */
    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataFrame"] [role="gridcell"] {
    background-color: #000000 !important;
    color: #FFFFFF !important;
      }

    /* Alert box */
    .stAlert {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 10px;
        color: white !important;
    }

    /* Entity highlighting */
    .entity-highlight {
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }

    .symptom {
        background-color: #ff4d4d;
        color: white;
    }

    .treatment {
        background-color: #28a745;
        color: white;
    }

    .diagnosis {
        background-color: #007bff;
        color: white;
    }

    /* SOAP section styling */
    .soap-section {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 4px solid #00aaff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


class MockPipeline:
    def process_conversation(self, text: str) -> Dict[str, Any]:
        time.sleep(1)
        
        return {
            "entities": [
                {"text": "neck pain", "label": "SYMPTOM", "start": 10, "end": 19, "confidence": 0.95},
                {"text": "back pain", "label": "SYMPTOM", "start": 25, "end": 34, "confidence": 0.93},
                {"text": "whiplash injury", "label": "DIAGNOSIS", "start": 100, "end": 115, "confidence": 0.88},
                {"text": "physiotherapy", "label": "TREATMENT", "start": 150, "end": 163, "confidence": 0.90},
                {"text": "painkillers", "label": "TREATMENT", "start": 170, "end": 181, "confidence": 0.85}
            ],
            "summary": {
                "patient_name": "Ms. Jones",
                "symptoms": ["neck pain", "back pain", "stiffness", "discomfort"],
                "diagnosis": ["whiplash injury"],
                "treatment": ["10 physiotherapy sessions", "painkillers"],
                "current_status": "Occasional backache",
                "prognosis": "Full recovery expected within six months",
                "timeline": {
                    "accident_date": "September 1st",
                    "initial_treatment": "Same day - A&E visit",
                    "recovery_duration": "4 weeks acute phase"
                },
                "severity_score": 0.4
            },
            "sentiment_analysis": [
                {
                    "text": "I'm doing better, but I still have some discomfort",
                    "sentiment": {
                        "sentiment": "hopeful",
                        "confidence": 0.75,
                        "intent": "reporting_symptoms",
                        "intent_confidence": 0.80,
                        "emotional_indicators": ["hopeful:better", "concerned:discomfort"]
                    }
                },
                {
                    "text": "The first four weeks were rough",
                    "sentiment": {
                        "sentiment": "anxious",
                        "confidence": 0.82,
                        "intent": "providing_history",
                        "intent_confidence": 0.85,
                        "emotional_indicators": ["frustrated:rough"]
                    }
                },
                {
                    "text": "That's a relief!",
                    "sentiment": {
                        "sentiment": "reassured",
                        "confidence": 0.90,
                        "intent": "expressing_relief",
                        "intent_confidence": 0.88,
                        "emotional_indicators": ["reassured:relief"]
                    }
                }
            ],
            "soap_note": {
                "subjective": {
                    "chief_complaint": "Neck and back pain following motor vehicle accident",
                    "history_of_present_illness": "Patient involved in rear-end collision on September 1st. Experienced immediate neck and back pain. Initial severe symptoms for 4 weeks, now improved with occasional discomfort.",
                    "symptoms": ["neck pain", "back pain", "stiffness", "occasional discomfort"],
                    "pain_scale": None,
                    "onset": "September 1st",
                    "patient_concerns": ["Future impact on daily life"]
                },
                "objective": {
                    "physical_exam": "Full range of motion in cervical and lumbar spine, no tenderness",
                    "observations": "Patient appears comfortable, normal gait observed",
                    "vital_signs": "Within normal limits",
                    "imaging": "None performed",
                    "laboratory": "None performed"
                },
                "assessment": {
                    "diagnosis": ["Whiplash injury", "Mechanical back pain"],
                    "differential_diagnosis": ["Cervical strain", "Lumbar strain", "Soft tissue injury"],
                    "severity": "Mild to Moderate",
                    "prognosis": "Full recovery expected within six months",
                    "clinical_impression": "Post-traumatic musculoskeletal injury with good recovery trajectory"
                },
                "plan": {
                    "treatment": ["Continue physiotherapy as needed", "Home exercise program"],
                    "medications": ["OTC analgesics PRN for pain"],
                    "follow_up": "As needed if symptoms worsen",
                    "patient_education": [
                        "Continue home exercises as prescribed",
                        "Use ice/heat for symptom management",
                        "Maintain normal activities as tolerated"
                    ],
                    "referrals": [],
                    "precautions": ["Return if symptoms worsen", "Avoid heavy lifting for 2 weeks"]
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "confidence_score": 0.85,
                    "icd10_codes": ["S13.4", "M54.2"],
                    "cpt_codes": ["99213", "97110"]
                }
            },
            "quality_metrics": {
                "entity_coverage": 0.75,
                "summary_completeness": 0.90,
                "soap_completeness": 0.85,
                "overall_confidence": 0.85
            }
        }

tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Input", "🔍 Entities", "📊 Analysis", "📋 SOAP Note", "📈 Metrics"
    ])
with tab1:
    st.subheader("Real-Time Transcription")
    if st.button("Start Live Transcription", key="demo_start_live"):
        def on_message(ws, message):
            st.session_state.live_results.append(json.loads(message))
            st.experimental_rerun()
        
        def on_open(ws):
            st.session_state.ws = ws
            st.success("Connected to live transcription")
        
        st.session_state.live_results = []
        ws = WebSocketApp(
            WS_URL + "/ws/transcribe-stream",
            on_message=on_message,
            on_open=on_open
        )
        threading.Thread(target=ws.run_forever, daemon=True).start()
        
        text_input = st.text_input("Send live text")
        if text_input and st.session_state.get("ws"):
            st.session_state.ws.send(text_input)
        
        if st.session_state.live_results:
            st.write("Live Entities:", st.session_state.live_results)


def main():
    st.title("🏥 Medical Transcription NLP Pipeline")
    st.markdown("### Advanced AI System for Medical Conversation Analysis")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        endpoint = st.selectbox(
            "Select API Endpoint",
            [
                "Full Analysis (/api/v1/analyze)",
                "Entity Extraction (/api/v1/entities/extract)",
                "Sentiment Analysis (/api/v1/sentiment/analyze)",
                "SOAP Note (/api/v1/soap/generate)",
                "Async Analysis (/api/v1/analyze/async)"
            ]
        )
        st.subheader("Processing Options")
        extract_entities = st.checkbox("Extract Medical Entities", value=True)
        generate_summary = st.checkbox("Generate Summary", value=True)
        analyze_sentiment = st.checkbox("Analyze Sentiment", value=True)
        generate_soap = st.checkbox("Generate SOAP Note", value=True)
        with st.expander("Advanced Settings"):
            confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7)
            include_icd_codes = st.checkbox("Include ICD-10 Codes", value=True)
            include_cpt_codes = st.checkbox("Include CPT Codes", value=True)
        st.markdown("---")
        st.subheader("About")
        st.info("""
        This pipeline demonstrates:
        - Medical NER with UMLS mapping
        - Clinical sentiment analysis
        - SOAP note generation
        - Quality metrics assessment
        """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Input", "🔍 Entities", "📊 Analysis", "📋 SOAP Note", "📈 Metrics"
    ])
    
    with tab1:
        st.header("Medical Conversation Input")
        input_method = st.radio(
            "Choose input method:",
            ["Use Example", "Paste Text", "Upload File"]
        )
        
        if input_method == "Use Example":
            conversation_text = st.text_area(
                "Medical Conversation",
                value=get_example_conversation(),
                height=400
            )
        elif input_method == "Paste Text":
            conversation_text = st.text_area(
                "Paste your medical conversation here",
                placeholder="Doctor: How are you feeling today?\nPatient: I have been experiencing...",
                height=400
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload conversation file",
                type=["txt", "json"]
            )
            conversation_text = ""
            if uploaded_file:
                conversation_text = uploaded_file.read().decode("utf-8")
                st.text_area("Uploaded content:", value=conversation_text, height=400)
        
        st.subheader("Real-Time Transcription")
        if st.button("Start Live Transcription", key="main_start_live"):
            def on_message(ws, message):
                if 'live_results' not in st.session_state:
                    st.session_state.live_results = []
                st.session_state.live_results.append(json.loads(message))
                st.experimental_rerun()
            
            def on_open(ws):
                st.session_state.ws = ws
                st.success("Connected to live transcription")
            
            st.session_state.live_results = []
            ws = WebSocketApp(
                WS_URL + "/ws/transcribe-stream",
                on_message=on_message,
                on_open=on_open
            )
            threading.Thread(target=ws.run_forever, daemon=True).start()
        
        text_input = st.text_input("Send live text")
        if text_input and st.session_state.get("ws"):
            st.session_state.ws.send(text_input)
        
        if st.session_state.get("live_results"):
            st.write("Live Entities:", st.session_state.live_results)
        
        if st.button("🚀 Analyze Conversation", type="primary"):
            if conversation_text:
                with st.spinner("Processing medical conversation..."):
                    try:
                        endpoint_map = {
                            "Full Analysis (/api/v1/analyze)": {
                                "url": f"{API_URL}/api/v1/analyze",
                                "payload": {
                                    "conversation_text": conversation_text,
                                    "patient_id": "PAT-" + str(int(time.time()))
                                }
                            },
                            "Entity Extraction (/api/v1/entities/extract)": {
                                "url": f"{API_URL}/api/v1/entities/extract",
                                "payload": {"text": conversation_text}
                            },
                            "Sentiment Analysis (/api/v1/sentiment/analyze)": {
                                "url": f"{API_URL}/api/v1/sentiment/analyze",
                                "payload": {"text": conversation_text}
                            },
                            "SOAP Note (/api/v1/soap/generate)": {
                                "url": f"{API_URL}/api/v1/soap/generate",
                                "payload": {
                                    "conversation_text": conversation_text,
                                    "patient_id": "PAT-" + str(int(time.time()))
                                }
                            },
                            "Async Analysis (/api/v1/analyze/async)": {
                                "url": f"{API_URL}/api/v1/analyze/async",
                                "payload": {
                                    "conversation_text": conversation_text,
                                    "patient_id": "PAT-" + str(int(time.time()))
                                }
                            }
                        }
                        
                        selected = endpoint_map[endpoint]
                        response = requests.post(
                            selected["url"],
                            json=selected["payload"],
                            timeout=30
                        )
                        response.raise_for_status()
                        results = response.json()
                        st.write("**API Response**:", results)  
                        
                        if endpoint == "Entity Extraction (/api/v1/entities/extract)":
                            results = {
                                "entities": results.get("entities", []),
                                "summary": {},
                                "sentiment_analysis": [],
                                "soap_note": {},
                                "quality_metrics": {"entity_coverage": 0.8, "overall_confidence": 0.8}
                            }
                        elif endpoint == "Sentiment Analysis (/api/v1/sentiment/analyze)":
                            results = {
                                "entities": [],
                                "summary": {},
                                "sentiment_analysis": [{"text": conversation_text, "sentiment": results}],
                                "soap_note": {},
                                "quality_metrics": {"overall_confidence": results.get("confidence", 0.8)}
                            }
                        elif endpoint == "SOAP Note (/api/v1/soap/generate)":
                            results = {
                                "entities": [],
                                "summary": {},
                                "sentiment_analysis": [],
                                "soap_note": results,
                                "quality_metrics": {"soap_completeness": 0.8, "overall_confidence": 0.8}
                            }
                        elif endpoint == "Async Analysis (/api/v1/analyze/async)":
                            job_id = results["job_id"]
                            with st.spinner("Waiting for async job to complete..."):
                                for _ in range(10):
                                    time.sleep(2)
                                    job_response = requests.get(
                                        f"{API_URL}/api/v1/jobs/{job_id}",
                                        timeout=10
                                    )
                                    job_response.raise_for_status()
                                    job_result = job_response.json()
                                    if job_result["status"] == "completed":
                                        results = job_result["result"]
                                        break
                                else:
                                    st.error("Async job did not complete in time")
                                    return
                        
                        normalized_results = {
                            "entities": results.get("entities", []),
                            "summary": results.get("summary", {}),
                            "sentiment_analysis": results.get("sentiment_analysis", []),
                            "soap_note": results.get("soap_note", {}),
                            "quality_metrics": results.get("quality_metrics", {
                                "entity_coverage": 0.8,
                                "summary_completeness": 0.8,
                                "soap_completeness": 0.8,
                                "overall_confidence": 0.8
                            })
                        }
                        
                        if not extract_entities:
                            normalized_results["entities"] = []
                        if not generate_summary:
                            normalized_results["summary"] = {}
                        if not analyze_sentiment:
                            normalized_results["sentiment_analysis"] = []
                        if not generate_soap:
                            normalized_results["soap_note"] = {}
                        if extract_entities and normalized_results.get("entities"):
                            normalized_results["entities"] = [
                                e for e in normalized_results["entities"] if e["confidence"] >= confidence_threshold
                            ]
                        
                        st.session_state.results = normalized_results
                        st.session_state.processed = True
                        st.success("✅ Analysis complete!")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to process conversation: {str(e)}")
                        st.error(f"API Error Details: {e.response.text if e.response else 'Unknown'}")
            else:
                st.error("Please provide conversation text")
    
    if hasattr(st.session_state, 'processed') and st.session_state.processed:
        results = st.session_state.results
        with tab2:
            st.write("Entities Data:", results["entities"])  
            display_entities(results["entities"], conversation_text)
        with tab3:
            st.write("Analysis Data:", results)  
            display_analysis(results)
        with tab4:
            st.write("SOAP Note Data:", results["soap_note"])  
            display_soap_note(results["soap_note"])
        with tab5:
            st.write("Metrics Data:", results["quality_metrics"])  
            display_metrics(results["quality_metrics"])



def get_example_conversation():
    """Return example medical conversation"""
    return """Physician: Good morning, Ms. Jones. How are you feeling today?
Patient: Good morning, doctor. I'm doing better, but I still have some discomfort now and then.
Physician: I understand you were in a car accident last September. Can you walk me through what happened?
Patient: Yes, it was on September 1st, around 12:30 in the afternoon. I was driving from Cheadle Hulme to Manchester when I had to stop in traffic. Out of nowhere, another car hit me from behind, which pushed my car into the one in front.
Physician: That sounds like a strong impact. Were you wearing your seatbelt?
Patient: Yes, I always do.
Physician: What did you feel immediately after the accident?
Patient: At first, I was just shocked. But then I realized I had hit my head on the steering wheel, and I could feel pain in my neck and back almost right away.
Physician: Did you seek medical attention at that time?
Patient: Yes, I went to Moss Bank Accident and Emergency. They checked me over and said it was a whiplash injury, but they didn't do any X-rays. They just gave me some advice and sent me home.
Physician: How did things progress after that?
Patient: The first four weeks were rough. My neck and back pain were really bad—I had trouble sleeping and had to take painkillers regularly. It started improving after that, but I had to go through ten sessions of physiotherapy to help with the stiffness and discomfort.
Physician: That makes sense. Are you still experiencing pain now?
Patient: It's not constant, but I do get occasional backaches. It's nothing like before, though.
Physician: That's good to hear. Have you noticed any other effects, like anxiety while driving or difficulty concentrating?
Patient: No, nothing like that. I don't feel nervous driving, and I haven't had any emotional issues from the accident.
Physician: And how has this impacted your daily life? Work, hobbies, anything like that?
Patient: I had to take a week off work, but after that, I was back to my usual routine. It hasn't really stopped me from doing anything.
Physician: That's encouraging. Let's go ahead and do a physical examination to check your mobility and any lingering pain.
[Physical Examination Conducted]
Physician: Everything looks good. Your neck and back have a full range of movement, and there's no tenderness or signs of lasting damage. Your muscles and spine seem to be in good condition.
Patient: That's a relief!
Physician: Yes, your recovery so far has been quite positive. Given your progress, I'd expect you to make a full recovery within six months of the accident. There are no signs of long-term damage or degeneration.
Patient: That's great to hear. So, I don't need to worry about this affecting me in the future?
Physician: That's right. I don't foresee any long-term impact on your work or daily life. If anything changes or you experience worsening symptoms, you can always come back for a follow-up. But at this point, you're on track for a full recovery.
Patient: Thank you, doctor. I appreciate it.
Physician: You're very welcome, Ms. Jones. Take care, and don't hesitate to reach out if you need anything."""


def display_entities(entities: List[Dict], original_text: str):
    """Display extracted entities with visualizations"""
    st.header("🔍 Extracted Medical Entities")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", len(entities))
    with col2:
        unique_types = len(set(e["label"] for e in entities))
        st.metric("Entity Types", unique_types)
    with col3:
        avg_confidence = sum(e["confidence"] for e in entities) / len(entities) if entities else 0
        st.metric("Avg Confidence", f"{avg_confidence:.2%}")
    
    st.subheader("Entity Distribution")
    entity_df = pd.DataFrame(entities)
    if not entity_df.empty:
        entity_counts = entity_df["label"].value_counts()
        
        fig = px.bar(
            x=entity_counts.index,
            y=entity_counts.values,
            labels={"x": "Entity Type", "y": "Count"},
            color=entity_counts.index,
            color_discrete_map={
                "SYMPTOM": "#ff6b6b",
                "TREATMENT": "#4ecdc4",
                "DIAGNOSIS": "#45b7d1",
                "BODY_PART": "#96ceb4",
                "TEMPORAL": "#dda0dd"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Detailed Entity List")
    
    entity_data = []
    for entity in entities:
        entity_data.append({
            "Text": entity["text"],
            "Type": entity["label"],
            "Confidence": f"{entity['confidence']:.2%}",
            "Position": f"{entity['start']}-{entity['end']}",
            "Normalized": entity.get("normalized_form", "-"),
            "UMLS Code": entity.get("umls_code", "-")
        })
    
    entity_df_display = pd.DataFrame(entity_data)
    
    def highlight_entity_type(row):
        colors = {
            "SYMPTOM": "background-color: #ffe0e0",
            "TREATMENT": "background-color: #e0ffe0",
            "DIAGNOSIS": "background-color: #e0e0ff",
            "BODY_PART": "background-color: #fff0e0",
            "TEMPORAL": "background-color: #f0e0ff"
        }
        return [colors.get(row["Type"], "")] * len(row)
    
    styled_df = entity_df_display.style.apply(highlight_entity_type, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    st.subheader("Annotated Text")
    highlighted_text = highlight_entities_in_text(original_text, entities)
    st.markdown(highlighted_text, unsafe_allow_html=True)


def highlight_entities_in_text(text: str, entities: List[Dict]) -> str:
    """Highlight entities in the original text"""
    sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)
    
    highlighted = text
    for entity in sorted_entities:
        entity_class = entity["label"].lower().replace("_", "-")
        replacement = f'<span class="entity-highlight {entity_class}">{entity["text"]}</span>'
        
        highlighted = highlighted.replace(entity["text"], replacement, 1)
    
    return (
       f'<div class="annotated-text" '
       f'style="line-height: 1.8; padding: 10px; border-radius: 5px;">'
       f'{highlighted}</div>'
   )

def display_analysis(results: Dict):
    """Display analysis results including summary and sentiment"""
    st.header("📊 Medical Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Medical Summary")
        summary = results["summary"]
        
        st.markdown("**Patient Information**")
        st.write(f"- Name: {summary['patient_name']}")
        st.write(f"- Current Status: {summary['current_status']}")
        st.write(f"- Severity Score: {summary['severity_score']:.2f}/1.0")
        
        st.markdown("**Medical Details**")
        st.write(f"- Symptoms: {', '.join(summary['symptoms'])}")
        st.write(f"- Diagnosis: {', '.join(summary['diagnosis'])}")
        st.write(f"- Treatment: {', '.join(summary['treatment'])}")
        st.write(f"- Prognosis: {summary['prognosis']}")
        
        if summary['timeline']:
            st.markdown("**Timeline**")
            for event, date in summary['timeline'].items():
                st.write(f"- {event.replace('_', ' ').title()}: {date}")
    
    with col2:
        st.subheader("Severity Assessment")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=summary['severity_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Severity Score"},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.3], 'color': "lightgreen"},
                    {'range': [0.3, 0.6], 'color': "yellow"},
                    {'range': [0.6, 0.8], 'color': "orange"},
                    {'range': [0.8, 1], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("😊 Sentiment Analysis")
    
    sentiment_data = results["sentiment_analysis"]
    
    sentiments = [s["sentiment"]["sentiment"] for s in sentiment_data]
    confidences = [s["sentiment"]["confidence"] for s in sentiment_data]
    
    fig_sentiment = go.Figure()
    
    fig_sentiment.add_trace(go.Scatter(
        x=list(range(len(sentiments))),
        y=confidences,
        mode='lines+markers',
        name='Confidence',
        line=dict(color='blue', width=2),
        marker=dict(size=10)
    ))
    
    colors = {
        "anxious": "red",
        "neutral": "gray",
        "hopeful": "green",
        "reassured": "blue",
        "concerned": "orange"
    }
    
    for i, (sent, conf) in enumerate(zip(sentiments, confidences)):
        fig_sentiment.add_annotation(
            x=i, y=conf + 0.05,
            text=sent,
            showarrow=False,
            bgcolor=colors.get(sent, "gray"),
            font=dict(color="white", size=10),
            borderpad=4,
            borderwidth=1,
            bordercolor="black",
            opacity=0.8
        )
    
    fig_sentiment.update_layout(
        title="Patient Sentiment Journey",
        xaxis_title="Conversation Progress",
        yaxis_title="Confidence",
        yaxis_range=[0, 1.1],
        showlegend=False,
        height=300
    )
    
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    st.markdown("**Sentiment Details**")
    for i, item in enumerate(sentiment_data[:5]):  
        with st.expander(f"Statement {i+1}: {item['sentiment']['sentiment'].title()}"):
            st.write(f"**Text:** {item['text']}")
            st.write(f"**Sentiment:** {item['sentiment']['sentiment']} (Confidence: {item['sentiment']['confidence']:.2%})")
            st.write(f"**Intent:** {item['sentiment']['intent'].replace('_', ' ').title()}")
            st.write(f"**Emotional Indicators:** {', '.join(item['sentiment']['emotional_indicators'])}")


def display_soap_note(soap_note: Dict):
    """Display SOAP note in clinical format, with safe `.get()` lookups."""

    if not soap_note:
        st.warning("No SOAP note generated.")
        return

    metadata   = soap_note.get("metadata", {})
    confidence = metadata.get("confidence_score", 0.0)
    icd_codes  = metadata.get("icd10_codes", [])
    cpt_codes  = metadata.get("cpt_codes", [])

    st.header("📋 SOAP Note")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence Score", f"{confidence:.2%}")
    with col2:
        st.metric("ICD-10 Codes", ", ".join(icd_codes) if icd_codes else "-")
    with col3:
        st.metric("CPT Codes", ", ".join(cpt_codes) if cpt_codes else "-")

    st.markdown("---")

    subjective = soap_note.get("subjective", {})
    with st.container():
        st.markdown('<div class="soap-section">', unsafe_allow_html=True)
        st.subheader("S - Subjective")

        st.markdown(f"**Chief Complaint:** {subjective.get('chief_complaint', '-')}")
        st.markdown(f"**History of Present Illness:** {subjective.get('history_of_present_illness', '-')}")
        st.markdown(f"**Symptoms:** {', '.join(subjective.get('symptoms', [])) or '-'}")
        st.markdown(f"**Onset:** {subjective.get('onset', '-')}")
        concerns = subjective.get('patient_concerns', [])
        if concerns:
            st.markdown(f"**Patient Concerns:** {', '.join(concerns)}")

        st.markdown('</div>', unsafe_allow_html=True)

    objective = soap_note.get("objective", {})
    with st.container():
        st.markdown('<div class="soap-section">', unsafe_allow_html=True)
        st.subheader("O - Objective")

        st.markdown(f"**Physical Exam:** {objective.get('physical_exam', '-')}")
        st.markdown(f"**Observations:** {objective.get('observations', '-')}")
        st.markdown(f"**Vital Signs:** {objective.get('vital_signs', '-')}")
        st.markdown(f"**Imaging:** {objective.get('imaging', '-')}")
        st.markdown(f"**Laboratory:** {objective.get('laboratory', '-')}")
        st.markdown('</div>', unsafe_allow_html=True)

    assessment = soap_note.get("assessment", {})
    with st.container():
        st.markdown('<div class="soap-section">', unsafe_allow_html=True)
        st.subheader("A - Assessment")

        st.markdown(f"**Diagnosis:** {', '.join(assessment.get('diagnosis', [])) or '-'}")
        st.markdown(f"**Differential Diagnosis:** {', '.join(assessment.get('differential_diagnosis', [])) or '-'}")
        st.markdown(f"**Severity:** {assessment.get('severity', '-')}")
        st.markdown(f"**Prognosis:** {assessment.get('prognosis', '-')}")
        st.markdown(f"**Clinical Impression:** {assessment.get('clinical_impression', '-')}")
        st.markdown('</div>', unsafe_allow_html=True)

    plan = soap_note.get("plan", {})
    with st.container():
        st.markdown('<div class="soap-section">', unsafe_allow_html=True)
        st.subheader("P - Plan")

        st.markdown(f"**Treatment:** {', '.join(plan.get('treatment', [])) or '-'}")
        st.markdown(f"**Medications:** {', '.join(plan.get('medications', [])) or '-'}")
        st.markdown(f"**Follow-up:** {plan.get('follow_up', '-')}")

        edus = plan.get('patient_education', [])
        if edus:
            st.markdown("**Patient Education:**")
            for line in edus:
                st.write(f"- {line}")

        refs = plan.get('referrals', [])
        if refs:
            st.markdown(f"**Referrals:** {', '.join(refs)}")

        precs = plan.get('precautions', [])
        if precs:
            st.markdown("**Precautions:**")
            for line in precs:
                st.write(f"- {line}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Export as PDF", key="export_pdf"):
            st.info("PDF export would be implemented here")
    with col2:
        if st.button("📧 Email to Provider", key="email_provider"):
            st.info("Email functionality would be implemented here")
    with col3:
        soap_json = json.dumps(soap_note, indent=2)
        st.download_button(
            label="💾 Download JSON",
            data=soap_json,
            file_name=f"soap_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="download_json"
        )



def display_metrics(metrics: Dict):
    """Display quality metrics and performance indicators"""
    st.header("📈 Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Entity Coverage",
            f"{metrics['entity_coverage']:.1%}",
            help="Percentage of expected entities extracted"
        )
    
    with col2:
        st.metric(
            "Summary Completeness",
            f"{metrics['summary_completeness']:.1%}",
            help="How complete the medical summary is"
        )
    
    with col3:
        st.metric(
            "SOAP Completeness",
            f"{metrics['soap_completeness']:.1%}",
            help="Completeness of SOAP note sections"
        )
    
    with col4:
        st.metric(
            "Overall Confidence",
            f"{metrics['overall_confidence']:.1%}",
            help="Overall pipeline confidence"
        )
    
    st.subheader("Detailed Performance Analysis")
    
    categories = list(metrics.keys())
    values = list(metrics.values())
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Quality Metrics'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        title="Pipeline Performance Radar"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🔍 Performance Insights")
    
    insights = generate_performance_insights(metrics)
    
    for insight in insights:
        if insight["type"] == "success":
            st.success(f"✅ {insight['message']}")
        elif insight["type"] == "warning":
            st.warning(f"⚠️ {insight['message']}")
        else:
            st.info(f"ℹ️ {insight['message']}")
    
    st.subheader("💡 Recommendations")
    
    recommendations = generate_recommendations(metrics)
    for rec in recommendations:
        st.write(f"• {rec}")


def generate_performance_insights(metrics: Dict) -> List[Dict]:
    """Generate insights based on metrics"""
    insights = []
    
    if metrics['entity_coverage'] > 0.8:
        insights.append({
            "type": "success",
            "message": "Excellent entity extraction coverage - most medical entities were identified"
        })
    elif metrics['entity_coverage'] < 0.5:
        insights.append({
            "type": "warning",
            "message": "Low entity coverage - consider reviewing the conversation for missed medical terms"
        })
    
    if metrics['summary_completeness'] > 0.85:
        insights.append({
            "type": "success",
            "message": "Comprehensive medical summary generated with all key components"
        })
    
    if metrics['soap_completeness'] < 0.7:
        insights.append({
            "type": "warning",
            "message": "SOAP note may be incomplete - some sections need more information"
        })
    
    if metrics['overall_confidence'] > 0.8:
        insights.append({
            "type": "success",
            "message": "High confidence in analysis results - suitable for clinical review"
        })
    else:
        insights.append({
            "type": "info",
            "message": "Moderate confidence - human review recommended before clinical use"
        })
    
    return insights


def generate_recommendations(metrics: Dict) -> List[str]:
    """Generate recommendations based on metrics"""
    recommendations = []
    
    if metrics['entity_coverage'] < 0.7:
        recommendations.append("Consider using additional medical dictionaries or fine-tuning the NER model")
    
    if metrics['summary_completeness'] < 0.8:
        recommendations.append("Ensure the conversation includes all relevant medical history and current symptoms")
    
    if metrics['soap_completeness'] < 0.8:
        recommendations.append("Include more objective findings and specific treatment plans in the conversation")
    
    if metrics['overall_confidence'] < 0.75:
        recommendations.append("Review and validate the extracted information with a healthcare professional")
    
    recommendations.append("Regular model updates with domain-specific medical data can improve accuracy")
    
    return recommendations


if __name__ == "__main__":
    main()