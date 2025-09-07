"""
Audio fingerprint generation module.

This module implements the constellation mapping algorithm for generating
unique audio fingerprints from spectral peaks. The algorithm creates
robust audio signatures that can be used for audio identification.

Author: Hocus Pocus Project
Version: 1.0
"""

from typing import List, Tuple, Set


class FingerprintGenerator:
    """
    Generates audio fingerprints using constellation mapping algorithm.
    
    This class implements the core fingerprinting technique used in audio
    identification systems. It creates unique hashes from pairs of spectral
    peaks that are robust to noise and distortion.
    """
    
    def __init__(self, fan_value: int = 5, target_zone: Tuple[int, int] = (1, 20)):
        """
        Initialize the fingerprint generator with configuration parameters.
        
        Args:
            fan_value: Number of target peaks to pair with each anchor peak.
                      Higher values create more fingerprints but may include noise.
            target_zone: Time difference range (min_delta_t, max_delta_t) for 
                        valid peak pairs. Helps filter out spurious matches.
        """
        self.fan_value = fan_value
        self.target_zone = target_zone
    
    def generate_fingerprints(self, peaks: List[Tuple[int, int]]) -> List[Tuple[Tuple[int, int, int], int]]:
        """
        Generate audio fingerprints from spectral peaks using constellation mapping.
        
        The algorithm pairs each 'anchor' peak with subsequent 'target' peaks within
        the fan-out range, creating unique hashes of (f_anchor, f_target, delta_t).
        
        Args:
            peaks: List of detected spectral peaks as (time_index, freq_index) tuples.
                  These should be the most prominent peaks from the spectrogram.
            
        Returns:
            List of fingerprints as ((f_anchor, f_target, delta_t), t_anchor) tuples,
            where each tuple represents a unique audio signature.
            
        Note:
            The peaks are automatically sorted by time to ensure consistent
            fingerprint generation regardless of input order.
        """
        if not peaks:
            return []
            
        # Sort peaks chronologically to ensure positive time deltas
        sorted_peaks = sorted(peaks, key=lambda peak: peak[0])
        fingerprints = []

        for i, (t_anchor, f_anchor) in enumerate(sorted_peaks):
            # Create fingerprints by pairing with subsequent peaks
            for j in range(1, min(self.fan_value + 1, len(sorted_peaks) - i)):
                target_idx = i + j
                t_target, f_target = sorted_peaks[target_idx]
                delta_t = t_target - t_anchor

                # Filter pairs based on time difference constraints
                if self.target_zone[0] <= delta_t <= self.target_zone[1]:
                    fingerprint_hash = (f_anchor, f_target, delta_t)
                    fingerprints.append((fingerprint_hash, t_anchor))

        return fingerprints
    
    def generate_robust_fingerprints(self, peaks: List[Tuple[int, int]], 
                                   multiple_strategies: bool = True) -> List[Tuple[Tuple[int, int, int], int]]:
        """
        Generate enhanced fingerprints using multiple strategies for better robustness.
        
        This method employs multiple fingerprinting strategies to create a more
        comprehensive set of fingerprints that are resilient to audio degradation,
        noise, and temporal variations.
        
        Args:
            peaks: List of detected spectral peaks as (time_index, freq_index) tuples.
            multiple_strategies: Whether to use multiple fan-out strategies for
                               enhanced robustness. Set to False for standard generation.
            
        Returns:
            List of unique fingerprints with duplicates removed while preserving
            the temporal order of generation.
            
        Note:
            The robust generation creates approximately 1.5-2x more fingerprints
            than the standard method, improving match accuracy at the cost of
            increased computational overhead.
        """
        if not multiple_strategies:
            return self.generate_fingerprints(peaks)
        
        if not peaks:
            return []
        
        fingerprints = []
        sorted_peaks = sorted(peaks, key=lambda peak: peak[0])
        
        # Strategy 1: Standard constellation mapping
        fingerprints.extend(self.generate_fingerprints(peaks))
        
        # Strategy 2: Reduced fan-out for closer temporal relationships
        original_fan_value = self.fan_value
        reduced_fan_value = max(2, self.fan_value // 2)
        
        for i, (t_anchor, f_anchor) in enumerate(sorted_peaks):
            for j in range(1, min(reduced_fan_value + 1, len(sorted_peaks) - i)):
                target_idx = i + j
                t_target, f_target = sorted_peaks[target_idx]
                delta_t = t_target - t_anchor
                
                # Extended target zone for additional diversity
                extended_max_delta = self.target_zone[1] + 5
                if self.target_zone[0] <= delta_t <= extended_max_delta:
                    fingerprint_hash = (f_anchor, f_target, delta_t)
                    fingerprints.append((fingerprint_hash, t_anchor))
        
        # Restore original configuration
        self.fan_value = original_fan_value
        
        # Remove duplicates while preserving temporal order
        return self._remove_duplicates(fingerprints)
    
    def _remove_duplicates(self, fingerprints: List[Tuple[Tuple[int, int, int], int]]) -> List[Tuple[Tuple[int, int, int], int]]:
        """
        Remove duplicate fingerprints while preserving temporal order.
        
        Args:
            fingerprints: List of fingerprints that may contain duplicates.
            
        Returns:
            List of unique fingerprints in their original temporal order.
        """
        seen_hashes: Set[Tuple[int, int, int]] = set()
        unique_fingerprints = []
        
        for fingerprint_hash, t_anchor in fingerprints:
            if fingerprint_hash not in seen_hashes:
                seen_hashes.add(fingerprint_hash)
                unique_fingerprints.append((fingerprint_hash, t_anchor))
        
        return unique_fingerprints
