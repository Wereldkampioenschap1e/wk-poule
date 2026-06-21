# ============================================================
#   WK POULE 2026 – Kompas Publishing
#   app.py  |  Streamlit Cloud deployment (Volledig & Gecorrigeerd)
# ============================================================

import json
import re
import streamlit as st
import streamlit.components.v1 as components
import requests

# ────────────────────────────────────────────────────────────
# 0. CONSTANTEN
# ────────────────────────────────────────────────────────────

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbznnUcqVJOZMc7g8AbT4zCZXQNBTHrzQqL9N7SKU4l07O-i4ieRgWznsbQS7-OMGZXq"
    "/exec"
)

DATASTUDIO_URL = (
    "https://datastudio.google.com/embed/reporting/"
    "bc9d502e-c325-4e39-8d4c-be767d896971/page/ZdQ0F?refresh=15"
)

# ── Zet op "Ronde 2" of "Ronde 3" om naar de volgende ronde te schakelen ──
HUIDIGE_RONDE = "Ronde 3"

# ── Wedstrijden per speelronde (elk 24 groepsfase-duels) ──────

WEDSTRIJDEN_R1: list[str] = [
    "Mexico - Zuid-Afrika", "Zuid-Korea - Tsjechië", "Canada - Bosnië & Herzegovina", "Verenigde Staten - Paraguay",
    "Australië - Turkije", "Qatar - Zwitserland", "Brazillië - Marokko", "Haïti - Schotland", "Duitsland - Curaçao",
    "Nederland - Japan", "Ivoorkust - Ecuador", "Zweden - Tunesië", "Spanje - Kaapverdië", "België - Egypte",
    "Saoedi-Arabië - Uruguay", "Iran - Nieuw-Zeeland", "Oostenrijk - Jordanië", "Frankrijk - Senegal",
    "Irak - Noorwegen", "Argentinië - Algerije", "Portugal - Congo", "Engeland - Kroatië", "Ghana - Panama",
    "Oezbekistan - Colombia",
]

WEDSTRIJDEN_R2: list[str] = [
    "Tsjechië - Zuid-Afrika", "Zwitserland - Bosnië & Herzegovina", "Canada - Qatar", "Mexico - Zuid-Korea",
    "Turkije - Paraguay", "Verenigde Staten - Australië", "Schotland - Marokko", "Brazillië - Haïti",
    "Tunesië - Japan", "Nederland - Zweden", "Duitsland - Ivoorkust", "Ecuador - Curaçao",
    "Spanje - Saoedi-Arabië", "België - Iran", "Uruguay - Kaapverdië", "Nieuw-Zeeland - Egypte",
    "Argentinië - Oostenrijk", "Frankrijk - Irak", "Noorwegen - Senegal", "Jordanië - Algerije",
    "Portugal - Oezbekistan", "Engeland - Ghana", "Panama - Kroatië", "Colombia - Congo",
]

WEDSTRIJDEN_R3: list[str] = [
    "Bosnië & Herzegovina - Qatar", "Zwitserland - Canada", "Marokko - Haïti", "Schotland - Brazillië",
    "Tsjechië - Mexico", "Zuid-Afrika - Zuid-Korea", "Curaçao - Ivoorkust", "Ecuador - Duitsland",
    "Japan - Zweden", "Tunesië - Nederland", "Paraguay - Australië", "Turkije - Verenigde Staten",
    "Noorwegen - Frankrijk", "Senegal - Irak", "Kaapverdië - Saoedi-Arabië", "Uruguay - Spanje",
    "Egypte - Iran", "Nieuw-Zeeland - België", "Kroatië - Ghana", "Panama - Engeland",
    "Colombia - Portugal", "Congo - Oezbekistan", "Algerije - Oostenrijk", "Jordanië - Argentinië",
]

WEDSTRIJDEN: list[str] = {
    "Ronde 1": WEDSTRIJDEN_R1,
    "Ronde 2": WEDSTRIJDEN_R2,
    "Ronde 3": WEDSTRIJDEN_R3,
}[HUIDIGE_RONDE]

_PH      = "-- Maak een keuze --"
_PH_LAND = "-- Selecteer een land --"

GELE_KAARTEN_OPTIES: list[str] = [_PH, "0-2 gele kaarten", "3-4 gele kaarten", "5+ gele kaarten"]
TIJD_DOELPUNT_OPTIES: list[str] = [_PH, "Geen doelpunt", "1–15 min", "16–30 min", "31–45+ min", "46–60 min", "61–75 min", "76–90+ min"]

LANDEN: list[str] = sorted([
    "Algerije", "Argentinië", "Australië", "België", "Bosnië & Herzegovina", "Brazillië", "Canada", "Colombia",
    "Congo", "Curaçao", "Duitsland", "Ecuador", "Egypte", "Engeland", "Frankrijk", "Ghana", "Haïti", "Irak", "Iran",
    "Ivoorkust", "Japan", "Jordanië", "Kaapverdië", "Kroatië", "Marokko", "Mexico", "Nederland", "Nieuw-Zeeland", "Noorwegen",
    "Oezbekistan", "Oostenrijk", "Panama", "Paraguay", "Portugal", "Qatar", "Saoedi-Arabië", "Schotland", "Senegal", "Spanje",
    "Tsjechië", "Tunesië", "Turkije", "Uruguay", "Verenigde Staten", "Zuid-Afrika", "Zuid-Korea", "Zweden", "Zwitserland",
])

_UITSLAG_RE = re.compile(r"^(10|[0-9])-(10|[0-9])$")

