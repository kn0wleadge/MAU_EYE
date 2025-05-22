from flask import Flask, render_template, request
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.models import Publication, Source  # Импортируем вашу модель
from flask import redirect, url_for, flash
from fpdf import FPDF
from datetime import datetime, timedelta
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)  # логи SQL-запросов
app = Flask(__name__)
app.secret_key = 'key!!!'
DATABASE_URL = "postgresql+psycopg2://postgres:Kapibara@localhost:5432/MAU_EYE"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
@app.route('/add_source', methods=['GET', 'POST'])
def add_source():
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        source_type = request.form.get('source_type')
        
        if not all([name, url, source_type]):
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('add_source'))
        
        session = Session()
        try:
            new_source = Source(
                sname=name,
                surl=url,
                source_type=source_type,
                added_date = datetime.fromtimestamp(int(str(int(datetime.now().timestamp()))))
            )
            session.add(new_source)
            print("INSERTing))))")
            session.commit()
            session.close()
        except Exception as e:
            logging.info(f"Error during inserting Source - {e}")
        
        flash('Источник успешно добавлен', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_source.html')

@app.route('/sources')
def sources_list():
    session = Session()
    sources = session.query(Source).order_by(Source.added_date.desc()).all()
    session.close()
    return render_template('sources.html', sources=sources)
# Подключение к БД (замените на свои параметры)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/publications')
def publications():
    session = Session()
    
    # Получаем параметры фильтрации из запроса
    source_filter = request.args.get('source')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sentiment = request.args.get('sentiment')
    mau_only = request.args.get('mau_only') == 'on'
    
    # Строим запрос с фильтрами
    query = session.query(Publication)
    
    if source_filter:
        query = query.filter(Publication.psource.ilike(f"%{source_filter}%"))
    
    if date_from:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(Publication.pdate >= date_from)
    
    if date_to:
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        query = query.filter(Publication.pdate <= date_to)
    
    if sentiment and sentiment != 'all':
        query = query.filter(Publication.assesment == sentiment)
    
    if mau_only:
        query = query.filter(Publication.mau_mentioned == True)
    
    # Сортируем по дате публикации (новые сначала)
    publications = query.order_by(Publication.pdate.desc()).all()
    
    session.close()
    return render_template('publications.html', publications=publications)

@app.route('/publication/<int:pid>')
def publication_detail(pid):
    session = Session()
    publication = session.query(Publication).filter_by(pid=pid).first()
    session.close()
    return render_template('publication_detail.html', publication=publication)
@app.route('/generate_report')
def generate_report():
    period = request.args.get('period', 'week')  # week или month
    
    # Определяем даты для фильтрации
    end_date = datetime.now()
    if period == 'week':
        start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=30)
    
    session = Session()
    
    # Получаем публикации за период с упоминанием университета
    publications = session.query(Publication).filter(
        Publication.mau_mentioned == True,
        Publication.pdate >= start_date,
        Publication.pdate <= end_date
    ).order_by(Publication.pdate.desc()).all()
    
    session.close()
    
    # Создаем PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    
    # Заголовок
    pdf.cell(0, 10, f'Отчет по упоминаниям университета за {period} ({start_date.date()} - {end_date.date()})', 0, 1, 'C')
    pdf.ln(10)
    
    # Статистика
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10, f'Всего упоминаний: {len(publications)}', 0, 1)
    
    # Таблица с публикациями
    pdf.set_font('DejaVu', '', 10)
    col_widths = [20, 40, 30, 100]
    
    # Заголовки таблицы
    pdf.cell(col_widths[0], 10, 'Дата', 1)
    pdf.cell(col_widths[1], 10, 'Источник', 1)
    pdf.cell(col_widths[2], 10, 'Тональность', 1)
    pdf.cell(col_widths[3], 10, 'Ссылка', 1)
    pdf.ln()
    
    # Данные
    for pub in publications:
        pdf.cell(col_widths[0], 10, pub.pdate.strftime('%d.%m.%Y'), 1)
        pdf.cell(col_widths[1], 10, pub.psource[:30], 1)
        pdf.cell(col_widths[2], 10, pub.assesment, 1)
        pdf.cell(col_widths[3], 10, pub.purl[:60], 1)
        pdf.ln()
    
    # Сохраняем PDF
    filename = f"university_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(f"static/reports/{filename}")
    
    return render_template('report_generated.html', filename=filename)
@app.route('/generate_report', methods=['GET'])
def report_options():
    return render_template('generate_report.html')
@app.context_processor
def inject_now():
    return {'now': datetime.now()}


if __name__ == '__main__':
    app.run(debug=True)