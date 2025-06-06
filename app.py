from flask import Flask, render_template, request
from sqlalchemy import create_engine, and_, or_, func, select
from sqlalchemy.orm import sessionmaker, joinedload
from datetime import datetime
from sqlalchemy import BigInteger
from database.models import Publication, Source 
from flask import redirect, url_for, flash
from fpdf import FPDF
from datetime import datetime, timedelta
from parser.vk_parser import get_group_data
from parser.tg_parser import get_chat_info
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)  # логи SQL-запросов
app = Flask(__name__)
app.secret_key = 'key!!!'
DATABASE_URL = "postgresql+psycopg2://postgres:Kapibara@localhost:5432/MAU_EYE"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_domain(url:str, source_type:str):
    domain = None
    #print(f"url - {url}, source_type - {source_type}")
    if source_type == "vk":
        if (url.find("?") != -1):
            domain = url[url.find("vk.com") + 7: url.find("?")]
        else:
            domain = url[url.find("vk.com") + 7:]
    elif source_type == "tg":
        domain = url[url.find("https://t.me/") + 13:]
    return domain

def get_source(url:str):
    source_type = None
    if (url.find("vk.com") != -1):
        source_type = "vk"
    elif (url.find("t.me") != -1):
        source_type = "tg" 
    session = Session()
    domain = get_domain(url, source_type)
    #print(f"domain - {domain}")
    source = session.query(Source).filter((Source.source_type == source_type) & (Source.sdomain == domain)).scalar()
    print(source)
    return source

@app.route('/add_source', methods=['GET', 'POST'])   
def add_source():
    if request.method == 'POST':
        url = request.form.get('url')
        source_type = None
        if (url.find("vk.com") != -1):
            source_type = "vk"
        elif (url.find("t.me") != -1):
            source_type = "tg"
        if not url:
            flash('URL обязателен для заполнения', 'danger')
            return redirect(url_for('add_source'))
        
        # Проверка, существует ли уже такой источник
        if get_source(url):
            flash('Такой источник уже добавлен', 'warning')
            return redirect(url_for('add_source'))

        session = Session()
        domain = get_domain(url, source_type)
        group_info = None
        if source_type == "vk":
            group_info = get_group_data(domain)
        elif source_type == "tg":
            group_info = get_chat_info(domain)

        try:
            new_source = Source(
                sid=group_info["id"],
                sname=group_info["name"],
                surl=url,
                source_type=source_type,
                sdomain=domain,
                added_date=datetime.fromtimestamp(int(str(int(datetime.now().timestamp()))))
            )
            session.add(new_source)
            logging.info(f"Inserting {source_type} group...")
            session.commit()
            flash('Источник успешно добавлен', 'success')
        except Exception as e:
            logging.info(f"Error during inserting Source - {e}")
            flash('Ошибка при добавлении источника', 'danger')
        finally:
            session.close()

        return redirect(url_for('index'))
    
    return render_template('add_source.html')

@app.route('/sources')
def sources_list():
    session = Session()
    sources = session.query(Source).order_by(Source.added_date.desc()).all()
    session.close()
    return render_template('sources.html', sources=sources)

@app.route('/toggle_source/<string:sid>', methods=['POST'])
def toggle_source(sid):
    new_status = request.json.get('is_active')
    session = Session()
    source = session.query(Source).filter(Source.sid == sid).first()
    if source:
        source.is_active = new_status
        session.commit()
        session.close()
        return {'success': True}
    else:
        session.close()
        return {'success': False, 'error': 'Источник не найден'}
@app.route('/delete_publication/<int:pid>', methods=['POST'])
def delete_publication(pid):
    session = Session()
    try:
        publication = session.query(Publication).filter_by(pid=pid).first()
        if publication:
            publication.deleted = True
            session.commit()
            return {'success': True}
        else:
            return {'success': False, 'error': 'Публикация не найдена'}, 404
    except Exception as e:
        session.rollback()
        return {'success': False, 'error': str(e)}, 500
    finally:
        session.close()
