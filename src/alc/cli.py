"""Command-line interface for Adaptive Loudness Compensation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .core import adaptive_loudness_compensation
from .io import write_audio


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Apply adaptive loudness compensation to a WAV file.",
    )
    parser.add_argument("input", type=Path, help="Input WAV file path.")
    parser.add_argument(
        "--mastering-level",
        type=float,
        required=True,
        help="Mastering level in phon.",
    )
    parser.add_argument(
        "--listening-level",
        type=float,
        required=True,
        help="Listening level in phon.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for the compensated WAV file. Defaults to '<input>_alc.wav'.",
    )
    parser.add_argument(
        "--attenuated-output",
        type=Path,
        help="Optional path for the attenuated, non-compensated WAV file.",
    )
    parser.add_argument(
        "--frame-size",
        type=int,
        default=4096,
        help="Processing frame size.",
    )
    parser.add_argument(
        "--hop-size",
        type=int,
        default=2048,
        help="Frame hop size.",
    )
    parser.add_argument(
        "--shelf-crossover-hz",
        type=float,
        default=122.0552,
        help="Low-shelf crossover frequency in Hz.",
    )
    parser.add_argument(
        "--gain-adjustment-db",
        type=float,
        default=0.4851,
        help="Gain offset added to the compensation trace before filter design.",
    )
    return parser


def main() -> int:
    """Run the CLI entry point."""

    parser = build_parser()
    args = parser.parse_args()

    input_path: Path = args.input
    output_path = args.output or input_path.with_name(f"{input_path.stem}_alc.wav")

    result = adaptive_loudness_compensation(
        input_path,
        mastering_level=args.mastering_level,
        listening_level=args.listening_level,
        frame_size=args.frame_size,
        hop_size=args.hop_size,
        shelf_crossover_hz=args.shelf_crossover_hz,
        gain_adjustment_db=args.gain_adjustment_db,
    )

    write_audio(output_path, result.sample_rate, result.compensated)

    if args.attenuated_output is not None:
        write_audio(args.attenuated_output, result.sample_rate, result.attenuated)

    print(f"Wrote compensated output to {output_path}")
    if args.attenuated_output is not None:
        print(f"Wrote attenuated output to {args.attenuated_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
