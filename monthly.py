from hourly import get_main_path, get_day
import os
import pandas as pd
import datetime
from calendar import monthrange
import matplotlib.pyplot as plt
import io

# Report libraries
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Frame, Table, PageTemplate, BaseDocTemplate, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pandas.core.frame import DataFrame
from pandas.core.series import Series

def get_width_height_ratio(path):
    size = ImageReader(path).getSize()
    return size[0]/size[1]

def create_basic_documnent(pdf_name = 'report.pdf',padding = [72,72,100,18], page_type = A4, month = ''):

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

    canvas.drawString(50, pagesize[1]-height-30,month)

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
  return BaseDocTemplate(pdf_name,pageTemplates=[portrait_template,landscape_template], title= f'Report - {month}', author= 'Inti Ura')

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

def get_doc_and_styles(month):

    # First wiil create the document

    # Defining the styles of the tables
    style=[
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('LINEBELOW',(0,0), (-1,0), 1, colors.black),
            ('ALIGN', (0,0),(-1,-1),'CENTER'),  # Aligns the text inside the tables not the titles
            ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.lightgrey, colors.white])]
    table_alignment = 'CENTER' # ('LEFT', 'RIGHT', 'CENTER' or 'CENTRE').

    styles = getSampleStyleSheet()

    return style, table_alignment, styles

def fig2image(f):
    buf = io.BytesIO()
    f.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    x, y = f.get_size_inches()
    return Image(buf, x * inch, y * inch)


def df2table(df, lista, style, alignment = 'CENTER', padding = [72,72,100,18], page_type = A4):

  if isinstance(df,DataFrame):
    table = Table([[Paragraph(col) for col in df.columns]] + df.values.tolist(), style= style, hAlign = alignment)
    lista.append(table)
  
  if isinstance(df,Series):
    table = Table([[col for col in df.axes[0]]]+[df.values.tolist()], style= style, hAlign = alignment)
    lista.append(table)

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

    lista += table

  return lista

def put_tables_in_doc(tablas,story):

  if type(tablas) == list:
    for tabla in tablas:
      story.append(tabla)
      story.append(Spacer(10,10))
  else:
    story.append(tablas)



