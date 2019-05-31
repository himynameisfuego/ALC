# ALC - Adaptive Loudness Compensation

Hello! This repository contains the MATLAB files relative to the implementation of the method proposed in the paper "Adaptive Loudness Compensation in Music Listening" presented at SMC 2019 (http://smc2019.uma.es/articles/S2/S2_01_SMC2019_paper.pdf). A C++ implementation will be provided in the future.

Contacts and info: l.fierro@studenti.unibs.it

The need for loudness compensation is a well known fact arising from the nonlinear behavior of human sound perception. Music and other sounds are mixed and mastered at a certain loudness level, usually louder than the level at which they are commonly played. This implies a change in the perceived spectral balance of the sound, which is largest in the low-frequency range. As the volume setting in music playing is decreased, a loudness compensation filter can be used to boost the bass appropriately, so that the low frequencies are still heard well and the perceived spectral balance is preserved. This repo includes a loudness compensation function derived from the standard equal-loudness-level contours and its implementation via a digital first-order shelving filter. 

# Files

- ellc.m: generates an Equal Loudness Contour as described in ISO 226/2003.
- OLA.m: performs the reconstruction of a signal that was buffered with the overlapp-and-add (OLA) method.
- traceLoudness.m: returns filtering trace-guide from ELLC (Equal-loudness level contours), as described in the paper.
- shelf1low.m: first order low-frequency shelving filter, as proposed by Valimaki and Reiss in "All About Audio Equalization: Solutions and                Frontiers", Applied Sciences, 2016.
- adaptiveLoudnessComp.m: applies adaptive loudness compensation to the selected track according to reproduction level.
