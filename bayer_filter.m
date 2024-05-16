close all; clc; clear vars;

input_image = imread("found_you.png","png");
x_top = size(input_image,2) - mod(size(input_image,2),2)
y_top = size(input_image,1) - mod(size(input_image,1),2)
figure; image(input_image) %debugging

image_in = zeros(y_top,x_top,3,"uint8"); %define input image size
% apply the bayer filter
for x = 1:1:x_top
    for y = 1:1:y_top
        if (mod(x,2)==1) && (mod(y,2)==1) %RedSubpixel
            image_in(y,x,1) = input_image(y,x,1);
        elseif (mod(x,2)==0) && (mod(y,2)==0)%BlueSubpixel
            image_in(y,x,1) = input_image(y,x,3);
        else
            image_in(y,x,1) = input_image(y,x,2);
        end
        image_in(y,x,2) = image_in(y,x,1);%make it grayscale for debugging
        image_in(y,x,3) = image_in(y,x,1);
    end
end

figure; image(image_in) %debugging viewer

%output image buffer
image_out = zeros(y_top,x_top,3,"uint8");
%run the de-bayering
for x = 1:1:x_top %these will be different in C
    for y = 1:1:y_top

        t_red = uint16(0);
        t_green = uint16(0);
        t_blue = uint16(0);

        c_red = uint16(0);
        c_green = uint16(0);
        c_blue = uint16(0);

        for t_x = x-1:1:x+1;
            for t_y = y-1:1:y+1;
                if (t_x>=1) && (t_y>=1) && (t_x<=x_top) && (t_y<=y_top)%if valid pixel

                    if (mod(t_x,2)==1) && (mod(t_y,2)==1) %RedSubpixel
                        c_red=c_red+1;
                        t_red=t_red+uint16(image_in(t_y,t_x,1));
            
                    elseif (mod(t_x,2)==0) && (mod(t_y,2)==0)%BlueSubpixel
                        c_blue=c_blue+1;
                        t_blue=t_blue+uint16(image_in(t_y,t_x,1));
            
                    else
                        c_green=c_green+1;
                        t_green=t_green+uint16(image_in(t_y,t_x,1));
            
                    end


                end
            end
        end

        %pixel is the average of its inputs
        image_out(y,x,1) = uint8(floor(t_red/c_red));
        image_out(y,x,2) = uint8(floor(t_green/c_green));
        image_out(y,x,3) = uint8(floor(t_blue/c_blue));
        

    end
end

figure; imshow(image_out) %debugging
t_pixel = zeros(3,"double");

%YCrCb
conversion = double([77,150,29;-43,-84,127;127,-106,-21]);
offset = double([0;128;128]);

for x = 1:1:x_top
    for y = 1:1:y_top

        t_pixel = double(reshape(image_out(y,x,:),3,[]));
        t_pixel = ((conversion*t_pixel)./256)+offset;
        image_out(y,x,:) = t_pixel;
    end
end

figure; imshow(image_out) %debugging