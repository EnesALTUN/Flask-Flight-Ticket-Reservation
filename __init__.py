import gc # Garbage collector
import datetime # tarih
import sqlite3 as sql # veritabanı
from functools import wraps # ekranda uyarı
from passlib.hash import sha256_crypt as sha256_crypt # password şifreleme
from flask import Flask, render_template, request, session, url_for, redirect, flash # web sunucusu ve sayfa yönlendirmeleri için

app = Flask(__name__) # web sunucusu oluştur
app.secret_key = "EbruBETÜL" # password şifreleme için 

conn = sql.connect('veritabani.db') # Veritabanı dosya adını belirterek bağlantı yapıldı
conn.execute("""CREATE TABLE IF NOT EXISTS kullanicilar (
	TCNo varchar(11) PRIMARY KEY NOT NULL, 
	Ad varchar(50) NOT NULL, 
	Soyad varchar(50) NOT NULL, 
	TelNo varchar(20), 
	Email varchar(50) NOT NULL, 
	Bakiye INT, 
	Bonus INT, 
	Parola varchar(20) NOT NULL, 
	Rol varchar(2) NOT NULL
	)
""") # kullanıcılar tablosu yoksa oluşturuldu ve ilgili alanlar eklendi

conn.execute("""CREATE TABLE IF NOT EXISTS biletler (
	BiletID INTEGER PRIMARY KEY AUTOINCREMENT,
	TCNo nvarchar(11) NOT NULL,
	KoltukID nvarchar(11) NOT NULL,
	BagajNo nvarchar(11),
	UcusID nvarchar(11),
	AlinmaTarih datetime NOT NULL,
	CONSTRAINT fk_user_tc FOREIGN KEY (TCNo) REFERENCES kullanicilar(TCNo),
	CONSTRAINT fk_ucus FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID),
	CONSTRAINT fk_koltuk FOREIGN KEY (KoltukID) REFERENCES koltuk(UcusID)
	)
""")  # biletler tablosu yoksa oluşturuldu ve ilgili alanlar eklendi

conn.execute("""CREATE TABLE IF NOT EXISTS sepet (
	SepetID INTEGER PRIMARY KEY AUTOINCREMENT,
	TCNo varchar(11),
	KoltukID varchar(11),
	UcusID varchar(11),	
	CONSTRAINT fk_user_tc2 FOREIGN KEY (TCNo) REFERENCES kullanicilar(TCNo),
	CONSTRAINT fk_ucus2 FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID)
	)
""") # sepet tablosu yoksa oluşturuldu ve ilgili alanlar eklendi

conn.execute("""CREATE TABLE IF NOT EXISTS ucuslar (
	UcusID INTEGER PRIMARY KEY AUTOINCREMENT,
	KalkisYeri varchar(30),
	InisYeri nvarchar(30),
	Fiyat INT,
	Tarih datetime,
	KoltukID varchar(11),
	CONSTRAINT fk_koltuk2 FOREIGN KEY (KoltukID) REFERENCES koltuk(UcusID)
	)
""") # ucuslar tablosu yoksa oluşturuldu ve ilgili alanlar eklendi

conn.execute("""CREATE TABLE IF NOT EXISTS koltuk (
	UcusID INTEGER PRIMARY KEY AUTOINCREMENT,
	Koltuk1 INT,
	Koltuk2 INT,
	Koltuk3 INT,
	Koltuk4 INT,
	Koltuk5 INT,
	Koltuk6 INT,
	Koltuk7 INT,
	Koltuk8 INT,
	Koltuk9 INT,
	Koltuk10 INT,
	DolulukOrani INT,
	CONSTRAINT fk_ucus3 FOREIGN KEY (UcusID) REFERENCES ucuslar(UcusID)
	)
""") # koltuk tablosu yoksa oluşturuldu ve ilgili alanlar eklendi

conn.commit() # Yapılan işlemleri veritabanına işle
conn.close() # Veritabanı bağlantısını kapat

