# Taidenäyttelyt

Sovellus tarjoaa yhteisöllisen alustan taidenäyttelyjen arvosteluun ja suosittelemiseen sekä tietoja taidenäyttelyistä.

Sovelluksessa on seuraavat ominaisuudet:

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen. Käyttäjä voi lisätä profiilikuvan omassa profiilissaan.
* Käyttäjä pystyy lisäämään sovellukseen taidenäyttelyjä niiden perustietoineen. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään taidenäyttelyjä.
* Käyttäjä näkee sovellukseen lisätyt taidenäyttelyt. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät näyttelyt.
* Käyttäjä pystyy etsimään näyttelyjä hakusanalla, paikkakunnalla, museon tai gallerian nimellä. Käyttäjä pystyy hakemaan sekä itse lisäämiään että muiden käyttäjien lisäämiä näyttelyjä.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät näyttelyt.
* Käyttäjä pystyy valitsemaan näyttelylle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
* Käyttäjä voi lisätä arvion ja oman arvosanansa arvosteluasteikolla 1-5 tähteä taidenäyttelyyn. Näyttelyistä on siten mahdollista koostaa yhteinen keskiarvo, jota voidaan käyttää yleisen mielipiteen indikaattorina.

## Sovelluksen asennus ja käyttö

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Käynnistä sovellus näin:

```
$ flask run
```

Testaukset suurilla tietomäärillä:

Ensimmäisellä kerralla suurella tietomäärällä seed.py testatessa pisimpään pyyntö kesti 0.14s. Pyyntö oli näyttelyn numero 100000 tietojen hakeminen ja näyttäminen. 

Kun tietomäärää kasvatettiin:
user_count = 1000
exhibition_count = 10**6
comment_count = 10**7
niin pisimmillään pyyntö kesti 0.15, kun sovellus etsi tiedot näyttelystä id-numerolla 99950. 

Indeksien lisäämisen (CREATE INDEX idx_exhibitions_comments ON comments (exhibition_id);) jälkeen pisin pyyntö oli vain 0.1s, eikä eri tyyppiset pyynnöt eronneet ajassa toisistaan. 