@app.route('/')
def index():
    session = Session()

    # 1. Публикации с упоминанием за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    mentions_by_day = session.query(
        func.date(Publication.pdate).label('date'),
        func.count(Publication.pid).label('count')
    ).filter(
        Publication.mau_mentioned == True,
        Publication.pdate >= week_ago,
        Publication.deleted == False
    ).group_by(
        func.date(Publication.pdate)
    ).all()

    dates = []
    mentions_count = []

    for i in range(7):
        current_date = (datetime.now() - timedelta(days=6 - i)).date()
        date_str = current_date.strftime('%d.%m')
        dates.append(date_str)
        count = next((item.count for item in mentions_by_day if item.date == current_date), 0)
        mentions_count.append(count)

    # 2. Средние охваты по дням (по всем постам с упоминанием)
    metrics_by_day = session.query(
        func.date(Publication.pdate).label('date'),
        func.avg(Publication.views).label('avg_views'),
        func.avg(Publication.likes).label('avg_likes'),
        func.avg(Publication.comments).label('avg_comments'),
        func.avg(Publication.reposts).label('avg_reposts')
    ).filter(
        Publication.mau_mentioned == True,
        Publication.pdate >= week_ago,
        Publication.deleted == False
    ).group_by(
        func.date(Publication.pdate)
    ).all()

    metrics_dict = {row.date: row for row in metrics_by_day}
    views, likes, comments, reposts = [], [], [], []

    for i in range(7):
        current_date = (datetime.now() - timedelta(days=6 - i)).date()
        metrics = metrics_dict.get(current_date)
        views.append(round(metrics.avg_views or 0, 1) if metrics else 0)
        likes.append(round(metrics.avg_likes or 0, 1) if metrics else 0)
        comments.append(round(metrics.avg_comments or 0, 1) if metrics else 0)
        reposts.append(round(metrics.avg_reposts or 0, 1) if metrics else 0)

    session.close()

    return render_template(
        'index.html',
        dates=dates,
        mentions_count=mentions_count,
        views=views,
        likes=likes,
        comments=comments,
        reposts=reposts
    )
@app.route('/publications')
def publications():
    session = Session()

    all_sources = session.query(Source).all()

    source_filter = request.args.get('source')
    source_type = request.args.get('source_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sentiment = request.args.get('sentiment')
    mau_only = request.args.get('mau_only') == 'on'
    sort_field = request.args.get('sort', 'views')
    sort_order = request.args.get('order', 'desc')

    query = session.query(Publication).filter(Publication.deleted == False).options(joinedload(Publication.source))

    if source_filter:
        query = query.join(Publication.source).filter(Source.sname.ilike(f"%{source_filter}%"))

    if source_type and source_type != 'all':
        query = query.join(Publication.source).filter(Source.source_type == source_type)

    if date_from:
        query = query.filter(Publication.pdate >= datetime.strptime(date_from, '%Y-%m-%d'))

    if date_to:
        query = query.filter(Publication.pdate <= datetime.strptime(date_to, '%Y-%m-%d'))

    if sentiment and sentiment != 'all':
        query = query.filter(Publication.assesment == sentiment)

    if mau_only:
        query = query.filter(Publication.mau_mentioned == True)

    sortable_fields = ['views', 'likes', 'comments', 'reposts', 'pdate']
    if sort_field in sortable_fields:
        sort_column = getattr(Publication, sort_field)
        query = query.order_by(sort_column.asc() if sort_order == 'asc' else sort_column.desc())
    else:
        query = query.order_by(Publication.pdate.desc())

    publications_list = query.all()
    session.close()

    return render_template('publications.html',
                           publications=publications_list,
                           all_sources=all_sources,
                           current_sort=sort_field,
                           current_order=sort_order,
                           reverse_order='asc' if sort_order == 'desc' else 'desc')

@app.route('/publication/<int:pid>')
def publication_detail(pid):
    session = Session()
    publication = session.query(Publication).options(joinedload(Publication.source)).filter_by(pid=pid).first()
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
    #get_source("https://t.me/Arctic_TV")