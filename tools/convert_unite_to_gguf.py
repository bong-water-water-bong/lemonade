#!/usr/bin/env python3
"""
Convert UNITE (UNIversal mulTimodal Embedder) models to GGUF format.

UNITE is a multimodal embedding model built on Qwen2-VL that produces
unified text/image/video embeddings.  This script downloads the HuggingFace
checkpoint, converts it to GGUF using llama.cpp's converter (which has been
patched to remap the custom "UniteQwen2VL" architecture to "qwen2vl"), and
extracts the vision projector (mmproj) file.

Usage:
  # Convert 2B variant (Q8_0 quant)
  python3 tools/convert_unite_to_gguf.py friedrichor/Unite-Base-Qwen2-VL-2B --outtype q8_0

  # Convert 7B variant (Q8_0 quant)
  python3 tools/convert_unite_to_gguf.py friedrichor/Unite-Base-Qwen2-VL-7B --outtype q8_0

  # Convert Instruct variant
  python3 tools/convert_unite_to_gguf.py friedrichor/Unite-Instruct-Qwen2-VL-2B --outtype q8_0
  python3 tools/convert_unite_to_gguf.py friedrichor/Unite-Instruct-Qwen2-VL-7B --outtype q8_0

Output:
  <model-name>-<ftype>.gguf       # Main model weights
  mmproj-<model-name>-f16.gguf    # Vision projector (for multimodal input)
"""

import argparse
import logging
import os
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("convert_unite")


def main():
    parser = argparse.ArgumentParser(description="Convert UNITE models to GGUF")
    parser.add_argument("model", type=str, help="HuggingFace model ID (e.g., friedrichor/Unite-Base-Qwen2-VL-2B)")
    parser.add_argument("--outtype", type=str, default="q8_0", choices=["f32", "f16", "bf16", "q8_0"],
                        help="Output quantization format (default: q8_0)")
    parser.add_argument("--llama-cpp-dir", type=str, default=None,
                        help="Path to llama.cpp root directory (default: auto-detect)")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Directory to write output files (default: current dir)")
    args = parser.parse_args()

    # Locate llama.cpp
    if args.llama_cpp_dir:
        llama_dir = Path(args.llama_cpp_dir)
    else:
        # Try common locations
        candidates = [
            Path(__file__).resolve().parent.parent.parent / "llama.cpp",   # sibling of lemonade/
            Path("/home/bcloud/llama.cpp"),
            Path.cwd() / "llama.cpp",
            Path.cwd().parent / "llama.cpp",
        ]
        llama_dir = None
        for c in candidates:
            if (c / "convert_hf_to_gguf.py").exists():
                llama_dir = c
                break
        if llama_dir is None:
            logger.error("Could not find llama.cpp directory. Use --llama-cpp-dir")
            sys.exit(1)

    converter = llama_dir / "convert_hf_to_gguf.py"
    if not converter.exists():
        logger.error(f"Converter not found at {converter}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Infer model name for output files
    model_name = args.model.replace("/", "-")
    gguf_name = f"{model_name}-{args.outtype}.gguf"
    gguf_path = output_dir / gguf_name

    mmproj_name = f"mmproj-{model_name}-f16.gguf"
    mmproj_path = output_dir / mmproj_name

    logger.info(f"Converting {args.model} → {gguf_path}")
    logger.info(f"  Using converter: {converter}")

    # Step 1: Convert the main model to GGUF
    # The converter will:
    #   - Download from HuggingFace (--remote flag)
    #   - Detect "UniteQwen2VL" architecture
    #   - Remap to "qwen2vl" (our patch in convert_hf_to_gguf.py)
    #   - Write the GGUF file
    cmd = [
        sys.executable, str(converter),
        "--remote", args.model,
        "--outtype", args.outtype,
        "--outfile", str(gguf_path),
    ]
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True)
    logger.info(f"✅ Model converted: {gguf_path}")

    # Step 2: Extract the vision projector (mmproj)
    # The visual encoder weights live inside the main safetensors under
    # "visual.*" keys.  For multimodal support, llama-server needs a
    # separate mmproj GGUF file containing just those visual weights.
    # If the converter didn't already produce one, extract it here.
    mmproj_auto = gguf_path.with_name(gguf_path.stem.replace(f"-{args.outtype}", "") + "-mmproj.gguf")
    if mmproj_auto.exists():
        shutil.move(str(mmproj_auto), str(mmproj_path))
        logger.info(f"✅ mmproj extracted: {mmproj_path}")
    elif (output_dir / f"mmproj-{model_name}-f16.gguf").exists():
        logger.info(f"✅ mmproj already present")
    else:
        # Try running converter with --mmproj flag for explicit extraction
        logger.info("Extracting mmproj (vision projector)...")
        mmproj_cmd = [
            sys.executable, str(converter),
            "--remote", args.model,
            "--outtype", "f16",
            "--mmproj",
            "--outfile", str(mmproj_path),
        ]
        try:
            subprocess.run(mmproj_cmd, check=True)
            logger.info(f"✅ mmproj extracted: {mmproj_path}")
        except subprocess.CalledProcessError:
            logger.warning("Could not auto-extract mmproj. "
                          "The model will work for text-only embeddings; "
                          "for image/video input, manually provide a mmproj file.")

    # Step 3: Verify
    gguf_size = gguf_path.stat().st_size
    logger.info(f"Done! Files in {output_dir}:")
    logger.info(f"  {gguf_name}  ({gguf_size / 1e9:.2f} GB)")
    if mmproj_path.exists():
        mmproj_size = mmproj_path.stat().st_size
        logger.info(f"  {mmproj_name}  ({mmproj_size / 1e6:.2f} MB)")

    logger.info("\nTo use with Lemonade, copy these files to the models cache and run:")
    logger.info(f"  lemonade pull {gguf_name}")
    logger.info(f"  lemonade run {gguf_name}")


if __name__ == "__main__":
    main()