# GİRİŞ GEREKLİLİĞİ İÇİN
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session: # Giriş yapıldıysa
            return f(*args, **kwargs)
        else:
            flash("Öncelikle giriş yapmalısınız!!!") # Ekranda gösterilecek uyarı
            return redirect(url_for('giris')) # giris fonksiyonunu çalıştır
    return wrap

# ADMİN GİRİŞİ GEREKLİLİĞİ İÇİN
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('admin'): # admin girişi yapıldıysa
            return f(*args, **kwargs)
        else:
            flash("Bu sayfa için yetkiniz bulunmamaktadır.")
            return redirect(url_for('home'))
    return wrap

# ANASAYFA
@app.route('/')
def home():
    con = sql.connect("veritabani.db")
    con.row_factory= sql.Row

    cur= con.cursor() # veritabanında bulunan tablolarda gezinmek için imleç oluştur
    cur.execute("select * from ucuslar")

    rows= cur.fetchall() # tüm kayıtları getir
    return render_template("index.html", ucuslar = rows)

# GİRİŞ YAP SAYFASI
@app.route('/giris/')
def giris():
    return render_template("giris.html", mesaj = "Kayıt eklendi")

# KAYIT OL SAYFASI
@app.route('/kayit/')
def kayit():
    return render_template("kayit.html")

# KAYIT EKLE
@app.route('/kayit_ekle', methods = ['POST', 'SET'])
def kayit_ekle():
    if request.method == 'POST':
        try:
            TC = request.form['TC'] # Formdan gelen name' i "TC" olan veriyi al
            Ad = request.form['Ad']
            Soyad = request.form['Soyad']
            Email = request.form['Email']
            Tel = request.form['Tel']
            Parola = sha256_crypt.hash(str(request.form['Parola'])) # Formdan gelen parolayı al hash ile şifrele
            Bakiye = 0
            Bonus = 0
            Rol = 0 # Rol = 0 Üye, Rol = 1 Admin

            with sql.connect("veritabani.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO kullanicilar (TCNo,Ad,Soyad,TelNo,Email,Bakiye,Bonus,Parola,Rol) values (?,?,?,?,?,?,?,?,?)", (TC,Ad,Soyad,Tel,Email,str(Bakiye),str(Bonus),Parola,str(Rol)))

                con.commit()
                msg = "Kayıt eklendi"
        except:
            con.rollback()
            msg = "Kayıt eklenirken hata oluştu"
        finally:
            con.close()
            return render_template("giris.html", mesaj = msg)
    return render_template('/home')

# GİRİŞ YAPA TIKLADIGIN ZAMAN
@app.route('/login/', methods=['GET', 'POST'])
def login():
	conn = sql.connect("veritabani.db")
	c= conn.cursor()
	if request.method == 'POST':
		c.execute("""SELECT * FROM kullanicilar WHERE TCNo = '%s'"""%(request.form['TC']))
        
		result=c.fetchone()
		tc= result[0]
		pas= result[7]
		role= result[8]
		if (tc == request.form['TC'] and sha256_crypt.verify(request.form['Parola'],pas)):
			session['logged_in']=True
			session['username']=tc
			if role=="0":
				session['admin']=False
			elif role=="1":
				session['admin']=True
			else:
				session['admin']=False
			gc.collect()
			flash("Başarıyla giriş yaptınız")
		else:
			flash("Hatalı giriş yaptınız. Tekrar deneyiniz.")
	return redirect(url_for('home'))

