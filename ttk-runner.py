import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def process_file():
    # 1. Open file dialog accepting all your requested formats
    file_types = [
        ("All Supported Files", "*.po *.xlf *.xliff *.tmx *.json *.csv"),
        ("Gettext PO Files", "*.po"),
        ("XLIFF Files", "*.xlf *.xliff"),
        ("TMX Memory Files", "*.tmx"),
        ("JSON i18n Files", "*.json"),
        ("CSV Files", "*.csv")
    ]
    
    input_path = filedialog.askopenfilename(filetypes=file_types)
    if not input_path:
        return
        
    base_path, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    # Define intermediate and final output file naming structures
    po_working_file = base_path + "_converted.po"
    final_output_file = base_path + "_checked.po"
    
    try:
        status_label.config(text="Processing file... Please wait.", fg="blue")
        root.update_idletasks()

        # 2. Convert source format to standard working PO format if necessary
        # Normalizing paths via os.path.normpath prevents mixed-slash anomalies
        input_path = os.path.normpath(input_path)
        po_working_file = os.path.normpath(po_working_file)
        final_output_file = os.path.normpath(final_output_file)

        if ext in ['.xlf', '.xliff']:
            subprocess.run(["xliff2po", "-i", input_path, "-o", po_working_file], check=True, shell=True)
            temp_po_used = True
        elif ext == '.tmx':
            # FIX: Explicitly passing -i and -o ensures pot2po outputs the file correctly
            subprocess.run(["pot2po", "-i", input_path, "-o", po_working_file, "--tm", input_path], check=True, shell=True)
            temp_po_used = True
        elif ext == '.json':
            subprocess.run(["json2po", "-i", input_path, "-o", po_working_file], check=True, shell=True)
            temp_po_used = True
        elif ext == '.csv':
            subprocess.run(["csv2po", "-i", input_path, "-o", po_working_file], check=True, shell=True)
            temp_po_used = True
        else:
            # It's already a PO file
            po_working_file = input_path
            temp_po_used = False


        # 3. Run the automated wxWidgets pofilter checks 
        subprocess.run(["pofilter", "--wx", "-i", po_working_file, "-o", final_output_file], check=True, shell=True)
        
        # Clean up the intermediate working PO file if one was generated
        if temp_po_used and os.path.exists(po_working_file):
            os.remove(po_working_file)
            
        status_label.config(text="Idle", fg="gray")
        messagebox.showinfo("Success", f"Conversion & QA Check Complete!\nSaved to: {final_output_file}")
        
    except FileNotFoundError:
        status_label.config(text="Error", fg="red")
        messagebox.showerror("Dependency Error", 
                             "Could not find Translate Toolkit command line utilities.\n"
                             "Please ensure your environment variables are configured.")
    except subprocess.CalledProcessError as e:
        status_label.config(text="Failed", fg="red")
        messagebox.showerror("Error", f"Failed processing file structure during conversion pipeline:\n{e}")

# --- Desktop Application Setup ---
root = tk.Tk()
root.title("Translate Toolkit - Universal Desktop Runner")
root.geometry("450x200")
root.resizable(False, False)

# Application Header Instructions
header = tk.Label(root, text="Universal Localization Format Tool", font=("Arial", 12, "bold"), pady=10)
header.pack()

desc = tk.Label(root, text="Select PO, XLIFF, TMX, JSON, or CSV files.\nThe app handles format conversion and applies wx filters seamlessly.", 
                wraplength=400, justify="center", fg="dim gray")
desc.pack(pady=5)

# Interactive Execution Button
btn = tk.Button(root, text="Browse & Run Pipeline", command=process_file, 
                bg="#007acc", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8)
btn.pack(pady=15)

# Simple App Status Footer Bar (Corrected Layout Alignment)
status_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = tk.Label(status_frame, text="Idle", fg="gray", font=("Arial", 9), anchor=tk.W)
status_label.pack(side=tk.LEFT, fill=tk.X, padx=5)

root.mainloop()
