clc;
clear;

% Set up TCP server
server = tcpip('127.0.0.1', 54321, 'NetworkRole', 'server');
server.OutputBufferSize = 128 * 128 * 8 + 8; % Include extra space for checksum
fopen(server);
disp('TCP server started.');

% Directory to save images
saveDir = 'C:\Users\User\Downloads\saving_image_matlab';
if ~exist(saveDir, 'dir')
    mkdir(saveDir);
end

% Generate and send images in a loop
frameWidth = 128;
frameHeight = 128;
imageCount = 0; % Counter for saved images

while true
    % Generate B-Mode image
    bModeImage = rand(frameHeight, frameWidth);

    % Normalize
    bModeImage = bModeImage - min(bModeImage(:));
    bModeImage = bModeImage / max(bModeImage(:));

    % Save the image
    imagePath = fullfile(saveDir, sprintf('b_mode_image_%04d.png', imageCount));
    imwrite(bModeImage, imagePath);
    disp(['Image saved: ', imagePath]);
    imageCount = imageCount + 1;

    % Compute checksum using mean
    checksum = mean(bModeImage(:));
    disp(['MATLAB checksum: ', num2str(checksum)]);

    % Convert checksum to big-endian byte order
    checksumBytes = typecast(swapbytes(checksum), 'uint8');

    % Send checksum
    fwrite(server, checksumBytes, 'uint8');

    % Flatten and convert image data to big-endian byte order
    bModeImageBytes = typecast(swapbytes(bModeImage(:)), 'uint8');

    % Send image data
    fwrite(server, bModeImageBytes, 'uint8');
    disp('B-Mode image transmitted.');

    % Pause for 0.2 seconds
    pause(0.2);
end

% Close server (not reachable unless manually terminated)
fclose(server);
disp('TCP server closed.');
