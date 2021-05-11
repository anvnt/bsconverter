import tkinter as tk
import PyPDF2
try:
    from PIL import ImageTk, Image  
except ImportError:
    import Image 

import tkinter.filedialog as fd
import core
import os

class App:
    def __init__(self):
        self.root = tk.Tk()
        # self.root.configure(bg='black')
        # self.root['bg']='black'
        canvas = tk.Canvas(self.root, width=1000, height=800) #, bg='black', bd=None
        colspan = 2
        canvas.grid(columnspan=colspan, rowspan=5)

        #logo
        logo = Image.open('logo.png')
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(image=logo)
        logo_label.image = logo
        logo_label.grid(columnspan=colspan, column=0, row=0)

        #instructions
        instructions = tk.Label(self.root, text="No more typing! We turn your PDF Bank Statements into Excel rows.", font="Arial")
        instructions.grid(columnspan=colspan, column=0, row=1)
        #browse button
        self.browse_text = tk.StringVar()
        self.browse_btn = tk.Button(self.root, textvariable=self.browse_text, command=lambda:self.open_file(), 
            font="Arial", bg="#46bcde", activebackground='#cbecf6', fg="white", height=2, width=25)
        self.browse_text.set("Browse")
        self.browse_btn.grid(column=0, row=2)

        #change dir button
        self.cd_text = tk.StringVar()
        self.cd_btn = tk.Button(self.root, textvariable=self.cd_text, command=lambda:self.change_save_loc(), 
            font="Arial", bg="#46bcde", activebackground='#cbecf6', fg="white", height=2, width=25)
        self.cd_text.set("Change save location")
        self.cd_btn.grid(column=1, row=2)

        #convert button
        self.convert_text = tk.StringVar()
        self.convert_btn = tk.Button(self.root, textvariable=self.convert_text, command=lambda:self.convert_to_excel(), 
            font="Raleway", bg="#46bcde", fg="white", activebackground='#cbecf6', height=2, width=30, disabledforeground="grey")
        self.convert_text.set("Convert")
        self.convert_btn["state"] = "disabled"
        self.convert_btn.grid(columnspan=colspan, row=4)
            
        #text box
        self.text_box = tk.Text(self.root, height=30, width=60, padx=0, pady=0)
        self.text_box.insert(1.0, 'Select files to convert.')
        self.text_box.config(state='disabled')
        self.text_box.tag_configure("center", justify="center")
        self.text_box.tag_add("center", 1.0, "end")
        self.text_box.grid(column=0 , row=3) #columnspan=2

        #converted text box
        self.convert_tb = tk.Text(self.root, height=30, width=60, padx=0, pady=0)
        self.convert_tb.insert(1.0, 'Choose your save file location.')
        self.convert_tb.config(state='disabled')
        self.convert_tb.tag_configure("center", justify="center")
        self.convert_tb.tag_add("center", 1.0, "end")
        self.convert_tb.grid(column=1 , row=3) #columnspan=2

        # canvas = tk.Canvas(self.root, width=600, height=250)
        # canvas.grid(columnspan=3)

        self.root.mainloop()
        
    def open_file(self):
        global file_names, save_loc
        self.browse_text.set("loading...")
        text        = ''
        file_names  = fd.askopenfilenames(parent=self.root,title="Choose PDF files", filetypes =[('PDF Files', '*.pdf')])  #   mode='rb', 
        self.text_box.config(state='normal')
        self.text_box.delete("1.0", "end-1c")
        print(file_names)

        if len(file_names)==0: 
            save_text    = 'Choose your save file location.'
            text        = 'Please select at least one PDF File.'
            self.convert_btn["state"] = "disabled"
        elif len(file_names)==1:
            save_loc    = os.path.split(file_names[0])[0]
            save_text   = 'Converted file will be saved to: \n' + save_loc
            text        = os.path.split(file_names[0])[1] + ' is selected.'
            self.convert_btn["state"] = "normal"
        elif len(file_names)>1:
            save_loc    = os.path.split(file_names[0])[0]
            save_text   = 'Converted files will be saved to: \n' + save_loc
            text        = str(len(file_names)) + ' files selected.\n'
            for f in file_names:
                text    += os.path.split(f)[1] + '\n'
            self.convert_btn["state"] = "normal"

        self.text_box.insert(1.0, text)
        self.text_box.tag_configure("center", justify="center")
        self.text_box.tag_add("center", 1.0, "end")
        self.text_box.config(state='disabled')
        self.browse_text.set("Browse")
        
        self.convert_tb.config(state='normal')
        self.convert_tb.delete("1.0", "end-1c")
        self.convert_tb.insert(1.0, save_text)
        self.convert_tb.tag_configure("center", justify="center")
        self.convert_tb.tag_add("center", 1.0, "end")
        self.convert_tb.config(state='disabled')
        self.convert_text.set("Convert")

    def change_save_loc(self):
        global save_loc
        self.cd_text.set("loading...")
        save_loc = fd.askdirectory()#parent=self.root,title="Choose PDF files", filetypes =[('PDF Files', '*.pdf')])  #   mode='rb',
        print(save_loc, type(save_loc))
        if save_loc:
            self.convert_tb.config(state='normal')
            self.convert_tb.delete("1.0", "end-1c")
            self.convert_tb.insert(1.0, 'Converted file(s) will be saved to: \n' + save_loc)
            self.convert_tb.tag_configure("center", justify="center")
            self.convert_tb.tag_add("center", 1.0, "end")
            self.convert_tb.config(state='disabled')
            self.convert_text.set("Convert")
        self.cd_text.set("Change save location")

    def convert_to_excel(self):
        self.convert_text.set("converting...")
        self.convert_tb.config(state='normal')
        self.convert_tb.insert('end-1c', '\nAll files are converted.\n')
        self.convert_tb.tag_configure("center", justify="center")
        self.convert_tb.tag_add("center", 1.0, "end")
        self.convert_tb.config(state='disabled')
        print('files: ', list(file_names), 'save location: ', save_loc)
        try: 
            core.main_convert(list(file_names), save_loc)
        except: 
            self.convert_tb.config(state='normal')
            self.convert_tb.insert('end-1c', 'There are problems while converting. Please try again.')
            self.convert_tb.tag_configure("center", justify="center")
            self.convert_tb.tag_add("center", 1.0, "end")
            self.convert_tb.config(state='disabled')    
        self.convert_text.set("Convert")

if __name__== "__main__":
    App()
