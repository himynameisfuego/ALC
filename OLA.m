function y = OLA(x, shift, dim)
%
% Performs the reconstruction of a signal that was buffered with the overlapp-and-add (OLA) method.
%
% Y = OLA(X, shift, dim);
% 
% OUTPUT:
% Y: output reconstructed vector
% 
% INPUTS:
% X: input matrix, containing the buffered signal to be reconstructed
% Shift: step size, number of overlapped samples 
% Dim: dimension of the matrix along which do the de-overlappingz
%
% 20.10.2018 Leonardo Fierro

if (nargin < 3 || isempty(dim))
	dim = 1; 
end

if (dim == 1)
    [frameSize, nFrames] = size(x);
    if nargin < 2 || isempty(shift)
    	shift = frameSize/2;
    end
    
    y = zeros((nFrames-1)*shift + frameSize, 1);
    
    for i = 1:nFrames
        iStart = (i-1)*shift + 1;
        iFinish = iStart + frameSize - 1;
        y(iStart:iFinish) = y(iStart:iFinish) + x(:,i);
    end

elseif dim == 2
    [nFrames,frameSize] = size(x);
    if nargin < 2 || isempty(shift)
    	shift = frameSize/2;
    end
    y = zeros(1,(nFrames-1)*shift + frameSize);
    for i = 1:nFrames
        iStart = (i-1)*shift + 1;
        iFinish = iStart + frameSize - 1;
        y(iStart:iFinish) = y(iStart:iFinish) + x(i,:);
    end
end

y(1:end-shift) = y(1:end-shift)/2;

end
