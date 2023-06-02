from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField, SubmitField

referendum_choices = [
    ('0', 'Kein Referendum'),
    ('1', '25.09.22 - Zusatzfinanzierung AHV'),
    ('2', ' - Änderung Bundesgesetz AHV'),
    ('3', ' - Verrechnungssteuer'),
    ('4', '15.05.22 - Filmproduktion'),
    ('5', ' - Transplantation'),
    ('6', ' - Schengen Besitzstand'),
    ('7', '13.02.22 - Stempelabgaben'),
    ('8', ' - Mediengesetz'),
    ('9', '28.11.21 - Covid 19 Gesetz'),
    ('10', '26.09.21 - Ehe für alle'),
    ('11', '13.06.21 - Covid 19 Gesetz'),
    ('12', ' - CO2 Gesetz'),
    ('13', ' - Bekämpfung Terrorismus'),
    ('14', '07.03.21 - E-ID Gesetz'),
    ('15', ' - Indonesien'),
    ('16', '27.09.20 - Jagdgesetz'),
    ('17', ' - Kinderdrittbetreuungskosten'),
    ('18', ' - Vaterschaftsurlaub'),
    ('19', ' - Kampfflugzeuge'),
    ('20', '09.02.20 - Straf / Militärgesetz'),
    ('21', '19.05.19 - Steuerreform / AHV Finanzierung'),
    ('22', ' - Waffengesetz')
]

yes_no_choices = [
    (1, 'Yes'),
    (2, 'No')
]

strategy_choices = [
    (0, 'No Strategy found'),
    (1, 'Information strategies'),
    (2, 'Moralization'),
    (3, 'Negative Campaigning'),
    (4, 'Encouragment'),
]

present_choices = [
    (0, 'Not present'),
    (1, 'Present')
]

neg_strat_choices = [
    (0, 'Not present'),
    (1, 'Acclaim'),
    (2, 'Attack'),
]

neg_focus_choices = [
    (0, 'Not clear'),
    (1, 'Issues or Positions'),
    (2, 'Qualities / Character'),
    (3, 'Qualities AND Character'),
]

neg_target_choices = [
    (10, 'Author of post'),
    (20, 'Government'),
    (30, 'Opposition'),
    (40, 'Specific Party'),
    (41, '- SVP'),
    (42, '- SP'),
    (43, '- FDP'),
    (44, '- Mitte'),
    (45, '- Grüne'),
    (46, '- GLP'),
    (50, 'Specific Person'),
    (51, '- SVP'),
    (52, '- SP'),
    (53, '- FDP'),
    (54, '- Mitte'),
    (55, '- Grüne'),
    (56, '- GLP'),
    (90, 'Other'),
]

person_choices = [
    (0, 'No mention'),
    (10, 'Mention of Party'),
    (20, 'Mention of Politician'),
    (21, 'SVP - Rösti / Chiesa'),
    (22, 'SP - Levrat / Wermuth/Meyer'),
    (23, 'FDP - Gössi / Burkhart'),
    (24, "Mitte - Pfister"),
    (25, 'GPS - Glättli'),
    (30, 'Mention of Party & Politician'),
]

person_priv_choices = [
    (1, 'Political Context'),
    (2, 'Personal Context')
]


class CodingForm(FlaskForm):
    referendum = SelectField('referendum', coerce=int, validators=None, choices=referendum_choices)
    direct_camp = RadioField('direct_camp', choices=yes_no_choices)
    strategy = RadioField('strategy', choices=strategy_choices)
    info_struct = RadioField('info_struct', choices=present_choices)
    info_posit = RadioField('info_posit', choices=present_choices)
    neg_strat = RadioField('neg_strat', choices=neg_strat_choices)
    neg_focus = RadioField('neg_focus', choices=neg_focus_choices)
    neg_inciv = RadioField('neg_inciv', choices=present_choices)
    twostep_strat = RadioField('twostep_strat', choices=present_choices)
    neg_targ = RadioField('neg_targ', choices=neg_target_choices)
    person_indiv = RadioField('person_indiv', choices=person_choices)
    person_priv = RadioField('person_priv', choices=person_priv_choices)

    submit = SubmitField('Submit')
