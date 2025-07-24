import pygame
import serial
import time
import struct
import tkinter as tk
from tkinter import ttk

# ----------------------- Serial Setup -----------------------
ser = serial.Serial('COM11', 115200, timeout=1)
time.sleep(2)

# -------------------- Pygame Joystick Setup -----------------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick found!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

LEFT_X = 0
LEFT_Y = 1
RIGHT_X = 2
RIGHT_Y = 3

def map_joystick_to_pulse(val):
    val = max(min(val, 1.0), -1.0)
    return int((val + 1.0) * 400 + 1100)

def send_command(values):
    command_str = ','.join(map(str, values)) + '\n'
    ser.write(command_str.encode())

def read_ahrs():
    if ser.in_waiting >= 12:
        data = ser.read(12)
        try:
            return struct.unpack('<fff', data)
        except:
            return None
    return None

# ------------------------ GUI Setup -------------------------
root = tk.Tk()
root.title("ROV Dashboard")
style = ttk.Style()
style.configure("TLabel", font=("Consolas", 12))
style.configure("Header.TLabel", font=("Consolas", 16, "bold"))

main_frame = ttk.Frame(root, padding="20")
main_frame.grid()

ttk.Label(main_frame, text="ROV Telemetry", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)

lx_var = tk.StringVar()
ly_var = tk.StringVar()
rx_var = tk.StringVar()
ry_var = tk.StringVar()
roll_var = tk.StringVar()
pitch_var = tk.StringVar()
yaw_var = tk.StringVar()
direction_var = tk.StringVar()

ttk.Label(main_frame, text="Joystick Input", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=5)
ttk.Label(main_frame, textvariable=lx_var).grid(row=2, column=0, sticky="w")
ttk.Label(main_frame, textvariable=ly_var).grid(row=3, column=0, sticky="w")
ttk.Label(main_frame, textvariable=rx_var).grid(row=4, column=0, sticky="w")
ttk.Label(main_frame, textvariable=ry_var).grid(row=5, column=0, sticky="w")

ttk.Label(main_frame, text="AHRS Orientation", style="Header.TLabel").grid(row=1, column=1, sticky="w", pady=5)
ttk.Label(main_frame, textvariable=roll_var).grid(row=2, column=1, sticky="w")
ttk.Label(main_frame, textvariable=pitch_var).grid(row=3, column=1, sticky="w")
ttk.Label(main_frame, textvariable=yaw_var).grid(row=4, column=1, sticky="w")

ttk.Label(main_frame, text="ROV Movement", style="Header.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 0))
ttk.Label(main_frame, textvariable=direction_var, font=("Consolas", 14, "bold")).grid(row=7, column=0, sticky="w")

def update_gui():
    pygame.event.pump()

    lx = joystick.get_axis(LEFT_X)
    ly = joystick.get_axis(LEFT_Y)
    rx = joystick.get_axis(RIGHT_X)
    ry = joystick.get_axis(RIGHT_Y)

    mapped_lx = map_joystick_to_pulse(lx)
    mapped_ly = map_joystick_to_pulse(-ly)
    mapped_rx = map_joystick_to_pulse(rx)
    mapped_ry = map_joystick_to_pulse(ry)

    send_command([mapped_lx, mapped_ly, mapped_rx, mapped_ry])

    lx_var.set(f"LX: {mapped_lx}")
    ly_var.set(f"LY: {mapped_ly}")
    rx_var.set(f"RX: {mapped_rx}")
    ry_var.set(f"RY: {mapped_ry}")

    direction = "STOP"
    if abs(mapped_ry - 1500) > 50:
        direction = "UP" if mapped_ry < 1500 else "DOWN"
    elif abs(mapped_ly - 1500) > 50:
        direction = "BACKWARD" if mapped_ly < 1500 else "FORWARD"
    elif abs(mapped_lx - 1500) > 50:
        direction = "LEFT" if mapped_lx < 1500 else "RIGHT"

    direction_var.set(f"→ {direction}")

    ahrs = read_ahrs()
    if ahrs:
        roll, pitch, yaw = ahrs
        roll_var.set(f"Roll : {roll:.2f}°")
        pitch_var.set(f"Pitch: {pitch:.2f}°")
        yaw_var.set(f"Yaw  : {yaw:.2f}°")

        # Print to IDLE/Console
        print(f"[Joystick] LX: {mapped_lx}, LY: {mapped_ly}, RX: {mapped_rx}, RY: {mapped_ry}")
        print(f"[AHRS] Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
        print(f"[Direction] {direction}")
        print("-" * 60)

    root.after(150, update_gui)

root.after(150, update_gui)
root.mainloop()

ser.close()
pygame.quit()