# HESABIM SAYFASI
@app.route('/hesabim')
@login_required
def hesabim():
	con = sql.connect("veritabani.db")
	con.row_factory= sql.Row

	cur= con.cursor()
	cur.execute("SELECT * FROM kullanicilar WHERE TCNo = ?",[session['username']]) # Kullanıcı bilgilerini çek
	rows= cur.fetchone()

	cur.execute("SELECT * FROM sepet INNER JOIN ucuslar ON sepet.UcusID = ucuslar.UcusID WHERE sepet.TCNo=?", [session['username']]) # Sepet ve sepetteki kayda ait ucuşun bilgilerini çek
	sepetBilgileri_ucusBilgileri = cur.fetchall()

	return render_template("hesabim.html", hesapbilgileri = rows, sepetBilgileri_ucusBilgileri = sepetBilgileri_ucusBilgileri)

# ADMİN SAYFASI
@app.route("/admin")
@admin_required
def adminSayfa():
	return render_template("admin.html")

# UÇUŞ EKLEME BAŞLANGIÇ
@app.route("/ucus_ekle")
@admin_required
def ucus_ekle():
    return render_template("ucus_ekle.html")

@app.route("/ucusekle", methods = ['POST', 'SET'])
@admin_required
def ucusekle():
	if request.method == 'POST':
		try:
			con = sql.connect("veritabani.db")
			con.row_factory = sql.Row
			cur = con.cursor()

			cur.execute("INSERT INTO koltuk (Koltuk1,Koltuk2,Koltuk3,Koltuk4,Koltuk5,Koltuk6,Koltuk7,Koltuk8,Koltuk9,Koltuk10,DolulukOrani) VALUES (0,0,0,0,0,0,0,0,0,0,0)")
			
			cur.execute("SELECT * FROM koltuk ORDER BY UcusID DESC LIMIT 1")
			sonuclar=cur.fetchall()

			KalkisYeri = request.form['kalkisYeri']
			InisYeri = request.form['inisYeri']
			Fiyat = request.form['fiyat']
			Tarih = request.form['tarih']

			cur.execute("INSERT INTO ucuslar (KalkisYeri,InisYeri,Fiyat,Tarih,KoltukID) values (?,?,?,?,?)", (KalkisYeri,InisYeri,Fiyat,Tarih,sonuclar[0][0]))

			con.commit()
		except:
			flash("HATA")
			con.rollback()
		finally:
			con.close()
	return redirect(url_for('home'))
# UÇUŞ EKLEME BİTİŞ

# UÇUŞ GÜNCELLEME BAŞLANGIÇ
@app.route("/ucus_duzenle")
@admin_required
def ucus_duzenle():
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row

	cur= con.cursor()
	cur.execute("select * from ucuslar")

	rows= cur.fetchall()
	return render_template("ucus_duzenle.html", ucuslar = rows)

@app.route("/ucusduzenle", methods = ['POST', 'SET'])
@admin_required
def ucusduzenle():
	if request.method == 'POST':
		try:
			UcusID = request.form['UcusID']
			with sql.connect("veritabani.db") as con:
				con.row_factory = sql.Row
				cur = con.cursor()
				cur.execute("SELECT * FROM ucuslar WHERE UcusID = ?", [UcusID])
				sonuclar = cur.fetchone()
		except:
			con.rollback()
			flash("HATA")
		finally:
			con.close()
			return render_template("ucus_guncelleme.html", kayit = sonuclar)
	return render_template("index.html")

@app.route("/ucusguncelle/<id>", methods = ['POST', 'SET'])
@admin_required
def ucusguncelle(id=0):
	conn = sql.connect("veritabani.db")
	conn.row_factory = sql.Row

	cur = conn.cursor()
	
	if request.method == 'POST':
		kalkisYeri = request.form['kalkisYeri']
		inisYeri = request.form['inisYeri']
		tarih = request.form['tarih']
		fiyat = request.form['fiyat']
		cur.execute("""UPDATE ucuslar SET KalkisYeri='%s', InisYeri='%s', Fiyat='%s', Tarih='%s' WHERE UcusID='%s'"""%(kalkisYeri,inisYeri,fiyat,str(tarih),id))
		conn.commit()
		conn.close()
		gc.collect()
		flash("Uçuş başarıyla güncellendi")
	return redirect(url_for('home'))
