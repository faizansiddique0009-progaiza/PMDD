import gradio as gr
import traceback
import json
from agents.agent1_preprocessor import run_agent1
from agents.agent2_pragmatic import run_agent2
from agents.agent3_semantic import run_agent3
from agents.agent4_statistics import run_agent4
from agents.agent5_orchestrator import run_orchestrator, save_report
from utils.helpers import get_sections_from_segments

def analyze_corpus(file_obj, text_input, corpus_name, keywords_input):
    if not file_obj and (not text_input or not text_input.strip()):
        yield [gr.update(value="Error: Please upload a file or paste text.")] + [gr.update()] * 10
        return
        
    if not keywords_input or not keywords_input.strip():
        yield [gr.update(value="Error: Please provide target keywords.")] + [gr.update()] * 10
        return
        
    keywords_list = [k.strip() for k in keywords_input.split(',')]
    
    try:
        # Agent 1
        source_name = file_obj.name if file_obj else "Pasted Text"
        yield [gr.update(value=f"Starting PMDD Pipeline...\n[Agent 1] Processing source: {source_name}\n")] + [gr.update()] * 10
        
        if file_obj:
            a1_out = run_agent1(file_path=file_obj.name)
        else:
            a1_out = run_agent1(raw_text=text_input.strip())
            
        stats = a1_out.get('corpus_stats', {})
        segments = a1_out.get('segments', [])
        
        if not segments:
            raise ValueError("Agent 1 returned no text segments. Check your file.")
            
        section_labels = get_sections_from_segments(segments)
        a1_display = f"Total Segments: {stats.get('total_segments', 0)}\nSections Detected: {stats.get('sections_detected', 0)}\nTypes: {stats.get('total_types', 0)}\nTokens: {stats.get('total_tokens', 0)}\nTTR: {stats.get('ttr', 0)}"
        
        yield [gr.update(value="[Agent 1] Complete. Starting Agent 2..."), gr.update(value=a1_display)] + [gr.update()] * 9
        
        # Agent 2
        a2_out = run_agent2(segments)
        a2_display = json.dumps([{'id': s['id'], 'speech_act': s.get('speech_act'), 'subtype': s.get('speech_act_subtype'), 'politeness': s.get('politeness_score')} for s in a2_out[:5]], indent=2) + "\n... (truncated for display)"
        
        yield [gr.update(value="[Agent 2] Complete. Starting Agent 3..."), gr.update(), gr.update(value=a2_display)] + [gr.update()] * 8
        
        # Agent 3
        a3_out = run_agent3(a2_out, keywords_list, section_labels)
        a3_display = json.dumps(a3_out, indent=2)
        
        yield [gr.update(value="[Agent 3] Complete. Starting Agent 4..."), gr.update(), gr.update(), gr.update(value=a3_display)] + [gr.update()] * 7
        
        # Agent 4
        a4_out = run_agent4(a2_out, keywords_list)
        a4_display = a4_out.get('interpretation', json.dumps(a4_out, indent=2))
        
        yield [gr.update(value="[Agent 4] Complete. Starting Agent 5..."), gr.update(), gr.update(), gr.update(), gr.update(value=a4_display)] + [gr.update()] * 6
        
        # Agent 5
        a5_out = run_orchestrator(a1_out, a2_out, a3_out, a4_out)
        
        if 'error' in a5_out and a5_out['error']:
            yield [gr.update(value=f"[Agent 5] Error: {a5_out['error']}")] + [gr.update()] * 10
            return
            
        report_path = save_report(a5_out)
        final_report = a5_out.get('report', 'No report available.')
        drift_score_str = f"Overall Drift Score: {a5_out.get('drift_score', 0)}/100"
        
        yield [gr.update(value=f"Pipeline Finished! Report saved at: {report_path}"), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(value=final_report), gr.update(value=drift_score_str), a1_out, a2_out, keywords_list, section_labels]
        
    except Exception as e:
        error_msg = f"An exception occurred:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        yield [gr.update(value=error_msg)] + [gr.update()] * 10

