from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import Table, Paragraph, NextPageTemplate, PageBreak, Image, BaseDocTemplate, PageTemplate, Frame, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import pandas as pd
from pandas.core.series import Series
from pandas.core.frame import DataFrame
from datetime import date
import io
import matplotlib.pyplot as plt
from data_from_daily import read_and_clean_data, plot_violin
import numpy as np

# https://www.tomshardware.com/how-to/python-remove-image-backgrounds
# https://nicd.org.uk/knowledge-hub/creating-pdf-reports-with-reportlab-and-pandas
# C:\Users\ikerm\Documents\python resources\report_writer\reportlab-userguide.pdf

def get_width_height_ratio(path):
    size = ImageReader(path).getSize()
    return size[0]/size[1]

def check_divisibility(a,b):
  if a%b!= 0:
    return False
  else:
    return True

def get_number_on_columns(n_columns,times_spread):

  # Another way
  n_with_less = n_columns%times_spread
  n_with_more = times_spread-n_with_less
  if n_with_less != 0:
    n_on_more = int(n_columns/times_spread)+1
    n_on_less = int((n_columns - n_on_more*n_with_more)/n_with_less)
  else:
    n_on_more = int(n_columns/times_spread)
    n_on_less = 0
  number_on_columns = [n_on_more]*n_with_more+[n_on_less]*n_with_less
  
  return number_on_columns

# Defining functions that will let us put images and tables in the reports
def fig2image(f):
    buf = io.BytesIO()
    f.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    x, y = f.get_size_inches()
    return Image(buf, x * inch, y * inch)

def df2table(df, style, alignment = 'CENTER', padding = [72,72,100,18], page_type = A4):

  if isinstance(df,DataFrame):
    table=  Table([[Paragraph(col) for col in df.columns]] + df.values.tolist(), style= style, hAlign = alignment)
  
  if isinstance(df,Series):
    table = Table([[col for col in df.axes[0]]]+[df.values.tolist()], style= style, hAlign = alignment)

  if (page_type[0]-padding[0]-padding[1])-table.minWidth() < 0:
    times_spread = int(table.minWidth()/(page_type[0]-padding[0]-padding[1]))+1

    if isinstance(df,DataFrame):
      n_columns = len(df.columns)

    if isinstance(df,Series):
      n_columns = len(df.axes[0])
    
    number_on_columns = get_number_on_columns(n_columns,times_spread)

    if isinstance(df,DataFrame):
      table = [df2table(df.loc[:,df.columns[0:number_on_columns[0]]],style)]
      min_index = 0
      max_index = number_on_columns[0]
      for i in range(times_spread-1):
        min_index = min_index + number_on_columns[i]
        max_index = max_index + number_on_columns[i+1]
        table.append(df2table(df.loc[:,df.columns[min_index:max_index]],style))

    if isinstance(df,Series):
      table = [df2table(df.loc[list(df.axes)[0][0:number_on_columns[0]]],style)]
      min_index = 0
      max_index = number_on_columns[0]
      for i in range(times_spread-1):
        min_index = min_index + number_on_columns[i]
        max_index = max_index + number_on_columns[i+1]
        table.append(df2table(df.loc[list(df.axes)[0][min_index:max_index]],style))

  return table

