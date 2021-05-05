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
    def open_file():
        global file_names, save_loc
        browse_text.set("loading...")
        text        = ''
        file_names  = fd.askopenfilenames(parent=root,title="Choose PDF files", filetypes =[('PDF Files', '*.pdf')])  #   mode='rb', 
        text_box.config(state='normal')
        text_box.delete("1.0", "end-1c")
        print(file_names)

        if len(file_names)==0: 
            save_text    = 'Choose your save file location.'
            text        = 'Please select at least one PDF File.'
        elif len(file_names)==1:
            save_loc    = os.path.split(file_names[0])[0]
            save_text   = 'Converted file will be saved to: \n' + save_loc
            text        = os.path.split(file_names[0])[1] + ' is selected.'
        elif len(file_names)>1:
            save_loc    = os.path.split(file_names[0])[0]
            save_text   = 'Converted files will be saved to: \n' + save_loc
            text        = str(len(file_names)) + ' files selected.\n'
            for f in file_names:
                text    += os.path.split(f)[1] + '\n'

        text_box.insert(1.0, text)
        text_box.tag_configure("center", justify="center")
        text_box.tag_add("center", 1.0, "end")
        text_box.config(state='disabled')
        browse_text.set("Browse")
        
        convert_tb.config(state='normal')
        convert_tb.delete("1.0", "end-1c")
        convert_tb.insert(1.0, save_text)
        convert_tb.tag_configure("center", justify="center")
        convert_tb.tag_add("center", 1.0, "end")
        convert_tb.config(state='disabled')
        convert_text.set("Convert")

    def change_save_loc():
        global save_loc
        cd_text.set("loading...")
        save_loc = fd.askdirectory()#parent=root,title="Choose PDF files", filetypes =[('PDF Files', '*.pdf')])  #   mode='rb',
        print(save_loc, type(save_loc))
        if save_loc:
            convert_tb.config(state='normal')
            convert_tb.delete("1.0", "end-1c")
            convert_tb.insert(1.0, 'Converted file(s) will be saved to: \n' + save_loc)
            convert_tb.tag_configure("center", justify="center")
            convert_tb.tag_add("center", 1.0, "end")
            convert_tb.config(state='disabled')
            convert_text.set("Convert")
        cd_text.set("Change save location")

    def convert_to_excel():
        convert_text.set("converting...")
        convert_tb.config(state='normal')
        convert_tb.insert('end-1c', '\n----------------\n')
        convert_tb.tag_configure("center", justify="center")
        convert_tb.tag_add("center", 1.0, "end")
        convert_tb.config(state='disabled')
        print('files: ', list(file_names), 'save location: ', save_loc)
        try: 
            core.main_convert(list(file_names), save_loc)
        except: 
            convert_text.set("converting...")
            convert_tb.config(state='normal')
            convert_tb.insert('end-1c', 'There are problems while converting. Please try again.')
            convert_tb.tag_configure("center", justify="center")
            convert_tb.tag_add("center", 1.0, "end")
            convert_tb.config(state='disabled')    convert_text.set("Convert")

    if __name__== "__main__":
        root = tk.Tk()
        # root.configure(bg='black')
        # root['bg']='black'
        canvas = tk.Canvas(root, width=1000, height=800) #, bg='black', bd=None
        colspan = 2
        canvas.grid(columnspan=colspan, rowspan=5)

        #logo
        logo = Image.open('logo.png')
        logo = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(image=logo)
        logo_label.image = logo
        logo_label.grid(columnspan=colspan, column=0, row=0)

        #instructions
        instructions = tk.Label(root, text="No more typing! We turn your PDF Bank Statements into Excel rows.", font="Raleway")
        instructions.grid(columnspan=colspan, column=0, row=1)
        #browse button
        browse_text = tk.StringVar()
        browse_btn = tk.Button(root, textvariable=browse_text, command=lambda:open_file(), font="Raleway", bg="#46bcde", fg="white", height=2, width=25)
        browse_text.set("Browse")
        browse_btn.grid(column=0, row=2)

        #change dir button
        cd_text = tk.StringVar()
        cd_btn = tk.Button(root, textvariable=cd_text, command=lambda:change_save_loc(), font="Raleway", bg="#46bcde", fg="white", height=2, width=25)
        cd_text.set("Change save location")
        cd_btn.grid(column=1, row=2)

        #convert button
        convert_text = tk.StringVar()
        convert_btn = tk.Button(root, textvariable=convert_text, command=lambda:convert_to_excel(), font="Raleway", bg="#46bcde", fg="white", height=2, width=30)
        convert_text.set("Convert")
        convert_btn.grid(columnspan=colspan, row=4)
            
        #text box
        text_box = tk.Text(root, height=30, width=60, padx=0, pady=0)
        text_box.insert(1.0, 'Select files to convert.')
        text_box.config(state='disabled')
        text_box.tag_configure("center", justify="center")
        text_box.tag_add("center", 1.0, "end")
        text_box.grid(column=0 , row=3) #columnspan=2

        #converted text box
        global convert_tb
        convert_tb = tk.Text(root, height=30, width=60, padx=0, pady=0)
        convert_tb.insert(1.0, 'Choose your save file location.')
        convert_tb.config(state='disabled')
        convert_tb.tag_configure("center", justify="center")
        convert_tb.tag_add("center", 1.0, "end")
        convert_tb.grid(column=1 , row=3) #columnspan=2

        # canvas = tk.Canvas(root, width=600, height=250)
        # canvas.grid(columnspan=3)

        root.mainloop()
