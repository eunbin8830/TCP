import socket
import numpy as np
import matplotlib.pyplot as plt
import os

def receive_ultrasound_image():
    # Set up TCP client
    server_address = ('127.0.0.1', 54321)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    print("Connected to server.")

    frame_width = 128
    frame_height = 128
    buffer_size = frame_width * frame_height * 8

    # Directory to save images
    save_dir = r"C:\Users\User\Downloads\saving_image_python"
    os.makedirs(save_dir, exist_ok=True)

    try:
        plt.ion()  # Turn on interactive mode for real-time plotting
        fig, ax = plt.subplots()
        img_display = ax.imshow(np.zeros((frame_height, frame_width)), cmap='gray', vmin=0, vmax=1)
        plt.colorbar(img_display, ax=ax)
        plt.title('Python: Received B-Mode Ultrasound Image')

        image_count = 0  # Counter for saved images

        while True:
            # Receive checksum (big-endian)
            try:
                received_checksum = np.frombuffer(sock.recv(8), dtype='>f8')[0]
                print(f"Received checksum: {received_checksum}")
            except Exception as e:
                print(f"Error receiving checksum: {e}")
                break

            # Receive image data
            received_data = b''
            while len(received_data) < buffer_size:
                chunk = sock.recv(buffer_size - len(received_data))
                if not chunk:
                    print("No more data received. Closing connection.")
                    return
                received_data += chunk

            # Convert received image data (big-endian)
            try:
                b_mode_image = np.frombuffer(received_data, dtype='>f8').reshape(frame_height, frame_width)
            except Exception as e:
                print(f"Error processing image data: {e}")
                continue

            # Compute checksum to validate
            computed_checksum = np.mean(b_mode_image)
            print(f"Computed checksum: {computed_checksum}")

            # Check for checksum mismatch
            if not np.isclose(received_checksum, computed_checksum, atol=1e-5):
                print("Checksum mismatch! Data might be corrupted.")
                continue

            # Save the image
            image_path = os.path.join(save_dir, f"ultrasound_image_{image_count:04d}.png")
            plt.imsave(image_path, b_mode_image, cmap='gray', vmin=0, vmax=1)
            print(f"Image saved: {image_path}")
            image_count += 1

            # Update plot
            img_display.set_data(b_mode_image)
            plt.draw()
            plt.pause(0.01)  # Allow the plot to update

    except KeyboardInterrupt:
        print("Terminated by user.")
    finally:
        plt.ioff()  # Turn off interactive mode
        plt.close(fig)  # Close the plot window
        sock.close()
        print("Connection closed.")

if __name__ == "__main__":
    receive_ultrasound_image()
