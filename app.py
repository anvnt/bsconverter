import tkinter as tk
import PyPDF2
try:
    from PIL import ImageTk, Image  
except ImportError:
    import Image 


from tkinter.filedialog import askopenfile

root = tk.Tk()
# root.configure(bg='black')
# root['bg']='black'
canvas = tk.Canvas(root, width=800, height=500) #, bg='black', bd=None
canvas.grid(columnspan=2, rowspan=5)

#logo
logo = Image.open('logo.png')
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(columnspan=2, column=0, row=0)

#instructions
instructions = tk.Label(root, text="No more typing! We turn your PDF Bank Statements into Excel rows.", font="Raleway")
instructions.grid(columnspan=2, column=0, row=1)

def open_file():
    browse_text.set("loading...")
    file = askopenfile(parent=root, mode='rb', title="Choose a file") #, filetype=[("Pdf file", "*.pdf")]
    if file:
        read_pdf = PyPDF2.PdfFileReader(file)
        page = read_pdf.getPage(0)
        page_content = page.extractText()

        #text box
        text_box = tk.Text(root, height=10, width=85, padx=15, pady=0)
        text_box.insert(1.0, page_content)
        text_box.tag_configure("center", justify="center")
        text_box.tag_add("center", 1.0, "end")
        text_box.grid(columnspan=2, row=3)

        browse_text.set("Browse")

#browse button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=lambda:open_file(), font="Raleway", bg="#46bcde", fg="white", height=2, width=25)
browse_text.set("Browse")
browse_btn.grid(column=0, row=2)

#convert button
convert_text = tk.StringVar()
convert_btn = tk.Button(root, textvariable=browse_text, command=lambda:open_file(), font="Raleway", bg="#46bcde", fg="white", height=2, width=25)
convert_text.set("Convert")
convert_btn.grid(column=1, row=2)

# canvas = tk.Canvas(root, width=600, height=250)
# canvas.grid(columnspan=3)

root.mainloop()
