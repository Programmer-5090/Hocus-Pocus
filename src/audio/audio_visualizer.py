"""
Audio Visualization Module - Professional Plotting and Analysis Display

This module provides comprehensive visualization capabilities for the Shazam clone
system, offering high-quality plotting functions for spectrograms, peak detection
results, and combined audio analysis visualizations.

Key Features:
- High-resolution spectrogram plotting with customizable colormaps
- Peak detection visualization with overlay capabilities
- Combined analysis plots for comprehensive audio inspection
- Professional styling with configurable parameters
- Export functionality for documentation and analysis

Dependencies:
- Matplotlib for plotting (configured with non-interactive backend)
- NumPy for numerical array handling

Author: Hocus Pocus Project
Version: 1.0
"""

import matplotlib
matplotlib.use('Agg')  # Configure non-interactive backend for server compatibility
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Optional


class AudioVisualizer:
    """
    Professional audio visualization system for spectrogram and peak analysis.
    
    This class provides high-quality plotting capabilities for visualizing
    audio analysis results, including spectrograms, constellation maps,
    and combined analysis views essential for audio fingerprinting systems.
    """
    
    @staticmethod
    def plot_spectrogram(spectrogram_db: np.ndarray, frequencies: np.ndarray, times: np.ndarray, 
                        title: str = "Audio Spectrogram", save_path: Optional[str] = None, 
                        show_plot: bool = False, figure_size: Tuple[int, int] = (12, 6)) -> None:
        """
        Generate high-quality spectrogram visualization with professional styling.
        
        This method creates a detailed time-frequency representation of the audio
        signal using a color-mapped plot that clearly shows spectral content
        distribution across time and frequency dimensions.
        
        Args:
            spectrogram_db: Magnitude spectrogram in decibel scale
            frequencies: Frequency bin centers in Hz
            times: Time frame centers in seconds
            title: Plot title for the visualization
            save_path: File path to save the plot (PNG format recommended)
            show_plot: Whether to display the plot interactively (not recommended for batch processing)
            figure_size: Plot dimensions as (width, height) in inches
        """
        plt.figure(figsize=figure_size)
        
        # Create high-quality spectrogram plot with smooth shading
        mesh_plot = plt.pcolormesh(times, frequencies, spectrogram_db, 
                                  shading="gouraud", cmap="magma")
        
        # Add professional colorbar with clear labeling
        colorbar = plt.colorbar(mesh_plot, label="Magnitude (dB)")
        colorbar.ax.tick_params(labelsize=10)
        
        # Configure axes with proper labels and limits
        plt.ylabel("Frequency (Hz)", fontsize=12)
        plt.xlabel("Time (s)", fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylim(0, np.max(frequencies))
        
        # Apply professional styling
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot if path specified
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"Spectrogram saved to: {save_path}")
        
        # Display plot if requested (typically not used in batch processing)
        if show_plot:
            plt.show()
        
        plt.close()

    @staticmethod
    def plot_peaks_only(frequencies: np.ndarray, times: np.ndarray, peak_coordinates: List[Tuple[int, int]], 
                       title: str = "Constellation Map - Audio Peaks", save_path: Optional[str] = None, 
                       show_plot: bool = False, figure_size: Tuple[int, int] = (12, 6)) -> None:
        """
        Generate constellation map visualization showing only detected peaks.
        
        This method creates a clean visualization of the detected peaks that form
        the constellation map used for audio fingerprinting, displayed as points
        on a white background for clear visibility and analysis.
        
        Args:
            frequencies: Frequency bin centers in Hz
            times: Time frame centers in seconds
            peak_coordinates: List of detected peaks as (time_index, freq_index) tuples
            title: Plot title for the visualization
            save_path: File path to save the plot (PNG format recommended)
            show_plot: Whether to display the plot interactively
            figure_size: Plot dimensions as (width, height) in inches
        """
        plt.figure(figsize=figure_size)
        plt.gca().set_facecolor('white')
        
        # Plot peaks if any were detected
        if peak_coordinates:
            # Convert indices to actual time/frequency values
            peak_times = [times[time_idx] for time_idx, freq_idx in peak_coordinates]
            peak_frequencies = [frequencies[freq_idx] for time_idx, freq_idx in peak_coordinates]
            
            # Create scatter plot of peaks with professional styling
            plt.scatter(peak_times, peak_frequencies, c='black', s=2, alpha=0.8, 
                       label=f'{len(peak_coordinates)} peaks detected')
            plt.legend(fontsize=10)
        else:
            plt.text(0.5, 0.5, 'No peaks detected', transform=plt.gca().transAxes,
                    ha='center', va='center', fontsize=12, alpha=0.5)
        
        # Configure axes and styling
        plt.ylabel("Frequency (Hz)", fontsize=12)
        plt.xlabel("Time (s)", fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlim(0, np.max(times))
        plt.ylim(0, np.max(frequencies))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot if path specified
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"Peaks plot saved to: {save_path}")
        
        # Display plot if requested
        if show_plot:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_combined_analysis(spectrogram_db: np.ndarray, frequencies: np.ndarray, times: np.ndarray,
                              peak_coordinates: List[Tuple[int, int]], 
                              title: str = "Combined Audio Analysis - Spectrogram with Constellation Map",
                              save_path: Optional[str] = None, show_plot: bool = False) -> None:
        """
        Generate comprehensive analysis plot with spectrogram and overlaid peaks.
        
        This method creates a professional visualization combining the spectrogram
        background with overlaid constellation peaks, providing a complete view
        of the audio fingerprinting analysis process.
        
        Args:
            spectrogram_db: Magnitude spectrogram in decibel scale
            frequencies: Frequency bin centers in Hz
            times: Time frame centers in seconds
            peak_coordinates: List of detected peaks as (time_index, freq_index) tuples
            title: Plot title for the comprehensive analysis
            save_path: File path to save the plot (PNG format recommended)
            show_plot: Whether to display the plot interactively
        """
        plt.figure(figsize=(14, 8))
        
        # Plot spectrogram as background with transparency
        mesh_plot = plt.pcolormesh(times, frequencies, spectrogram_db, 
                                  shading="gouraud", cmap="magma", alpha=0.8)
        colorbar = plt.colorbar(mesh_plot, label="Magnitude (dB)")
        colorbar.ax.tick_params(labelsize=10)
        
        # Overlay constellation peaks with high visibility
        if peak_coordinates:
            # Convert indices to actual time/frequency values
            peak_times = [times[time_idx] for time_idx, freq_idx in peak_coordinates]
            peak_frequencies = [frequencies[freq_idx] for time_idx, freq_idx in peak_coordinates]
            
            # Plot peaks with cyan color and white edges for maximum visibility
            plt.scatter(peak_times, peak_frequencies, c='cyan', s=3, alpha=0.9, 
                       label=f'{len(peak_coordinates)} constellation peaks', 
                       edgecolors='white', linewidths=0.5)
            plt.legend(fontsize=10, loc='upper right')
        
        # Configure axes with professional styling
        plt.ylabel("Frequency (Hz)", fontsize=12)
        plt.xlabel("Time (s)", fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.ylim(0, np.max(frequencies))
        plt.grid(True, alpha=0.2)
        plt.tight_layout()
        
        # Save plot if path specified
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
            print(f"Combined analysis plot saved to: {save_path}")
        
        # Display plot if requested
        if show_plot:
            plt.show()
        
        plt.close()
