from App import app, db, engine
from flask import render_template, url_for, redirect, request, flash, g
from App.admin import Admin
from App.forms import LoginForm
from flask_login import login_user, logout_user, current_user

@app.route('/')
@app.route('/home')
def home_page():
    with engine.connect() as con:
        # grA = con.execute('SELECT nazwa, id_reprezentacja FROM mundial.view_gr(\'A\')')
        grA = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'A\' order by nazwa;')
        grB = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'B\' order by nazwa;')
        grC = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'C\' order by nazwa;')
        grD = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'D\' order by nazwa;')
        grE = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'E\' order by nazwa;')
        grF = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'F\' order by nazwa;')
        grG = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'G\' order by nazwa;')
        grH = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'H\' order by nazwa;')
    return render_template('home.html', a = grA, b = grB, c = grC, d = grD, e = grE, f = grF, g = grG, h = grH)

@app.route('/grupa/<gr>', methods=['GET', 'POST'])
def grupa_page(gr):
    with engine.connect() as con:
        # grupa = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.view_gr(\'{gr}\');')
        grupa = con.execute(f'SELECT nazwa, id_reprezentacja FROM mundial.reprezentacja WHERE grupa=\'{gr}\' order by nazwa;')
        mecze = con.execute(f'SELECT * FROM mundial.grupa_mecze_view WHERE grupa = \'{gr}\';')
    return render_template('grupa.html', grupa = grupa, mecze = mecze)

@app.route('/mecze')
def mecze_page():
    with engine.connect() as con:
        mecze = con.execute('SELECT * FROM mundial.wynik_view;')
    return render_template('mecze.html', items = mecze)

@app.route('/mecz_admin/<int:id_m>/<int:id_r1>/<int:w_r1>/<int:id_r2>/<int:w_r2>', methods=['GET', 'POST'])
def mecz_admin_page(id_m, id_r1, w_r1, id_r2, w_r2):
    with engine.connect() as con:
        mecz_id = id_m
        r1_id = id_r1
        r1_w = w_r1
        r2_id = id_r2
        r2_w = w_r2
        mecz = con.execute('SELECT * FROM mundial.wynik_view WHERE id_mecz =' + str(id_m) + ';')
        reprezentacja1 = con.execute('SELECT * FROM mundial.pilkarz WHERE id_reprezentacja=' + str(id_r1) + ';')
        reprezentacja2 = con.execute('SELECT * FROM mundial.pilkarz WHERE id_reprezentacja=' + str(id_r2) + ';')
        if request.method == 'POST':
            if request.form.get('submit') == 'Submit':
                w1 = str(request.form.get('wynik1'))
                w2 = str(request.form.get('wynik2'))
                if w1 == '0' and w2 == '0':
                    con.execute(f'DELETE FROM mundial.zdarzenie_boiskowe WHERE id_mecz={str(id_m)};')
                con.execute(f'UPDATE mundial.wynik_meczu SET wynik_reprezentacja1 = {w1}, wynik_reprezentacja2 = {w2} WHERE id_mecz ={str(id_m)};')
                return redirect(url_for('mecz_admin_page', id_m = mecz_id, id_r1 =r1_id, w_r1 = w1, id_r2 = r2_id, w_r2 = w2))
            if request.form.get('submit1') == 'Submit1':
                con.execute(f'DELETE FROM mundial.zdarzenie_boiskowe WHERE id_mecz={str(id_m)};')
                sum1 = 0
                sum2 = 0
                for i in range(26):
                    if w_r1>0:
                        sum1 += int(request.form[f'gole1_{i+1}'])
                    if w_r2>0:
                        sum2 += int(request.form[f'gole2_{i+1}'])
                if sum1 == w_r1 and sum2 == w_r2:
                    for i in range(26):
                        if w_r1>0:
                            if int(request.form[f'gole1_{i+1}']) > 0:
                                text = request.form[f'gole1_{i+1}']
                                if i < 9:
                                    i1 = '0' + str(i+1)
                                else:
                                    i1 = str(i+1)
                                con.execute(f'INSERT INTO mundial.zdarzenie_boiskowe (id_mecz, id_pilkarz, liczba_goli, id_reprezentacja) values ({id_m}, {r1_id}{i1}, {text}, {r1_id})')
                        if w_r2>0:
                            if int(request.form[f'gole2_{i+1}']) > 0:
                                text = request.form[f'gole2_{i+1}']
                                if i < 10:
                                    i1 = '0' + str(i+1)
                                else:
                                    i1 = str(i+1)
                                con.execute(f'INSERT INTO mundial.zdarzenie_boiskowe (id_mecz, id_pilkarz, liczba_goli, id_reprezentacja) values ({id_m}, {r2_id}{i1}, {text}, {r2_id})')
                return redirect(url_for('mecz_admin_page', id_m = mecz_id, id_r1 =r1_id, w_r1 = r1_w, id_r2 = r2_id, w_r2 = r2_w))
    return render_template('mecz_a.html', mecz_id = mecz_id, items = mecz, reprezentacja1 = reprezentacja1, reprezentacja2 = reprezentacja2)