_SPELERS_RAW: list[str] = [
    # Mexico
    "Jorge Sánchez", "Israel Reyes", "César Montes", "Johan Vásquez", "Jesús Gallardo", "Mateo Chávez", "Luis Romo",
    "Erik Lira", "Brian Gutiérrez", "Gilberto Mora", "Álvaro Fidalgo", "Obed Vargas", "Orbelin Pineda", "Edson Álvarez", "Luis Chávez",
    "Alexis Vega", "César Huerta", "Armando González", "Guillermo Martínez", "Roberto Alvarado", "Julián Quiñones", "Raúl Jiménez", "Santiago Giménez",
    # Zuid-Afrika
    "Bradley Cross", "Samukele Kabini", "Olwethu Makhanya", "Thabang Matuludi", "Mbekezeli Mbokazi", "Aubrey Modiba", "Khuliso Mudau", "Khulumani Ndamane",
    "Ime Okon", "Nkosinathi Sibisi", "Kamogelo Sebelebele", "Jayden Adamas", "Thalente Mbatha", "Teboho Mokoena", "Sphephelo Sithole",
    "Oswin Appollis", "Lyle Foster", "Thapelo Maseko", "Evidence Makgopa", "Relebohile Mofokeng", "Tshepang Moremi", "Iqraam Rayners", "Themba Zwane",
    # Zuid-Korea
    "Kim Moon-hwan", "Kim Min-jae", "Kim Tae-hyeon", "Park Jin-seob", "Seol Young-woo", "Jens Castrop", "Lee Ki-hyuk", "Lee Tae-seok",
    "Lee Han-beom", "Cho Yu-min", "Kim Jin-Kyu", "Bae Jun-ho", "Paik Seung-ho", "Yang Hyun-jun", "Eom Ji-sung", "Lee Kang-in", "Lee Dong-gyeong", "Lee Jae-sung",
    "Hwang In-beom", "Hwang Hee-chan", "Son Heung-min", "Oh Hyeon-gyu", "Cho Gue-sung",
    # Tsjechië
    "Vladimír Coufal", "David Doudera", "Tomás Holes", "Robin Hranác", "Stepán Chaloupek", "David Jurásek", "Ladislav Krejcí", "Jaroslav Zelený",
    "David Zima", "Lukás Cerv", "Vladimír Darida", "Lukás Provod", "Michal Sadílek", "Hugo Sochurek", "Alexandr Sojka", "Tomás Soucek", "Pavel Sulc",
    "Denis Visinský", "Adam Hlozek", "Tomás Chorý", "Mojmír Chytil", "Jan Kuchta", "Patrik Schick",
    # Canada
    "Moïse Bombito", "Derek Cornelius", "Alphonso Davies", "Luc de Fougerolles", "Alistair Johnston", "Alfie Jones", "Richie Laryea", "Niko Sigur",
    "Joel Waterman", "Ali Ahmed", "Tajon Buchanan", "Mathieu Choinière", "Stephen Eustáquio", "Marcelo Flores", "Ismaël Koné", "Liam Millar", "Jonathan Osorio",
    "Nathan Saliba", "Jacob Shaffelburg", "Jonathan David", "Promise David", "Cyle Larin", "Tani Oluwaseyi",
    # Bosnië en Herzegovina
    "Sead Kolasinac", "Amar Dedic", "Nihad Mujakic", "Nikola Katic", "Tarik Muharemovic", "Stjepan Radeljic", "Dennis Hadzikadunic", "Nidal Celik",
    "Amir Hadziahmetovic", "Ivan Sunjic", "Ivan Basic", "Dzenis Burnic", "Ermin Mahmic", "Benjamin Tahirovic", "Amar Memic", "Armin Gigovic",
    "Kerim Alajbegovic", "Esmir Bajraktarevic", "Ermedin Demirovic", "Jovo Lukic", "Samed Bazdar", "Haris Tabakovic", "Edin Dzeko",
    # Qatar
    "Pedro Miguel", "Sultan Al Brake", "Al-Hashmi Al-Hussain", "Ayoub Al-Alawi", "Issa Laye", "Lucas Mendes", "Boualem Khoukhi", "Homam El-Amin",
    "Ahmed Fathi", "Jassim Gaber", "Assim Madibo", "Abdulaziz Hatem", "Karim Boudiaf", "Mohammed Mannai", "Almoez Ali", "Akram Afif", "Tahsin Jamshid", "Edmílson Junior",
    "Ahmed Alaaeldin", "Hassan Al-Haydos", "Ahmed Al-Ganehi", "Mohammed Muntari", "Yusuf Abdurisag",
    # Zwitserland
    "Ricardo Rodríguez", "Manuel Akanji", "Silvan Widmer", "Miro Muheim", "Nico Elvedi", "Eray Cömert", "Aurèle Amenda", "Luca Jaquez",
    "Remo Freuler", "Granit Xhaka", "Djibril Sow", "Denis Zakaria", "Johan Manzambi", "Ardon Jashari", "Christian Fassnacht", "Michel Aebischer",
    "Fabian Rieder", "Noah Okafor", "Dan Ndoye", "Zeki Amdouni", "Breel Embolo", "Ruben Vargas", "Cedric Itten",
    # Brazilië
    "Alex Sandro", "Bremer", "Danilo", "Douglas Santos", "Gabriel Magalhães", "Leo Pereira", "Marquinhos", "Roger Ibañez", "Wesley",
    "Bruno Guimarães", "Casemiro", "Fabinho", "Lucas Paquetá", "Endrick", "Gabriel Martinelli", "Igor Thiago", "Luiz Henrique",
    "Matheus Cunha", "Neymar", "Raphinha", "Rayan", "Vinícius Júnior",
    # Haïti
    "Carlens Arcus", "Wilguens Paugain", "Ricardo Adé", "Jean Kévin Duverne", "Hannes Delcroix", "Keeto Thermoncy", "Martin Expérience", "Duke Lacroix",
    "Josué Casimir", "Leverton Pierre", "Dominique Simon", "Woodensky Pierre", "Carl Fred Sainté", "Danley Jean-Jacques", "Jean Ricner Bellegarde",
    "Duckens Nazon", "Frantzdy Pierrot", "Deedson Louicius", "Ruben Providence", "Yassin Fortuné", "Wilson Isidor", "Lenny Joseph", "Derrick Etienne jr.",
    # Marokko
    "Nayef Aguerd", "Youssef Belammari", "Issa Diop", "Achraf Hakimi", "Redouane Halhal", "Noussair Mazraoui", "Zakaria El Ouahdi", "Chadi Riad",
    "Anass Salah-Eddine", "Sofyan Amrabat", "Neil El Aynaoui", "Ayyoub Bouaddi", "Bilal El Khannouss", "Samir El Mourabet", "Azzedine Ounahi", "Ismael Saibari",
    "Ayoube Amaimouni", "Brahim Díaz", "Abde Ezzalzouli", "Ayoub El Kaabi", "Gessime Yassine", "Soufiane Rahimi", "Chemsdine Talbi",
    # Schotland
    "Grant Hanley", "Jack Hendry", "Aaron Hickey", "Dom Hyam", "Scott McKenna", "Nathan Patterson", "Anthony Ralston", "Andy Robertson",
    "John Souttar", "Kieran Tierney", "Ryan Christie", "Findlay Curtis", "Lewis Ferguson", "Ben Gannon-Doak", "Tyler Fletcher", "John McGinn", "Kenny McLean", "Scott McTominay",
    "Ché Adams", "Lyndon Dykes", "George Hirst", "Lawrence Shankland", "Ross Stewart",
    # Australië
    "Aziz Behich", "Jordan Bos", "Cameron Burgess", "Alessandro Circati", "Milos Degenek", "Jason Geria", "Lucas Herrington", "Jacob Italiano",
    "Harry Souttar", "Kai Trewin", "Cameron Devlin", "Ajdin Hrustic", "Jackson Irvine", "Connor Metcalfe", "Paul Okon-Engstler", "Aiden O'Neill",
    "Nestory Irankunda", "Mathew Leckie", "Awer Mabil", "Mohamed Touré", "Nishan Velupillay", "Cristian Volpato", "Tete Yengi",
    # Paraguay
    "Juan José Cáceres", "Gustavo Velázquez", "Gustavo Gómez", "Júnior Alonso", "José Canale", "Omar Alderete", "Alexandro Maidana", "Fabián Balbuena",
    "Diego Gómez", "Mauricio Magalhães", "Damián Bobadilla", "Braian Ojeda", "Andrés Cubas", "Matías Galarza", "Alejandro Romero Gamarra",
    "Gustavo Caballero", "Ramons Sosa", "Áxl Arce", "Isidro Pitta", "Gabriel Ávalos", "Miguel Almirón", "Julio Enciso", "Antonio Sanabria",
    # Turkije
    "Abdülkerim Bardakci", "Çaglar Söyüncü", "Eren Elmali", "Ferdi Kadioglu", "Merih Demiral", "Mert Müldür", "Ozan Kabak", "Samet Akaydin", "Zeki Çelik",
    "Hakan Çalhanoglu", "İsmail Yüksek", "Kaan Ayhan", "Orkun Kökçü", "Salih Özcan", "Arda Güler", "Can Uzun", "Baris Alper Yilmaz", "Deniz Gül", "İrfan Can Kahveci", "Kenan Yildiz",
    "Kerem Aktürkoglu", "Oguz Aydin", "Yunus Akgün",
    # Verenigde Staten
    "Max Arfsten", "Sergiño Dest", "Alex Freeman", "Mark McKenzie", "Chris Richards", "Tim Ream", "Antonee Robinson", "Miles Robinson",
    "Joe Scally", "Auston Trusty", "Brenden Aaronson", "Tyler Adams", "Sebastian Berhalter", "Weston McKennie", "Cristian Roldan", "Malik Tillman",
    "Folarin Balogun", "Ricardo Pepi", "Christian Pulisic", "Gio Reyna", "Tim Weah", "Haji Wright", "Alejandro Zendejas",
    # Ecuador
    "Willian Pacho", "Piero Hincapie", "Joel Ordóñez", "Félix Torres", "Pervis Estupiñán", "Yaimar Medina", "Ángelo Preciado", "Jackson Porozo",
    "Alan Minda", "Moisés Caicedo", "Jordy Alcívar", "Denil Castillo", "John Yeboah", "Alan Franco", "Pedro Vite", "Kendry Páez",
    "Nilson Angulo", "Gonzalo Plata", "Kevin Rodríguez", "Anthony Valencia", "Enner Valencia", "Jordy Caicedo", "Jeremy Arévalo",
    # Duitsland
    "Waldemar Anton", "Nathaniel Brown", "David Raum", "Antonio Rüdiger", "Nico Schlotback", "Jonathan Tah", "Malick Thiaw", "Nadiem Amiri", "Leon Goretzka", "Pascal Gross", "Lennart Karl",
    "Joshua Kimmich", "Jamal Musiala", "Felix Nmecha", "Aleksandar Pavlovic", "Angelo Stiller", "Florian Wirtz", "Kai Havertz", "Maximilian Beier", "Jamie Leweling", "Leroy Sané",
    "Deniz Undav", "Nick Woltemade",
    # Ivoorkust
    "Emmanuel Agbadou", "Clément Akpa", "Ousmane Diomande", "Guéla Doué", "Ghislain Konan", "Odilon Kossounou", "Evan Ndicka", "Wilfried Singo",
    "Seko Fofana", "Parfait Guiagon", "Christ Inao Oulaï", "Franck Kessié", "Ibrahim Sangaré", "Jean-Michaël Seri", "Simon Adingra", "Ange-Yoan Bonny", "Amada Diallo", "Oumar Diakité",
    "Yan Diomande", "Evann Guessand", "Nicolas Pépé", "Bazoumana Touré", "Elye Wahi",
    # Curaçao
    "Riechedly Bazoer", "Joshua Brenet", "Roshon van Eijma", "Sherel Floranus", "Deveron Fonville", "Jurjen Gaari", "Armando Obispo", "Shurandy Sambo",
    "Juninho Bacuna", "Leandro Bacuna", "Livano Comenencia", "Kevin Felida", "Ar'jany Martha", "Tyrese Noslin", "Godfried Roemeratoe",
    "Jeremy Antonisse", "Tahith Chong", "Sontje Hansen", "Kenji Gorré", "Gervane Kastaneer", "Brandley Kuwas", "Jürgen Locadia", "Jearl Margaritha",
    # Nederland
    "Nathan Aké", "Virgil van Dijk", "Denzel Dumfries", "Jorrel Hato", "Jan Paul van Hecke", "Jurriën Timber", "Micky van de Ven",
    "Ryan Gravenberch", "Frenkie de Jong", "Justin Kluivert", "Teun Koopmeiners", "Tijjani Reijnders", "Marten de Roon", "Guus Til", "Quinten Timber", "Mats Wieffer",
    "Brian Brobbey", "Memphis Depay", "Cody Gakpo", "Noa Lang", "Donyell Malen", "Crysencio Summerville", "Wout Weghorst",
    # Japan
    "Yuta Nagatamo", "Shogo Taniguchi", "Ko Itakura", "Tsuyoshi Watanabe", "Takehiro Tomiyasu", "Hiroki Ito", "Ayumu Seko", "Yukinari Sugawara",
    "Junnosuke Suzuki", "Wataru Endo", "Junya Ito", "Daichi Kamada", "Ritsu Doan", "Ao Tanaka", "Keito Nakamura", "Kaishu Sano", "Takefusa Kubo", "Yuito Suzuki",
    "Koki Ogawa", "Daizen Maeda", "Ayase Ueda", "Kento Shiogai", "Keisuke Goto",
    # Zweden
    "Victor Lindelöf", "Isak Hien", "Gustaf Lagerbielke", "Carl Starfelt", "Gabriel Gudmundsson", "Daniel Svensson", "Herman Johansson", "Eric Smith",
    "Hjalmar Ekdal", "Elliot Stroud", "Besfort Zeneli", "Mattias Svanberg", "Jesper Karlström", "Yasin Ayari", "Lucas Bergvall", "Viktor Gyökeres", "Alexander Isak", "Anthony Elanga", "Benjamin Nygren",
    "Alexander Bernhardsson", "Ken Sema", "Gustaf Nilsson", "Taha Ali",
    # Tunesië
    "Yan Valéry", "Moutaz Neffati", "Dylan Bronn", "Raed Chikhaoui", "Montassar Talbi", "Adem Arous", "Omar Rekik", "Ali Abdi", "Mohamed Ben Hmida",
    "Ellyes Skhiri", "Anis Ben Slimane", "Rani Khedira", "Mortada Ben Ouanes", "Ismaël Gharbi", "Mohamed Hadj-Mahmoud", "Hannibal Mejrbi", "Elias Saad", "Khalil Ayari", "Elias Achouri", "Sebastien Tounekti",
    "Hazem Mastouri", "Firas Chawat", "Rayan Elloumi",
    # België
    "Maxim De Cuyper", "Timothy Castagne", "Thomas Meunier", "Joaquin Seys", "Brandon Mechele", "Koni De Winter", "Zeno Debast", "Arthur Theate", "Nathan Ngoy",
    "Kevin De Bruyne", "Amadou Onana", "Nicolas Raskin", "Youri Tielemans", "Hans Vanaken", "Alex Witsel", "Charles De Ketelaere", "Jérémy Doku", "Matías Fernández-Pardo",
    "Romelu Lukaku", "Dodi Lukébakio", "Diego Moreira", "Alexis Saelemaekers", "Leandro Trossard",
    # Egypte
    "Mohamed Hany", "Tarek Alaa", "Hamdi Fathi", "Rami Rabia", "Yasser Ibrahim", "Hossam Abdelmaguid", "Mohamed Abdelmonemn", "Ahmed Fattouh", "Karim Hafez",
    "Marwan Attia", "Mohanad Lasheen", "Nabil Emad", "Mahmoud Saber", "Zizo", "Emam Ashour", "Ahmed Raouf", "Mahmoud Trezeguet", "Ibrahim Adel", "Haissem Hassan",
    "Omar Marmoush", "Mohamed Salah", "Hamza Abdelkarim",
    # Iran
    "Danial Eiri", "Ehsan Hajsafi", "Saleh Hardani", "Hossein Kanaani", "Shoja Khalilzadeh", "Milad Mohammadi", "Ali Nemati", "Omid Noorafkan", "Ramin Rezaeian",
    "Rouzbeh Cheshmi", "Saeid Ezatolahi", "Mehdi Ghaedi", "Saman Ghoddos", "Mohammad Ghorbani", "Alireza Jahanbakhsh", "Mohammad Mohebi", "Amir Mohammad Razzaghinia", "Mehdi Torabi", "Aria Yousefi",
    "Ali Alipour", "Dennis Dargahi", "Amirhossein Hosseinzadeh", "Amirhossein Mahmoudi", "Mehdi Taremi",
    # Nieuw-Zeeland
    "Tim Payne", "Francis De Vries", "Tyler Bindon", "Michael Boxall", "Liberato Cacace", "Nando Pijnaker", "Finn Surman", "Callan Elliot", "Tommy Smith",
    "Joe Bell", "Marko Stamenic", "Alex Rufer", "Ryan Thomas", "Lachlan Bayliss", "Matt Garbett", "Chris Wood", "Sarpreet Singh", "Eli Just",
    "Kosta Barbarouses", "Ben Waine", "Ben Old", "Callum McCowatt", "Jesse Randall",
    # Kaapverdië
    "Diney Borges", "Sidny Cabral", "Logan Costa", "Roberto Pico Lopes", "Steven Moreira", "Wagner Pina", "Kelvin Pires", "Stopira",
    "Telmo Arcanjo", "Deroy Duarte", "Laros Duarte", "João Paulo Fernandes", "Jamiro Monteiro", "Kevin Pina", "Yannick Semedo", "Jovane Cabral", "Nuno da Costa", "Dailon Livramento", "Ryan Mendes",
    "Garry Rodrigues", "Willy Semedo", "Gilson Benchimol Tavares", "Hélio Varela",
    # Saoedi-Arabië
    "Saud Abdulhamid", "Jehad Thakri", "Abdulelah Al-Amri", "Hassan Tambakti", "Ali Lajami", "Hassan Kadesh", "Moteb Al-Harbi", "Ali Majrashi",
    "Mohammed Abu Al-Shamat", "Ayman Yahya", "Ziyad Al-Johani", "Nasser Al-Dawsari", "Mohamed Kanno", "Abdullah Al-Khaibari", "Nawaf Boushal", "Alaa Hejji", "Musab Al-Juwayr",
    "Abdullah Al-Hamdan", "Khalid Al-Ghannam", "Sultan Mandash", "Salem Al-Dawsari", "Firas Al-Buraikan", "Saleh Al-Shehri",
    # Spanje
    "Pedro Porro", "Marcos Llorente", "Pau Cubarsí", "Eric García", "Aymeric Laporte", "Marc Cucurella", "Alejandro Grimaldo", "Marc Pubill",
    "Rodrigo", "Martín Zubimendi", "Mikel Merino", "Pedri", "Gavi", "Fabián Ruiz", "Álex Baena", "Lamine Yamal", "Ferran Torres", "Dani Olmo", "Nico Williams",
    "Mikel Oyarzabal", "Borja Iglesias", "Victor Muñoz", "Yéremy Pino",
    # Uruguay
    "Guillermo Varela", "Ronald Araújo", "José María Giménez", "Santiago Bueno", "Sebastián Cáceres", "Mathías Olivera", "Joaquín Piquerez", "Matías Viña",
    "Manuel Ugarte", "Emiliano Martínez", "Rodrigo Bentancur", "Federico Valverde", "Agustín Canobbio", "Juan Manuel Sanabria", "Giorgian de Arrascaeta", "Nicolás de la Cruz", "Rodrigo Zalazar",
    "Facundo Pellistri", "Maximiliano Araújo", "Brian Rodríguez", "Rodrigo Aguirre", "Federico Viñas", "Darwin Núñez",
    # Frankrijk
    "Lucas Digne", "Malo Gusto", "Lucas Hernández", "Theo Hernández", "Ibrahima Konaté", "Jules Koundé", "Maxence Lacroix", "William Saliba", "Dayot Upamecano",
    "N'Golo Kanté", "Manu Koné", "Adrien Rabiot", "Aurélien Tchouaméni", "Warren Zaïre-Emery", "Maghnes Akliouche", "Bradley Barcola", "Rayan Cherki", "Ousmane Dembélé",
    "Désiré Doué", "Jean-Philippe Mateta", "Kylian Mbappé", "Michael Olise", "Marcus Thuram",
    # Irak
    "Hussein Ali", "Manaf Younis", "Zaid Tahseen", "Rebin Sulaka", "Akam Hashem", "Merchas Doski", "Ahmed Yahya", "Zaid Ismail", "Frans Putros", "Mustafa Saadoon",
    "Amir Al Ammari", "Kevin Yakob", "Zidane Iqbal", "Aimar Sher", "Ibrahim Bayesh", "Ahmed Qasim", "Youssef Amyn", "Marko Farji", "Ali Jassim", "Ali Al Hamadi", "Ali Yousif", "Aymen Hussein",
    "Mohanad Ali",
    # Noorwegen
    "Kristoffer Vassbakk Ajer", "Fredrik Bjørkan", "Henrik Falchener", "Sondre Langas", "Torbjørn Heggem", "Marcus Pedersen", "Julian Ryerson", "David Møller Wolfe", "Leo Østungard",
    "Fredrik Aursnes", "Patrick Berg", "Sander Berge", "Morten Thorsby", "Kristian Thorstvedt", "Martin Ødegaard", "Thelonious Aasgaard", "Oscar Bobb", "Jens Petter Hauge", "Antonio Nusa", "Andreas Schjelderup",
    "Erling Braut Haaland", "Jørgen Strand Larsen", "Alexander Sørloth",
    # Senegal
    "Krépin Diatta", "El Hadji Malick Diouf", "Ismail Jakobs", "Kalidou Koulibaly", "Antoine Mendy", "Moussa Niakhaté", "Mamadou Sarr", "Abdoulaye Seck",
    "Lamine Camara", "Pathé Ciss", "Habib Diarra", "Gana Gueye", "Pape Gueye", "Bara Sapoko Ndiaye", "Pape Sarr", "Assane Diao", "Bamba Dieng", "Nicolas Jackson", "Sadio Mané",
    "Ibrahim Mbaye", "Cherif Ndiaye", "Iliman Ndiaye", "Ismaïla Sarr",
    # Algerije
    "Rafik Belghali", "Samir Chergui", "Rayan Aït-Nouri", "Jaouen Hadjam", "Aïssa Mandi", "Ramy Bensebaïni", "Zineddine Belaïd", "Achref Abada", "Mohamed Amine Tougaï",
    "Nabil Bentaleb", "Hicham Boudaoui", "Houssem Aouar", "Farès Chaïbi", "Ibrahim Maza", "Yacine Titraoui", "Ramiz Zerrouki", "Mohamed Amine Amoura", "Nadhir Benbouali", "Adil Boulbina",
    "Farès Ghedjemis", "Amine Gouiri", "Anis Hadj Moussa", "Riyad Mahrez",
    # Argentinië
    "Gonzalo Montiel", "Nahuel Molina", "Lisandro Martínez", "Nicolás Otamendi", "Leonardo Balerdi", "Cristian Romero", "Nicolás Tagliafico", "Facundo Medina",
    "Giovani Lo Celso", "Leandro Paredes", "Rodrigo De Paul", "Exequiel Palacios", "Enzo Fernández", "Alexis Mac Allister", "Valentín Barco", "Thiago Almada", "Nico Paz",
    "Lionel Messi", "Nicolás González", "Giuliano Simeone", "Lautaro Martínez", "José Manuel López", "Julián Álvarez",
    # Oostenrijk
    "David Affengruber", "David Alaba", "Kevin Danso", "Marco Friedl", "Philipp Lienhart", "Phillipp Mwene", "Stefan Posch", "Alexander Prass", "Michael Svoboda",
    "Christoph Baumgartner", "Carney Chukwuemeka", "Florian Grillitsch", "Konrad Laimer", "Marcel Sabitzer", "Xaver Schlager", "Romano Schmid", "Alessandro Schöpf", "Nicolas Seiwald", "Paul Wanner", "Patrick Wimmer",
    "Marko Arnautovic", "Michael Gregoritsch", "Sasa Kalajdzic",
    # Jordanië
    "Mohammad Abu Hashish", "Abdallah Nasib", "Husam Abu Dahab", "Yazan Al-Arab", "Mo Abualnadi", "Salim Obaid", "Saed Al-Rosan", "Ihsan Haddad", "Anas Badawi",
    "Amer Jamous", "Noor Al-Rawabdeh", "Rajaei Ayed", "Ibrahim Sadej", "Mohannad Abu Taha", "Nizer Al-Rashdan", "Mohammad Al-Dawoud", "Mohammad Abu Zrayq", "Ali Olwan", "Musa Al-Taamari", "Odeh Al-Fakhouri",
    "Mahmoud Al-Mardi", "Ibrahim Sabra", "Ali Azaizeh",
    # Colombia
    "Santiago Arias", "Willer Ditta", "Jhon Lucumí", "Deiver Machado", "Yerry Mina", "Johan Mojica", "Daniel Muñoz", "Davinson Sánchez",
    "Jhon Arias", "Jorge Carrascal", "Kevin Castaño", "Jefferson Lerma", "Juan Portilla", "Gustavo Puerta", "Juan Fernando Quintero", "Richard Ríos", "James Rodríguez",
    "Jaminton Campaz", "Jhon Córdoba", "Luís Díaz", "Andrés Gómez", "Cucho Hernandez", "Luis Suárez",
    # DR Congo
    "Aaron Wan-Bissaka", "Jeremy Ngakia", "Joris Kayembe", "Arthur Masuaku", "Steve Kapuadi", "Rocky Bushiri", "Axel Tuanzebe", "Chancel Mbemba", "Dylan Batubinsika",
    "Noah Sadiki", "Samuel Moutoussamy", "Edo Kayembe", "Ngal'ayel Mukau", "Charles Pickel", "Nathanaël Mbuku", "Brian Cipenga", "Grady Diangana", "Meschack Elia", "Théo Bongonda",
    "Fiston Mayele", "Cédric Bakambu", "Simon Banza", "Yoane Wissa",
    # Portugal
    "Tomás Araújo", "João Cancelo", "Diogo Dalot", "Rúben Dias", "Gonçalo Inácio", "Nuno Mendes", "Matheus Nunes", "Nélson Semedo", "Renato Veiga",
    "Samú Costa", "Bruno Fernandes", "João Neves", "Rúben Neves", "Bernardo Silva", "Vitinha", "Francisco Conceição", "João Félix", "Gonçalo Guedes", "Rafael Leão",
    "Pedro Neto", "Gonçalo Ramos", "Cristiano Ronaldo", "Francisco Trincão",
    # Oezbekistan
    "Abdulla Abdullaev", "Khojiakbar Alijonov", "Rustam Ashurmatov", "Umar Eshmurodov", "Bekhruz Karimov", "Abdukodir Khusanov", "Sherzod Nasrullaev", "Farrukh Sayfiev", "Avazbek Ulmasaliev",
    "Jakhongir Urozov", "Azizjon Ganiev", "Odiljon Hamrobekov", "Jamshid Iskanderov", "Akmal Mozgovoy", "Otabek Shukurov", "Azizbek Amonov", "Abbosbek Fayzullaev", "Dostonbek Khamdamov",
    "Jaloliddin Masharipov", "Igor Sergeev", "Eldor Shomurodov", "Oston Urunov",
    # Engeland
    "Dan Burn", "Marc Guehi", "Reece James", "Ezri Konsa", "Tino Livramento", "Nico O'Reilly", "Jarell Quansah", "John Stones", "Djed Spence",
    "Elliot Anderson", "Jude Bellingham", "Jordan Henderson", "Kobbie Mainoo", "Declan Rice", "Morgan Rogers", "Eberechi Eze", "Harry Kane", "Anthony Gordon", "Noni Madueke",
    "Marcus Rashford", "Bukayo Saka", "Ivan Toney", "Ollie Watkins",
    # Kroatië
    "Duje Caleta-Car", "Martin Erlic", "Josko Gvardiol", "Marin Pongracic", "Josip Stanisic", "Josip Sutalo", "Luka Vuskovic",
    "Martin Baturina", "Toni Fruk", "Kristijan Jakic", "Mateo Kovacic", "Luka Modric", "Nikola Moro", "Mario Pasalic", "Luka Sucic", "Petar Sucic", "Nikola Vlasic",
    "Ante Budimir", "Andrej Kramaric", "Igor Matanovic", "Petar Musa", "Marco Pasalic", "Ivan Perisic",
    # Ghana
    "Jonas Adjetey", "Derrick Luckassen", "Gideon Mensah", "Abdul Mumin", "Jerome Opoku", "Kojo Peprah Oppong", "Abdul Rahman Baba", "Alidu Seidu", "Marvin Senaya",
    "Augustine Boakye", "Abdul Fatawu", "Elisha Owusu", "Thomas Partey", "Kwasi Sibo", "Kamaldeen Sulemana", "Caleb Yirenkyi", "Prince Kwabena Adu", "Jordan Ayew", "Christopher Bonsu Baah",
    "Ernest Nuamah", "Antoine Semenyo", "Brandon Thomas-Asante", "Iñaki Williams",
    # Panama
    "Andrés Andrade", "César Blackman", "José Córdoba", "Éric Davis", "Fidel Escobar", "Edgardo Fariña", "Jorge Gutiérrez", "Amir Murillo", "Jiovany Ramos", "Roderick Miller",
    "Yoel Bárcenas", "Adalberto Carrasquilla", "Aníbal Godoy", "Carlos Harvey", "Azarias Londoño", "Cristian Martínez", "Alberto Quintero", "José Luis Rodriguez", "César Yanis",
    "Ismael Díaz", "José Fajardo", "Tomás Rodríguez", "Cecilio Waterman"
]