# UÇUŞ GÜNCELLEME BİTİŞ

# UÇUŞ SİL BAŞLANGIÇ
@app.route("/ucus_sil")
@admin_required
def ucus_sil():
	con = sql.connect("veritabani.db")
	con.row_factory= sql.Row

	cur= con.cursor()
	cur.execute("select * from ucuslar")

	rows= cur.fetchall()
	return render_template("ucus_sil.html", ucuslar = rows)

@app.route("/ucussilme", methods = ['POST', 'SET'])
@admin_required
def ucussilme():
	if request.method == 'POST':
		UcusID = request.form['UcusID']

		conn = sql.connect("veritabani.db")
		conn.row_factory = sql.Row

		cur = conn.cursor()
		cur.execute("DELETE FROM ucuslar WHERE UcusID=?",[UcusID])
		cur.execute("DELETE FROM koltuk WHERE UcusID=?",[UcusID])
		conn.commit()
		conn.close()
		gc.collect()
		flash("İlgili uçuş başarıyla silindi")
		return redirect(url_for('home'))
	else:
		flash("Silme işleminde hata oluştu")
		return redirect(url_for('home'))
# UÇUŞ SİL BİTİŞ

# UÇUŞ DETAYLARI
@app.route("/ucusdetay/<id>", methods = ['POST', 'SET'])
def ucusdetay(id=0):
	if request.method == 'POST':
		UcusID = id
		con = sql.connect("veritabani.db")
		con.row_factory= sql.Row

		cur= con.cursor()
		cur.execute("select * from ucuslar WHERE UcusID=?", [UcusID])
		ucuslar= cur.fetchall()

		cur.execute("SELECT * FROM koltuk WHERE UcusID=?", [UcusID])
		koltuk = cur.fetchone()

		cur.execute("SELECT * FROM sepet INNER JOIN koltuk ON sepet.UcusID = koltuk.UcusID WHERE sepet.SepetID=?", [id])
		koltuklar = cur.fetchone()
		return render_template("ucus_detay.html", ucuslar = ucuslar, koltuklar = koltuklar, koltuk = koltuk)
	else:
		flash("HATA")
		return redirect(url_for('home'))

# ÜYE ÇIKIŞ
@app.route("/logout/")
@login_required
def logout():
	con = sql.connect("veritabani.db")
	cur= con.cursor()

	cur.execute("DELETE FROM sepet WHERE TCNo=?", [session['username']])
	con.commit()	

	session.clear()
	flash("Başarı ile çıkış yaptınız.")
	gc.collect()

	return redirect(url_for('home'))

# SEPET EKLEME
@app.route("/sepetekle/<id>", methods = ['POST', 'SET'])
@login_required
def sepetekle(id=0):
	if request.method == 'POST':
		UcusID = id
		KoltukNo = request.form['Koltuk']
		KoltukNoStn = "Koltuk"+KoltukNo
		with sql.connect("veritabani.db") as con:
			con.row_factory = sql.Row
			cursor = con.cursor()

			cursor.execute("SELECT * FROM koltuk WHERE UcusID=?", [UcusID])
			ucusKayit = cursor.fetchone()

			if ucusKayit[KoltukNoStn] == 0:
				cursor.execute("INSERT INTO sepet (TCNo,KoltukID,UcusID) VALUES (?,?,?)", (str(session['username']),str(KoltukNo),str(UcusID)))
				con.commit()
				flash("BAŞARILI")
			else:
				flash("REZERVE EDİLMİŞ")
	else:
		flash("HATA")
	return redirect(url_for('home'))

# SEPET SİLME
@app.route("/sepetsil/<id>")
@login_required
def sepetsil(id=0):
	con = sql.connect("veritabani.db")
	cur = con.cursor()

	cur.execute("DELETE FROM sepet WHERE SepetID=?", [id])
	con.commit()

	flash("SEPETTEN BAŞARIYLA SİLİNDİ")
	return redirect(url_for('hesabim'))

