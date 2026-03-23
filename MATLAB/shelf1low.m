function [num,den] = shelf1low(G,wc)
%shelf1low.m
% first order low-frequency shelving filter derived in the review article: 
% V. Valimaki and J. D. Reiss, "All About Audio Equalization: Solutions 
% and Frontiers", Applied Sciences, 2016
%
% INPUTS % OUTPUTS
% G = Gain at low frequencies (linear, not dB)
% wc = crossover frequency
% num = numerator coefficients b0 and b1
% den = denominator coefficients a0 and a1
%
% Written by Vesa Valimaki, Nov. 5, 2015.

% Transfer function coefficients
a0 = tan(wc/2) + sqrt(G);
a1 = (tan(wc/2) - sqrt(G));
b0 = (G*tan(wc/2) + sqrt(G));
b1 = (G*tan(wc/2) - sqrt(G));

% Transfer function polynomials
den = [a0 a1];
num = [b0 b1];
%figure(1);clf;freqz(num,den)

