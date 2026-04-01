import os
import io
from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

@app.route('/generate-offer', methods=['POST'])
def generate_offer_letter():
    # 1. Get data from the POST request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    name = data.get("name", "Candidate Name")
    role = data.get("role", "Role")
    client = data.get("client", "Client")
    start_date = data.get("start_date", "TBD")
    salary = data.get("salary", "TBD")
    contract_type = data.get("contract_type", "Indefinitely/full-time")
    hr_name = data.get("hr_name", "HR Team")
    hr_email = data.get("hr_email", "hr@potentiam.co.uk")

    # 2. Setup the PDF document in MEMORY using BytesIO
    pdf_buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        pdf_buffer, # Pointing to buffer instead of a file path
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = []

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        leading=11
    )

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=15
    )

    # 3. Load Logo (Using absolute path so Vercel can find it in the api folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "img.png")
    
    if os.path.exists(logo_path):
        try:
            img_reader = ImageReader(logo_path)
            orig_width, orig_height = img_reader.getSize()
            aspect_ratio = orig_height / float(orig_width)
            target_width = 120
            target_height = target_width * aspect_ratio

            logo = Image(logo_path, width=target_width, height=target_height)
            logo.hAlign = 'LEFT'

            elements.append(logo)
            elements.append(Spacer(1, 10))
        except Exception as e:
            print(f"Logo error: {e}")

    # 4. Document Title
    title = Paragraph("<b><u>Potentiam Offer Letter of employment</u></b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 10))

    # 5. Define Table Content
    work_schedule = """- 9:00 – 18:00; 1h lunch<br/>
    - Hybrid mode _ minimum 3 office days per week<br/>
    - Depending on business needs, the office attendance schedule can be modified at any time by the employer"""

    benefits = """<b>(under the Potentiam Benefits Policy)</b><br/>
    Daily meal vouchers of 35 (thirty-five) RON per worked day. This is a subject of taxation that is going to be deducted from your Net salary.<br/>
    Christmas & Easter vouchers - 650 (six hundred and fifty) RON for each event - providing you are still employed by Potentiam SRL and are not under notice from either party.<br/>
    Medical subscription currently with Regina Maria<br/>
    Loyalty vouchers<br/>
    Personal event vouchers (Marriage/ Maternity)<br/>
    Birthday voucher<br/>
    1 free day for your birthday<br/>
    Sport subscription reimbursement (within the budget regulated by legislation_)<br/>
    20 days of annual leave per annum<br/>
    Additional vacation, up to 24 days per year maximum, as per policy"""

    # 6. Formulating the Table Data
    table_data = [
        ["Name", name],
        ["Role", role],
        ["Client", client],
        ["Start Date", start_date],
        ["Monthly Salary", salary],
        ["Contract Type", contract_type],
        ["Work schedule", Paragraph(work_schedule, normal_style)],
        ["Benefits", Paragraph(benefits, normal_style)],
        ["Probation Period", "90 calendar days"],
        ["Notice period",
         Paragraph("20 working days after the successful completion of the probation period for both parties.", normal_style)]
    ]

    # 7. Create and Style the Table
    t = Table(table_data, colWidths=[100, 440])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 15))

    # 8. Outro & Signature Section
    outro_text = """
    If you are happy with the above terms, please sign below were indicated and return to <b>{1}</b> ({2}) via e-mail.<br/><br/>
    I, <b>{0}</b> accept the above terms of employment subject only to receipt and agreement to the full employment contract reflecting the above.<br/><br/>
    -------------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Date: ------------------<br/>
    (NAME)<br/><br/>
    On receipt of the signed offer letter an employment contract detailing all the above terms will be provided for your review and signature.
    """.format(name, hr_name, hr_email)

    elements.append(Paragraph(outro_text, normal_style))

    # 9. Build the PDF and send it back
    doc.build(elements)
    
    # Reset the buffer's cursor to the beginning before sending
    pdf_buffer.seek(0)
    
    filename = f"{name.replace(' ', '_')}_Offer_Letter.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    # This allows you to run it locally using: python api/index.py
    app.run(debug=True, port=5000)