@app.route('/mecz/<int:id_m>/<int:id_r1>/<int:id_r2>', methods=['GET', 'POST'])
def mecz_page(id_m, id_r1, id_r2):
    with engine.connect() as con:
        mecz_id = id_m
        mecz = con.execute(f'SELECT * FROM mundial.sedzia_mecz_view WHERE id_mecz = {str(id_m)};')
        r1_strz = con.execute(f'SELECT * FROM mundial.strzelcy_view WHERE id_mecz = {str(id_m)} AND id_reprezentacja = {str(id_r1)};')
        r2_strz = con.execute(f'SELECT * FROM mundial.strzelcy_view WHERE id_mecz = {str(id_m)} AND id_reprezentacja = {str(id_r2)};')
        stadion = con.execute(f'SELECT * FROM mundial.stadion_view WHERE id_mecz = {str(id_m)};')
    return render_template('mecz.html', mecz_id = mecz_id, items = mecz, strz_r1 = r1_strz, strz_r2 = r2_strz, stadion = stadion)

@app.route('/reprezentacje')
def reprezentacje_page():
    with engine.connect() as con:
        reprezentacje = con.execute('SELECT * FROM mundial.reprezentacja;')
        reprezentacje2 = con.execute('SELECT * FROM mundial.reprezentacja_view;')
    return render_template('reprezentacje.html', items = reprezentacje2, items2 = reprezentacje)

@app.route('/reprezentacja/<int:id_r>', methods=['GET', 'POST'])
def reprezentacja_page(id_r):
    with engine.connect() as con:
        reprezentacja = con.execute('SELECT * FROM mundial.pilkarz WHERE id_reprezentacja=' + str(id_r) + ';')
        # rep_nazwa = con.execute('SELECT mundial.rep_name(' + str(id_r) + ');')
        rep_nazwa = con.execute(f'SELECT nazwa from mundial.reprezentacja WHERE id_reprezentacja = {str(id_r)};')
        rep_nazwa1 = con.execute(f'SELECT nazwa from mundial.reprezentacja WHERE id_reprezentacja = {str(id_r)};')
        rep_nazwa = rep_nazwa.mappings().all()[0]['nazwa']
        rep_nazwa1 = rep_nazwa1.mappings().all()[0]['nazwa']
        mecze_rep = con.execute('SELECT * FROM mundial.wynik_view WHERE id_reprezentacja1 = \'' + str(id_r) + '\' OR id_reprezentacja2 = \'' + str(id_r) + '\';')
        id_rep = id_r
        mecz_count = con.execute('SELECT COUNT(id_mecz) FROM mundial.mecz_view WHERE id_reprezentacja1 = \'' + str(id_r) + '\' OR id_reprezentacja2 = \'' + str(id_r) + '\';')
        grupa = con.execute(f'SELECT grupa FROM mundial.reprezentacja WHERE id_reprezentacja = {str(id_r)};')
        kf = con.execute(f'SELECT konfederacja FROM mundial.reprezentacja_view WHERE id_reprezentacja = {str(id_r)};')
        selekcjoner = con.execute(f'SELECT * FROM mundial.selekcjoner_view WHERE id_reprezentacja = {str(id_r)};')
    return render_template('reprezentacja.html', items = reprezentacja, mecze = mecze_rep, id_rep = id_rep, id_png = 'images/flagi/' + str(id_rep) + '.png', m_count = mecz_count, rep_nazwa = rep_nazwa, rep_nazwa1 = rep_nazwa1, grupa = grupa, konfederacja = kf, selekcjoner = selekcjoner)