# SEPETİ BOŞALT
@app.route("/sepetbosalt")
@login_required
def sepetbosalt():
	con = sql.connect("veritabani.db")
	cur = con.cursor()

	cur.execute("DELETE FROM sepet WHERE TCNo=?", [session['username']])
	con.commit()

	con.close()
	flash("SEPET BOŞALTILDI")
	return redirect(url_for('hesabim'))

# SEPET GÜNCELLE
@app.route("/sepetguncelle/<id>")
@login_required
def sepetguncelle(id=0):
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	cur.execute("SELECT * FROM sepet INNER JOIN koltuk ON sepet.UcusID = koltuk.UcusID WHERE sepet.SepetID=?", [id])
	sepet_koltukBigileri = cur.fetchone()

	return render_template("sepet_guncelle.html", id = id, sepet_koltukBigileri = sepet_koltukBigileri)

# SEPET GÜNCELLE -> KOLTUK GÜNCELLE
@app.route("/koltukGuncelle/<id>/<koltukNo>/<ucusID>", methods = ['POST', 'GET'])
@login_required
def koltukGuncelle(id=0,koltukNo=0,ucusID=0):
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	koltukNo = "Koltuk" + koltukNo #eski koltuk numarası sütunu
	KoltukNo = request.form['Koltuk'] #yeni koltuk numarası
	
	cur.execute("SELECT * FROM koltuk WHERE UcusID=?", [ucusID])
	sonuc = cur.fetchone()

	if sonuc[int(KoltukNo)] == 0:
		cur.execute("UPDATE sepet SET KoltukID=? WHERE SepetID=?", [KoltukNo,id])
		con.commit()

		flash("Koltuk numarası başarıyla güncellendi")
	else:
		flash("Seçilen koltuk numarası rezerve edilmiş")

	con.close()
	return redirect(url_for('hesabim'))

# UÇUŞ ARAMA
@app.route("/ucusfiltre", methods = ['POST', 'GET'])
def ucusfiltre():
	KalkisYeri = request.form["KalkisYeri"]
	InisYeri = request.form["InisYeri"]
	Tarih = request.form["Tarih"]

	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	cur.execute("SELECT * FROM ucuslar WHERE KalkisYeri=? and InisYeri=? and Tarih=?", [KalkisYeri,InisYeri,Tarih])
	sonuclar = cur.fetchall()

	if sonuclar == []:
		flash("Aranan kriterlerde uçuş bulunamadı")
		return redirect(url_for('home'))
	else:
		return render_template("ucus_filtre.html", ucuslar = sonuclar)

# BAKİYE YÜKLE SAYFASI
@app.route("/bakiyeyukle")
@login_required
def bakiyeyukle():
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row
	cur = con.cursor()

	cur.execute("SELECT * FROM kullanicilar WHERE TCNo=?", [session['username']])
	sonuc = cur.fetchone()
	return render_template("bakiye_yukle.html", bakiye = sonuc[5])

# BAKİYE YÜKLEME
@app.route("/bakiyeYukleme", methods = ['POST', 'SET'])
@login_required
def bakiyeYukleme():
	if request.method == 'POST':
		yuklenecekTutar = request.form["Tutar"]
		con = sql.connect("veritabani.db")
		con.row_factory = sql.Row
		cur = con.cursor()

		cur.execute("SELECT * FROM kullanicilar WHERE TCNo=?", [session['username']])
		sonuc = cur.fetchone()

		yeniTutar = sonuc[5] + int(yuklenecekTutar)

		cur.execute("UPDATE kullanicilar SET Bakiye=? WHERE TCNo=?", [yeniTutar,session['username']])
		con.commit()
		con.close()

		flash("Bakiye başarıyla yüklendi.")
		return redirect(url_for('hesabim'))
	else:
		return redirect(url_for('home'))

