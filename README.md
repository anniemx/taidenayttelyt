# Taidenäyttelyt

Sovellus tarjoaa yhteisöllisen alustan taidenäyttelyjen arvosteluun ja suosittelemiseen. 

Sovelluksessa on seuraavat ominaisuudet:

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään sovellukseen taidenäyttelyarvosteluja. Lisäksi käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään arvosteluja.
* Käyttäjä näkee sovellukseen lisätyt arvostelut. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät arvostelut.
* Käyttäjä pystyy etsimään arvosteluja hakusanalla, paikkakunnalla, museon tai gallerian nimellä tai arvosteluasteikolla (1-5 tähteä). Käyttäjä pystyy hakemaan sekä itse lisäämiään että muiden käyttäjien lisäämiä arvosteluja.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät jokaisesta käyttäjästä tilastoja ja käyttäjän lisäämät arvostelut.
* Käyttäjä pystyy valitsemaan arvostelulle yhden tai useamman luokittelun. Mahdolliset luokat ovat tietokannassa.
* Käyttäjä voi lisätä kommentin ja oman arvosanansa arvosteluasteikolla 1-5 tähteä jo annettuun arvosteluun. Näyttelyistä on siten mahdollista koostaa yhteinen keskiarvo, jota voidaan käyttää yleisen  mielipiteen indikaattorina.

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