@app.route('/pilkarz/<int:id_p>')
def pilkarz_page(id_p):
    id_r = str(id_p)[:-2]
    with engine.connect() as con:
        mecze_rep = con.execute('SELECT * FROM mundial.wynik_view WHERE id_reprezentacja1 = \'' + str(id_r) + '\' OR id_reprezentacja2 = \'' + str(id_r) + '\';')
        pilkarz = con.execute(f'SELECT * FROM mundial.pilkarz_view WHERE id_pilkarz = {str(id_p)};')
    return render_template('pilkarz.html', mecze = mecze_rep, pilkarz = pilkarz, selekcjoner = False)

@app.route('/sedziowie')
def sedziowie_page():
    with engine.connect() as con:
        sedziowie = con.execute('SELECT * FROM mundial.sedziowie_view;')
    return render_template('sedziowie.html', items = sedziowie)

@app.route('/sedzia/<int:id_s>', methods=['GET', 'POST'])
def sedzia_page(id_s):
    with engine.connect() as con:
        mecze = con.execute(f'SELECT * FROM mundial.sedzia_mecz_view WHERE id_sedzia = {id_s};')
        sedzia = con.execute(f'SELECT * FROM mundial.sedziowie_view WHERE id_sedzia = {id_s};')
    return render_template('sedzia.html', items = sedzia, mecze = mecze)

@app.route('/stadiony')
def stadiony_page():
    with engine.connect() as con:
        stadiony = con.execute('SELECT * FROM mundial.stadion;')
    return render_template('stadiony.html', items = stadiony)

@app.route('/stadion/<int:id_st>')
def stadion_page(id_st):
    with engine.connect() as con:
        stadion = con.execute(f'SELECT * FROM mundial.stadion WHERE id_stadion = {id_st};')
        mecze = con.execute(f'SELECT * FROM mundial.stadion_mecze_view WHERE id_stadion = {str(id_st)};')
    return render_template('stadion.html', items = stadion, id_png = 'images/stadiony/' + str(id_st) + '.jpg', mecze = mecze)

@app.route('/selekcjonerzy')
def selekcjonerzy_page():
    with engine.connect() as con:
        selekcjonerzy = con.execute('SELECT * FROM mundial.selekcjoner_view ORDER BY nazwisko;')
    return render_template('selekcjonerzy.html', items = selekcjonerzy)

@app.route('/selekcjoner/<int:id_s>')
def selekcjoner_page(id_s):
    with engine.connect() as con:
        mecze_rep = con.execute('SELECT * FROM mundial.wynik_view WHERE id_reprezentacja1 = \'' + str(id_s) + '\' OR id_reprezentacja2 = \'' + str(id_s) + '\';')
        selekcjoner = con.execute(f'SELECT * FROM mundial.selekcjoner_view WHERE id_reprezentacja = {str(id_s)};')
    return render_template('pilkarz.html', mecze = mecze_rep, pilkarz = selekcjoner, selekcjoner = True)

@app.route('/konfederacje')
def konfederacje_page():
    with engine.connect() as con:
        konfederacje = con.execute('SELECT * FROM mundial.federacja;')
    return render_template('konfederacje.html', items = konfederacje)

@app.route('/konfederacja/<kf>')
def konfederacja_page(kf):
    with engine.connect() as con:
        konfederacja = con.execute(f'SELECT * FROM mundial.federacja WHERE nazwa = \'{kf}\';')
        druzyny = con.execute(f'SELECT id_reprezentacja, nazwa FROM mundial.reprezentacja_view WHERE konfederacja = \'{kf}\';')
        sedziowie = con.execute(f'SELECT * FROM mundial.sedziowie_view WHERE federacja = \'{kf}\';')
    return render_template('konfederacja.html', items = konfederacja, druzyny = druzyny, sedziowie = sedziowie)

@app.route('/admin/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Admin.query.first()
        if form.username.data == 'Admin' and form.password.data == 'AdminPass23':
            login_user(attempted_user)
            flash('Jestes zalogowany jako Admin!', category = 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Dane nieprawidlowe!', category='danger')
    if form.errors:
        for err in form.errors.values():
            flash(f'Wystapił błąd, te dane nie należą do Admina!', category='danger')
    return render_template('login.html', form = form)

@app.route('/admin/logout')
def logout_page():
    logout_user()
    flash('Zostałeś wylogowany i nie masz już uprawnień do edycji meczów!', category='info')
    return redirect(url_for('home_page'))

@app.route('/ranking')
def ranking_page():
    with engine.connect() as con:
        ranking = con.execute('SELECT * FROM mundial.ranking_strzelcow;')
    return render_template('ranking.html', items = ranking)