if __name__ == '__main__':

  # Mirar donde se guarda el report

  main_file_path = get_main_path()
  xlsx_path = os.path.join(main_file_path, 'Facturacion.xlsx')
  pdf_path = os.path.join(main_file_path, 'Report.pdf')

  day = get_day()

  # # -------------------------- Overriden ---------------------------
  # xlsx_path = 'Facturacion_YBL.xlsx'

  today = datetime.date.today()
  first = today.replace(day=1)
  month = (first - datetime.timedelta(days=1)).strftime("%Y/%m")

  number_days_on_month = monthrange(int(month[:4]), int(month[-2:]))[1]

  data = pd.read_excel(xlsx_path, sheet_name='data_mensual')
  monthly_data_raw = data[data['Day'].str.contains(month)]
  monthly_data = monthly_data_raw[~monthly_data_raw["Average Hashrate"].str.contains('No hashrate', na= False)]
  if len(monthly_data) == 0:
      total_usd = 0
  else: 
      average_usd = sum(monthly_data['USD'])/len(monthly_data)
      total_usd = sum(monthly_data['USD']) + average_usd * (number_days_on_month-len(monthly_data))

  total_btc = sum(monthly_data_raw['BTC'])

  monthly_values = {'month': [month], 'Total USD': [total_usd], 'Total BTC': [total_btc]}
  monthly_values = pd.DataFrame(data= monthly_values)

  with pd.ExcelWriter(xlsx_path, mode = 'a', engine="openpyxl", if_sheet_exists = 'overlay') as writer:
      monthly_values.to_excel(writer, sheet_name="factura", startrow=writer.sheets['factura'].max_row, header = False, index=False)


  # ------------------- Documento ------------------------
  pdf_name = 'Report_' + month.replace('/','-')
  pdf_path = os.path.join(main_file_path, f'{pdf_name}.pdf')
  doc = create_basic_documnent(pdf_name= pdf_path, month=month)
  style, table_alignment, styles = get_doc_and_styles(month)

  # Titulo del documento
  story = [Paragraph(f'Reporte de datos mensual', styles['Heading1'])]

  # 1. Tabla con resumen general del mes
  resumen_together = [Paragraph('Resumen:', styles['Heading2'])]
  resumen_together.append(Paragraph(f'En la siguiente tabla se muestran los valores del {month}, el total facturado en USD ($) y los Bitcoins (BTC) totales minados:', styles['BodyText']))
  resumen_together.append(Spacer(10,10))
  tabla_resumen = {'Mes': [month], 'Total USD': [round(total_usd,2)], 'Total BTC': [round(total_btc,2)]}
  resumen_together = df2table(pd.DataFrame(data= tabla_resumen), resumen_together, style, table_alignment)
  story.append(KeepTogether(resumen_together))

  # 2. Gráfico de los hasheos reales
  hash_together = [Paragraph('Gráfico de los hasheos diarios:', styles['Heading2'])]
  daily_hash = monthly_data_raw['USD']/10
  plot_hash = plt.figure()
  plt.stem(range(len(daily_hash)), list(daily_hash))
  plt.title('Hasheo de cada día del mes en pentahashes')
  hash_together.append(fig2image(plot_hash))
  hash_together.append(Paragraph('Para el calculo del total en USD se ha multiplicado el valor diario de los pentahashes por diez y se han sumado.', styles['BodyText']))

  if list(daily_hash).count(0.0) > 0:
    hash_together.append(Paragraph('En el caso de los días que no ha habido producción se ha considerado como si se hubiera hasheado la media de los días que sí ha habido producción.', styles['BodyText']))
    
  story.append(KeepTogether(hash_together))

  if list(daily_hash).count(0.0) > 0:
    # 2.5. Gráfico de los hasheos ponderados si es necesario
    hash_pond_together = [Paragraph('Gráfico de los hasheos diarios ponderados:', styles['Heading2'])]
    daily_hash = monthly_data_raw['USD']/10
    plot_hash = plt.figure()
    hash_ponderado = []
    for value in daily_hash:
        if value == 0:
            hash_ponderado.append(average_usd/10)
        else:
            hash_ponderado.append(value)
    plt.stem(range(len(hash_ponderado)), list(hash_ponderado))
    plt.title('Hasheo ponderado de cada día del mes en pentahashes')
    hash_pond_together.append(fig2image(plot_hash))

    story.append(KeepTogether(hash_pond_together))

  # 3. Gráfico de los BTC reales
  btc_together = [Paragraph('Gráfico de los Bitcoins minados diarios:', styles['Heading2'])]
  daily_BTC = monthly_data_raw['BTC']
  plot_BTC = plt.figure()
  plt.stem(range(len(daily_BTC)), list(daily_BTC))
  plt.title('Bitcoins minados cada día del mes')
  btc_together.append(fig2image(plot_BTC))
  btc_together.append(Paragraph('Para el calculo del total en BTC se ha sumado los valores de los BTC minados cada día.', styles['BodyText']))
  story.append(KeepTogether(btc_together))

  # 5. Tabla con los valores del mes
  month_table_together = [Paragraph('Tabla detallada del mes: ', styles['Heading2'])]
  month_table_together.append(Paragraph(f'En la siguiente tabla se muestran los valores detallados del {month}, el promedio de la producción diaria en peta-hashes, el valor de la producción en USD ($) y los BTC minados:', styles['BodyText']))
  month_table_together.append(Spacer(10,10))
  average_hashrate_list = []
  for hashrate in monthly_data_raw['Average Hashrate']:
    if isinstance(hashrate, float):
      average_hashrate_list.append(round(hashrate, 2))
    else:
      average_hashrate_list.append(hashrate)

  tabla_month = {'Día': monthly_data_raw['Day'], 'Hashrate promedio': average_hashrate_list, 'USD': [round(value,2) for value in monthly_data_raw['USD']], 'BTC': [round(value,2) for value in monthly_data_raw['BTC']]}
  month_table_together = df2table(pd.DataFrame(data= tabla_month), month_table_together, style, table_alignment)
  story.append(KeepTogether(month_table_together))

  doc.build(story)

  
  # 4. Los dos graficos principales a la vez
  plot_together_list = [Paragraph('Gráficos de la producción:', styles['Heading2'])]
  plot_together_list.append(Paragraph('A continuación se muestrán los gráficos de la producción diaria. El gráfico de la izquierda muestra el hash rate (en peta-hashes) y el gráfico de la derecha muestra la producción de bitcoins diaria.', styles['BodyText']))
  plot_together_list.append(Spacer(10,10))
  plot_together = plt.figure(figsize= (7,4))
  plt.subplot(1,2,1)
  plt.bar(range(1,len(daily_hash)+1), list(daily_hash))
  plt.title('Hash Rate (peta-hashes)', wrap= True)
  plt.subplot(1,2,2)
  plt.bar(range(1,len(daily_BTC)+1), list(daily_BTC))
  plt.title('Bitcoins minados (BTC)', wrap= True)
  plt.tight_layout()
  plot_together_list.append(fig2image(plot_together))
  plot_together_list.append(Spacer(10,10))
  
  bottom_text ='Para el calculo del total en USD se ha multiplicado el valor diario de los peta-hashes por diez y se han sumado.'

  if list(daily_hash).count(0.0) > 0:
    bottom_text+= ' En el caso de los días que no ha habido producción se ha considerado como si se hubiera hasheado la media de los días que sí ha habido producción.'
  
  plot_together_list.append(Paragraph(bottom_text, styles['BodyText']))
  plot_together_list.append(Paragraph('Para el calculo del total en BTC se han sumado los valores de los BTC minados cada día.', styles['BodyText']))


  pdf_name = 'Report_' + month.replace('/','-') + '_'
  pdf_path = os.path.join(main_file_path, f'{pdf_name}.pdf')
  doc = create_basic_documnent(pdf_name= pdf_path, month=month)
  story_ = [Paragraph(f'Reporte de datos mensual', styles['Heading1'])]
  story_.append(Spacer(10,10))
  story_.append(KeepTogether(resumen_together))
  story_.append(Spacer(20,20))
  story_.append(KeepTogether(plot_together_list))
  story_.append(KeepTogether(month_table_together))
  doc.build(story_)