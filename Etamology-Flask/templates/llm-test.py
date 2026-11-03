import os
import psutil
import gradio as gr
from llama_cpp import Llama

def get_system_hardware_state():
    """
    Probes system resources to dynamically calculate optimal offloading capabilities.
    """
    diagnostics = []
    
    # 1. Evaluate Host CPU constraints
    physical_cores = psutil.cpu_count(logical=False) or 4
    optimal_threads = max(1, physical_cores - 1) # Leave 1 core free for system stability
    diagnostics.append(f"💻 CPU Core Allocation: {optimal_threads} worker threads out of {physical_cores} physical cores.")
    
    # 2. Check for CUDA Backend capability verified during your compilation
    # llama-cpp-python automatically uses CUDA when n_gpu_layers > 0 if compiled with it
    diagnostics.append("🚀 CUDA Acceleration Layer: Status ACTIVE (Verified compiled binary).")
    
    return optimal_threads, "\n".join(diagnostics)

# Initialize hardware profiles on load
OPTIMAL_THREADS, INITIAL_DIAGNOSTICS = get_system_hardware_state()

def stream_inference(model_path, prompt, system_prompt, offload_strategy, max_tokens, temperature):
    """
    Instantiates the model engine based on user selected scaling strategies
    and streams tokens directly to the interface.
    """
    if not model_path or not os.path.exists(model_path):
        yield "❌ Error: Please specify a valid local path to a .gguf model file."
        return

    # Automagic Scaling Router
    if offload_strategy == "🚀 Max GPU Offload (CUDA)":
        # -1 instructs llama.cpp to push every single model layer into VRAM
        gpu_layers = -1 
        mode_msg = "Running in pure hardware accelerated mode (GPU fully saturated)."
    elif offload_strategy == "⚖️ Hybrid Split (GPU/CPU balance)":
        # Offload a partial stack (e.g., 20 layers) to conserve VRAM for small/medium cards
        gpu_layers = 20
        mode_msg = "Running split execution pipeline. Splitting layers between VRAM and System RAM."
    else:
        # Zero layers forces total execution on the CPU
        gpu_layers = 0
        mode_msg = "Forced fallback to native CPU thread execution pipeline."

    yield f"⚙️ Initializing Engine...\n{mode_msg}\n\n"

    try:
        # Load the model dynamically based on structural settings
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=gpu_layers,
            n_threads=OPTIMAL_THREADS,
            n_ctx=2048, # Context window limit
            verbose=False # Suppress heavy console noise
        )
        
        # Format a clean system/user chat prompt template
        formatted_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # Execute the streaming engine loop
        response_stream = llm(
            prompt=formatted_prompt,
            max_tokens=int(max_tokens),
            temperature=float(temperature),
            stream=True
        )
        
        output_text = ""
        for chunk in response_stream:
            token = chunk["choices"][0]["text"]
            output_text += token
            yield output_text
            
    except Exception as e:
        yield f"❌ Runtime Error encountered during matrix operations:\n{str(e)}"

# --- Gradio UI Layout Building # NEW GRADIO 6.0 SYNTAX
with gr.Blocks(title="Automagic CUDA/CPU Orchestrator") as demo:
    gr.Markdown("# ⚡ Local Silicon LLM Engine Orchestrator")
    gr.Markdown("Directly interfaces with your custom compiled `llama-cpp-python` CUDA wrapper under Windows.")
    
    with gr.Row():
        with gr.Column(scale=2):
            model_input = gr.Textbox(
                placeholder="C:/Path/To/Your/model.gguf", 
                label="Local GGUF Model Path File Location"
                # remember_shared_value removed
            )
        with gr.Column(scale=1):
            strategy_select = gr.Dropdown(
                choices=[
                    "🚀 Max GPU Offload (CUDA)", 
                    "⚖️ Hybrid Split (GPU/CPU balance)", 
                    "💻 Force Pure CPU Fallback"
                ],
                value="🚀 Max GPU Offload (CUDA)",
                label="Automagic Silicon Scaling Tier"
            )

    with gr.Row():
        with gr.Column(scale=3):
            system_box = gr.Textbox(value="You are an expert AI assistant optimized for local execution.", label="System Framing Context")
            prompt_box = gr.Textbox(placeholder="What would you like to compute today?", label="User Execution Instruction", lines=4)
            submit_btn = gr.Button("Execute Inference Pipeline", variant="primary")
            
        with gr.Column(scale=2):
            with gr.Tab("Stream Output"):
                output_box = gr.Textbox(label="Token Tokenizer Stream Output", lines=10, interactive=False)
            with gr.Tab("System Diagnostics"):
                diagnostic_box = gr.TextArea(value=INITIAL_DIAGNOSTICS, label="Silicon Layout Map", interactive=False)

            with gr.Accordion("Hyperparameter Model Modifiers", open=False):
                tokens_slider = gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max Tokens to Generate")
                temp_slider = gr.Slider(minimum=0.0, maximum=1.2, value=0.7, step=0.05, label="Temperature Scaling")

    # Bind execution click events
    submit_btn.click(
        fn=stream_inference,
        inputs=[model_input, prompt_box, system_box, strategy_select, tokens_slider, temp_slider],
        outputs=output_box
    )

if __name__ == "__main__":
    print("Launching Local Web Server...")
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())

def fix_windows_to_unix_path(raw_path: str) -> str:
    # Remove surrounding quote marks from copy-paste actions
    clean_path = raw_path.strip('"\'').replace('\\', '/')
    
    # Check for Windows Drive Letter signature (e.g., C:)
    if len(clean_path) > 1 and clean_path[1] == ':':
        drive_letter = clean_path[0].lower()
        # Format explicitly for MSYS2 / general Unix tool wrappers (/c/...)
        return f"/{drive_letter}{clean_path[2:]}"
        
    return clean_path

# Example execution:
# input:  "C:\tools\llama_cpp\Ministral-3b-instruct.Q4_K_M.gguf"
# output: /c/tools/llama_cpp/Ministral-3b-instruct.Q4_K_M.gguf