# Gesorteerde, gededupliceerde spelerslijst voor de multiselect
TOPSPELERS: list[str] = sorted(set(_SPELERS_RAW))

# ────────────────────────────────────────────────────────────
# 1. PAGINA-CONFIGURATIE
# ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="WK Poule 2026 – Kompas Publishing",
    page_icon="⚽",
    layout="centered",
)

st.markdown("""
<style>
    .wk-title { font-size:2.4rem; font-weight:800; text-align:center; color:#FF7A00; margin:0; line-height:1.1; }
    .wk-sub   { text-align:center; color:#888; font-size:0.95rem; margin:0.3rem 0 1.2rem; }
    div[data-testid="stExpander"] summary { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────
# 2. SESSION STATE
# ────────────────────────────────────────────────────────────

if f"ingestuurd_{HUIDIGE_RONDE}" not in st.session_state:
    st.session_state[f"ingestuurd_{HUIDIGE_RONDE}"] = False

# ────────────────────────────────────────────────────────────
# 3. HEADER
# ────────────────────────────────────────────────────────────

st.markdown('<p class="wk-title">⚽ WK Poule 2026</p>', unsafe_allow_html=True)
st.markdown(f'<p class="wk-sub">Kompas Publishing – {HUIDIGE_RONDE} · 48 landen · Jouw voorspelling</p>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────
# 4. HOOFD-TABS
# ────────────────────────────────────────────────────────────

main_tab1, main_tab2 = st.tabs(["📝 Voorspellingen Insturen", "🏆 Live Klassement"])

# ============================================================
# TAB 1 – VOORSPELLINGEN
# ============================================================

with main_tab1:

    if st.session_state.get(f"ingestuurd_{HUIDIGE_RONDE}", False):
        st.success(
            f"✅ Je voorspellingen voor **{HUIDIGE_RONDE}** zijn succesvol verwerkt! "
            "Check het **🏆 Live Klassement**-tabblad om de actuele stand te bekijken."
        )
    else:
        st.info(f"**{HUIDIGE_RONDE} is geopend.** Vul hieronder de 24 wedstrijden in en kies je 4 topscorers.")

        with st.form(f"wk_poule_{HUIDIGE_RONDE.lower().replace(' ', '_')}", border=False):

            # ── Sectie 1: Persoonsgegevens ──────────────────
            st.subheader("👤 Jouw gegevens")
            with st.container(border=True):
                nickname_val = st.text_input("Nickname *", placeholder="Bijv. VoetbalFan88", key="nickname")
                email_val = st.text_input("E-mailadres *", placeholder="naam@kompas.nl", key="email")

            st.divider()

            # ── Sectie 2: Wedstrijdvoorspellingen ───────────
            st.subheader(f"⚽ Wedstrijdvoorspellingen – {HUIDIGE_RONDE}")
            st.caption("Vul per wedstrijd de uitslag in (bijv. **2-1**), kies de kaartenmarge en het doelpuntmoment.")

            uitslag_vals, gele_vals, tijd_vals = {}, {}, {}
            oranje_min_val, oranje_overtreding_val, oranje_wissel_val = 15, 10, 60

            wed_tabs = st.tabs(["🌍 Wedstrijden 1–6", "🌍 Wedstrijden 7–12", "🌍 Wedstrijden 13–18", "🌍 Wedstrijden 19–24"])

            for tab_idx, (wtab, start) in enumerate(zip(wed_tabs, [0, 6, 12, 18])):
                with wtab:
                    for local_i in range(6):
                        global_i = start + local_i
                        wed = WEDSTRIJDEN[global_i]
                        with st.expander(f"⚽ {wed}"):
                            uitslag_vals[wed] = st.text_input("Uitslag (bijv. 2-1)", placeholder="bijv. 2-1", key=f"u_{global_i}")
                            gele_vals[wed] = st.selectbox("Gele kaarten", GELE_KAARTEN_OPTIES, key=f"g_{global_i}")
                            tijd_vals[wed] = st.selectbox("Tijd 1e doelpunt", TIJD_DOELPUNT_OPTIES, key=f"t_{global_i}")

                            # Waterdichte Dagspecials per ronde (ongevoelig voor exacte trema's/spatiering)
                            if "Nederland" in wed and "Japan" in wed:
                                st.markdown("🟠 **Oranje Special!** In welke minuut verwacht jij het eerste schot op doel van Nederland?")
                                oranje_min_val = st.number_input("Minuut 1e schot op doel", min_value=1, max_value=90, value=15, key="oranje_schot_min")
                            elif "Nederland" in wed and "Zweden" in wed:
                                st.markdown("🟠 **Oranje Special!** In welke minuut verwacht jij de eerste overtreding van Nederland?")
                                oranje_overtreding_val = st.number_input("Minuut 1e overtreding", min_value=1, max_value=90, value=10, key="oranje_overtreding_min")
                            elif "Tunesi" in wed and "Nederland" in wed:
                                st.markdown("🟠 **Oranje Special!** In welke minuut valt de **allereerste wissel** aan de kant van het Nederlands Elftal?")
                                oranje_wissel_val = st.number_input("Minuut 1e wissel Nederland", min_value=1, max_value=90, value=60, key="oranje_wissel_min")

            st.divider()

            # ── Sectie 3: Bonusvragen ────────────────────────
            st.subheader("🏆 Bonusvragen")

            if HUIDIGE_RONDE == "Ronde 1":
                kampioen_val = st.selectbox("Wie wordt wereldkampioen? *", [_PH_LAND] + LANDEN, key="kampioen")
            else:
                kampioen_val = None
                st.caption("🔒 De kampioenskeuze staat definitief vast en is gesloten na Ronde 1.")

            topscorer_val = st.multiselect("Kies precies 4 topscorers (type een naam om te zoeken) *", TOPSPELERS, max_selections=4, key="topscorers")
            if topscorer_val:
                st.caption(f"Geselecteerd: {len(topscorer_val)}/4")

            st.divider()

            # ── Submit Knop ──────────────────────────────────
            submitted = st.form_submit_button(f"📨 Insturen – {HUIDIGE_RONDE}", use_container_width=True, type="primary")

        # ── Verwerking na Submit ─────────────────────────────
        if submitted:
            fouten = []

            if not nickname_val.strip(): fouten.append("Vul je nickname in.")
            if not email_val.strip() or "@" not in email_val: fouten.append("Vul een geldig e-mailadres in.")
            if HUIDIGE_RONDE == "Ronde 1" and kampioen_val == _PH_LAND: fouten.append("Kies een wereldkampioen.")
            if len(topscorer_val) != 4: fouten.append(f"Selecteer precies 4 topscorers (nu {len(topscorer_val)} geselecteerd).")

            for wed in WEDSTRIJDEN:
                if not _UITSLAG_RE.match(uitslag_vals[wed].strip()): fouten.append(f"Uitslag incorrect of leeg bij '{wed}'.")
                if gele_vals[wed] == _PH: fouten.append(f"Gele kaarten ontbreken bij '{wed}'.")
                if tijd_vals[wed] == _PH: fouten.append(f"Tijd 1e doelpunt ontbreekt bij '{wed}'.")

            if fouten:
                st.error("⚠️ Je bent vergeten een aantal verplichte velden in te vullen. Loop de tabbladen rustig langs!")
            else:
                can_submit = True
                try:
                    resp_get = requests.get(APPS_SCRIPT_URL, timeout=6)
                    data_get = resp_get.json()
                    rows = data_get if isinstance(data_get, list) else data_get.get("data", [])
                    existing_for_ronde = [
                        str(r.get("E-mailadres", "")).strip().lower()
                        for r in rows if isinstance(r, dict) and r.get("Huidige Ronde") == HUIDIGE_RONDE
                    ]
                    if email_val.strip().lower() in existing_for_ronde:
                        st.error(f"🚨 Dit e-mailadres heeft al meegedaan voor **{HUIDIGE_RONDE}**! Dubbele inzendingen zijn geblokkeerd.")
                        can_submit = False
                except Exception:
                    pass

                if can_submit:
                    payload = {
                        "Huidige Ronde": HUIDIGE_RONDE,
                        "Nickname": nickname_val.strip(),
                        "E-mailadres": email_val.strip().lower(),
                    }
                    
                    if HUIDIGE_RONDE == "Ronde 1":
                        payload["Voorspelling Kampioen"] = kampioen_val
                        payload["Nederland - Japan (Minuut 1e schot op doel)"] = oranje_min_val
                        for j, speler in enumerate(topscorer_val, 1): payload[f"Topscorer Speler {j}"] = speler
                    elif HUIDIGE_RONDE == "Ronde 2":
                        payload["Nederland - Zweden (Minuut 1e overtreding)"] = oranje_overtreding_val
                        for j, speler in enumerate(topscorer_val, 1): payload[f"Topscorer Speler {j} (Ronde 2)"] = speler
                    elif HUIDIGE_RONDE == "Ronde 3":
                        payload["Tunesië - Nederland (Minuut 1e wissel door nederlands elftal)"] = oranje_wissel_val
                        for j, speler in enumerate(topscorer_val, 1): payload[f"Topscorer Speler {j} (Ronde 3)"] = speler

                    for wed in WEDSTRIJDEN:
                        payload[f"{wed} (Uitslag)"] = uitslag_vals[wed].strip()
                        payload[f"{wed} (Gele Kaarten)"] = gele_vals[wed]
                        payload[f"{wed} (Tijd 1e Doelpunt)"] = tijd_vals[wed]

                    try:
                        resp_post = requests.post(APPS_SCRIPT_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"}, timeout=12)
                        if resp_post.status_code == 200:
                            st.session_state[f"ingestuurd_{HUIDIGE_RONDE}"] = True
                            st.success(f"✅ Gelukt! Je voorspellingen voor **{HUIDIGE_RONDE}** zijn succesvol verwerkt en opgeslagen.")
                            st.balloons()
                        else:
                            st.error(f"Fout bij opslaan in centrale database (status {resp_post.status_code}).")
                    except Exception as e:
                        st.error(f"Verbindingsfout naar database: {e}")

# ============================================================
# TAB 2 – LIVE KLASSEMENT
# ============================================================

with main_tab2:
    st.markdown("### 📊 Live Klassement")
    st.info("Het klassement wordt elke 15 minuten herberekend. Ververs de pagina voor de allernieuwste data.")

    components.html(
        f'<iframe src="{DATASTUDIO_URL}" width="100%" height="700" style="border:0; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);" allowfullscreen sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>',
        height=720,
    )

# ────────────────────────────────────────────────────────────
# 5. FOOTER
# ────────────────────────────────────────────────────────────

st.divider()
st.caption("⚽ WK Poule 2026 · Kompas Publishing · Alleen voor intern gebruik")