def rerun_a2(a1_out, keywords_list, section_labels, feedback):
    if not a1_out: return [gr.update(value="Run full pipeline first.")] + [gr.update()]*5
    try:
        segments = a1_out.get('segments', [])
        a2_out = run_agent2(segments, feedback=feedback)
        a2_display = json.dumps([{'id': s['id'], 'speech_act': s.get('speech_act'), 'subtype': s.get('speech_act_subtype'), 'politeness': s.get('politeness_score')} for s in a2_out[:5]], indent=2) + "\n... (truncated for display)"
        
        a3_out = run_agent3(a2_out, keywords_list, section_labels)
        a3_display = json.dumps(a3_out, indent=2)
        
        a4_out = run_agent4(a2_out, keywords_list)
        a4_display = a4_out.get('interpretation', json.dumps(a4_out, indent=2))
        
        a5_out = run_orchestrator(a1_out, a2_out, a3_out, a4_out)
        final_report = a5_out.get('report', 'No report available.')
        drift_score_str = f"Overall Drift Score: {a5_out.get('drift_score', 0)}/100"
        
        return [gr.update(value=a2_display), gr.update(value=a3_display), gr.update(value=a4_display), gr.update(value=final_report), gr.update(value=drift_score_str), a2_out]
    except Exception as e:
        return [gr.update(value=f"Error: {e}")] + [gr.update()]*5

def rerun_a3(a1_out, a2_out, keywords_list, section_labels, feedback):
    if not a2_out: return [gr.update(value="Run full pipeline first.")] + [gr.update()]*4
    try:
        a3_out = run_agent3(a2_out, keywords_list, section_labels, feedback=feedback)
        a3_display = json.dumps(a3_out, indent=2)
        
        # A4 does not depend on A3, so we can just re-run A4 without feedback or just reuse state.
        # But we don't have A4 state saved explicitly to reuse easily without refactoring states again, 
        # so let's just re-run A4 quickly or we should save A4 state too.
        a4_out = run_agent4(a2_out, keywords_list)
        a4_display = a4_out.get('interpretation', json.dumps(a4_out, indent=2))

        a5_out = run_orchestrator(a1_out, a2_out, a3_out, a4_out)
        final_report = a5_out.get('report', 'No report available.')
        drift_score_str = f"Overall Drift Score: {a5_out.get('drift_score', 0)}/100"
        
        return [gr.update(value=a3_display), gr.update(value=a4_display), gr.update(value=final_report), gr.update(value=drift_score_str)]
    except Exception as e:
        return [gr.update(value=f"Error: {e}")] + [gr.update()]*3

def rerun_a4(a1_out, a2_out, keywords_list, section_labels, feedback):
    if not a2_out: return [gr.update(value="Run full pipeline first.")] + [gr.update()]*3
    try:
        a3_out = run_agent3(a2_out, keywords_list, section_labels)
        a4_out = run_agent4(a2_out, keywords_list, feedback=feedback)
        a4_display = a4_out.get('interpretation', json.dumps(a4_out, indent=2))
        
        a5_out = run_orchestrator(a1_out, a2_out, a3_out, a4_out)
        final_report = a5_out.get('report', 'No report available.')
        drift_score_str = f"Overall Drift Score: {a5_out.get('drift_score', 0)}/100"
        
        return [gr.update(value=a4_display), gr.update(value=final_report), gr.update(value=drift_score_str)]
    except Exception as e:
        return [gr.update(value=f"Error: {e}")] + [gr.update()]*2

title = 'PMDD — Pragmatic Meaning Drift Detector'
description = 'Upload a text corpus and receive a full academic linguistic report.\nFive AI agents analyse pragmatic drift, semantic field shifts, register changes, and corpus statistics.'

