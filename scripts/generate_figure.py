#!/usr/bin/env python3
"""
Scientific Figure Generation Script

Self-contained module for generating publication-ready scientific figures
using matplotlib, seaborn, and optional TikZ conversion.

Usage:
    python generate_figure.py training --output training_curves.pdf
    python generate_figure.py comparison --data results.json --tikz
    python generate_figure.py custom --script my_plot.py

Contract:
    Input: Figure type + data + configuration
    Output: Publication-ready figure (PDF/PNG/TikZ)
    Side Effects: Creates figure files

Dependencies:
    - matplotlib
    - numpy
    - seaborn (optional, for statistical plots)
    - scienceplots (optional, recommended)
    - tikzplotlib (optional, for TikZ export)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes

# Optional imports with availability flags
HAS_SCIENCEPLOTS = False
HAS_SEABORN = False
HAS_TIKZPLOTLIB = False

try:
    import scienceplots  # type: ignore  # noqa: F401

    HAS_SCIENCEPLOTS = True
except ImportError:
    HAS_SCIENCEPLOTS = False

try:
    import seaborn as sns  # type: ignore

    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    sns = None  # type: ignore

try:
    import tikzplotlib  # type: ignore

    HAS_TIKZPLOTLIB = True
except ImportError:
    HAS_TIKZPLOTLIB = False
    tikzplotlib = None  # type: ignore


class FigureGenerator:
    """
    Generates publication-ready scientific figures.

    Attributes:
        style: Matplotlib style to use (default: 'science,ieee')
        dpi: Resolution for raster output (default: 300)
        figsize: Figure size in inches (width, height)
    """

    # Conference-specific figure sizes (width, height in inches)
    CONFERENCE_SIZES = {
        "neurips": (5.5, 3.5),  # Single column, full width
        "icml": (3.25, 2.5),  # Two-column, single column width
        "icml-wide": (6.75, 3.0),  # Two-column, full width
        "acl": (3.33, 2.5),  # Two-column, single column
        "ieee": (3.5, 2.5),  # Two-column, single column
        "acm": (3.33, 2.5),  # Two-column, single column
        "arxiv": (5.5, 3.5),  # Flexible
    }

    def __init__(
        self,
        style: str = "science,ieee",
        dpi: int = 300,
        figsize: Optional[Tuple[float, float]] = None,
    ):
        """
        Initialize figure generator.

        Args:
            style: Matplotlib style (comma-separated for multiple)
            dpi: Resolution for output
            figsize: Figure size (width, height) in inches
        """
        self.dpi = dpi
        self.figsize = figsize or (3.5, 2.5)

        # Apply style if available
        if HAS_SCIENCEPLOTS:
            plt.style.use(style.split(","))
        else:
            print("⚠️ scienceplots not available - using default matplotlib style")

        # Configure defaults
        plt.rcParams.update(
            {
                "font.size": 10,
                "axes.labelsize": 10,
                "axes.titlesize": 10,
                "xtick.labelsize": 9,
                "ytick.labelsize": 9,
                "legend.fontsize": 9,
                "figure.dpi": dpi,
                "savefig.dpi": dpi,
                "savefig.bbox": "tight",
                "savefig.pad_inches": 0.05,
            }
        )

    def training_curves(
        self,
        epochs: np.ndarray,
        train_loss: np.ndarray,
        val_loss: np.ndarray,
        train_std: Optional[np.ndarray] = None,
        val_std: Optional[np.ndarray] = None,
    ) -> Tuple[Figure, Axes]:
        """
        Generate training curves with optional error regions.

        Args:
            epochs: Array of epoch numbers
            train_loss: Training loss per epoch
            val_loss: Validation loss per epoch
            train_std: Optional training loss std dev
            val_std: Optional validation loss std dev

        Returns:
            (fig, ax) tuple
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Plot lines
        ax.plot(
            epochs,
            train_loss,
            label="Training",
            linewidth=1.5,
            color="#1f77b4",
            alpha=0.9,
        )
        ax.plot(
            epochs,
            val_loss,
            label="Validation",
            linewidth=1.5,
            color="#ff7f0e",
            alpha=0.9,
        )

        # Add error regions if provided
        if train_std is not None:
            ax.fill_between(
                epochs,
                train_loss - train_std,
                train_loss + train_std,
                alpha=0.2,
                color="#1f77b4",
            )
        if val_std is not None:
            ax.fill_between(
                epochs,
                val_loss - val_std,
                val_loss + val_std,
                alpha=0.2,
                color="#ff7f0e",
            )

        # Mark best validation point
        best_idx = np.argmin(val_loss)
        ax.scatter(
            epochs[best_idx],
            val_loss[best_idx],
            s=50,
            color="red",
            zorder=5,
            marker="*",
        )

        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Training Progress")
        ax.legend(frameon=True, loc="upper right")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def comparison_bars(
        self,
        model_names: List[str],
        accuracies: List[float],
        std_devs: Optional[List[float]] = None,
    ) -> Tuple[Figure, Axes]:
        """
        Generate model comparison bar chart.

        Args:
            model_names: List of model names
            accuracies: Accuracy for each model
            std_devs: Optional standard deviations

        Returns:
            (fig, ax) tuple
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        x = np.arange(len(model_names))
        width = 0.6
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

        # Create bars
        yerr = std_devs if std_devs else None
        bars = ax.bar(
            x,
            accuracies,
            width,
            yerr=yerr,
            color=colors[: len(model_names)],
            alpha=0.8,
            capsize=5,
            ecolor="black",
            error_kw={"linewidth": 1, "elinewidth": 1},
        )

        # Add value labels
        for i, (bar, acc) in enumerate(zip(bars, accuracies)):
            height = bar.get_height()
            offset = std_devs[i] if std_devs else 0
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + offset + max(accuracies) * 0.02,
                f"{acc:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        # Highlight best
        best_idx = np.argmax(accuracies)
        bars[best_idx].set_edgecolor("red")
        bars[best_idx].set_linewidth(2)

        ax.set_ylabel("Accuracy (%)")
        ax.set_title("Model Performance Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=15, ha="right")
        ax.set_ylim(0, max(accuracies) * 1.15)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def confusion_matrix(
        self, cm: np.ndarray, class_names: List[str], normalize: bool = True
    ) -> Tuple[Figure, Axes]:
        """
        Generate confusion matrix heatmap.

        Args:
            cm: Confusion matrix (2D array)
            class_names: List of class names
            normalize: Whether to normalize by row

        Returns:
            (fig, ax) tuple
        """
        if not HAS_SEABORN or sns is None:
            raise ImportError(
                "seaborn required for confusion matrix. Install: pip install seaborn"
            )

        fig, ax = plt.subplots(figsize=(4, 3.5))

        if normalize:
            cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
            fmt = ".2f"
            vmax = 1.0
        else:
            cm_normalized = cm
            fmt = "d"
            vmax = cm.max()

        # Create heatmap
        sns.heatmap(
            cm_normalized,
            annot=True,
            fmt=fmt,
            cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names,
            cbar_kws={"label": "Proportion" if normalize else "Count"},
            vmin=0,
            vmax=vmax,
            ax=ax,
            linewidths=0.5,
            linecolor="gray",
        )

        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")
        ax.set_title("Confusion Matrix")

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.setp(ax.get_yticklabels(), rotation=0)

        plt.tight_layout()
        return fig, ax

    def embeddings_2d(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray,
        title: str = "t-SNE Visualization",
    ) -> Tuple[Figure, Axes]:
        """
        Plot 2D embeddings colored by class.

        Args:
            embeddings: 2D array (n_samples x 2)
            labels: Class labels (n_samples,)
            title: Plot title

        Returns:
            (fig, ax) tuple
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        unique_labels = np.unique(labels)
        cmap = plt.colormaps.get_cmap("tab10")
        colors = cmap(np.linspace(0, 1, len(unique_labels)))

        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax.scatter(
                embeddings[mask, 0],
                embeddings[mask, 1],
                c=[colors[i]],
                label=f"Class {label}",
                alpha=0.6,
                s=20,
                edgecolors="none",
            )

        ax.set_xlabel("Dimension 1")
        ax.set_ylabel("Dimension 2")
        ax.set_title(title)
        ax.legend(frameon=True, loc="best", markerscale=1.5)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig, ax

    def save(
        self,
        fig: Figure,
        output_path: Path,
        tikz: bool = False,
        tikz_path: Optional[Path] = None,
    ):
        """
        Save figure to file with optional TikZ export.

        Args:
            fig: Matplotlib figure to save
            output_path: Output file path (PDF/PNG)
            tikz: Whether to also export TikZ
            tikz_path: Optional TikZ output path (default: replace extension with .tex)

        Raises:
            ImportError: If tikz=True but tikzplotlib not available
        """
        # Save matplotlib version
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        print(f"✅ Saved figure to {output_path}")

        # Save TikZ version if requested
        if tikz:
            if not HAS_TIKZPLOTLIB or tikzplotlib is None:
                raise ImportError(
                    "tikzplotlib required for TikZ export. Install: pip install tikzplotlib"
                )

            tikz_output = tikz_path or output_path.with_suffix(".tex")
            tikzplotlib.save(
                tikz_output,
                axis_width=f"{self.figsize[0]}in",
                axis_height=f"{self.figsize[1]}in",
                externalize_tables=True,
                override_externals=True,
            )
            print(f"✅ Saved TikZ to {tikz_output}")