def create_basic_documnent(pdf_name = 'report.pdf',padding = [72,72,100,18], page_type = A4):

  # Functions that will be called on each page and put in it
  def on_page(canvas, doc, pagesize=A4): 

      canvas.line(20,20,20,pagesize[1]-20)
      canvas.line(20,20,pagesize[0]-20,20)
      canvas.line(pagesize[0]-20,20,pagesize[0]-20,pagesize[1]-20)
      canvas.line(20,pagesize[1]-20,pagesize[0]-20,pagesize[1]-20)

      page_num = canvas.getPageNumber()
      canvas.drawCentredString(pagesize[0]/2, 30, str(page_num))

      image_path = 'INTIURA.PNG'
      width = 125
      height = width/get_width_height_ratio(image_path)
      canvas.drawImage(image_path, pagesize[0]-width-30, pagesize[1]-height-30,width,height)

      date_string = date.today().strftime("%d/%m/%Y")
      header = date_string + ' - YARUCAYA, DATA CENTER 1'
      canvas.drawString(50, pagesize[1]-height-30,header)

  def on_page_landscape(canvas, doc):
      return on_page(canvas, doc, pagesize=landscape(A4))
  
  # Defining the sizes of the pages and the paddings
  padding = dict(
      leftPadding=padding[0], 
      rightPadding=padding[1],
      topPadding=padding[2],
      bottomPadding=padding[3])

  portrait_frame = Frame(0, 0, *page_type, **padding)
  landscape_frame = Frame(0, 0, *landscape(page_type), **padding)

  # Creating the templates of the pages 
  portrait_template = PageTemplate(
    id='portrait', 
    frames=portrait_frame,
    onPage=on_page, 
    pagesize=page_type)

  landscape_template = PageTemplate(
    id='landscape', 
    frames=landscape_frame, 
    onPage=on_page_landscape, 
    pagesize=landscape(page_type))

  # Defining the document we will create
  return BaseDocTemplate(pdf_name,pageTemplates=[portrait_template,landscape_template])

def put_tables_in_doc(tablas,story):

  if type(tablas) == list:
    for tabla in tablas:
      story.append(tabla)
      story.append(Spacer(10,10))
  else:
    story.append(tablas)