# REZERVE
@app.route("/rezerve/<id>")
@login_required
def rezerve(id=0):
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row

	cur = con.cursor()

	cur.execute("SELECT * FROM kullanicilar WHERE TCNo=?", [session['username']])
	kullaniciBilgi = cur.fetchone()
	
	cur.execute("SELECT * FROM sepet WHERE SepetID=?", [id])
	sepetBilgi = cur.fetchone()

	cur.execute("SELECT * FROM ucuslar WHERE UcusID=?", sepetBilgi[3])
	ucusBilgi = cur.fetchone()

	cur.execute("SELECT * FROM koltuk WHERE UcusID=?", [sepetBilgi[3]])
	koltukBilgi = cur.fetchone()

	DolulukOran = koltukBilgi[11] + 1

	KoltukNoStn = "Koltuk" + sepetBilgi[2]
	YeniBakiye = kullaniciBilgi[5] - ucusBilgi[3] # BAKİYEDEN BİLET FİYATINI ÇIKART
	YeniBonus = kullaniciBilgi[6] + (ucusBilgi[3] * 0.03) # BİLET FİYATININ %3 Ü KADAR BONUS EKLE
	BagajNo = kullaniciBilgi[0] + sepetBilgi[3] + sepetBilgi[2] # BAGAJ NO OLUŞTUR
	AlinmaTarih = datetime.datetime.now()

	AlinmaTarih = AlinmaTarih.strftime("%d %b %Y %H:%M:%S") # ALINMA TARİHİ FORMATINI DÜZENLE

	if YeniBakiye >= 0: # KULLANICI BAKİYESİ BİLET FİYATINDAN BÜYÜK VEYA EŞİT Mİ?
		cur.execute("UPDATE kullanicilar SET Bakiye=?, Bonus=? WHERE TCNo=?", [YeniBakiye,YeniBonus,session['username']]) # KULLANICI BAKİYESİNİ VE BONUSU GÜNCELLE
		cur.execute("DELETE FROM sepet WHERE SepetID=?", [id]) # SEPETTEKİ KAYDI SİL
		cur.execute("UPDATE koltuk SET " + KoltukNoStn + "=1, DolulukOrani=? WHERE UcusID=?", [DolulukOran,ucusBilgi[5]]) # KOLTUĞU REZERVE ET
		cur.execute("INSERT INTO biletler (TCNo,KoltukID,BagajNo,UcusID,AlinmaTarih) VALUES (?,?,?,?,?)", [session['username'],sepetBilgi[2],str(BagajNo),sepetBilgi[3],AlinmaTarih]) # BİLETLER TABLOSUNA EKLE
		con.commit()
		flash("BİLET BAŞARIYLA SATIN ALINDI")
	else:
		flash("BAKİYE YETERSİZ, BİLETİ SATIN ALMAK İÇİN BAKİYE YÜKLEYİNİZ")
	
	con.close()
	return redirect(url_for('hesabim'))

