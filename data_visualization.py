import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Serial communication setup
com_ports = ['COM8', 'COM9']

for com_port in com_ports:
    try:
        serialcomm = serial.Serial(com_port, 9600, timeout=1)
        print(f"Opened {com_port}")
        break  # If successfully opened, break out of the loop
    except serial.SerialException as e:
        print(f"Failed to open {com_port}: {e}")
else:
    # This block is executed if none of the ports are successfully opened
    print("Unable to open any COM port.")

# Initialize plot
rows = []  # List to store all rows
heatmap = []
counter = 0  # Counter to track the number of updates
NUMBER_OF_CAR_STEPS = 10

# Function to update the plot
def update_plot(frame):
    global counter  # Declare counter as global to modify its value
    if serialcomm.in_waiting > 0:
        raw_data = serialcomm.readline().decode('utf-8').strip().split(',')
        raw_data = raw_data[:-1]

        # Data processing and transformation
        distance_results = np.array(raw_data, dtype=float)
        print(distance_results)
        for idx, val in np.ndenumerate(distance_results):
            if round(val) > 16:
                distance_results[idx] = 15
        heatmap.append(np.flip(distance_results, 0))
        coloured_grid = np.copy(distance_results)
        for idx, val in np.ndenumerate(coloured_grid):
            if round(val) > 11:
                coloured_grid[idx] = 1
            else: coloured_grid[idx] = 0

        print(coloured_grid)
        coloured_grid = np.flip(coloured_grid, 0)

        # Update the list of rows
        rows.append(coloured_grid)

        # Update the plot
        axes[0].clear()
        combined_rows = np.array(rows)
        axes[0].imshow(combined_rows, cmap='gray', interpolation='nearest', aspect='auto', extent=(50,0,10,0))
        axes[0].set_title('Live Object Scan')
        
        # Increment the counter
        counter += 1

        # Check if counter reaches 10, stop the animation
        if counter == NUMBER_OF_CAR_STEPS:
            ani.event_source.stop()

def prediction_algorithm(sum):
    x = sum
    
    paper_values = [270, 274, 250, 245,241]
    scissor_values = [323, 293, 328, 322, 314]
    rock_values = [336, 374, 377, 375]
    
    meanp = np.mean(paper_values)
    sdp = np.std(paper_values)
    
    means = np.mean(scissor_values)
    sds = np.std(scissor_values)
    
    meanr = np.mean(rock_values)
    sdr = np.std(rock_values)
    
    def distribution_creator(x,mean,sd):
        prob_density = (np.pi*sd) * np.exp(-0.5*((x-mean)/sd)**2)
        return prob_density
    
    pdp = distribution_creator(x,meanp,sdp) #likelihood of paper
    pds = distribution_creator(x,means,sds) #likelihood of scissors
    pdr = distribution_creator(x,meanr,sdr) #likelihood of rock
    
    if pdp > pds and pdp > pdr:
        imgpath = 'paper.png'
        confidence = pdp/(pdp+pds+pdr)
        print(imgpath)
    
    if pdr > pds and pdr>pdp:
        imgpath = 'rock.png'
        confidence = pdr/(pdp+pds+pdr)
        print(imgpath)
        
    if pds > pdp and pds>pdr:
        imgpath = 'scissors.png'
        pred_conf = pds/(pdp+pds+pdr)
        confidence = round(pred_conf,2)
        print(imgpath)
        
    print(pdp,pds,pdr)
    print (confidence) 
    return imgpath, confidence

def animation_done():
    if counter == NUMBER_OF_CAR_STEPS - 1:
        global heatmap
        global rows
        total_sum = np.sum(rows)
        img_path, confidence = prediction_algorithm(total_sum)
        heatmap_2 = axes[1].imshow(heatmap, cmap='Blues', interpolation='sinc', aspect='auto', extent=(50,0,10,0))
        axes[1].set_title('Processed Distance Heatmap')
        fig.colorbar(heatmap_2, ax=axes[1])  # Add a colorbar
        plt.show() 
        time.sleep(2)
        img = plt.imread(img_path)
        axes[2].set_title('Prediction: {}'.format(confidence))
        axes[2].axis('off')  # Hide axis for the image
        axes[2].imshow(img)
        plt.imshow()

# Function to be called when middle subplot is done
def processed_image_done():
    img_path = 'paper_gif.gif'  # Replace with the actual path to your image file
    img = plt.imread(img_path)
    axes[2].set_title('Prediction')
    axes[2].axis('off')  # Hide axis for the image
    axes[2].imshow(img)

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))

# Plot on the first subplot (animated)
line, = axes[0].plot([], [])
axes[0].set_title('Live Object Scan')

line, = axes[1].plot([], [])
axes[0].set_title('Processed Image')

line, = axes[2].plot([], [])
axes[0].set_title('Prediction')

# Adjust layout to prevent clipping of titles
plt.tight_layout()

# Create an animation
ani = FuncAnimation(fig, update_plot, frames=NUMBER_OF_CAR_STEPS + 1, interval=3000, blit=False)

ani.event_source.start()
ani.event_source.add_callback(animation_done)

# Show the plot
plt.show()