function [AudioFinal,AudioRed] = adaptiveLoudnessComp(fileName,ML,LL);
%
% Applies adaptive loudness compensation to the selected track according to reproduction level.
%
% [AudioFinal,AudioRed] = adaptiveLoudnessComp(fileName,ML,LL);
% 
% OUTPUT:
% AudioFinal: compensated quiet audio file
% AudioRed: non-compensated quiet audio file
% 
% INPUTS:
% fileName: string referring to the input audio file
% ML,LL : Mastering Level, Listening Level
%
% 20.10.2018 Leonardo Fierro

wc = 2*pi*122.0552; adj = 0.4851; 
[audio_signal,Fs] = audioread(fileName);
AudioFile = sum(audio_signal, 2) / size(audio_signal, 2);
t = (0:length(AudioFile)-1)./audio_fs;

[filtTrace,~] = fitLoudnessContoursX(ML,LL);
G = 10^((filtTrace(1)+adj)/20);
[num1,den1] = shelf1low(G,wc/Fs);

soundG = 10^((LL-ML)/20); AudioRed = soundG * AudioFile;
AudioFil = buffer(AudioRed,4096,2048); AudioFinal = [];

for i = 1:size(AudioFil,2)
   AudioFinal(:,i) =  filter(num1,den1,AudioFil(:,i));
end

AudioFinal = ola(AudioFinal,2048,[],1);