def load_data_from_json(json_path: Path) -> Dict[str, Any]:
    """
    Load figure data from JSON file.

    Args:
        json_path: Path to JSON data file

    Returns:
        Dictionary with figure data

    Example JSON format:
        {
            "type": "training",
            "epochs": [1, 2, 3, ...],
            "train_loss": [2.0, 1.5, 1.2, ...],
            "val_loss": [2.2, 1.6, 1.3, ...]
        }
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # Convert lists to numpy arrays
    for key, value in data.items():
        if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
            data[key] = np.array(value)

    return data


def generate_demo_training_data() -> Dict[str, np.ndarray]:
    """Generate synthetic training data for demonstration."""
    epochs = np.arange(1, 101)
    train_loss = 2.0 * np.exp(-epochs / 30) + 0.1
    val_loss = 2.2 * np.exp(-epochs / 30) + 0.15 + 0.05 * np.sin(epochs / 5)
    train_std = 0.1 * np.exp(-epochs / 40)
    val_std = 0.12 * np.exp(-epochs / 40)

    return {
        "epochs": epochs,
        "train_loss": train_loss,
        "val_loss": val_loss,
        "train_std": train_std,
        "val_std": val_std,
    }


def generate_demo_comparison_data() -> Tuple[List[str], List[float], List[float]]:
    """Generate synthetic comparison data for demonstration."""
    models = ["Baseline", "CNN", "ResNet", "Transformer", "Ours"]
    accuracies = [75.2, 82.4, 87.1, 89.3, 91.7]
    std_devs = [1.2, 0.9, 1.1, 0.8, 0.7]
    return models, accuracies, std_devs


def generate_demo_confusion_matrix() -> Tuple[np.ndarray, List[str]]:
    """Generate synthetic confusion matrix for demonstration."""
    cm = np.array([[45, 3, 2], [2, 48, 0], [1, 1, 48]])
    classes = ["Class A", "Class B", "Class C"]
    return cm, classes


def main():
    """Command-line interface for figure generation."""
    parser = argparse.ArgumentParser(
        description="Generate publication-ready scientific figures"
    )

    parser.add_argument(
        "figure_type",
        choices=["training", "comparison", "confusion", "embeddings", "custom", "demo"],
        help="Type of figure to generate",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("figure.pdf"),
        help="Output file path (default: figure.pdf)",
    )

    parser.add_argument(
        "-d", "--data", type=Path, help="JSON file with figure data (optional)"
    )

    parser.add_argument(
        "-s",
        "--style",
        default="science,ieee",
        help="Matplotlib style (default: science,ieee)",
    )

    parser.add_argument(
        "-c",
        "--conference",
        choices=["neurips", "icml", "icml-wide", "acl", "ieee", "acm", "arxiv"],
        help="Conference format (sets appropriate figure size)",
    )

    parser.add_argument(
        "--tikz", action="store_true", help="Also export as TikZ (.tex file)"
    )

    parser.add_argument(
        "--script", type=Path, help="Custom Python script for 'custom' figure type"
    )

    parser.add_argument(
        "--dpi", type=int, default=300, help="Resolution (default: 300)"
    )

    args = parser.parse_args()

    # Determine figure size
    if args.conference:
        figsize = FigureGenerator.CONFERENCE_SIZES[args.conference]
    else:
        figsize = (3.5, 2.5)  # Default

    # Initialize generator
    try:
        generator = FigureGenerator(style=args.style, dpi=args.dpi, figsize=figsize)
    except Exception as e:
        print(f"❌ Error initializing generator: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate figure based on type
    try:
        if args.figure_type == "demo":
            # Generate all demo figures
            print("🎨 Generating demo figures...\n")

            # Training curves
            data = generate_demo_training_data()
            fig, ax = generator.training_curves(**data)
            demo_path = args.output.parent / "demo_training.pdf"
            generator.save(fig, demo_path, tikz=args.tikz)
            plt.close()

            # Comparison
            models, accs, stds = generate_demo_comparison_data()
            fig, ax = generator.comparison_bars(models, accs, stds)
            demo_path = args.output.parent / "demo_comparison.pdf"
            generator.save(fig, demo_path, tikz=args.tikz)
            plt.close()

            # Confusion matrix
            cm, classes = generate_demo_confusion_matrix()
            fig, ax = generator.confusion_matrix(cm, classes)
            demo_path = args.output.parent / "demo_confusion.pdf"
            generator.save(fig, demo_path, tikz=args.tikz)
            plt.close()

            print("\n✅ Generated 3 demo figures")

        elif args.figure_type == "training":
            # Load or generate training data
            if args.data:
                data = load_data_from_json(args.data)
            else:
                print("ℹ️ No data provided, generating demo data...")
                data = generate_demo_training_data()

            fig, ax = generator.training_curves(**data)
            generator.save(fig, args.output, tikz=args.tikz)

        elif args.figure_type == "comparison":
            if args.data:
                data = load_data_from_json(args.data)
                fig, ax = generator.comparison_bars(
                    data["models"], data["accuracies"], data.get("std_devs")
                )
            else:
                print("ℹ️ No data provided, generating demo data...")
                models, accs, stds = generate_demo_comparison_data()
                fig, ax = generator.comparison_bars(models, accs, stds)

            generator.save(fig, args.output, tikz=args.tikz)

        elif args.figure_type == "confusion":
            if args.data:
                data = load_data_from_json(args.data)
                fig, ax = generator.confusion_matrix(
                    np.array(data["matrix"]), data["classes"]
                )
            else:
                print("ℹ️ No data provided, generating demo data...")
                cm, classes = generate_demo_confusion_matrix()
                fig, ax = generator.confusion_matrix(cm, classes)

            generator.save(fig, args.output, tikz=args.tikz)

        elif args.figure_type == "embeddings":
            if not args.data:
                print(
                    "❌ Embeddings require --data with 'embeddings' and 'labels' arrays"
                )
                sys.exit(1)

            data = load_data_from_json(args.data)
            fig, ax = generator.embeddings_2d(
                np.array(data["embeddings"]), np.array(data["labels"])
            )
            generator.save(fig, args.output, tikz=args.tikz)

        elif args.figure_type == "custom":
            if not args.script:
                print("❌ Custom figures require --script path")
                sys.exit(1)

            # Execute custom script
            print(f"🔧 Running custom script: {args.script}")
            with open(args.script) as f:
                script_code = f.read()

            # Create namespace with generator
            namespace = {"generator": generator, "plt": plt, "np": np}
            exec(script_code, namespace)

            # Expect script to create 'fig' variable
            if "fig" not in namespace:
                print("❌ Custom script must create 'fig' variable")
                sys.exit(1)

            generator.save(namespace["fig"], args.output, tikz=args.tikz)

        else:
            print(f"❌ Unknown figure type: {args.figure_type}")
            sys.exit(1)

        print("\n✅ Figure generation complete")

    except ImportError as e:
        print(f"❌ Missing dependency: {e}", file=sys.stderr)
        print("\nInstall with: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating figure: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