with gr.Blocks(title=title) as demo:
    state_a1 = gr.State()
    state_a2 = gr.State()
    state_kw = gr.State()
    state_sec = gr.State()

    gr.Markdown(f"<h1 style='text-align: center; color: #2C3E50;'>{title}</h1>")
    gr.Markdown(f"<p style='text-align: center; font-size: 1.1em; color: #34495E;'>{description}</p>")
    
    with gr.Row():
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### 📥 Step 1: Input Corpus")
            file_input = gr.File(label="Option 1: Upload File (.txt, .pdf, .csv, .json, .docx)")
            text_input = gr.Textbox(label="Option 2: Paste Text Directly", lines=5, placeholder="Paste your text corpus here...")
            corpus_name_input = gr.Textbox(label="Corpus Name (Optional)", placeholder="e.g. pakistan_press_2024")
            keywords_input = gr.Textbox(label="Target Keywords (Comma-separated, Required)", placeholder="e.g. democracy, power, people")
            run_btn = gr.Button("🚀 Start Automatic PMDD Analysis Pipeline", variant="primary", size="lg")
            progress_log = gr.Textbox(label="Pipeline Status", lines=2, interactive=False)
            
    with gr.Accordion("Agent 1: Corpus Preprocessor", open=True):
        a1_disp = gr.Textbox(label="Agent 1 Statistics", interactive=False)
        
    with gr.Accordion("Agent 2: Pragmatic Analyzer", open=True):
        a2_disp = gr.Textbox(label="Speech Acts & Politeness (Sample)", interactive=False, lines=6)
        with gr.Row():
            a2_rating = gr.Radio(choices=["1", "2", "3", "4", "5"], label="Rate Agent 2", value="3")
            a2_feedback = gr.Textbox(label="Feedback for Agent 2", placeholder="e.g. Classify more statements as directives.")
            a2_rerun = gr.Button("Re-run Agent 2")
            
    with gr.Accordion("Agent 3: Semantic & Register Detector", open=True):
        a3_disp = gr.Textbox(label="Semantic Fields & Register", interactive=False, lines=6)
        with gr.Row():
            a3_rating = gr.Radio(choices=["1", "2", "3", "4", "5"], label="Rate Agent 3", value="3")
            a3_feedback = gr.Textbox(label="Feedback for Agent 3", placeholder="e.g. Pay more attention to the solidarity field.")
            a3_rerun = gr.Button("Re-run Agent 3")

    with gr.Accordion("Agent 4: Corpus Statistician", open=True):
        a4_disp = gr.Textbox(label="Statistical Interpretation", interactive=False, lines=6)
        with gr.Row():
            a4_rating = gr.Radio(choices=["1", "2", "3", "4", "5"], label="Rate Agent 4", value="3")
            a4_feedback = gr.Textbox(label="Feedback for Agent 4 Interpretation", placeholder="e.g. Explain MI scores more simply.")
            a4_rerun = gr.Button("Re-run Agent 4")

    with gr.Accordion("Agent 5: Orchestrator & Final Report", open=True):
        drift_score_summary = gr.Textbox(label="Final Drift Score", lines=1, interactive=False)
        full_report = gr.Textbox(label="Report Output", lines=30, interactive=False)

    run_btn.click(
        fn=analyze_corpus,
        inputs=[file_input, text_input, corpus_name_input, keywords_input],
        outputs=[progress_log, a1_disp, a2_disp, a3_disp, a4_disp, full_report, drift_score_summary, state_a1, state_a2, state_kw, state_sec]
    )
    
    a2_rerun.click(
        fn=rerun_a2,
        inputs=[state_a1, state_kw, state_sec, a2_feedback],
        outputs=[a2_disp, a3_disp, a4_disp, full_report, drift_score_summary, state_a2]
    )

    a3_rerun.click(
        fn=rerun_a3,
        inputs=[state_a1, state_a2, state_kw, state_sec, a3_feedback],
        outputs=[a3_disp, a4_disp, full_report, drift_score_summary]
    )
    
    a4_rerun.click(
        fn=rerun_a4,
        inputs=[state_a1, state_a2, state_kw, state_sec, a4_feedback],
        outputs=[a4_disp, full_report, drift_score_summary]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_port=7861, theme=gr.themes.Soft())