if __name__ == '__main__':

  # First wiil create the document
  doc = create_basic_documnent()

  # Defining the styles of the tables
  style=[
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
        ('ALIGN', (0,0),(-1,-1),'CENTER'),  # Aligns the text inside the tables not the titles
        ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])]
  table_alingment = 'CENTER' # ('LEFT', 'RIGHT', 'CENTER' or 'CENTRE').

  # Will use the reports from the daily csv data of the miners
  input_path = 'Facturacion_YBL.xlsx'
  data, data_to_check, date_of_data = read_and_clean_data(input_path, shorten_titles= True, use_text_names = True)

  # Lo primero el titulo del documento
  styles = getSampleStyleSheet() # Importing the heading styles 
  story = [Paragraph('Reporte de datos diaria', styles['Heading1'])]

  # 1. Tabla de los hashrates
  story.append(Paragraph('Tabla de los hashrates', styles['Heading2']))
  tabla_hashrate= data_to_check.loc[:,['TIEMPO','HASHRATE_MEDIA','HASHRATE_MIN', 'HASHRATE_MAX']]
  tabla = df2table(tabla_hashrate, style, table_alingment)
  put_tables_in_doc(tabla,story)
  
  # 2. Tabla de los fallos del sistema
  tabla_fallos = data_to_check.loc[:,['TIEMPO','FALLOS_REINICIO_FOREMAN','FALLOS_RED_TELECO', 'FALLOS_ELÉCTRICO']]
  story.append(Paragraph('Tabla de los fallos del sistema', styles['Heading2']))
  tabla = df2table(tabla_fallos, style, table_alingment)
  put_tables_in_doc(tabla,story)

  # 3. Graficos de las temperaturas externas
  titles_ext_temp = list(data.columns[1:4])
  story.append(Paragraph('Temperaturas', styles['Heading2']))

  plot_ext_temp = plt.figure()
  for i in range(len(titles_ext_temp)):
    plt.subplot(1,3,i+1)
    plt = plot_violin(titles_ext_temp[i],data,data_to_check,date_of_data,title_type='short')
    
  story.append(fig2image(plot_ext_temp))

  # 4. Tabla de los consumos medios
  story.append(Paragraph('Tabla de los consumos medios', styles['Heading2']))
  tabla_consumos_media_check = data_to_check.loc[:,['CONSUMO_L1','CONSUMO_L2', 'CONSUMO_L3']].astype(np.float16).mean()
  tabla = df2table(tabla_consumos_media_check, style)
  put_tables_in_doc(tabla,story)

  # 5. Grafico temperaturas bobinado de motores
  titles_temp_motor = list(data.columns[4:10])
  story.append(Paragraph('Temperaturas de los bobinados de los motores', styles['Heading2']))

  plot_temp_motor = plt.figure(figsize=(7,7))
  for i in range(len(titles_temp_motor)):
    plt.subplot(2,3,i+1)
    plt = plot_violin(titles_temp_motor[i],data,data_to_check,date_of_data,title_type='short')

  story.append(fig2image(plot_temp_motor))

  # Cambiar de pagina para tener todas las tablas en la misma pagina
  story.append(PageBreak())

  # 6. Tabla con la medición de los voltajes
  titles_voltaje = list(data.columns.values[-18:-6])
  titles_voltaje.append(data.columns.values[-5])
  titles_voltaje.append(data.columns.values[-3])

  tabla_voltaje_media_check = data_to_check.loc[:,titles_voltaje].astype(np.float16).mean()
  tabla = df2table(tabla_voltaje_media_check, style)
  max_percent = 0
  for value in list(tabla_voltaje_media_check.values):
    if (abs(value-230)/230)>max_percent:  
      max_percent = (abs(value-230)/230)
      regleta_mas_desviacion = list(tabla_voltaje_media_check.values).index(value)

  deviation_text = 'Mayor desviación de los 230V: ' + str(max_percent*100)[:5]+'%, dada en la regleta: ' + str(tabla_voltaje_media_check.axes[0][regleta_mas_desviacion][-5:])

  story.append(Paragraph('Tabla de los voltajes de las regletas', styles['Heading2']))
  story.append(Paragraph(deviation_text,  styles['Heading3']))
  story.append(Spacer(10,10))
  put_tables_in_doc(tabla,story)
  story.append(PageBreak())

  # 7. Tabla con los valores de las temperaturas 
  titulos_temp_PDU =  list(data.columns.values[-36:-18])
  story.append(Paragraph('Graficos de las temperaturas de las PDU-s', styles['Heading2']))
  story.append(Paragraph('Las temperaturas historicas han sido muy altas dado que hay data de antes de poner un sistema de ventilacion para enfriar', styles['Heading3']))

  plot_temp_PDU = plt.figure(figsize=(7,8))
  for i in range(len(titulos_temp_PDU[:9])):
    plt.subplot(3,3,i+1)
    plt = plot_violin(titulos_temp_PDU[i],data,data_to_check,date_of_data)

  story.append(fig2image(plot_temp_PDU))

  plot_temp_PDU = plt.figure(figsize=(7,9))
  for i in range(len(titulos_temp_PDU[9:])):
    plt.subplot(3,3,i+1)
    plt = plot_violin(titulos_temp_PDU[i],data,data_to_check,date_of_data)

  story.append(fig2image(plot_temp_PDU))

  # 8. Mostrar regleta erronea Si existe voltaje mal
  voltaje_anormal_data = data_to_check.loc[:,'VOLTAJE_ANORMAL']
  list_with_errors = list(set(list(voltaje_anormal_data.values))) # Removing duplicate values
  if len(list_with_errors)>1:

    story.append(Paragraph('Tabla de las regletas anormales', styles['Heading2']))
    tabla = df2table(data_to_check.loc[:,['TIEMPO','REGLETA_ANORMAL']], style)
    put_tables_in_doc(tabla,story)
  
  story.append(PageBreak())
  
  # 9. Estado de los paneles 1, 2 y 3
  story.append(Paragraph('Estado de los paneles', styles['Heading2']))
  tabla = df2table(data_to_check.loc[:,['TIEMPO','PANEL_1', 'PANEL_2', 'PANEL_3']], style)
  put_tables_in_doc(tabla,story)

  # 10. Comentarios finales si es que los hay

  comentarios = list(data_to_check.loc[:,'COMENTARIOS'])
  comentario_str = ''
  for comentario in comentarios:
    if str(comentario)!='nan':
      comentario_str = comentario_str + comentario + '. ' 
  
  if comentario_str == '':
    comentario_str = 'No hay ningun comentario respecto a la revision diaria'

  story.append(Paragraph('Comentarios y observaciones: ', styles['Heading2']))
  story.append(Paragraph(comentario_str, styles['Heading3']))

  # # 10. Pagina en horizontal
  # story.append(NextPageTemplate('landscape'))
  # story.append(PageBreak())

  doc.build(story)

  print('')
