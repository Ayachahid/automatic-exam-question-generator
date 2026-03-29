import argparse
import sys
from pathlib import Path
from src.core.config import load_config
from src.core.logger import get_logger
from src.data.chunkers.registry import ChunkerFactory
from src.data.cleaner import TextCleaner
from src.data.loaders.registry import LoaderFactory

logger = get_logger("scripts.preprocess")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preprocess a document: load → clean → chunk → save",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input file (PDF, DOCX, TXT, PPTX) or a URL.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to save the cleaned text. Defaults to data/processed/<filename>.txt",
    )
    parser.add_argument(
        "--strategy",
        default=None,
        choices=["fixed_size", "sentence", "semantic", "hybrid"],
        help="Chunking strategy. Overrides config.yaml if provided.",
    )
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to the YAML config file.",
    )
    parser.add_argument(
        "--show-chunks",
        action="store_true",
        help="Print each chunk to stdout after processing.",
    )
    return parser.parse_args()


def resolve_output_path(input_path: str, output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg)
    stem = Path(input_path).stem if not input_path.startswith("http") else "web_content"
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{stem}_cleaned.txt"


def main() -> int:
    args = parse_args()

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return 1

    # Load document
    logger.info(f"Loading document: {args.input}")
    try:
        loader = LoaderFactory().get_loader(args.input)
        raw_text = loader.load(args.input)
        logger.info(f"Loaded {len(raw_text):,} characters")
    except Exception as e:
        logger.error(f"Failed to load document: {e}")
        return 1

    #  Clean text
    logger.info("Cleaning text...")
    cleaner = TextCleaner()
    clean_text = cleaner.clean(raw_text)
    logger.info(f"Cleaned text: {len(clean_text):,} characters")

    #  Chunk text
    strategy = args.strategy or config.chunker.strategy
    logger.info(f"Chunking with strategy: {strategy}")

    chunker = ChunkerFactory().get_chunker(
        chunker_name=strategy,
        chunk_size=config.chunker.chunk_size,
        overlap=config.chunker.overlap,
    )
    chunks = chunker.chunk(clean_text)
    logger.info(f"Produced {len(chunks)} chunks")

    #  Save cleaned text
    output_path = resolve_output_path(args.input, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clean_text, encoding="utf-8")
    logger.info(f"Cleaned text saved to: {output_path}")

    #  Optional: print chunks
    if args.show_chunks:
        print(f"\n{'='*60}")
        print(f"  {len(chunks)} chunks produced by [{strategy}]")
        print(f"{'='*60}")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n── Chunk {i}/{len(chunks)} ({len(chunk)} chars) ──")
            print(chunk[:300] + ("..." if len(chunk) > 300 else ""))

    #  Summary
    print("Preprocessing complete!")
    print(f"   Input     : {args.input}")
    print(f"   Output    : {output_path}")
    print(f"   Strategy  : {strategy}")
    print(f"   Chunks    : {len(chunks)}")
    print(f"   Characters: {len(clean_text):,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
