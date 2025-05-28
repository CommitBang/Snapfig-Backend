# figure_summarizer.py
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import torch
from typing import List, Optional
import os # For environment variables and path joining
import uuid # For unique temporary file names (if you were saving images here)

# --- Model and Processor Loading ---
MODEL_ID = "microsoft/Florence-2-base-ft"
PROCESSOR = None
MODEL = None
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Read the GPU_PROFILE environment variable. Default to "4060" (memory-constrained) if not set.
# Users can set this to "3090" for higher VRAM GPUs.
GPU_PROFILE = os.environ.get("GPU_PROFILE", "4060").upper()

def load_model_and_processor():
    """Loads the Florence-2 model and processor based on the GPU_PROFILE."""
    global PROCESSOR, MODEL
    if PROCESSOR is None or MODEL is None:
        print(f"Loading figure summarization model: {MODEL_ID}")
        print(f"Targeting GPU_PROFILE: {GPU_PROFILE} on DEVICE: {DEVICE}")
        
        load_kwargs = {"trust_remote_code": True}

        if DEVICE == "cuda":
            if GPU_PROFILE == "3090":
                print("Applying RTX 3090 (high VRAM) profile: Using float16.")
                load_kwargs["torch_dtype"] = torch.float16 # Use float16 for good performance
            elif GPU_PROFILE == "4060":
                print("Applying RTX 4060 (memory-constrained) profile: Using 8-bit quantization.")
                load_kwargs["load_in_8bit"] = True # Use 8-bit to reduce VRAM usage
            else:
                # Default for an unrecognized CUDA profile or if user sets something else
                print(f"Warning: Unrecognized GPU_PROFILE '{GPU_PROFILE}' for CUDA. Defaulting to RTX 4060 (8-bit) profile.")
                load_kwargs["load_in_8bit"] = True
            load_kwargs["device_map"] = "auto" # Handles device placement for CUDA
        else: # CPU
            print("Applying CPU profile.")
            # No quantization like load_in_8bit for CPU by default here, as its benefits/support vary.
            # device_map="auto" would also map to CPU if DEVICE is "cpu".
            load_kwargs["device_map"] = DEVICE


        MODEL = AutoModelForCausalLM.from_pretrained(MODEL_ID, **load_kwargs)
        PROCESSOR = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        
        # Ensure model is on the correct device if not using device_map="auto" effectively for CPU
        if DEVICE == "cpu" and "device_map" not in load_kwargs: # Or if device_map was not "auto" or DEVICE
             MODEL.to(DEVICE)

        model_dtype_info = str(MODEL.dtype) if hasattr(MODEL, 'dtype') else "N/A (could be mixed if quantized)"
        print(f"Figure summarization model and processor loaded. Effective model dtype on device: {model_dtype_info}.")

# The rest of the `summarize_figure_with_ocr` function remains the same as before.
# It is independent of how the model was loaded, as long as it's loaded.
def summarize_figure_with_ocr(
    image_path: str,
    ocr_texts: Optional[List[str]] = None,
    base_prompt: str = "<MORE_DETAILED_CAPTION>"
) -> str:
    """
    Generates a detailed caption (summary) for the given image using Florence-2,
    optionally incorporating provided OCR text into the prompt.
    """
    global PROCESSOR, MODEL

    if PROCESSOR is None or MODEL is None:
        print("Figure summarization model not pre-loaded by app. Loading now (this might be slow for a request)...")
        load_model_and_processor()

    try:
        image = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        return "Error: Image file not found at path."
    except Exception as e:
        return f"Error: Could not open image from path. {e}"

    full_prompt = base_prompt
    if ocr_texts and len(ocr_texts) > 0:
        concatenated_ocr_text = " ".join(ocr_texts)
        max_ocr_text_len = 500
        if len(concatenated_ocr_text) > max_ocr_text_len:
            concatenated_ocr_text = concatenated_ocr_text[:max_ocr_text_len] + "..."
        ocr_context_prompt = f" The figure contains the following text elements: \"{concatenated_ocr_text}\"."
        full_prompt += ocr_context_prompt
    
    inputs = PROCESSOR(text=full_prompt, images=image, return_tensors="pt")
    model_device = next(MODEL.parameters()).device
    inputs = inputs.to(model_device)

    # For quantized models (like 8-bit), the model often expects float16 or bfloat16 for inputs
    # even if its weights are int8. The .to(model_device) should handle this,
    # but sometimes explicit casting is needed if errors occur.
    # on lab's 3090, if an error on dtype occurs, refer to either one of the examples written below
    if 'pixel_values' in inputs:
        # --- EXPLICIT CASTING EXAMPLE ---
        # If you encounter a dtype error for pixel_values, you might need to cast it explicitly.
        # Choose the dtype based on what the error message suggests or what the model expects.
        # Common choices for GPU operations are torch.float16 or torch.bfloat16.

        # Example 1: Casting to float16
        # This is often a good choice for NVIDIA GPUs if the model supports/expects it.
        try:
            expected_dtype = torch.float16 # Or torch.bfloat16, or model.dtype if that's appropriate
            if inputs['pixel_values'].dtype != expected_dtype:
                print(f"Explicitly casting pixel_values from {inputs['pixel_values'].dtype} to {expected_dtype}")
                inputs['pixel_values'] = inputs['pixel_values'].to(dtype=expected_dtype)
        except Exception as e:
            print(f"Warning: Failed to explicitly cast pixel_values. Error: {e}")
            # Fallback or re-raise error depending on how critical this is

        # Example 2: Casting to the model's own advertised dtype (if weights are not int8)
        # This might be useful if the model isn't quantized to int8 but is, say, a float16 model.
        # If MODEL.dtype is something like torch.int8 (for quantized models),
        # this might not be what you want for the input pixel_values,
        # as inputs are usually float16/bfloat16/float32.
        # if hasattr(MODEL, 'dtype') and MODEL.dtype != torch.int8: # Avoid casting to int8 for inputs
        #     if inputs['pixel_values'].dtype != MODEL.dtype:
        #         print(f"Explicitly casting pixel_values to model's dtype: {MODEL.dtype}")
        #         inputs['pixel_values'] = inputs['pixel_values'].to(dtype=MODEL.dtype)
        
        # --- END OF EXPLICIT CASTING EXAMPLE ---

    try:
        generated_ids = MODEL.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=512,
            num_beams=3,
            early_stopping=True
        )
        summary = PROCESSOR.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return summary
    except Exception as e:
        return f"Error during figure summarization model inference: {str(e)}"