# BONUS REZERVE
@app.route("/bonusrezerve/<id>")
@login_required
def bonusrezerve(id=0):
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row

	cur = con.cursor()

	cur.execute("SELECT * FROM kullanicilar WHERE TCNo=?", [session['username']])
	kullaniciBilgi = cur.fetchone()
	
	cur.execute("SELECT * FROM sepet WHERE SepetID=?", [id])
	sepetBilgi = cur.fetchone()

	cur.execute("SELECT * FROM ucuslar WHERE UcusID=?", sepetBilgi[3])
	ucusBilgi = cur.fetchone()

	cur.execute("SELECT * FROM koltuk WHERE UcusID=?", [sepetBilgi[3]])
	koltukBilgi = cur.fetchone()

	DolulukOran = koltukBilgi[11] + 1

	KoltukNoStn = "Koltuk" + sepetBilgi[2]
	YeniBonus = kullaniciBilgi[6] - ucusBilgi[3] # BONUSTAN BİLET FİYATINI ÇIKART
	BagajNo = kullaniciBilgi[0] + sepetBilgi[3] + sepetBilgi[2] # BAGAJ NO OLUŞTUR
	AlinmaTarih = datetime.datetime.now()

	if kullaniciBilgi[6] >= ucusBilgi[3]: # KULLANICI BAKİYESİ BİLET FİYATINDAN BÜYÜK VEYA EŞİT Mİ?
		cur.execute("UPDATE kullanicilar SET Bonus=? WHERE TCNo=?", [YeniBonus,session['username']]) # KULLANICI BAKİYESİNİ VE BONUSU GÜNCELLE
		cur.execute("DELETE FROM sepet WHERE SepetID=?", [id]) # SEPETTEKİ KAYDI SİL
		cur.execute("UPDATE koltuk SET " + KoltukNoStn + "=1, DolulukOrani=? WHERE UcusID=?", [DolulukOran,ucusBilgi[5]]) # KOLTUĞU REZERVE ET
		cur.execute("INSERT INTO biletler (TCNo,KoltukID,BagajNo,UcusID,AlinmaTarih) VALUES (?,?,?,?,?)", [session['username'],sepetBilgi[2],str(BagajNo),sepetBilgi[3],AlinmaTarih]) # BİLETLER TABLOSUNA EKLE
		con.commit()
		flash("BİLET BAŞARIYLA SATIN ALINDI")
	else:
		flash("BONUS YETERSİZ, BİLETİ SATIN ALMAK İÇİN BAKİYE YÜKLEYİNİZ")
	
	con.close()
	return redirect(url_for('hesabim'))

# GEÇMİŞ BİLETLERİ GÖSTER
@app.route("/biletgoster")
@login_required
def biletgoster():
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row

	cur = con.cursor()

	cur.execute("SELECT * FROM biletler INNER JOIN ucuslar ON biletler.UcusID = ucuslar.UcusID WHERE biletler.TCNo=?", [session['username']])
	gecmisBiletler = cur.fetchall()

	con.close()
	return render_template("bilet_goster.html", gecmisBiletler = gecmisBiletler)

# UÇUŞ DOLULUK ORANI
@app.route("/ucusdoluluk")
def ucusdoluluk():
	return render_template("ucus_doluluk.html")

# UÇUŞ DOLULUK ORANI HESABI
@app.route("/ucus_doluluk_hesabi", methods=['POST', 'GET'])
def ucus_doluluk_hesabi():
	if request.method == 'POST':
		baslangicTarih = request.form['baslangicTarih']
		bitisTarih = request.form['bitisTarih']

		con = sql.connect("veritabani.db")
		con.row_factory= sql.Row
		cur= con.cursor()

		cur.execute("SELECT * FROM ucuslar INNER JOIN koltuk ON ucuslar.KoltukID = koltuk.UcusID WHERE ucuslar.Tarih BETWEEN ? AND ? ORDER BY koltuk.DolulukOrani DESC", [baslangicTarih,bitisTarih])
		ucuslar = cur.fetchall()

		if ucuslar == []:
			flash("Girilen tarih aralığında uçuş bulunamadı")
			return redirect(url_for('home'))
		else:
			return render_template("ucus_doluluklari.html", ucuslar=ucuslar)
	else:
		return redirect(url_for('home'))

# ÜYE LİSTELE
@app.route("/uye_listele")
def uye_listele():
	con = sql.connect("veritabani.db")
	con.row_factory = sql.Row
	cursor = con.cursor()

	cursor.execute("SELECT * FROM kullanicilar")
	kullanicilar = cursor.fetchall()
	return render_template("uye_listele.html", kullanicilar = kullanicilar)

@app.route("/face")
def face():
	return render_template("faceYonlendir.html")

@app.route("/faceYonlendir", methods=['POST', 'GET'])
def faceAktar():
	name = request.form['facename']
	return redirect("https://www.facebook.com/" + name)


if __name__ == '__main__':
    app.run(debug=True)