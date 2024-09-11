import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Chemins vers les images
images = [
    {'image': 'photo_felix.jpg', 'name': 'Félix Lapierre'},
    {'image': 'photo_cedryk.jpg', 'name': 'Cédryk Jutras'}
]

# Créer un PDF
pdf_path = 'output.pdf'
pdf = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# Dimensions des images et des noms
img_size = min(width / 2 - 40, height / 2 - 40)  # Assurer que l'image reste carrée
x_positions = [20, width / 2 + 20]
y_positions = [height / 2 + 20, height / 2 + 20]

for idx, img_info in enumerate(images):
    x = x_positions[idx]
    y = y_positions[idx]

    # Ajouter l'image
    pdf.drawImage(img_info['image'], x, y, width=img_size, height=img_size)

    # Ajouter le nom en dessous de l'image
    pdf.setFont("Helvetica", 12)
    pdf.drawString(x, y - 20, img_info['name'])

pdf.save()
