


class State:
    (ABIA,      ADAMAWA, AKWA_IBOM,   ANAMBRA, BAUCHI, BAYELSA, 
     BENUE,     BORNO,   CROSS_RIVER, DELTA,   EBOYIN, EDO,
     EKITI,     ENUGU,   GOMBE,       IMO,     JIGAWA, KADUNA, 
     KANO,      KATSINA, KEBBI,       KOGI,    KWARA,  LAGOS,
     NASSARAWA, NIGER,   OGUN,        ONDO,    OSUN,   OYO,
     PLATEAU,   RIVIERS, SOKOTO,      TARABA,  YOBE,   ZAMFARA,
     FCT) = (
        'AB', 'AD', 'AK', 'AN', 'BA', 'BY', 'BE', 'BO', 'CR', 'DE', 'EB', 'ED',
        'EK', 'EN', 'GO', 'IM', 'JI', 'KD', 'KN', 'KT', 'KE', 'KO', 'KW', 'LA', 
        'NA', 'NI', 'OG', 'ON', 'OS', 'OY', 'PL', 'RI', 'SO', 'TA', 'YO', 'ZA',
        'FC',
    )
    NORTH_CENTRAL_CHOICES = (
        (BENUE, 'Benue'), (KOGI,      'Kogi'), 
        (KWARA, 'Kwara'), (NASSARAWA, 'Nassarawa'), 
        (NIGER, 'Niger'), (PLATEAU,   'Plateau'),
        (FCT,   'FCT'),
    )
    NORTH_EAST_CHOICES = (
        (ADAMAWA, 'Adamawa'), (BAUCHI, 'Bauchi'),
        (BORNO,   'Borno'),   (GOMBE,  'Gombe'),
        (TARABA,  'Taraba'),  (YOBE,   'Yobe'),
    )
    NORTH_WEST_CHOICES = (
        (JIGAWA,  'Jigawa'), (KADUNA,  'Kaduna'),
        (KANO,    'Kano'),   (KATSINA, 'Katsina'),
        (KEBBI,   'Kebbi'),  (SOKOTO,  'Sokoto'),
        (ZAMFARA, 'Zamfara'),
    )
    SOUTH_EAST_CHOICES = (
        (ABIA,   'Abia'),   (ANAMBRA, 'Anambra'), 
        (EBOYIN, 'Eboyin'), (ENUGU,   'Enugu'), 
        (IMO,    'Imo'),
    )
    SOUTH_SOUTH_CHOICES = (
        (AKWA_IBOM,   'Akwa Ibom'),   (BAYELSA, 'Bayelsa'), 
        (CROSS_RIVER, 'Cross River'), (DELTA,   'Delta'), 
        (EDO,         'Edo'),         (RIVIERS, 'Rivers'), 
    )
    SOUTH_WEST_CHOICES = (
        (EKITI, 'Ekiti'), (LAGOS, 'Lagos'),
        (OGUN,  'Ogun'),  (ONDO,  'Ondo'),
        (OSUN,  'Osun'),  (OYO,   'Oyo')
    )
    ALL_CHOICES = (
        NORTH_CENTRAL_CHOICES + 
        NORTH_EAST_CHOICES + 
        NORTH_WEST_CHOICES +
        SOUTH_EAST_CHOICES +
        SOUTH_WEST_CHOICES +
        SOUTH_SOUTH_CHOICES
    )
